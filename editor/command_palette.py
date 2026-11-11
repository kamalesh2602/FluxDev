"""
Command Palette Module for FluxDev (Ctrl+Shift+P / Ctrl+K).
A centered, floating spotlight modal to discover and execute any action.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent, QColor
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget,
    QListWidgetItem, QLabel, QWidget, QGraphicsDropShadowEffect
)

from .icons import get_svg_icon


class CommandItemWidget(QWidget):
    """Row widget for Command Palette items showing title, category, and shortcut."""

    def __init__(self, title: str, category: str, shortcut: str = "", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("font-weight: 500; font-size: 13px; color: #F1F5F9;")
        layout.addWidget(self.lbl_title)

        layout.addStretch()

        if category:
            lbl_cat = QLabel(category.upper())
            lbl_cat.setStyleSheet(
                "font-size: 9px; font-weight: bold; color: #8B5CF6; "
                "background-color: rgba(139, 92, 246, 0.15); "
                "border-radius: 4px; padding: 2px 6px;"
            )
            layout.addWidget(lbl_cat)

        if shortcut:
            lbl_key = QLabel(shortcut)
            lbl_key.setStyleSheet(
                "font-family: 'Consolas', monospace; font-size: 10px; color: #94A3B8; "
                "background-color: rgba(255, 255, 255, 0.06); "
                "border: 1px solid rgba(255, 255, 255, 0.1); "
                "border-radius: 4px; padding: 2px 6px;"
            )
            layout.addWidget(lbl_key)


class CommandPalette(QDialog):
    """Floating spotlight command palette."""

    action_selected = pyqtSignal(object)

    def __init__(self, actions_list: list = None, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedWidth(560)

        self.all_actions = actions_list or []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Card container with shadow
        card = QWidget()
        card.setObjectName("palette-card")
        card.setStyleSheet("""
            #palette-card {
                background-color: #121626;
                border: 1px solid rgba(139, 92, 246, 0.35);
                border-radius: 14px;
            }
        """)

        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(36)
        shadow.setColor(QColor(0, 0, 0, 200))
        shadow.setOffset(0, 10)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 14, 14, 14)
        card_layout.setSpacing(10)

        # Search Bar
        search_box = QHBoxLayout()
        search_box.setSpacing(8)

        lbl_icon = QLabel()
        lbl_icon.setPixmap(get_svg_icon("search", color="#8B5CF6", size=18).pixmap(18, 18))
        search_box.addWidget(lbl_icon)

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Type a command or search actions... (Esc to close)")
        self.txt_search.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                font-size: 15px;
                color: #FFFFFF;
                padding: 4px;
            }
        """)
        self.txt_search.textChanged.connect(self._filter_commands)
        search_box.addWidget(self.txt_search)
        card_layout.addLayout(search_box)

        # Divider line
        divider = QLabel()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: rgba(255, 255, 255, 0.08);")
        card_layout.addWidget(divider)

        # Results list
        self.list_widget = QListWidget()
        self.list_widget.setFixedHeight(280)
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
            }
            QListWidget::item {
                border-radius: 8px;
                margin: 2px 0;
            }
            QListWidget::item:selected {
                background-color: #1E2542;
                border: 1px solid rgba(139, 92, 246, 0.4);
            }
        """)
        self.list_widget.itemActivated.connect(self._execute_selected)
        card_layout.addWidget(self.list_widget)

        # Footer hint
        lbl_hint = QLabel("Use arrows to navigate • Enter to select • Esc to dismiss")
        lbl_hint.setStyleSheet("font-size: 11px; color: #64748B; padding-top: 4px;")
        card_layout.addWidget(lbl_hint)

        main_layout.addWidget(card)

        self._populate_list(self.all_actions)

    def set_actions(self, actions_list: list):
        self.all_actions = actions_list
        self._filter_commands(self.txt_search.text())

    def _populate_list(self, items: list):
        self.list_widget.clear()
        for item in items:
            list_item = QListWidgetItem(self.list_widget)
            list_item.setSizeHint(CommandItemWidget("", "").sizeHint())
            row_widget = CommandItemWidget(
                title=item["title"],
                category=item.get("category", ""),
                shortcut=item.get("shortcut", "")
            )
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, row_widget)
            list_item.setData(Qt.ItemDataRole.UserRole, item)

        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def _filter_commands(self, text: str):
        query = text.strip().lower()
        if not query:
            filtered = self.all_actions
        else:
            filtered = [
                a for a in self.all_actions
                if query in a["title"].lower() or query in a.get("category", "").lower()
            ]
        self._populate_list(filtered)

    def _execute_selected(self):
        cur_item = self.list_widget.currentItem()
        if cur_item:
            action_data = cur_item.data(Qt.ItemDataRole.UserRole)
            if action_data and "callback" in action_data:
                self.hide()
                action_data["callback"]()

    def keyPressEvent(self, e: QKeyEvent):
        if e.key() == Qt.Key.Key_Down:
            cur = self.list_widget.currentRow()
            if cur < self.list_widget.count() - 1:
                self.list_widget.setCurrentRow(cur + 1)
            return
        elif e.key() == Qt.Key.Key_Up:
            cur = self.list_widget.currentRow()
            if cur > 0:
                self.list_widget.setCurrentRow(cur - 1)
            return
        elif e.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            self._execute_selected()
            return
        elif e.key() == Qt.Key.Key_Escape:
            self.hide()
            return
        super().keyPressEvent(e)

    def show_centered(self, parent_window):
        self.txt_search.clear()
        self._filter_commands("")
        self.txt_search.setFocus()

        parent_rect = parent_window.geometry()
        x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
        y = parent_rect.y() + int(parent_rect.height() * 0.14)
        self.move(x, y)
        self.show()
        self.raise_()
        self.activateWindow()
