"""
Find and Replace Panel Module for Aether.
Supports case-sensitive, whole-word, regex searches, and Find in All Open Files.
"""

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit,
    QPushButton, QCheckBox, QLabel, QListWidget, QListWidgetItem, QFrame
)

from .icons import get_svg_icon


class FindReplaceWidget(QFrame):
    """Modern floating Find & Replace panel."""

    jump_to_file_line = pyqtSignal(object, int, int)

    def __init__(self, tab_manager=None, parent=None):
        super().__init__(parent)
        self.tab_manager = tab_manager
        self.setObjectName("find-replace-panel")

        self.setStyleSheet("""
            #find-replace-panel {
                background-color: #121626;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        # Header with close button
        header = QHBoxLayout()
        self.lbl_title = QLabel("FIND & REPLACE")
        self.lbl_title.setStyleSheet("font-weight: 700; font-size: 11px; letter-spacing: 0.8px; color: #64748B;")
        header.addWidget(self.lbl_title)
        header.addStretch()

        self.btn_close = QPushButton()
        self.btn_close.setIcon(get_svg_icon("close", color="#94A3B8", size=12))
        self.btn_close.setFixedSize(22, 22)
        self.btn_close.clicked.connect(self.hide)
        header.addWidget(self.btn_close)
        layout.addLayout(header)

        # Grid of inputs and buttons
        grid = QGridLayout()
        grid.setSpacing(6)

        # Find row
        grid.addWidget(QLabel("Find:"), 0, 0)
        self.txt_find = QLineEdit()
        self.txt_find.setPlaceholderText("Search term...")
        self.txt_find.returnPressed.connect(self.find_next)
        grid.addWidget(self.txt_find, 0, 1)

        self.btn_find_next = QPushButton("Find Next")
        self.btn_find_next.clicked.connect(self.find_next)
        grid.addWidget(self.btn_find_next, 0, 2)

        self.btn_find_prev = QPushButton("Find Prev")
        self.btn_find_prev.clicked.connect(self.find_prev)
        grid.addWidget(self.btn_find_prev, 0, 3)

        # Replace row
        grid.addWidget(QLabel("Replace:"), 1, 0)
        self.txt_replace = QLineEdit()
        self.txt_replace.setPlaceholderText("Replace with...")
        self.txt_replace.returnPressed.connect(self.replace_one)
        grid.addWidget(self.txt_replace, 1, 1)

        self.btn_replace = QPushButton("Replace")
        self.btn_replace.clicked.connect(self.replace_one)
        grid.addWidget(self.btn_replace, 1, 2)

        self.btn_replace_all = QPushButton("Replace All")
        self.btn_replace_all.clicked.connect(self.replace_all)
        grid.addWidget(self.btn_replace_all, 1, 3)

        layout.addLayout(grid)

        # Search Options
        opt_layout = QHBoxLayout()
        self.chk_case = QCheckBox("Match Case")
        self.chk_word = QCheckBox("Whole Word")
        self.chk_regex = QCheckBox("Regex")
        opt_layout.addWidget(self.chk_case)
        opt_layout.addWidget(self.chk_word)
        opt_layout.addWidget(self.chk_regex)
        opt_layout.addStretch()

        self.btn_find_all = QPushButton("Find in All Open Files")
        self.btn_find_all.setIcon(get_svg_icon("search", color="#94A3B8", size=13))
        self.btn_find_all.clicked.connect(self.find_in_all_files)
        opt_layout.addWidget(self.btn_find_all)

        layout.addLayout(opt_layout)

        # Status readout
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("font-size: 11px; color: #8B5CF6;")
        layout.addWidget(self.lbl_status)

        # Results list for "Find in all open files"
        self.results_list = QListWidget()
        self.results_list.setMaximumHeight(120)
        self.results_list.hide()
        self.results_list.setStyleSheet("""
            QListWidget {
                background: #0B0D14;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 4px 8px;
            }
        """)
        self.results_list.itemDoubleClicked.connect(self._on_result_clicked)
        layout.addWidget(self.results_list)

    def _get_active_editor(self):
        if self.tab_manager:
            return self.tab_manager.current_editor()
        return None

    def find_next(self) -> bool:
        editor = self._get_active_editor()
        term = self.txt_find.text()
        if not editor or not term:
            return False

        found = editor.findFirst(
            term,
            self.chk_regex.isChecked(),
            self.chk_case.isChecked(),
            self.chk_word.isChecked(),
            True,
            True
        )

        self.lbl_status.setText("Match found." if found else "No matches found.")
        return found

    def find_prev(self) -> bool:
        editor = self._get_active_editor()
        term = self.txt_find.text()
        if not editor or not term:
            return False

        found = editor.findFirst(
            term,
            self.chk_regex.isChecked(),
            self.chk_case.isChecked(),
            self.chk_word.isChecked(),
            True,
            False
        )

        self.lbl_status.setText("Match found." if found else "No previous matches found.")
        return found

    def replace_one(self):
        editor = self._get_active_editor()
        if not editor or not self.txt_find.text():
            return

        if editor.hasSelectedText():
            editor.replaceSelectedText(self.txt_replace.text())

        self.find_next()

    def replace_all(self):
        editor = self._get_active_editor()
        term = self.txt_find.text()
        repl = self.txt_replace.text()
        if not editor or not term:
            return

        count = 0
        editor.beginUndoAction()
        try:
            found = editor.findFirst(
                term,
                self.chk_regex.isChecked(),
                self.chk_case.isChecked(),
                self.chk_word.isChecked(),
                False,
                True,
                0,
                0
            )
            while found:
                editor.replaceSelectedText(repl)
                count += 1
                found = editor.findNext()
        finally:
            editor.endUndoAction()

        self.lbl_status.setText(f"Replaced {count} occurrence(s).")

    def find_in_all_files(self):
        if not self.tab_manager:
            return

        term = self.txt_find.text()
        if not term:
            return

        self.results_list.clear()
        self.results_list.show()

        case_sensitive = self.chk_case.isChecked()
        whole_word = self.chk_word.isChecked()
        regex = self.chk_regex.isChecked()

        import re
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern_str = term if regex else re.escape(term)
        if whole_word:
            pattern_str = r"\b" + pattern_str + r"\b"

        try:
            compiled_regex = re.compile(pattern_str, flags)
        except Exception as e:
            self.lbl_status.setText(f"Regex error: {e}")
            return

        total_matches = 0
        for i in range(self.tab_manager.count()):
            editor = self.tab_manager.widget(i)
            if not editor:
                continue

            file_title = editor.get_file_name()
            lines = editor.text().splitlines()

            for line_idx, line_content in enumerate(lines):
                for match in compiled_regex.finditer(line_content):
                    total_matches += 1
                    col_idx = match.start()
                    snippet = line_content.strip()
                    item_text = f"[{file_title}:{line_idx + 1}:{col_idx + 1}] {snippet}"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.ItemDataRole.UserRole, (editor, line_idx, col_idx))
                    self.results_list.addItem(item)

        self.lbl_status.setText(f"Found {total_matches} match(es) across open files.")

    def _on_result_clicked(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            editor, line, col = data
            idx = self.tab_manager.indexOf(editor)
            if idx != -1:
                self.tab_manager.setCurrentIndex(idx)
                editor.setCursorPosition(line, col)
                editor.ensureLineVisible(line)
                editor.setFocus()
