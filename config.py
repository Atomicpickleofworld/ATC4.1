#!/usr/bin/env python3
"""Константы, палитра, флаги библиотек и конфигурация ATC 4.1"""
import string

# ✅ Проверка доступности крипто-библиотек (теперь определены здесь)
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

MAGIC_ATC4 = b'ATC4'
FORMAT_VERSION = 4
KEY_CHARS = string.ascii_letters + string.digits + "!@#$%^&*-_=+[]|"
MIN_BLOCK = 64
MAX_BLOCK = 256
SALT_SIZE = 16
NONCE_SIZE = 12
TAG_SIZE = 16
HMAC_SIZE = 32

# Палитра
C_BG = "#F5F0EB"
C_BG2 = "#EDE6DD"
C_BG3 = "#E2D9CE"
C_BORDER = "#D4C8BA"
C_LILAC = "#9B7FBD"
C_LILAC2 = "#B99DD4"
C_ORANGE = "#E07A3A"
C_ORANGE2 = "#F0A060"
C_TEXT = "#3D2E20"
C_TEXT2 = "#7A6555"
C_TEXT3 = "#A89080"
C_GREEN = "#5A9E6F"
C_RED = "#C0413A"

STYLE = f"""
* {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; color: {C_TEXT}; }}
QMainWindow, QWidget {{ background: {C_BG}; }}
QTabWidget::pane {{ border: 1px solid {C_BORDER}; border-radius: 10px; background: {C_BG}; }}
QTabBar::tab {{
    background: {C_BG2}; border: 1px solid {C_BORDER};
    border-radius: 6px; padding: 8px 20px; margin: 2px; color: {C_TEXT2};
}}
QTabBar::tab:selected {{ background: {C_LILAC}; color: white; font-weight: bold; }}
QTabBar::tab:hover {{ background: {C_LILAC2}; color: white; }}
QGroupBox {{
    border: 1.5px solid {C_BORDER}; border-radius: 10px;
    margin-top: 14px; padding: 12px; font-weight: bold; color: {C_TEXT2};
}}
QGroupBox::title {{
    subcontrol-origin: margin; left: 12px; padding: 0 6px;
    color: {C_LILAC}; font-size: 10px; letter-spacing: 2px;
}}
QTextEdit, QLineEdit {{
    background: white; border: 1.5px solid {C_BORDER};
    border-radius: 8px; padding: 8px 12px; color: {C_TEXT};
    selection-background-color: {C_LILAC2};
}}
QTextEdit:focus, QLineEdit:focus {{ border-color: {C_LILAC}; }}
QPushButton {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
    stop:0 {C_LILAC}, stop:1 {C_ORANGE});
    border: none; border-radius: 9px; color: white;
    font-weight: bold; padding: 10px 18px;
}}
QPushButton:hover {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
    stop:0 {C_LILAC2}, stop:1 {C_ORANGE2});
}}
QPushButton#sec {{
    background: transparent; border: 1.5px solid {C_BORDER}; color: {C_TEXT2};
}}
QPushButton#sec:hover {{ border-color:{C_LILAC}; color:{C_LILAC}; background:rgba(155,127,189,0.07); }}
QCheckBox {{ spacing: 8px; color: {C_TEXT2}; }}
QCheckBox::indicator {{
    width:18px; height:18px; border:2px solid {C_BORDER};
    border-radius:4px; background:white;
}}
QCheckBox::indicator:checked {{ background:{C_LILAC}; border-color:{C_LILAC}; }}
QProgressBar {{
    border:none; border-radius:4px; background:{C_BG3}; height:6px;
}}
QProgressBar::chunk {{ background:{C_LILAC}; border-radius:4px; }}
QScrollBar:vertical {{ background:{C_BG2}; width:6px; border-radius:3px; }}
QScrollBar::handle:vertical {{ background:{C_BORDER}; border-radius:3px; min-height:24px; }}
QStatusBar {{ background:{C_BG2}; border-top:1px solid {C_BORDER}; color:{C_TEXT3}; }}
"""