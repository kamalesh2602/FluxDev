"""
Tab Manager Module for FluxDev.
Controls open editor tabs, modified dots ('•'), close confirmations,
session restore, and initializes untitled tabs with HTML5 boilerplate.
"""

import os
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QTabWidget, QMessageBox, QFileDialog

from .editor_widget import CodeEditorWidget
from .templates import HTML5_BOILERPLATE


class TabManager(QTabWidget):
    """Manages document tabs with modified indicators and safe closing."""

    active_editor_changed = pyqtSignal(object)  # CodeEditorWidget
    file_saved = pyqtSignal(str)  # absolute path
    file_closed = pyqtSignal(str)
    empty_state_changed = pyqtSignal(bool)  # True if 0 tabs open

    def __init__(self, theme_name: str = "FluxDev Dark", parent=None):
        super().__init__(parent)
        self.theme_name = theme_name

        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)

        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self._on_current_changed)

    def _on_current_changed(self, index: int):
        editor = self.widget(index)
        self.active_editor_changed.emit(editor)
        self.empty_state_changed.emit(self.count() == 0)

    def current_editor(self) -> CodeEditorWidget:
        return self.currentWidget()

    def new_file(self, content: str = "", file_path: str = None) -> CodeEditorWidget:
        """
        Creates a new editor tab.
        If content is empty and file_path is None, defaults to short HTML5 boilerplate.
        """
        # Issue 6: Default new untitled tab to HTML5 boilerplate
        if not content and not file_path:
            content = HTML5_BOILERPLATE

        editor = CodeEditorWidget(file_path=file_path, theme_name=self.theme_name, parent=self)
        if content:
            editor.setText(content)
            editor.setModified(False)  # Unmodified on fresh creation

        editor.file_status_changed.connect(lambda: self._refresh_tab_title(editor))

        idx = self.addTab(editor, editor.get_file_name())
        self.setTabToolTip(idx, editor.file_path or "New unsaved file")
        self.setCurrentIndex(idx)
        self._refresh_tab_title(editor)
        self.empty_state_changed.emit(False)
        return editor

    def open_file(self, path: str) -> CodeEditorWidget:
        """Opens an existing file or activates its tab if already open."""
        path = os.path.abspath(path)

        for i in range(self.count()):
            editor = self.widget(i)
            if editor and editor.file_path and os.path.abspath(editor.file_path) == path:
                self.setCurrentIndex(i)
                return editor

        editor = self.new_file(file_path=path)
        return editor

    def _refresh_tab_title(self, editor: CodeEditorWidget):
        idx = self.indexOf(editor)
        if idx == -1:
            return

        name = editor.get_file_name()
        if editor.isModified():
            title = f"• {name}"
        else:
            title = name

        self.setTabText(idx, title)
        self.setTabToolTip(idx, editor.file_path or "New unsaved file")

    def save_current_file(self) -> bool:
        """Saves active tab to disk, prompting if untitled."""
        editor = self.current_editor()
        if not editor:
            return False

        if not editor.file_path:
            return self.save_file_as(editor)

        success = editor.save_file()
        if success:
            self._refresh_tab_title(editor)
            self.file_saved.emit(editor.file_path)
        return success

    def save_file_as(self, editor: CodeEditorWidget = None) -> bool:
        """Prompts for target path and saves."""
        if not editor:
            editor = self.current_editor()
        if not editor:
            return False

        default_dir = os.path.dirname(editor.file_path) if editor.file_path else os.getcwd()
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            default_dir,
            "Web Files (*.html *.htm *.css *.js *.json *.md);;All Files (*.*)"
        )

        if not path:
            return False

        success = editor.save_file(path)
        if success:
            self._refresh_tab_title(editor)
            self.file_saved.emit(editor.file_path)
        return success

    def save_all_files(self) -> bool:
        """Saves all modified tabs."""
        all_ok = True
        for i in range(self.count()):
            editor = self.widget(i)
            if editor and editor.isModified():
                if not editor.file_path:
                    ok = self.save_file_as(editor)
                else:
                    ok = editor.save_file()
                if ok:
                    self._refresh_tab_title(editor)
                    self.file_saved.emit(editor.file_path)
                else:
                    all_ok = False
        return all_ok

    def close_tab(self, index: int) -> bool:
        """Prompts to save if modified. Returns True if closed, False if canceled."""
        editor = self.widget(index)
        if not editor:
            return True

        if editor.isModified():
            name = editor.get_file_name()
            reply = QMessageBox.question(
                self,
                "Save Changes?",
                f"File '{name}' has unsaved changes.\nDo you want to save them before closing?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )

            if reply == QMessageBox.StandardButton.Save:
                if not self.save_current_file():
                    return False
            elif reply == QMessageBox.StandardButton.Cancel:
                return False

        closed_path = editor.file_path
        self.removeTab(index)
        editor.deleteLater()

        if closed_path:
            self.file_closed.emit(closed_path)

        if self.count() == 0:
            self.empty_state_changed.emit(True)

        return True

    def close_all(self) -> bool:
        """Attempts to close all tabs safely."""
        while self.count() > 0:
            if not self.close_tab(0):
                return False
        return True

    def apply_theme(self, theme_name: str):
        """Applies theme to all open tabs."""
        self.theme_name = theme_name
        for i in range(self.count()):
            editor = self.widget(i)
            if editor:
                editor.apply_theme(theme_name)

    # -------------------------------------------------------------
    # SESSION RESTORATION
    # -------------------------------------------------------------

    def save_session(self, settings_mgr):
        """Persists open file paths to QSettings."""
        open_paths = []
        for i in range(self.count()):
            editor = self.widget(i)
            if editor and editor.file_path and os.path.exists(editor.file_path):
                open_paths.append(editor.file_path)

        settings_mgr.set_open_files(open_paths)
        settings_mgr.set_active_file_index(self.currentIndex())

    def restore_session(self, settings_mgr):
        """Restores tabs from previous session."""
        open_paths = settings_mgr.get_open_files()
        active_idx = settings_mgr.get_active_file_index()

        for path in open_paths:
            if os.path.exists(path):
                self.open_file(path)

        if self.count() > 0:
            if 0 <= active_idx < self.count():
                self.setCurrentIndex(active_idx)
            self.empty_state_changed.emit(False)
        else:
            self.empty_state_changed.emit(True)
