#!/usr/bin/env python3
"""Точка входа приложения"""
import sys
from PyQt6.QtWidgets import QApplication
from ui.tabs.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Atomic TriFlow Cipher v4.1")
    app.setApplicationDisplayName("ATC4.1")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()