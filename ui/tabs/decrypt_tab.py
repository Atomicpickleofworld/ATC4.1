#!/usr/bin/env python3
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QTextEdit, QLineEdit, QPushButton)
from PyQt6.QtCore import Qt
from pathlib import Path

class DecryptTab(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        ct_group = QGroupBox("Файл .atc4")
        ct_layout = QHBoxLayout(ct_group)
        self.ct_path = QLineEdit()
        self.ct_path.setPlaceholderText("Выберите зашифрованный файл...")
        ct_layout.addWidget(self.ct_path)
        browse_ct_btn = QPushButton("📂 Обзор")
        browse_ct_btn.setObjectName("sec")
        browse_ct_btn.clicked.connect(self._browse_atc4)
        ct_layout.addWidget(browse_ct_btn)
        layout.addWidget(ct_group)

        db_group = QGroupBox("Файл кодбазы .atcdb")
        db_layout = QHBoxLayout(db_group)
        self.db_path = QLineEdit()
        self.db_path.setPlaceholderText("Выберите файл кодбазы...")
        db_layout.addWidget(self.db_path)
        browse_db_btn = QPushButton("📂 Обзор")
        browse_db_btn.setObjectName("sec")
        browse_db_btn.clicked.connect(self._browse_codebase)
        db_layout.addWidget(browse_db_btn)
        layout.addWidget(db_group)

        pw_group = QGroupBox("Мастер-пароль (если кодбаза защищена)")
        pw_layout = QHBoxLayout(pw_group)
        self.decrypt_master = QLineEdit()
        self.decrypt_master.setPlaceholderText("Введите мастер-пароль...")
        self.decrypt_master.setEchoMode(QLineEdit.EchoMode.Password)
        pw_layout.addWidget(self.decrypt_master)
        show_pw_btn = QPushButton("👁")
        show_pw_btn.setObjectName("sec")
        show_pw_btn.setFixedWidth(40)
        show_pw_btn.setCheckable(True)
        show_pw_btn.toggled.connect(lambda c: self.decrypt_master.setEchoMode(
            QLineEdit.EchoMode.Normal if c else QLineEdit.EchoMode.Password))
        pw_layout.addWidget(show_pw_btn)
        layout.addWidget(pw_group)

        buttons_layout = QHBoxLayout()
        self.decrypt_btn = QPushButton("🔓 Расшифровать")
        buttons_layout.addWidget(self.decrypt_btn)
        copy_btn = QPushButton("📋 Копировать")
        copy_btn.setObjectName("sec")
        copy_btn.clicked.connect(self._copy_decrypted)
        buttons_layout.addWidget(copy_btn)
        save_txt_btn = QPushButton("💾 Сохранить .txt")
        save_txt_btn.setObjectName("sec")
        buttons_layout.addWidget(save_txt_btn)
        layout.addLayout(buttons_layout)

        result_group = QGroupBox("Расшифрованный текст")
        result_layout = QVBoxLayout(result_group)
        self.decrypt_output = QTextEdit()
        self.decrypt_output.setReadOnly(True)
        self.decrypt_output.setPlaceholderText("Здесь появится расшифрованный текст...")
        self.decrypt_output.setMinimumHeight(200)
        result_layout.addWidget(self.decrypt_output)
        layout.addWidget(result_group)
        layout.addStretch()

    def _browse_atc4(self):
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self, "Выберите файл .atc4", "", "*.atc4;;Все файлы (*)")
        if path: self.ct_path.setText(path)

    def _browse_codebase(self):
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self, "Выберите файл .atcdb", "", "*.atcdb;;Все файлы (*)")
        if path: self.db_path.setText(path)

    def _copy_decrypted(self):
        from PyQt6.QtWidgets import QApplication
        text = self.decrypt_output.toPlainText()
        if text: QApplication.clipboard().setText(text)