#!/usr/bin/env python3
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from config import C_LILAC, C_ORANGE, C_BG2, C_BORDER, C_BG3

class InfoTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setStyleSheet(f"background: {C_BG2}; border: 1px solid {C_BORDER}; border-radius: 10px; padding: 16px;")
        info_text.setHtml(f"""
<h2 style='color:{C_LILAC};'>Atomic TriFlow Cipher v4.1 — Stable Edition</h2>
<h3 style='color:{C_ORANGE};'>🔐 Криптографическая схема</h3>
<p><b>Argon2id KDF</b> — современная функция вывода ключа с защитой от GPU/ASIC атак.<br>
<b>ChaCha20-Poly1305</b> — аутентифицированное шифрование с AAD.<br>
<b>AAD (Associated Authenticated Data)</b> — привязка каждого блока к его позиции.</p>
<h3 style='color:{C_ORANGE};'>📦 Блочная структура</h3>
<p>• Текст разбивается на блоки случайной длины (64–256 байт)<br>
• Каждый блок шифруется своим уникальным ключом<br>
• Ключи блоков хранятся в отдельной кодбазе (.atcdb)<br>
• Кодбаза опционально защищается мастер-паролем</p>
<h3 style='color:{C_ORANGE};'>🛡️ Защита от атак</h3>
<p>✓ <b>Перестановка блоков</b> — AAD привязывает блок к индексу<br>
✓ <b>Downgrade attack</b> — числовая версия в AAD<br>
✓ <b>Replay attack</b> — timestamp в AAD<br>
✓ <b>Timing attack</b> — dummy KDF при проверке пароля<br>
✓ <b>Подмена формата</b> — HMAC заголовка с отдельным ключом</p>
<h3 style='color:{C_ORANGE};'>📄 Формат пакета</h3>
<pre style='background:{C_BG3}; padding: 10px; border-radius: 8px;'>
.atc4 файл:
MAGIC(4) + VERSION(1) + SALT(16) + TIMESTAMP(8) + COUNT(4)
+ для каждого блока: LEN(4) + SALT(16) + NONCE(12) + TAG(16) + LEN_CT(4) + CT
+ HEADER_HMAC(32)
.atcdb файл:
JSON с ключами блоков, опционально зашифрованный мастер-паролем
</pre>
<h3 style='color:{C_ORANGE};'>⚠️ Важно</h3>
<p>• .atc4 и .atcdb нужно передавать <b>разными каналами</b><br>
• Без кодбазы расшифровка <b>математически невозможна</b><br>
• Потеря любого файла = потеря данных<br>
• Минимальная длина пароля: <b>16 символов</b></p>
""")
        layout.addWidget(info_text)