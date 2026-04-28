#!/usr/bin/env python3
import base64
import json
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QFrame, QTabWidget, QStatusBar, QProgressBar, QMessageBox, QFileDialog,
                             QSizePolicy)
from PyQt6.QtCore import Qt
from config import STYLE, C_LILAC, C_ORANGE, C_BG2, C_BORDER, C_TEXT3, ARGON2_OK, CRYPTO_OK
from ui.tabs.encrypt_tab import EncryptTab
from ui.tabs.decrypt_tab import DecryptTab
from ui.tabs.info_tab import InfoTab
from utils.worker import CryptoThread


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Atomic TriFlow Cipher v4.1 — Stable Edition")

        # ✅ УВЕЛИЧЕНО: Минимальный и стартовый размер, чтобы интерфейс не сжимался
        self.setMinimumSize(940, 920)
        self.resize(940, 920)

        self.setStyleSheet(STYLE)
        self._enc_blob = None
        self._enc_codebase = None
        self._init_ui()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 20, 24, 12)
        layout.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("ATC")
        title.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {C_LILAC};")
        header.addWidget(title)
        version = QLabel("v4.1 Stable")
        version.setStyleSheet(f"font-size: 14px; color: {C_ORANGE}; font-weight: bold;")
        header.addWidget(version)
        header.addStretch()
        for ok, name in [(ARGON2_OK, "Argon2id"), (CRYPTO_OK, "ChaCha20")]:
            badge = QLabel(f"{'✓' if ok else '✗'} {name}")
            badge.setStyleSheet(
                f"background: {'rgba(90,158,111,0.12)' if ok else 'rgba(192,65,58,0.12)'};"
                f"border: 1px solid {'rgba(90,158,111,0.4)' if ok else 'rgba(192,65,58,0.4)'};"
                f"border-radius: 5px; padding: 4px 10px;"
                f"color: {'#5A9E6F' if ok else '#C0413A'}; font-size: 11px;"
            )
            header.addWidget(badge)
        layout.addLayout(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: {C_BORDER}; max-height: 1px;")
        layout.addWidget(sep)

        tabs = QTabWidget()
        # ✅ QSizePolicy теперь импортирован и работает корректно
        tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.encrypt_tab = EncryptTab()
        self.decrypt_tab = DecryptTab()
        self.info_tab = InfoTab()
        tabs.addTab(self.encrypt_tab, "🔒 Шифрование")
        tabs.addTab(self.decrypt_tab, "🔓 Дешифрование")
        tabs.addTab(self.info_tab, "ℹ️ О схеме")
        layout.addWidget(tabs)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedWidth(150)
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.status_bar.showMessage("Готов к работе")

        self._connect_signals()

    def _connect_signals(self):
        self.encrypt_tab.encrypt_btn.clicked.connect(self._do_encrypt)
        self.encrypt_tab.save_ct_btn.clicked.connect(self._save_atc4)
        self.encrypt_tab.save_db_btn.clicked.connect(self._save_codebase)
        self.decrypt_tab.decrypt_btn.clicked.connect(self._do_decrypt)

    def _do_encrypt(self):
        text = self.encrypt_tab.text_input.toPlainText()
        if self.encrypt_tab.file_path.text() and Path(self.encrypt_tab.file_path.text()).exists():
            try:
                text = Path(self.encrypt_tab.file_path.text()).read_text(encoding='utf-8')
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось прочитать файл: {e}"); return
        if not text.strip(): QMessageBox.warning(self, "Ошибка", "Введите текст или выберите файл"); return

        master = None
        if self.encrypt_tab.protect_check.isChecked():
            master = self.encrypt_tab.master_password.text()
            if len(master) < 16: QMessageBox.warning(self, "Ошибка",
                                                     "Мастер-пароль должен быть минимум 16 символов"); return

        self.progress_bar.setVisible(True)
        self.status_bar.showMessage("Шифрование...")
        self.encrypt_thread = CryptoThread("encrypt", text=text, master=master)
        self.encrypt_thread.finished.connect(self._on_encrypt_finished)
        self.encrypt_thread.progress.connect(self.status_bar.showMessage)
        self.encrypt_thread.start()

    def _on_encrypt_finished(self, blob, codebase, error):
        self.progress_bar.setVisible(False)
        if error:
            self.status_bar.showMessage("Ошибка шифрования")
            QMessageBox.critical(self, "Ошибка", f"Не удалось зашифровать данные:\n{error}");
            return
        self._enc_blob = blob;
        self._enc_codebase = codebase
        preview = base64.b64encode(blob).decode()
        if len(preview) > 1000: preview = preview[:1000] + "\n...(обрезано для предпросмотра)"
        self.encrypt_tab.result_output.setPlainText(preview)
        block_count = codebase.get("block_count", 0)
        protected = codebase.get("protected", False)
        self.status_bar.showMessage(f"✓ Зашифровано: {len(blob)} байт, {block_count} блоков")
        QMessageBox.information(self, "Успех",
                                f"Шифрование завершено!\n• Размер: {len(blob)} байт\n• Блоков: {block_count}\n• Кодбаза: {'защищена паролем' if protected else 'не защищена'}\nСохраните оба файла (.atc4 и .atcdb) и передавайте их РАЗНЫМИ КАНАЛАМИ!")

    def _do_decrypt(self):
        ct_path = self.decrypt_tab.ct_path.text()
        db_path = self.decrypt_tab.db_path.text()
        if not ct_path or not Path(ct_path).exists(): QMessageBox.warning(self, "Ошибка", "Выберите файл .atc4"); return
        if not db_path or not Path(db_path).exists(): QMessageBox.warning(self, "Ошибка",
                                                                          "Выберите файл .atcdb"); return
        try:
            blob = Path(ct_path).read_bytes()
            with open(db_path, 'r', encoding='utf-8') as f:
                codebase = json.load(f)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось прочитать файлы:\n{e}"); return

        master = self.decrypt_tab.decrypt_master.text() or None
        self.progress_bar.setVisible(True)
        self.status_bar.showMessage("Дешифрование с верификацией AAD...")
        self.decrypt_thread = CryptoThread("decrypt", blob=blob, codebase=codebase, master=master)
        self.decrypt_thread.finished.connect(self._on_decrypt_finished)
        self.decrypt_thread.progress.connect(self.status_bar.showMessage)
        self.decrypt_thread.start()

    def _on_decrypt_finished(self, result, _, error):
        self.progress_bar.setVisible(False)
        if error:
            self.status_bar.showMessage("Ошибка дешифрования")
            QMessageBox.critical(self, "Ошибка", f"Не удалось расшифровать данные:\n{error}");
            return
        self.decrypt_tab.decrypt_output.setPlainText(result)
        self.status_bar.showMessage(f"✓ Расшифровано: {len(result)} символов")

    def _save_atc4(self):
        if not self._enc_blob: QMessageBox.warning(self, "Ошибка", "Нет данных для сохранения"); return
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить .atc4 файл", "encrypted.atc4", "*.atc4")
        if path: Path(path).write_bytes(self._enc_blob); self.status_bar.showMessage(f"Сохранено: {path}")

    def _save_codebase(self):
        if not self._enc_codebase: QMessageBox.warning(self, "Ошибка", "Нет данных для сохранения"); return
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить .atcdb файл", "codebase.atcdb", "*.atcdb")
        if path:
            with open(path, 'w', encoding='utf-8') as f: json.dump(self._enc_codebase, f, ensure_ascii=False, indent=2)
            self.status_bar.showMessage(f"Сохранено: {path}")