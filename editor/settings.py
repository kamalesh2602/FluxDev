"""
Settings Manager module for FluxDev using QSettings to persist application state.
Handles window geometry, theme, font preferences, recent files, and open sessions.
"""

from PyQt6.QtCore import QSettings, QByteArray


class SettingsManager:
    """Manages application persistence using Qt QSettings."""

    ORGANIZATION = "FluxDevStudio"
    APPLICATION = "FluxDev"

    def __init__(self):
        self.settings = QSettings(self.ORGANIZATION, self.APPLICATION)

    # Theme (default: FluxDev Dark)
    def get_theme(self) -> str:
        return self.settings.value("ui/theme", "FluxDev Dark", type=str)

    def set_theme(self, theme: str):
        self.settings.setValue("ui/theme", theme)

    # Font (default: 14pt)
    def get_font_family(self) -> str:
        return self.settings.value("editor/font_family", "JetBrains Mono", type=str)

    def set_font_family(self, family: str):
        self.settings.setValue("editor/font_family", family)

    def get_font_size(self) -> int:
        return self.settings.value("editor/font_size", 14, type=int)

    def set_font_size(self, size: int):
        self.settings.setValue("editor/font_size", size)

    # Window geometry and state
    def get_window_geometry(self) -> QByteArray:
        return self.settings.value("window/geometry", QByteArray())

    def set_window_geometry(self, geometry: QByteArray):
        self.settings.setValue("window/geometry", geometry)

    def get_window_state(self) -> QByteArray:
        return self.settings.value("window/state", QByteArray())

    def set_window_state(self, state: QByteArray):
        self.settings.setValue("window/state", state)

    # Splitter states
    def get_main_splitter_state(self) -> QByteArray:
        return self.settings.value("layout/main_splitter", QByteArray())

    def set_main_splitter_state(self, state: QByteArray):
        self.settings.setValue("layout/main_splitter", state)

    # Last Session
    def get_open_files(self) -> list:
        val = self.settings.value("session/open_files", [])
        if isinstance(val, str):
            return [val] if val else []
        return list(val) if val else []

    def set_open_files(self, file_paths: list):
        self.settings.setValue("session/open_files", file_paths)

    def get_active_file_index(self) -> int:
        return self.settings.value("session/active_index", 0, type=int)

    def set_active_file_index(self, index: int):
        self.settings.setValue("session/active_index", index)

    def get_last_project_dir(self) -> str:
        return self.settings.value("session/last_project_dir", "", type=str)

    def set_last_project_dir(self, directory: str):
        self.settings.setValue("session/last_project_dir", directory)

    # Live Preview visible state (Issue 2: Hidden by default)
    def get_preview_visible(self) -> bool:
        return self.settings.value("ui/preview_visible", False, type=bool)

    def set_preview_visible(self, visible: bool):
        self.settings.setValue("ui/preview_visible", visible)

    def sync(self):
        self.settings.sync()
