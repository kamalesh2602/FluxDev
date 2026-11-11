"""
JavaScript Console Panel Module for Aether.
Displays console.log, console.warn, and JavaScript runtime errors with colored badges.
"""

from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QFrame
)

from .icons import get_svg_icon


class ConsolePanel(QFrame):
    """Panel displaying real-time JavaScript console logs and errors."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("console-panel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 8)
        layout.setSpacing(6)

        # Header bar
        bar = QHBoxLayout()
        self.lbl_title = QLabel("CONSOLE")
        self.lbl_title.setStyleSheet("font-weight: 700; font-size: 11px; letter-spacing: 0.8px; color: #64748B;")
        bar.addWidget(self.lbl_title)
        bar.addStretch()

        self.btn_clear = QPushButton("Clear")
        self.btn_clear.setIcon(get_svg_icon("close", color="#94A3B8", size=12))
        self.btn_clear.clicked.connect(self.clear_logs)
        bar.addWidget(self.btn_clear)
        layout.addLayout(bar)

        # Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Time", "Level", "Message", "Location"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 4px 8px;
                font-size: 12px;
            }
        """)

        layout.addWidget(self.table)

    def log_message(self, level: str, message: str, line: int, source: str):
        row = self.table.rowCount()
        self.table.insertRow(row)

        now = datetime.now().strftime("%H:%M:%S")
        time_item = QTableWidgetItem(now)
        level_item = QTableWidgetItem(f" {level.upper()} ")
        msg_item = QTableWidgetItem(message)
        loc_str = f"{source}:{line}" if source else f"Line {line}"
        loc_item = QTableWidgetItem(loc_str)

        if level.lower() == "error":
            level_item.setForeground(QColor("#EF4444"))
            msg_item.setForeground(QColor("#FCA5A5"))
        elif level.lower() == "warning":
            level_item.setForeground(QColor("#F59E0B"))
            msg_item.setForeground(QColor("#FDE68A"))
        else:
            level_item.setForeground(QColor("#10B981"))
            msg_item.setForeground(QColor("#E2E8F0"))

        time_item.setForeground(QColor("#64748B"))
        loc_item.setForeground(QColor("#64748B"))

        self.table.setItem(row, 0, time_item)
        self.table.setItem(row, 1, level_item)
        self.table.setItem(row, 2, msg_item)
        self.table.setItem(row, 3, loc_item)

        self.table.scrollToBottom()

    def clear_logs(self):
        self.table.setRowCount(0)
