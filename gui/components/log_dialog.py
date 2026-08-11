"""
Harness Index — Log Viewer Dialog
Floating window displaying real-time application logs with auto-scroll and clear functionality.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QPushButton
)
from PyQt5.QtCore import Qt
from core.logger import app_logger


class LogDialog(QDialog):
    """Real-time application log viewer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📋 运行日志与请求记录 — Harness Index")
        self.resize(760, 480)
        self.setMinimumSize(600, 360)
        self._init_ui()

        # Connect to logger signals
        app_logger.log_added.connect(self._on_log_added)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header
        header = QHBoxLayout()
        title = QLabel("📋 实时请求与交互日志")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ece5d6;")
        header.addWidget(title)

        header.addStretch()

        btn_clear = QPushButton("清空日志")
        btn_clear.setCursor(Qt.PointingHandCursor)
        btn_clear.setStyleSheet("""
            QPushButton {
                background: rgba(158, 178, 205, 0.12);
                color: #9aa7ba;
                border: 1px solid rgba(158, 178, 205, 0.25);
                border-radius: 12px;
                padding: 4px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #ece5d6;
                background: rgba(158, 178, 205, 0.25);
            }
        """)
        btn_clear.clicked.connect(self._clear_logs)
        header.addWidget(btn_clear)

        layout.addLayout(header)

        # Text Console Box
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("""
            QTextEdit {
                background-color: #0b1019;
                color: #38ef7d;
                font-family: 'Menlo', 'Courier New', monospace;
                font-size: 12px;
                line-height: 1.5;
                border: 1px solid rgba(158, 178, 205, 0.15);
                border-radius: 8px;
                padding: 12px;
            }
        """)
        self.console.setPlainText(app_logger.get_logs_text())
        self.console.moveCursor(self.console.textCursor().End)
        layout.addWidget(self.console, 1)

    def _on_log_added(self, text: str):
        self.console.append(text)
        self.console.moveCursor(self.console.textCursor().End)

    def _clear_logs(self):
        app_logger.logs.clear()
        self.console.clear()
