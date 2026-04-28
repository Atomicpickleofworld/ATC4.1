#!/usr/bin/env python3
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QTextEdit, QLineEdit, QPushButton, QCheckBox, QLabel)
from PyQt6.QtCore import Qt
from pathlib import Path
from config import C_TEXT3

class EncryptTab(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        input_group = QGroupBox("Исходные данные")
        input_layout = QVBoxLayout(input_group)
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Введите текст для шифрования...")
        self.text_input.setMinimumHeight(150)
        input_layout.addWidget(self.text_input)

        file_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.setPlaceholderText("Или выберите текстовый файл...")
        file_layout.addWidget(self.file_path)
        browse_btn = QPushButton("📂 Обзор")
        browse_btn.setObjectName("sec")
        browse_btn.clicked.connect(lambda: self._browse(self.file_path, self.text_input))
        file_layout.addWidget(browse_btn)
        input_layout.addLayout(file_layout)
        layout.addWidget(input_group)

        options_group = QGroupBox("Параметры")
        options_layout = QVBoxLayout(options_group)
        self.protect_check = QCheckBox("Защитить кодбазу мастер-паролем")
        options_layout.addWidget(self.protect_check)

        self.master_row = QWidget()
        master_layout = QHBoxLayout(self.master_row)
        master_layout.setContentsMargins(0, 0, 0, 0)
        self.master_password = QLineEdit()
        self.master_password.setPlaceholderText("Мастер-пароль (минимум 16 символов)")
        self.master_password.setEchoMode(QLineEdit.EchoMode.Password)
        master_layout.addWidget(self.master_password)
        show_btn = QPushButton("👁")
        show_btn.setObjectName("sec")
        show_btn.setFixedWidth(40)
        show_btn.setCheckable(True)
        show_btn.toggled.connect(lambda c: self.master_password.setEchoMode(
            QLineEdit.EchoMode.Normal if c else QLineEdit.EchoMode.Password))
        master_layout.addWidget(show_btn)
        self.master_row.setVisible(False)
        options_layout.addWidget(self.master_row)

        self.stats_label = QLabel()
        self.stats_label.setStyleSheet(f"color: {C_TEXT3}; font-size: 11px;")
        self.text_input.textChanged.connect(self._update_stats)
        options_layout.addWidget(self.stats_label)
        layout.addWidget(options_group)

        buttons_layout = QHBoxLayout()
        self.encrypt_btn = QPushButton("🔒 Зашифровать")
        buttons_layout.addWidget(self.encrypt_btn)
        self.save_ct_btn = QPushButton("💾 Сохранить .atc4")
        self.save_ct_btn.setObjectName("sec")
        buttons_layout.addWidget(self.save_ct_btn)
        self.save_db_btn = QPushButton("💾 Сохранить .atcdb")
        self.save_db_btn.setObjectName("sec")
        buttons_layout.addWidget(self.save_db_btn)
        layout.addLayout(buttons_layout)

        result_group = QGroupBox("Результат (Base64)")
        result_layout = QVBoxLayout(result_group)
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setPlaceholderText("Здесь появится зашифрованный текст...")
        self.result_output.setMinimumHeight(120)
        result_layout.addWidget(self.result_output)
        copy_btn = QPushButton("📋 Копировать")
        copy_btn.setObjectName("sec")
        copy_btn.clicked.connect(self._copy_result)
        result_layout.addWidget(copy_btn)
        layout.addWidget(result_group)

        self.protect_check.toggled.connect(self.master_row.setVisible)
        layout.addStretch()

    def _browse(self, path_edit, text_edit):
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self, "Выберите текстовый файл", "", "*.txt *.md *.json;;Все файлы (*)")
        if path:
            path_edit.setText(path)
            try:
                text_edit.setPlainText(Path(path).read_text(encoding='utf-8'))
            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Ошибка", f"Не удалось прочитать файл: {e}")

    def _update_stats(self):
        text = self.text_input.toPlainText()
        if not text:
            self.stats_label.setText(""); return
        data = text.encode('utf-8')
        size = len(data)
        from config import MIN_BLOCK, MAX_BLOCK
        min_blocks = max(1, size // MAX_BLOCK)
        max_blocks = max(1, (size + MIN_BLOCK - 1) // MIN_BLOCK)
        self.stats_label.setText(f"📊 Размер: {size} байт | Блоков: {min_blocks}–{max_blocks} | AAD защита активна")

    def _copy_result(self):
        from PyQt6.QtWidgets import QApplication
        text = self.result_output.toPlainText()
        if text:
            QApplication.clipboard().setText(text)