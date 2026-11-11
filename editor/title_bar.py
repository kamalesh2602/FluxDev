"""
Custom Frameless Title Bar Module for FluxDev.
Features draggable window header, custom dot window controls,
FluxDev logo, Command Palette search trigger, and quick action pills.
"""

from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy
)

from .icons import get_svg_icon, get_svg_pixmap


class CustomTitleBar(QWidget):
    """Custom sleek title bar for the frameless window."""

    command_palette_requested = pyqtSignal()
    toggle_sidebar_requested = pyqtSignal()
    toggle_preview_requested = pyqtSignal()
    format_doc_requested = pyqtSignal()
    toggle_theme_requested = pyqtSignal()

    def __init__(self, parent_window=None):
        super().__init__(parent_window)
        self.parent_window = parent_window
        self.drag_start_pos = None

        self.setObjectName("title-bar")
        self.setFixedHeight(42)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(12)

        # 1. Window Controls (Dots: Close, Min, Max)
        ctrl_box = QHBoxLayout()
        ctrl_box.setSpacing(8)

        self.btn_close = QPushButton()
        self.btn_close.setObjectName("btn-win-close")
        self.btn_close.setToolTip("Close FluxDev")
        self.btn_close.clicked.connect(self.parent_window.close)
        ctrl_box.addWidget(self.btn_close)

        self.btn_min = QPushButton()
        self.btn_min.setObjectName("btn-win-min")
        self.btn_min.setToolTip("Minimize")
        self.btn_min.clicked.connect(self.parent_window.showMinimized)
        ctrl_box.addWidget(self.btn_min)

        self.btn_max = QPushButton()
        self.btn_max.setObjectName("btn-win-max")
        self.btn_max.setToolTip("Maximize / Restore")
        self.btn_max.clicked.connect(self._toggle_maximize)
        ctrl_box.addWidget(self.btn_max)

        layout.addLayout(ctrl_box)

        # 2. FluxDev Brand & Document Indicator
        brand_box = QHBoxLayout()
        brand_box.setSpacing(8)
        lbl_logo = QLabel()
        lbl_logo.setPixmap(get_svg_pixmap("fluxdev-logo", size=20))
        brand_box.addWidget(lbl_logo)

        self.lbl_title = QLabel("FluxDev")
        self.lbl_title.setStyleSheet("font-weight: 700; font-size: 13px; color: #FFFFFF;")
        brand_box.addWidget(self.lbl_title)

        self.lbl_subtitle = QLabel("• Web Studio")
        self.lbl_subtitle.setStyleSheet("font-size: 11px; color: #64748B;")
        brand_box.addWidget(self.lbl_subtitle)
        layout.addLayout(brand_box)

        layout.addStretch(1)

        # 3. Center: Command Palette Trigger Pill
        self.btn_palette = QPushButton()
        self.btn_palette.setObjectName("btn-cmd-palette-trigger")
        self.btn_palette.setIcon(get_svg_icon("search", color="#94A3B8", size=14))
        self.btn_palette.setText("  Search commands or files...  Ctrl+Shift+P")
        self.btn_palette.clicked.connect(self.command_palette_requested.emit)
        layout.addWidget(self.btn_palette)

        layout.addStretch(1)

        # 4. Right: Quick Action Buttons
        actions_box = QHBoxLayout()
        actions_box.setSpacing(6)

        self.btn_preview = QPushButton()
        self.btn_preview.setIcon(get_svg_icon("globe", color="#94A3B8", size=15))
        self.btn_preview.setToolTip("Toggle Live Preview (F6 / Ctrl+P)")
        self.btn_preview.setCheckable(True)
        self.btn_preview.setChecked(False)  # Hidden by default per Issue 2
        self.btn_preview.clicked.connect(self.toggle_preview_requested.emit)
        actions_box.addWidget(self.btn_preview)

        self.btn_sidebar = QPushButton()
        self.btn_sidebar.setIcon(get_svg_icon("panel-left", color="#94A3B8", size=15))
        self.btn_sidebar.setToolTip("Toggle Project Sidebar (Ctrl+B)")
        self.btn_sidebar.setCheckable(True)
        self.btn_sidebar.setChecked(True)
        self.btn_sidebar.clicked.connect(self.toggle_sidebar_requested.emit)
        actions_box.addWidget(self.btn_sidebar)

        self.btn_format = QPushButton()
        self.btn_format.setIcon(get_svg_icon("sparkles", color="#94A3B8", size=15))
        self.btn_format.setToolTip("Format Document (Ctrl+Alt+F)")
        self.btn_format.clicked.connect(self.format_doc_requested.emit)
        actions_box.addWidget(self.btn_format)

        self.btn_theme = QPushButton("Theme")
        self.btn_theme.setIcon(get_svg_icon("moon", color="#94A3B8", size=14))
        self.btn_theme.setToolTip("Cycle Themes (Dark / Midnight / Light)")
        self.btn_theme.clicked.connect(self.toggle_theme_requested.emit)
        actions_box.addWidget(self.btn_theme)

        layout.addLayout(actions_box)

    def _toggle_maximize(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
        else:
            self.parent_window.showMaximized()

    def set_document_title(self, title: str):
        if title:
            self.lbl_subtitle.setText(f"• {title}")
        else:
            self.lbl_subtitle.setText("• Web Studio")

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = e.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if self.drag_start_pos is not None and e.buttons() == Qt.MouseButton.LeftButton:
            if not self.parent_window.isMaximized():
                self.parent_window.move(e.globalPosition().toPoint() - self.drag_start_pos)
        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        self.drag_start_pos = None
        super().mouseReleaseEvent(e)

    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._toggle_maximize()
        super().mouseDoubleClickEvent(e)
