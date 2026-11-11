"""
Welcome Screen Module for FluxDev.
Displays the FluxDev gradient flow logo mark, tagline,
starter action cards, and recent projects list.
"""

import os
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QScrollArea
)

from .icons import get_svg_pixmap, get_svg_icon


class ActionCard(QFrame):
    """Modern elevated action card for the welcome screen."""

    clicked = pyqtSignal()

    def __init__(self, icon_name: str, title: str, subtitle: str, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("action-card")
        self.setFixedSize(240, 110)

        self.setStyleSheet("""
            #action-card {
                background-color: #121626;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                padding: 14px;
            }
            #action-card:hover {
                background-color: #1A2035;
                border: 1px solid rgba(139, 92, 246, 0.5);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(6)

        # Top icon & title row
        top_row = QHBoxLayout()
        lbl_icon = QLabel()
        lbl_icon.setPixmap(get_svg_pixmap(icon_name, color="#8B5CF6", size=22))
        top_row.addWidget(lbl_icon)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-weight: 600; font-size: 14px; color: #F8FAFC;")
        top_row.addWidget(lbl_title)
        top_row.addStretch()
        layout.addLayout(top_row)

        lbl_sub = QLabel(subtitle)
        lbl_sub.setStyleSheet("font-size: 11px; color: #94A3B8;")
        lbl_sub.setWordWrap(True)
        layout.addWidget(lbl_sub)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()


class WelcomeScreen(QWidget):
    """Minimal, elegant welcome screen for FluxDev."""

    new_file_requested = pyqtSignal()
    open_file_requested = pyqtSignal()
    open_folder_requested = pyqtSignal()
    starter_project_requested = pyqtSignal()
    html5_template_requested = pyqtSignal()
    open_recent_path_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        main_layout = QVBoxLayout(container)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(40, 50, 40, 50)
        main_layout.setSpacing(24)

        # 1. FluxDev Logo & Tagline Header
        header_box = QVBoxLayout()
        header_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_box.setSpacing(8)

        lbl_logo = QLabel()
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_logo.setPixmap(get_svg_pixmap("fluxdev-logo", size=54))
        header_box.addWidget(lbl_logo)

        lbl_title = QLabel("FLUXDEV")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setStyleSheet("""
            font-size: 32px;
            font-weight: 800;
            color: #FFFFFF;
        """)
        header_box.addWidget(lbl_title)

        # Tagline: "Where ideas flow into code."
        lbl_tagline = QLabel("Where ideas flow into code.")
        lbl_tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_tagline.setStyleSheet("font-size: 14px; font-weight: 500; color: #A78BFA;")
        header_box.addWidget(lbl_tagline)

        main_layout.addLayout(header_box)

        # 2. Action Cards Grid (2x2)
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(16)
        grid.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_starter = ActionCard("rocket", "Starter Project", "HTML + CSS + JS interactive app scaffold")
        card_starter.clicked.connect(self.starter_project_requested.emit)
        grid.addWidget(card_starter, 0, 0)

        card_new = ActionCard("file-plus", "New File", "Open a fresh blank document")
        card_new.clicked.connect(self.new_file_requested.emit)
        grid.addWidget(card_new, 0, 1)

        card_html5 = ActionCard("code", "HTML5 Boilerplate", "Standard responsive HTML5 skeleton")
        card_html5.clicked.connect(self.html5_template_requested.emit)
        grid.addWidget(card_html5, 1, 0)

        card_folder = ActionCard("folder-open", "Open Folder", "Browse an existing web project")
        card_folder.clicked.connect(self.open_folder_requested.emit)
        grid.addWidget(card_folder, 1, 1)

        main_layout.addWidget(grid_widget)

        # 3. Recent Projects Section
        self.recent_box = QVBoxLayout()
        self.recent_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.recent_box.setSpacing(6)

        lbl_recents_title = QLabel("RECENT PROJECTS")
        lbl_recents_title.setStyleSheet("font-size: 11px; font-weight: 700; color: #64748B;")
        lbl_recents_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.recent_box.addWidget(lbl_recents_title)

        self.recents_list_container = QVBoxLayout()
        self.recents_list_container.setSpacing(4)
        self.recent_box.addLayout(self.recents_list_container)

        main_layout.addLayout(self.recent_box)

        # 4. Command Palette Hint
        lbl_hint = QLabel("Press Ctrl+Shift+P to open the Command Palette anywhere")
        lbl_hint.setStyleSheet("font-size: 12px; color: #64748B; padding-top: 8px;")
        lbl_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(lbl_hint)

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def set_recent_files(self, paths: list):
        """Populates recent project buttons."""
        while self.recents_list_container.count() > 0:
            child = self.recents_list_container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        valid_paths = [p for p in paths if os.path.exists(p)][:4]
        if not valid_paths:
            lbl_none = QLabel("No recent projects yet.")
            lbl_none.setStyleSheet("color: #64748B; font-size: 12px;")
            lbl_none.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.recents_list_container.addWidget(lbl_none)
            return

        for p in valid_paths:
            btn = QPushButton()
            name = os.path.basename(p) or p
            btn.setText(f"  {name}   —   {p}")
            btn.setIcon(get_svg_icon("folder" if os.path.isdir(p) else "code", color="#94A3B8", size=14))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 1px solid transparent;
                    color: #94A3B8;
                    text-align: left;
                    font-size: 12px;
                    padding: 6px 12px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #121626;
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    color: #F8FAFC;
                }
            """)
            btn.clicked.connect(lambda _, path=p: self.open_recent_path_requested.emit(path))
            self.recents_list_container.addWidget(btn)
