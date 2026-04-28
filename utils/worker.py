#!/usr/bin/env python3
"""Поток для неблокирующих крипто-операций"""
from PyQt6.QtCore import QThread, pyqtSignal
from typing import Optional

class CryptoThread(QThread):
    finished = pyqtSignal(object, object, str)
    progress = pyqtSignal(str)

    def __init__(self, mode: str, text: str = "", blob: bytes = None,
                 codebase: dict = None, master: str = None):
        super().__init__()
        self.mode, self.text, self.blob = mode, text, blob
        self.codebase, self.master = codebase, master

    def run(self):
        try:
            if self.mode == "encrypt":
                from crypto.multiblock import multiblock_encrypt
                self.progress.emit("Шифрование с AAD-привязкой...")
                blob, codebase = multiblock_encrypt(self.text, self.master)
                self.finished.emit(blob, codebase, None)
            else:
                from crypto.multiblock import multiblock_decrypt
                self.progress.emit("Дешифрование с верификацией AAD...")
                result = multiblock_decrypt(self.blob, self.codebase, self.master)
                self.finished.emit(result, None, None)
        except Exception as e:
            self.finished.emit(None, None, str(e))