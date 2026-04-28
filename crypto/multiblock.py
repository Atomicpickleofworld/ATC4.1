#!/usr/bin/env python3
"""Мультиблочное шифрование/дешифрование + управление кодбазой"""
import os
import json
import base64
import hashlib
import hmac
import secrets
from datetime import datetime
from typing import Tuple, Dict, Optional
from pathlib import Path

from config import MAGIC_ATC4, FORMAT_VERSION, SALT_SIZE, MIN_BLOCK, MAX_BLOCK, TAG_SIZE, HMAC_SIZE
from crypto.core import derive_key, aead_encrypt, aead_decrypt, generate_key, build_aad
from crypto.core import NONCE_SIZE, CRYPTO_OK

def multiblock_encrypt(text: str, master_password: Optional[str] = None) -> Tuple[bytes, dict]:
    data = text.encode('utf-8')
    total = len(data)
    pos = 0
    blocks_ct, blocks_db = [], []
    global_salt = os.urandom(SALT_SIZE)
    timestamp = int(datetime.now().timestamp()).to_bytes(8, 'big')

    while pos < total:
        remaining = total - pos
        if remaining <= MIN_BLOCK:
            block_len = remaining
            key_len = MIN_BLOCK
        else:
            key_len = secrets.randbelow(MAX_BLOCK - MIN_BLOCK + 1) + MIN_BLOCK
            block_len = min(key_len, remaining)

        block_data = data[pos:pos + block_len]
        key_str = generate_key(key_len)
        block_salt = os.urandom(SALT_SIZE)
        key_bytes = derive_key(key_str, block_salt)
        block_idx = len(blocks_db)
        aad = build_aad(block_idx) + timestamp
        nonce, ct, tag = aead_encrypt(block_data, key_bytes, aad)

        block_packed = block_salt + nonce + tag + len(ct).to_bytes(4, 'big') + ct
        blocks_ct.append(block_packed)
        blocks_db.append({
            "idx": block_idx, "key": key_str, "key_len": key_len,
            "blk_len": block_len, "timestamp": datetime.now().isoformat()
        })
        pos += block_len

    header = MAGIC_ATC4 + FORMAT_VERSION.to_bytes(1, 'big') + global_salt + timestamp + len(blocks_ct).to_bytes(4, 'big')
    blob = header + b''.join(len(b).to_bytes(4, 'big') + b for b in blocks_ct)

    hmac_key = hashlib.blake2b(global_salt + timestamp, digest_size=32).digest()
    header_hmac = hmac.new(hmac_key, blob, hashlib.blake2b).digest()[:HMAC_SIZE]
    blob += header_hmac

    codebase = {
        "version": "4.1", "format": FORMAT_VERSION,
        "global_salt": global_salt.hex(), "timestamp": timestamp.hex(),
        "block_count": len(blocks_db), "blocks": blocks_db, "protected": False
    }
    if master_password and len(master_password) >= 16:
        db_json = json.dumps(codebase, ensure_ascii=False).encode('utf-8')
        db_salt = os.urandom(32)
        db_key = derive_key(master_password, db_salt)
        db_nonce, db_ct, db_tag = aead_encrypt(db_json, db_key, aad=b'ATCDB_v41')
        codebase = {
            "version": "4.1", "protected": True,
            "salt": db_salt.hex(), "nonce": db_nonce.hex(),
            "tag": db_tag.hex(), "data": base64.b64encode(db_ct).decode()
        }
    return blob, codebase

def multiblock_decrypt(blob: bytes, codebase: dict, master_password: Optional[str] = None) -> str:
    if codebase.get("protected"):
        if not master_password:
            raise ValueError("Кодбаза защищена паролем — введите мастер-пароль")
        db_salt = bytes.fromhex(codebase["salt"])
        db_nonce = bytes.fromhex(codebase["nonce"])
        db_tag = bytes.fromhex(codebase["tag"])
        db_ct = base64.b64decode(codebase["data"])
        db_key = derive_key(master_password, db_salt)
        db_json = aead_decrypt(db_nonce, db_ct, db_tag, db_key, aad=b'ATCDB_v41')
        codebase = json.loads(db_json.decode('utf-8'))

    if blob[:4] != MAGIC_ATC4:
        raise ValueError("Неверный формат .atc4 или файл повреждён")
    version = blob[4]
    if version != FORMAT_VERSION:
        raise ValueError(f"Неподдерживаемая версия: {version}. Ожидалась: {FORMAT_VERSION}")

    header_hmac = blob[-HMAC_SIZE:]
    blob_without_hmac = blob[:-HMAC_SIZE]
    global_salt = bytes.fromhex(codebase["global_salt"])
    timestamp = bytes.fromhex(codebase["timestamp"])
    hmac_key = hashlib.blake2b(global_salt + timestamp, digest_size=32).digest()
    expected_hmac = hmac.new(hmac_key, blob_without_hmac, hashlib.blake2b).digest()[:HMAC_SIZE]
    if not hmac.compare_digest(header_hmac, expected_hmac):
        raise ValueError("Файл повреждён или изменён (HMAC не совпадает)")

    block_count = codebase["block_count"]
    blocks_db = codebase["blocks"]
    off = 4 + 1 + SALT_SIZE + 8 + 4
    plaintext = b''

    for i in range(block_count):
        if off >= len(blob_without_hmac):
            raise ValueError("Файл обрезан: не хватает блоков")
        blen = int.from_bytes(blob_without_hmac[off:off+4], 'big'); off += 4
        block_raw = blob_without_hmac[off:off+blen]; off += blen

        block_salt = block_raw[:SALT_SIZE]
        nonce = block_raw[SALT_SIZE:SALT_SIZE+NONCE_SIZE]
        tag = block_raw[SALT_SIZE+NONCE_SIZE:SALT_SIZE+NONCE_SIZE+TAG_SIZE]
        ct_len = int.from_bytes(block_raw[SALT_SIZE+NONCE_SIZE+TAG_SIZE:SALT_SIZE+NONCE_SIZE+TAG_SIZE+4], 'big')
        ct = block_raw[SALT_SIZE+NONCE_SIZE+TAG_SIZE+4:SALT_SIZE+NONCE_SIZE+TAG_SIZE+4+ct_len]

        db_entry = blocks_db[i]
        key_bytes = derive_key(db_entry["key"], block_salt)
        aad = build_aad(db_entry["idx"]) + timestamp
        try:
            plaintext += aead_decrypt(nonce, ct, tag, key_bytes, aad)
        except ValueError as e:
            raise ValueError(f"Ошибка верификации блока #{i}: {e}")
    return plaintext.decode('utf-8')