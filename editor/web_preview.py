"""
Live WebEngine Preview Module for FluxDev.
Renders the current HTML document and linked CSS/JS with debounced 500ms auto-refresh,
slim fixed 38px toolbar, and theme-matching dark placeholder when empty.
"""

import os
from PyQt6.QtCore import pyqtSignal, QUrl, QTimer, Qt
from PyQt6.QtGui import QDesktopServices, QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy
)

from .icons import get_svg_icon
from .themes import THEMES

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEnginePage
except ImportError:
    QWebEngineView = None
    QWebEnginePage = None


EMPTY_PLACEHOLDER_HTML = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{
      margin: 0;
      background-color: {bg_color};
      color: {text_color};
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
      flex-direction: column;
      text-align: center;
    }}
    .icon {{
      width: 44px;
      height: 44px;
      margin-bottom: 14px;
    }}
    h3 {{
      margin: 0 0 6px 0;
      font-size: 15px;
      font-weight: 600;
      color: {title_color};
    }}
    p {{
      margin: 0;
      font-size: 13px;
      color: {sub_color};
    }}
  </style>
</head>
<body>
  <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="{accent_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <line x1="2" y1="12" x2="22" y2="12"/>
    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
  </svg>
  <h3>No preview available</h3>
  <p>Open an HTML file to preview</p>
</body>
</html>"""


class CustomWebEnginePage(QWebEnginePage if QWebEnginePage else object):
    """Custom page routing JavaScript console messages to the console dock."""

    def __init__(self, console_callback=None, parent=None):
        if QWebEnginePage:
            super().__init__(parent)
        self.console_callback = console_callback

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        if not self.console_callback:
            return

        lvl_name = "info"
        if QWebEnginePage:
            if level == QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel:
                lvl_name = "error"
            elif level == QWebEnginePage.JavaScriptConsoleMessageLevel.WarningMessageLevel:
                lvl_name = "warning"

        short_source = os.path.basename(sourceID) if sourceID else ""
        self.console_callback(lvl_name, message, lineNumber, short_source)


class LivePreviewWidget(QWidget):
    """Live web preview widget with debounced auto-reloading and slim fixed toolbar."""

    def __init__(self, console_panel=None, theme_name: str = "FluxDev Dark", parent=None):
        super().__init__(parent)
        self.console_panel = console_panel
        self.theme_name = theme_name
        self.current_html_path = ""
        self.current_html_content = ""

        self.debounce_timer = QTimer(self)
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(500)
        self.debounce_timer.timeout.connect(self._perform_reload)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Issue 3: Slim Fixed-Height Header Bar of 38px (Never stretches)
        self.header = QFrame()
        self.header.setObjectName("preview-header")
        self.header.setFixedHeight(38)
        self.header.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        h_layout = QHBoxLayout(self.header)
        h_layout.setContentsMargins(10, 0, 10, 0)
        h_layout.setSpacing(8)

        self.lbl_status = QLabel("LIVE PREVIEW")
        self.lbl_status.setStyleSheet("font-weight: 700; font-size: 11px; color: #64748B;")
        h_layout.addWidget(self.lbl_status)
        h_layout.addStretch()

        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setIcon(get_svg_icon("refresh", color="#94A3B8", size=13))
        self.btn_refresh.setToolTip("Reload preview (F5 / F6)")
        self.btn_refresh.setFixedHeight(26)
        self.btn_refresh.clicked.connect(self._perform_reload)
        h_layout.addWidget(self.btn_refresh)

        self.btn_external = QPushButton("Open Browser")
        self.btn_external.setIcon(get_svg_icon("external-link", color="#94A3B8", size=13))
        self.btn_external.setToolTip("Open in default system browser")
        self.btn_external.setFixedHeight(26)
        self.btn_external.clicked.connect(self.open_in_external_browser)
        h_layout.addWidget(self.btn_external)

        layout.addWidget(self.header)

        # WebEngine View
        if QWebEngineView:
            self.web_view = QWebEngineView()
            self.web_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.custom_page = CustomWebEnginePage(
                console_callback=self._on_console_msg,
                parent=self.web_view
            )
            self.web_view.setPage(self.custom_page)

            # Issue 4: Background matches theme
            self._apply_theme_background()
            self._show_placeholder()

            layout.addWidget(self.web_view, stretch=1)
        else:
            self.web_view = None
            lbl_fallback = QLabel("PyQt6-WebEngine not available on this platform.")
            lbl_fallback.setStyleSheet("color: red; padding: 20px;")
            layout.addWidget(lbl_fallback, stretch=1)

    def set_theme(self, theme_name: str):
        self.theme_name = theme_name
        self._apply_theme_background()
        if not self.current_html_content and not self.current_html_path:
            self._show_placeholder()

    def _apply_theme_background(self):
        if not self.web_view:
            return
        t = THEMES.get(self.theme_name, THEMES["FluxDev Dark"])
        bg_color = QColor(t["bg_main"])
        self.web_view.page().setBackgroundColor(bg_color)

    def _show_placeholder(self):
        if not self.web_view:
            return
        t = THEMES.get(self.theme_name, THEMES["FluxDev Dark"])
        html = EMPTY_PLACEHOLDER_HTML.format(
            bg_color=t["bg_main"],
            text_color=t["text_muted"],
            title_color=t["text_main"],
            sub_color=t["text_dim"],
            accent_color=t["accent_start"]
        )
        self.web_view.setHtml(html)
        self.lbl_status.setText("LIVE PREVIEW")

    def _on_console_msg(self, level, message, line, source):
        if self.console_panel:
            self.console_panel.log_message(level, message, line, source)

    def schedule_refresh(self, html_path: str = None, html_content: str = None):
        if html_path:
            self.current_html_path = os.path.abspath(html_path)
        if html_content is not None:
            self.current_html_content = html_content

        self.debounce_timer.start()

    def _perform_reload(self):
        if not self.web_view:
            return

        if not self.current_html_content and (not self.current_html_path or not os.path.exists(self.current_html_path)):
            self._show_placeholder()
            return

        base_dir = os.path.dirname(self.current_html_path) if self.current_html_path else os.getcwd()
        base_url = QUrl.fromLocalFile(base_dir + os.sep)

        if self.current_html_content:
            self.web_view.setHtml(self.current_html_content, baseUrl=base_url)
        elif self.current_html_path and os.path.exists(self.current_html_path):
            self.web_view.load(QUrl.fromLocalFile(self.current_html_path))

        display_name = os.path.basename(self.current_html_path) if self.current_html_path else "Unsaved HTML"
        self.lbl_status.setText(f"LIVE PREVIEW — {display_name}")

    def open_in_external_browser(self):
        if self.current_html_path and os.path.exists(self.current_html_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.current_html_path))
        elif self.current_html_content:
            import tempfile
            temp_path = os.path.join(tempfile.gettempdir(), "fluxdev_preview_temp.html")
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(self.current_html_content)
            QDesktopServices.openUrl(QUrl.fromLocalFile(temp_path))
