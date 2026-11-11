"""
FluxDev Main Window Module.
Features a frameless, rounded architectural shell with custom title bar,
a single 3-pane QSplitter (sidebar | editor | preview),
Command Palette (Ctrl+Shift+P / Ctrl+K), and live preview toggle (F6 / Ctrl+P).
"""

import os
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QAction, QColor, QKeySequence
from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QFileDialog, QInputDialog,
    QMessageBox, QLabel, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QGraphicsDropShadowEffect
)

from .settings import SettingsManager
from .themes import generate_qss, save_active_qss, THEMES
from .icons import get_svg_icon
from .title_bar import CustomTitleBar
from .tab_manager import TabManager
from .sidebar import ProjectSidebar
from .web_preview import LivePreviewWidget
from .console_panel import ConsolePanel
from .find_replace import FindReplaceWidget
from .welcome_screen import WelcomeScreen
from .command_palette import CommandPalette
from .formatters import format_document
from .templates import HTML5_BOILERPLATE, create_starter_project


class MainWindow(QMainWindow):
    """Frameless modern code studio for FluxDev."""

    THEME_CYCLE = ["FluxDev Dark", "FluxDev Midnight", "FluxDev Light"]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FluxDev — Where ideas flow into code")
        self.settings_mgr = SettingsManager()

        # Frameless Window with Translucent Background for Rounded Corners & Shadow
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # Theme Initialization
        saved_theme = self.settings_mgr.get_theme()
        self.current_theme = saved_theme if saved_theme in THEMES else "FluxDev Dark"

        # Root Outer Container
        self.outer_widget = QWidget(self)
        self.setCentralWidget(self.outer_widget)

        outer_layout = QVBoxLayout(self.outer_widget)
        outer_layout.setContentsMargins(10, 10, 10, 10)

        # Inner Frameless Shell with Rounded Corners & Shadow
        self.shell = QWidget()
        self.shell.setObjectName("root-container")

        self.shadow = QGraphicsDropShadowEffect(self.shell)
        self.shadow.setBlurRadius(28)
        self.shadow.setColor(QColor(0, 0, 0, 180))
        self.shadow.setOffset(0, 8)
        self.shell.setGraphicsEffect(self.shadow)

        shell_layout = QVBoxLayout(self.shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        # 1. Custom Title Bar
        self.title_bar = CustomTitleBar(parent_window=self)
        shell_layout.addWidget(self.title_bar)

        # 2. Main 3-Pane QSplitter [sidebar | editor | preview] (Issue 2)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setChildrenCollapsible(True)

        # Pane 0: Sidebar (fixed ~220px, collapsible)
        self.sidebar = ProjectSidebar(parent=self)
        self.main_splitter.addWidget(self.sidebar)

        # Pane 1: Editor Area (stretch factor 3, min width 400px)
        self.editor_container = QWidget()
        self.editor_container.setMinimumWidth(400)
        ed_layout = QVBoxLayout(self.editor_container)
        ed_layout.setContentsMargins(0, 0, 0, 0)
        ed_layout.setSpacing(0)

        # Stacked central area: [0: Tabs, 1: Welcome Screen]
        self.center_stack = QStackedWidget()

        self.tab_manager = TabManager(theme_name=self.current_theme, parent=self)
        self.center_stack.addWidget(self.tab_manager)  # Index 0

        self.welcome_screen = WelcomeScreen(parent=self)
        self.center_stack.addWidget(self.welcome_screen)  # Index 1

        ed_layout.addWidget(self.center_stack, stretch=1)

        # Bottom docks inside editor container
        self.find_replace = FindReplaceWidget(tab_manager=self.tab_manager, parent=self)
        self.find_replace.hide()
        ed_layout.addWidget(self.find_replace)

        self.console_panel = ConsolePanel(parent=self)
        self.console_panel.hide()
        ed_layout.addWidget(self.console_panel)

        self.main_splitter.addWidget(self.editor_container)

        # Pane 2: Live Preview (stretch factor 2, HIDDEN by default)
        self.live_preview = LivePreviewWidget(
            console_panel=self.console_panel,
            theme_name=self.current_theme,
            parent=self
        )
        self.main_splitter.addWidget(self.live_preview)

        # Configure Splitter stretch factors
        self.main_splitter.setStretchFactor(0, 0)  # Sidebar
        self.main_splitter.setStretchFactor(1, 3)  # Editor (stretch factor 3)
        self.main_splitter.setStretchFactor(2, 2)  # Preview (stretch factor 2)

        self.main_splitter.setCollapsible(0, True)
        self.main_splitter.setCollapsible(1, False)
        self.main_splitter.setCollapsible(2, True)

        shell_layout.addWidget(self.main_splitter, stretch=1)

        # 3. Status Bar
        self._setup_status_bar()
        shell_layout.addWidget(self.status_bar)

        outer_layout.addWidget(self.shell)

        # Command Palette
        self.command_palette = CommandPalette(parent=self)

        # Setup shortcuts, signals, and palette actions
        self._setup_actions()
        self._connect_signals()
        self._build_command_palette_actions()

        # Apply Theme & Restore Session
        self.apply_theme(self.current_theme)
        self._restore_session_and_geometry()

    def _setup_status_bar(self):
        self.status_bar = QWidget()
        self.status_bar.setFixedHeight(26)
        self.status_bar.setStyleSheet("background-color: transparent; border-top: 1px solid rgba(255, 255, 255, 0.06);")

        sb_layout = QHBoxLayout(self.status_bar)
        sb_layout.setContentsMargins(12, 0, 12, 0)
        sb_layout.setSpacing(16)

        self.lbl_sb_pos = QLabel("Ln 1, Col 1")
        self.lbl_sb_pos.setStyleSheet("font-size: 11px; color: #64748B;")
        sb_layout.addWidget(self.lbl_sb_pos)

        self.lbl_sb_size = QLabel("0 B")
        self.lbl_sb_size.setStyleSheet("font-size: 11px; color: #64748B;")
        sb_layout.addWidget(self.lbl_sb_size)

        sb_layout.addStretch()

        self.lbl_sb_encoding = QLabel("UTF-8")
        self.lbl_sb_encoding.setStyleSheet("font-size: 11px; color: #64748B;")
        sb_layout.addWidget(self.lbl_sb_encoding)

        self.lbl_sb_lang = QLabel("HTML")
        self.lbl_sb_lang.setStyleSheet("font-size: 11px; font-weight: bold; color: #8B5CF6;")
        sb_layout.addWidget(self.lbl_sb_lang)

    def _setup_actions(self):
        """Registers global keyboard shortcuts."""
        def reg_shortcut(key_seq, callback):
            act = QAction(self)
            act.setShortcut(QKeySequence(key_seq))
            act.triggered.connect(callback)
            self.addAction(act)
            return act

        self.act_new = reg_shortcut("Ctrl+N", self.on_new_file)
        self.act_open = reg_shortcut("Ctrl+O", self.on_open_file)
        self.act_save = reg_shortcut("Ctrl+S", self.tab_manager.save_current_file)
        self.act_save_as = reg_shortcut("Ctrl+Shift+S", lambda: self.tab_manager.save_file_as())
        self.act_save_all = reg_shortcut("Ctrl+Alt+S", self.tab_manager.save_all_files)
        self.act_close_tab = reg_shortcut("Ctrl+W", self._close_current_tab)

        self.act_palette = reg_shortcut("Ctrl+Shift+P", self.open_command_palette)
        self.act_palette_k = reg_shortcut("Ctrl+K", self.open_command_palette)

        self.act_find = reg_shortcut("Ctrl+F", self.on_show_find)
        self.act_replace = reg_shortcut("Ctrl+H", self.on_show_replace)
        self.act_goto = reg_shortcut("Ctrl+G", self.on_goto_line)

        self.act_toggle_sidebar = reg_shortcut("Ctrl+B", self.toggle_sidebar)

        # Issue 2: Preview toggled by toolbar button or F6 (and Ctrl+P)
        self.act_toggle_preview_f6 = reg_shortcut("F6", self.toggle_preview)
        self.act_toggle_preview_p = reg_shortcut("Ctrl+P", self.toggle_preview)

        self.act_toggle_console = reg_shortcut("Ctrl+J", self.toggle_console)
        self.act_refresh_preview = reg_shortcut("F5", self.live_preview._perform_reload)

        self.act_format = reg_shortcut("Ctrl+Alt+F", self.on_format_document)
        self.act_dup_line = reg_shortcut("Ctrl+D", self._dispatch_editor("duplicate_line"))
        self.act_comment = reg_shortcut("Ctrl+/", self._dispatch_editor("toggle_comment"))
        self.act_zoom_in = reg_shortcut("Ctrl++", self._dispatch_editor("zoomIn"))
        self.act_zoom_out = reg_shortcut("Ctrl+-", self._dispatch_editor("zoomOut"))

    def _connect_signals(self):
        self.title_bar.command_palette_requested.connect(self.open_command_palette)
        self.title_bar.toggle_sidebar_requested.connect(self.toggle_sidebar)
        self.title_bar.toggle_preview_requested.connect(self.toggle_preview)
        self.title_bar.format_doc_requested.connect(self.on_format_document)
        self.title_bar.toggle_theme_requested.connect(self.cycle_theme)

        self.tab_manager.active_editor_changed.connect(self._on_active_editor_changed)
        self.tab_manager.file_saved.connect(self._on_file_saved)
        self.tab_manager.empty_state_changed.connect(self._on_empty_state_changed)

        self.sidebar.file_opened.connect(self.tab_manager.open_file)
        self.sidebar.root_folder_changed.connect(self._on_project_folder_changed)
        self.sidebar.new_project_requested.connect(self.on_template_starter_project)

        self.welcome_screen.new_file_requested.connect(self.on_new_file)
        self.welcome_screen.open_file_requested.connect(self.on_open_file)
        self.welcome_screen.open_folder_requested.connect(self.sidebar.prompt_open_folder)
        self.welcome_screen.starter_project_requested.connect(self.on_template_starter_project)
        self.welcome_screen.html5_template_requested.connect(self.on_template_html5)
        self.welcome_screen.open_recent_path_requested.connect(self._open_recent_path)

    def _build_command_palette_actions(self):
        actions = [
            {"title": "New File", "category": "File", "shortcut": "Ctrl+N", "callback": self.on_new_file},
            {"title": "Open File...", "category": "File", "shortcut": "Ctrl+O", "callback": self.on_open_file},
            {"title": "Open Project Folder...", "category": "File", "shortcut": "", "callback": self.sidebar.prompt_open_folder},
            {"title": "Save File", "category": "File", "shortcut": "Ctrl+S", "callback": self.tab_manager.save_current_file},
            {"title": "Save File As...", "category": "File", "shortcut": "Ctrl+Shift+S", "callback": lambda: self.tab_manager.save_file_as()},
            {"title": "Save All Files", "category": "File", "shortcut": "Ctrl+Alt+S", "callback": self.tab_manager.save_all_files},
            {"title": "Close Tab", "category": "File", "shortcut": "Ctrl+W", "callback": self._close_current_tab},

            {"title": "Format Document", "category": "Edit", "shortcut": "Ctrl+Alt+F", "callback": self.on_format_document},
            {"title": "Toggle Comment", "category": "Edit", "shortcut": "Ctrl+/", "callback": self._dispatch_editor("toggle_comment")},
            {"title": "Duplicate Line", "category": "Edit", "shortcut": "Ctrl+D", "callback": self._dispatch_editor("duplicate_line")},

            {"title": "Find in Document", "category": "Search", "shortcut": "Ctrl+F", "callback": self.on_show_find},
            {"title": "Replace in Document", "category": "Search", "shortcut": "Ctrl+H", "callback": self.on_show_replace},
            {"title": "Go to Line...", "category": "Search", "shortcut": "Ctrl+G", "callback": self.on_goto_line},

            {"title": "Toggle Project Sidebar", "category": "View", "shortcut": "Ctrl+B", "callback": self.toggle_sidebar},
            {"title": "Toggle Live Preview", "category": "View", "shortcut": "F6 / Ctrl+P", "callback": self.toggle_preview},
            {"title": "Toggle JavaScript Console", "category": "View", "shortcut": "Ctrl+J", "callback": self.toggle_console},
            {"title": "Force Refresh Preview", "category": "View", "shortcut": "F5", "callback": self.live_preview._perform_reload},

            {"title": "Theme: Switch to FluxDev Dark", "category": "Theme", "shortcut": "", "callback": lambda: self.apply_theme("FluxDev Dark")},
            {"title": "Theme: Switch to FluxDev Midnight (OLED)", "category": "Theme", "shortcut": "", "callback": lambda: self.apply_theme("FluxDev Midnight")},
            {"title": "Theme: Switch to FluxDev Light", "category": "Theme", "shortcut": "", "callback": lambda: self.apply_theme("FluxDev Light")},

            {"title": "Template: Blank HTML5 Boilerplate", "category": "Templates", "shortcut": "", "callback": self.on_template_html5},
            {"title": "Template: HTML + CSS + JS Starter Project", "category": "Templates", "shortcut": "", "callback": self.on_template_starter_project},
        ]
        self.command_palette.set_actions(actions)

    def open_command_palette(self):
        self.command_palette.show_centered(self)

    # -------------------------------------------------------------
    # EDITOR & STATUS BAR SYNC
    # -------------------------------------------------------------

    def _on_active_editor_changed(self, editor):
        if not editor:
            self.lbl_sb_pos.setText("Ln 0, Col 0")
            self.lbl_sb_size.setText("0 B")
            self.lbl_sb_lang.setText("None")
            self.title_bar.set_document_title("")
            return

        editor.cursor_info_changed.connect(self._update_status_cursor)
        editor.textChanged.connect(self._on_editor_text_changed)

        line, col = editor.getCursorPosition()
        self.lbl_sb_pos.setText(f"Ln {line + 1}, Col {col + 1}")
        self.lbl_sb_encoding.setText(editor.encoding)
        self.lbl_sb_lang.setText(editor.language_name)
        self.lbl_sb_size.setText(editor.get_file_size_str())
        self.title_bar.set_document_title(editor.get_file_name())

        self._sync_preview(editor)

    def _update_status_cursor(self, line, col):
        self.lbl_sb_pos.setText(f"Ln {line}, Col {col}")
        editor = self.tab_manager.current_editor()
        if editor:
            self.lbl_sb_size.setText(editor.get_file_size_str())

    def _on_editor_text_changed(self):
        editor = self.tab_manager.current_editor()
        if editor:
            self._sync_preview(editor)

    def _sync_preview(self, editor):
        if not editor:
            return

        ext = os.path.splitext(editor.file_path)[1].lower() if editor.file_path else ".html"

        if ext in [".html", ".htm"] or not editor.file_path:
            self.live_preview.schedule_refresh(
                html_path=editor.file_path,
                html_content=editor.text()
            )
        elif ext in [".css", ".js"]:
            self.live_preview.schedule_refresh()

    def _on_file_saved(self, path):
        editor = self.tab_manager.current_editor()
        if editor:
            self._sync_preview(editor)
        self.sidebar.refresh_tree()

    def _on_empty_state_changed(self, is_empty: bool):
        if is_empty:
            self.center_stack.setCurrentIndex(1)  # Welcome screen
            self.welcome_screen.set_recent_files(self.settings_mgr.get_open_files())
        else:
            self.center_stack.setCurrentIndex(0)  # Editor workspace

    def _close_current_tab(self):
        if self.tab_manager.count() > 0:
            self.tab_manager.close_tab(self.tab_manager.currentIndex())

    def _dispatch_editor(self, method_name: str):
        def callback():
            editor = self.tab_manager.current_editor()
            if editor and hasattr(editor, method_name):
                getattr(editor, method_name)()
        return callback

    # -------------------------------------------------------------
    # ACTION HANDLERS
    # -------------------------------------------------------------

    def on_new_file(self):
        self.tab_manager.new_file()
        self.center_stack.setCurrentIndex(0)

    def on_open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            self.settings_mgr.get_last_project_dir() or os.getcwd(),
            "Web Files (*.html *.htm *.css *.js *.json *.md);;All Files (*.*)"
        )
        if path:
            self.tab_manager.open_file(path)
            self.center_stack.setCurrentIndex(0)

    def _open_recent_path(self, path: str):
        if os.path.isdir(path):
            self.sidebar.set_root_path(path)
        elif os.path.isfile(path):
            self.tab_manager.open_file(path)
            self.center_stack.setCurrentIndex(0)

    def _on_project_folder_changed(self, path: str):
        self.settings_mgr.set_last_project_dir(path)
        self.welcome_screen.set_recent_files([path] + self.settings_mgr.get_open_files())

    def on_format_document(self):
        editor = self.tab_manager.current_editor()
        if not editor:
            return

        ext = os.path.splitext(editor.file_path)[1].lower() if editor.file_path else ".html"
        code = editor.text()

        formatted, success, msg = format_document(code, ext)
        if success:
            line, col = editor.getCursorPosition()
            editor.beginUndoAction()
            try:
                editor.setText(formatted)
                editor.setCursorPosition(min(line, editor.lines() - 1), col)
            finally:
                editor.endUndoAction()
            self.lbl_sb_pos.setText(msg)
        else:
            self.lbl_sb_pos.setText(msg)

    def on_show_find(self):
        self.find_replace.show()
        self.find_replace.txt_find.setFocus()
        self.find_replace.txt_find.selectAll()

    def on_show_replace(self):
        self.find_replace.show()
        self.find_replace.txt_replace.setFocus()
        self.find_replace.txt_replace.selectAll()

    def on_goto_line(self):
        editor = self.tab_manager.current_editor()
        if not editor:
            return

        total_lines = editor.lines()
        line_num, ok = QInputDialog.getInt(
            self,
            "Go to Line",
            f"Enter line number (1 - {total_lines}):",
            value=editor.getCursorPosition()[0] + 1,
            min=1,
            max=total_lines
        )
        if ok:
            editor.goto_line(line_num)

    def on_template_html5(self):
        self.tab_manager.new_file(content=HTML5_BOILERPLATE)
        self.center_stack.setCurrentIndex(0)

    def on_template_starter_project(self):
        target_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Folder for Starter Project",
            self.settings_mgr.get_last_project_dir() or os.getcwd()
        )
        if not target_dir:
            return

        created_files = create_starter_project(target_dir)
        self.sidebar.set_root_path(target_dir)

        for f in created_files:
            if f.endswith("index.html"):
                self.tab_manager.open_file(f)
                break

        self.center_stack.setCurrentIndex(0)

    # -------------------------------------------------------------
    # VIEW TOGGLES & THEMES (Issue 2)
    # -------------------------------------------------------------

    def toggle_sidebar(self):
        is_now_visible = not self.sidebar.isVisible()
        self.sidebar.toggle_animated(is_now_visible)
        self.title_bar.btn_sidebar.setChecked(is_now_visible)

    def toggle_preview(self):
        """
        Toggles live preview (F6 / Ctrl+P).
        When shown, splits editor and preview about 55/45.
        """
        is_visible = not self.live_preview.isVisible()
        self.live_preview.setVisible(is_visible)
        self.title_bar.btn_preview.setChecked(is_visible)
        self.settings_mgr.set_preview_visible(is_visible)

        # Issue 2: When shown, split editor and preview about 55/45
        if is_visible:
            total_w = self.main_splitter.width()
            sb_w = self.sidebar.width() if self.sidebar.isVisible() else 0
            avail_w = max(600, total_w - sb_w)
            editor_w = int(avail_w * 0.55)
            preview_w = avail_w - editor_w
            self.main_splitter.setSizes([sb_w, editor_w, preview_w])
        else:
            sb_w = self.sidebar.width() if self.sidebar.isVisible() else 0
            self.main_splitter.setSizes([sb_w, self.main_splitter.width() - sb_w, 0])

    def toggle_console(self):
        self.console_panel.setVisible(not self.console_panel.isVisible())

    def cycle_theme(self):
        cur_idx = self.THEME_CYCLE.index(self.current_theme) if self.current_theme in self.THEME_CYCLE else 0
        next_theme = self.THEME_CYCLE[(cur_idx + 1) % len(self.THEME_CYCLE)]
        self.apply_theme(next_theme)

    def apply_theme(self, theme_name: str):
        if theme_name not in THEMES:
            theme_name = "FluxDev Dark"

        self.current_theme = theme_name
        self.settings_mgr.set_theme(theme_name)

        qss = generate_qss(theme_name)
        self.setStyleSheet(qss)
        save_active_qss(theme_name)

        if theme_name == "FluxDev Dark":
            self.title_bar.btn_theme.setText("Dark")
            self.title_bar.btn_theme.setIcon(get_svg_icon("moon", color="#94A3B8", size=14))
        elif theme_name == "FluxDev Midnight":
            self.title_bar.btn_theme.setText("Midnight")
            self.title_bar.btn_theme.setIcon(get_svg_icon("zap", color="#A855F7", size=14))
        else:
            self.title_bar.btn_theme.setText("Light")
            self.title_bar.btn_theme.setIcon(get_svg_icon("sun", color="#F59E0B", size=14))

        self.tab_manager.apply_theme(theme_name)
        self.live_preview.set_theme(theme_name)

    # -------------------------------------------------------------
    # SESSION & CLOSE EVENT
    # -------------------------------------------------------------

    def _restore_session_and_geometry(self):
        geom = self.settings_mgr.get_window_geometry()
        if not geom.isEmpty():
            self.restoreGeometry(geom)
        else:
            self.resize(1280, 840)

        # Issue 2: Preview HIDDEN by default
        prev_vis = self.settings_mgr.get_preview_visible()
        self.live_preview.setVisible(prev_vis)
        self.title_bar.btn_preview.setChecked(prev_vis)

        # Set initial splitter layout: sidebar 220px, editor takes rest, preview hidden or 55/45
        if prev_vis:
            total_w = self.width() - 20
            avail_w = max(600, total_w - 220)
            self.main_splitter.setSizes([220, int(avail_w * 0.55), int(avail_w * 0.45)])
        else:
            self.main_splitter.setSizes([220, self.width() - 240, 0])

        last_proj = self.settings_mgr.get_last_project_dir()
        if last_proj and os.path.isdir(last_proj):
            self.sidebar.set_root_path(last_proj)

        self.tab_manager.restore_session(self.settings_mgr)
        self.welcome_screen.set_recent_files(self.settings_mgr.get_open_files())

    def closeEvent(self, event):
        if not self.tab_manager.close_all():
            event.ignore()
            return

        self.settings_mgr.set_window_geometry(self.saveGeometry())
        self.settings_mgr.set_preview_visible(self.live_preview.isVisible())
        self.tab_manager.save_session(self.settings_mgr)
        self.settings_mgr.sync()

        event.accept()
