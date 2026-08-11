"""
Harness Index — Logger Module
Handles console logging to stdout and maintains an in-memory log buffer for GUI log inspection.
"""

import sys
import time
from collections import deque
from PyQt5.QtCore import QObject, pyqtSignal


class AppLogger(QObject):
    """Central application logger with Qt signals."""
    log_added = pyqtSignal(str)

    def __init__(self, max_records=200):
        super().__init__()
        self.logs = deque(maxlen=max_records)

    def log(self, category: str, message: str, level: str = "INFO"):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] [{level}] [{category}] {message}"
        
        # Print to standard output for terminal visibility
        print(formatted, flush=True)
        
        # Append to GUI log memory
        self.logs.append(formatted)
        self.log_added.emit(formatted)

    def info(self, category: str, message: str):
        self.log(category, message, level="INFO")

    def warn(self, category: str, message: str):
        self.log(category, message, level="WARN")

    def error(self, category: str, message: str):
        self.log(category, message, level="ERROR")

    def get_logs_text(self) -> str:
        return "\n".join(self.logs)


# Global singleton instance
app_logger = AppLogger()
