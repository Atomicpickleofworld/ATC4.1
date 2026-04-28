#!/usr/bin/env python3
"""Ядро криптографии: KDF, AEAD, генерация ключей, AAD"""
import os
import hashlib
import secrets
from typing import Tuple
from config import KEY_CHARS, NONCE_SIZE, SALT_SIZE, FORMAT_VERSION

try:
    from argon2.low_level import hash_secret_raw, Type
    ARGON2_OK = True
except ImportError:
    ARGON2_OK = False

try:
    from Crypto.Cipher import ChaCha20_Poly1305
    CRYPTO_OK = True
except ImportError:
    CRYPTO_OK = False

def derive_key(password: str, salt: bytes) -> bytes:
    pwd = password.encode('utf-8')
    if len(password) < 16:
        _ = hashlib.pbkdf2_hmac('sha256', b'dummy', os.urandom(16), 100000)
        raise ValueError("Пароль должен быть минимум 16 символов")
    if ARGON2_OK:
        return hash_secret_raw(pwd, salt, time_cost=3, memory_cost=65536,
                               parallelism=4, hash_len=32, type=Type.ID)
    return hashlib.pbkdf2_hmac('sha256', pwd, salt, 300000, dklen=32)

def aead_encrypt(data: bytes, key: bytes, aad: bytes) -> Tuple[bytes, bytes, bytes]:
    nonce = os.urandom(NONCE_SIZE)
    if CRYPTO_OK:
        cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
        cipher.update(aad)
        ct, tag = cipher.encrypt_and_digest(data)
    else:
        from Crypto.Cipher import AES
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        cipher.update(aad)
        ct, tag = cipher.encrypt_and_digest(data)
    return nonce, ct, tag


def aead_decrypt(nonce: bytes, ct: bytes, tag: bytes, key: bytes, aad: bytes) -> bytes:
    if CRYPTO_OK:
        cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
        cipher.update(aad)
        return cipher.decrypt_and_verify(ct, tag)
    else:
        from Crypto.Cipher import AES
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        cipher.update(aad)
        return cipher.decrypt_and_verify(ct, tag)

def generate_key(length: int) -> str:
    return ''.join(secrets.choice(KEY_CHARS) for _ in range(length))

def build_aad(block_idx: int) -> bytes:
    version_bytes = FORMAT_VERSION.to_bytes(4, 'big')
    idx_bytes = block_idx.to_bytes(4, 'big')
    return version_bytes + idx_bytes