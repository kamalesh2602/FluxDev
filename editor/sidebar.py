"""
Project Explorer Sidebar Module for FluxDev.
Features empty state when no folder is open, project file tree when opened,
smooth QPropertyAnimation collapse/expand, and CRUD file operations.
"""

import os
import shutil
from PyQt6.QtCore import pyqtSignal, QDir, Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QPushButton,
    QLabel, QMenu, QInputDialog, QMessageBox, QFileDialog, QFrame,
    QStackedWidget
)

from .icons import get_svg_icon, get_svg_pixmap


class ProjectSidebar(QFrame):
    """Modern project explorer with empty state and smooth animated collapse."""

    file_opened = pyqtSignal(str)
    root_folder_changed = pyqtSignal(str)
    new_project_requested = pyqtSignal()

    EXPANDED_WIDTH = 220

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar-panel")
        self.current_root = ""
        self.is_collapsed = False

        self.setFixedWidth(self.EXPANDED_WIDTH)

        self.anim = QPropertyAnimation(self, b"maximumWidth")
        self.anim.setDuration(220)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 10, 8, 8)
        layout.setSpacing(6)

        # 1. Header bar
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(4, 0, 4, 4)
        header_layout.setSpacing(4)

        self.lbl_title = QLabel("EXPLORER")
        self.lbl_title.setStyleSheet("font-weight: 700; font-size: 11px; color: #64748B;")
        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch()

        self.btn_open_folder = QPushButton()
        self.btn_open_folder.setIcon(get_svg_icon("folder-open", color="#94A3B8", size=14))
        self.btn_open_folder.setToolTip("Open Folder")
        self.btn_open_folder.setFixedSize(26, 26)
        self.btn_open_folder.clicked.connect(self.prompt_open_folder)
        header_layout.addWidget(self.btn_open_folder)

        self.btn_new_file = QPushButton()
        self.btn_new_file.setIcon(get_svg_icon("file-plus", color="#94A3B8", size=14))
        self.btn_new_file.setToolTip("New File")
        self.btn_new_file.setFixedSize(26, 26)
        self.btn_new_file.clicked.connect(lambda: self._create_new_file(self.current_root or os.getcwd()))
        header_layout.addWidget(self.btn_new_file)

        self.btn_refresh = QPushButton()
        self.btn_refresh.setIcon(get_svg_icon("refresh", color="#94A3B8", size=14))
        self.btn_refresh.setToolTip("Refresh Explorer")
        self.btn_refresh.setFixedSize(26, 26)
        self.btn_refresh.clicked.connect(self.refresh_tree)
        header_layout.addWidget(self.btn_refresh)

        layout.addLayout(header_layout)

        # 2. Stacked Content: [Page 0: Empty State, Page 1: File Tree]
        self.stack = QStackedWidget()

        # Page 0: Empty state widget (Issue 5)
        self.empty_widget = QWidget()
        empty_layout = QVBoxLayout(self.empty_widget)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.setContentsMargins(10, 30, 10, 30)
        empty_layout.setSpacing(12)

        lbl_empty_icon = QLabel()
        lbl_empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_empty_icon.setPixmap(get_svg_pixmap("folder", color="#475569", size=32))
        empty_layout.addWidget(lbl_empty_icon)

        lbl_no_folder = QLabel("No Folder Open")
        lbl_no_folder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_no_folder.setStyleSheet("font-weight: 600; font-size: 13px; color: #94A3B8;")
        empty_layout.addWidget(lbl_no_folder)

        lbl_no_desc = QLabel("Open a folder or start a new project to explore files.")
        lbl_no_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_no_desc.setWordWrap(True)
        lbl_no_desc.setStyleSheet("font-size: 11px; color: #64748B; text-align: center;")
        empty_layout.addWidget(lbl_no_desc)

        btn_open = QPushButton("Open Folder")
        btn_open.setIcon(get_svg_icon("folder-open", color="#FFFFFF", size=14))
        btn_open.setProperty("class", "btn-primary")
        btn_open.clicked.connect(self.prompt_open_folder)
        empty_layout.addWidget(btn_open)

        btn_new_proj = QPushButton("New Project")
        btn_new_proj.setIcon(get_svg_icon("rocket", color="#94A3B8", size=14))
        btn_new_proj.clicked.connect(self.new_project_requested.emit)
        empty_layout.addWidget(btn_new_proj)

        empty_layout.addStretch()
        self.stack.addWidget(self.empty_widget)  # Index 0

        # Page 1: File tree
        self.tree_widget = QWidget()
        tree_layout = QVBoxLayout(self.tree_widget)
        tree_layout.setContentsMargins(0, 0, 0, 0)

        self.fs_model = QFileSystemModel()
        self.fs_model.setReadOnly(False)
        self.fs_model.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot)

        self.tree = QTreeView()
        self.tree.setModel(self.fs_model)
        self.tree.setAnimated(True)
        self.tree.setIndentation(14)
        self.tree.setSortingEnabled(True)
        self.tree.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        for col in [1, 2, 3]:
            self.tree.hideColumn(col)
        self.tree.setHeaderHidden(True)

        self.tree.doubleClicked.connect(self._on_item_double_clicked)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)

        tree_layout.addWidget(self.tree)
        self.stack.addWidget(self.tree_widget)  # Index 1

        layout.addWidget(self.stack)

        # Show empty state by default
        self.stack.setCurrentIndex(0)

    def toggle_animated(self, make_visible: bool):
        self.anim.stop()
        if make_visible:
            self.setVisible(True)
            self.anim.setStartValue(self.width())
            self.anim.setEndValue(self.EXPANDED_WIDTH)
            self.anim.start()
            self.is_collapsed = False
        else:
            self.anim.setStartValue(self.width())
            self.anim.setEndValue(0)
            self.anim.finished.connect(lambda: self.setVisible(False) if self.maximumWidth() == 0 else None)
            self.anim.start()
            self.is_collapsed = True

    def set_root_path(self, folder_path: str):
        if not folder_path or not os.path.isdir(folder_path):
            self.current_root = ""
            self.lbl_title.setText("EXPLORER")
            self.stack.setCurrentIndex(0)  # Empty state
            return

        self.current_root = os.path.abspath(folder_path)
        root_idx = self.fs_model.setRootPath(self.current_root)
        self.tree.setRootIndex(root_idx)
        folder_name = os.path.basename(self.current_root) or self.current_root

        # Issue 5: Once folder is open, show its name in header
        self.lbl_title.setText(folder_name.upper())
        self.lbl_title.setToolTip(self.current_root)
        self.stack.setCurrentIndex(1)  # Show tree
        self.root_folder_changed.emit(self.current_root)

    def prompt_open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Project Folder", self.current_root or os.getcwd())
        if folder:
            self.set_root_path(folder)

    def refresh_tree(self):
        if self.current_root:
            self.fs_model.setRootPath("")
            root_idx = self.fs_model.setRootPath(self.current_root)
            self.tree.setRootIndex(root_idx)

    def _on_item_double_clicked(self, index):
        if not index.isValid():
            return
        file_path = self.fs_model.filePath(index)
        if os.path.isfile(file_path):
            self.file_opened.emit(file_path)

    def _get_target_directory(self, index) -> str:
        if index.isValid():
            path = self.fs_model.filePath(index)
            if os.path.isdir(path):
                return path
            return os.path.dirname(path)
        return self.current_root or os.getcwd()

    def _show_context_menu(self, position):
        index = self.tree.indexAt(position)
        target_dir = self._get_target_directory(index)
        clicked_path = self.fs_model.filePath(index) if index.isValid() else ""

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #121626;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 18px;
                border-radius: 4px;
                color: #E2E8F0;
            }
            QMenu::item:selected {
                background-color: #1E2542;
                color: #FFFFFF;
            }
        """)

        act_new_file = menu.addAction(get_svg_icon("file-plus", color="#94A3B8", size=14), "New File...")
        act_new_folder = menu.addAction(get_svg_icon("folder", color="#94A3B8", size=14), "New Folder...")
        menu.addSeparator()

        act_rename = None
        act_delete = None
        act_reveal = None

        if clicked_path:
            act_rename = menu.addAction("Rename...")
            act_delete = menu.addAction(get_svg_icon("close", color="#EF4444", size=14), "Delete")
            menu.addSeparator()
            act_reveal = menu.addAction(get_svg_icon("external-link", color="#94A3B8", size=14), "Reveal in Explorer")

        chosen = menu.exec(self.tree.viewport().mapToGlobal(position))

        if chosen == act_new_file:
            self._create_new_file(target_dir)
        elif chosen == act_new_folder:
            self._create_new_folder(target_dir)
        elif chosen == act_rename and clicked_path:
            self._rename_item(clicked_path)
        elif chosen == act_delete and clicked_path:
            self._delete_item(clicked_path)
        elif chosen == act_reveal and clicked_path:
            self._reveal_in_explorer(clicked_path)

    def _create_new_file(self, target_dir: str):
        name, ok = QInputDialog.getText(self, "New File", "Enter file name:")
        if ok and name.strip():
            file_path = os.path.join(target_dir, name.strip())
            if os.path.exists(file_path):
                QMessageBox.warning(self, "Exists", "A file with that name already exists.")
                return
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("")
                self.file_opened.emit(file_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not create file:\n{str(e)}")

    def _create_new_folder(self, target_dir: str):
        name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if ok and name.strip():
            folder_path = os.path.join(target_dir, name.strip())
            if os.path.exists(folder_path):
                QMessageBox.warning(self, "Exists", "A folder with that name already exists.")
                return
            try:
                os.makedirs(folder_path, exist_ok=True)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not create folder:\n{str(e)}")

    def _rename_item(self, path: str):
        old_name = os.path.basename(path)
        new_name, ok = QInputDialog.getText(self, "Rename", "Enter new name:", text=old_name)
        if ok and new_name.strip() and new_name.strip() != old_name:
            parent_dir = os.path.dirname(path)
            new_path = os.path.join(parent_dir, new_name.strip())
            try:
                os.rename(path, new_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not rename:\n{str(e)}")

    def _delete_item(self, path: str):
        name = os.path.basename(path)
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{name}'?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete:\n{str(e)}")

    def _reveal_in_explorer(self, path: str):
        abs_path = os.path.abspath(path)
        if os.name == "nt":
            os.system(f'explorer /select,"{abs_path}"')
        else:
            folder = abs_path if os.path.isdir(abs_path) else os.path.dirname(abs_path)
            os.system(f'xdg-open "{folder}"')
