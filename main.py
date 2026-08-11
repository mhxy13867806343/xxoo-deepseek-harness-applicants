#!/usr/bin/env python3
"""
Harness Index — DeepSeek Harness 内测报名档案
Desktop Application Entry Point (Python 3.11 + PyQt5)
"""

import sys
import os

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from gui.styles import APP_QSS
from gui.main_window import MainWindow


def main():
    # Enable High DPI scaling
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Harness Index")
    app.setOrganizationName("DeepSeek Harness Community")
    app.setStyleSheet(APP_QSS)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
