"""
FluxDev Themes & Styling Engine.
Defines three color palettes: FluxDev Dark (default), FluxDev Midnight, and FluxDev Light,
along with lexer color mappings and strict Qt-compliant QSS stylesheet generation.
Zero non-Qt CSS properties to ensure clean console output without warnings.
"""

import os
from PyQt6.QtGui import QColor

# ----------------------------------------------------------------------
# PALETTES
# ----------------------------------------------------------------------

THEMES = {
    "FluxDev Dark": {
        "name": "FluxDev Dark",
        "bg_main": "#0B0D14",
        "bg_surface": "#121626",
        "bg_surface_elevated": "#161B30",
        "bg_surface_hover": "#1D233D",
        "bg_input": "#181D33",
        "border": "rgba(255, 255, 255, 0.08)",
        "border_focus": "#8B5CF6",
        "text_main": "#F8FAFC",
        "text_muted": "#94A3B8",
        "text_dim": "#64748B",
        "accent_start": "#8B5CF6",  # Violet
        "accent_end": "#06B6D4",    # Cyan
        "pill_active_bg": "#1E2542",
        "pill_active_border": "rgba(139, 92, 246, 0.5)",
        "scrollbar_thumb": "rgba(255, 255, 255, 0.12)",
        "scrollbar_thumb_hover": "rgba(139, 92, 246, 0.6)",

        # QScintilla Lexer Colors
        "lexer": {
            "bg": QColor("#0B0D14"),
            "fg": QColor("#E2E8F0"),
            "caret": QColor("#38BDF8"),
            "caret_line": QColor("#14192B"),
            "indent_guide": QColor("#22283D"),
            "line_num_bg": QColor("#0B0D14"),
            "line_num_fg": QColor("#475569"),
            "fold_margin_bg": QColor("#0B0D14"),
            "selection_bg": QColor("#2E1065"),
            "match_brace_bg": QColor("#3B0764"),
            "unmatch_brace_bg": QColor("#7F1D1D"),
            "tag": QColor("#38BDF8"),        # Sky cyan
            "attribute": QColor("#C084FC"),  # Soft purple
            "keyword": QColor("#A78BFA"),    # Light violet
            "string": QColor("#34D399"),     # Emerald mint
            "comment": QColor("#64748B"),    # Slate grey
            "number": QColor("#F472B6"),     # Rose pink
            "css_prop": QColor("#38BDF8"),
            "css_val": QColor("#34D399"),
            "json_key": QColor("#A78BFA"),
        }
    },

    "FluxDev Midnight": {
        "name": "FluxDev Midnight",
        "bg_main": "#000000",
        "bg_surface": "#090A0F",
        "bg_surface_elevated": "#10121A",
        "bg_surface_hover": "#171A26",
        "bg_input": "#0F111A",
        "border": "rgba(255, 255, 255, 0.10)",
        "border_focus": "#A855F7",
        "text_main": "#FFFFFF",
        "text_muted": "#71717A",
        "text_dim": "#52525B",
        "accent_start": "#A855F7",  # Neon violet
        "accent_end": "#22D3EE",    # Neon cyan
        "pill_active_bg": "#151824",
        "pill_active_border": "rgba(168, 85, 247, 0.6)",
        "scrollbar_thumb": "rgba(255, 255, 255, 0.15)",
        "scrollbar_thumb_hover": "rgba(168, 85, 247, 0.7)",

        "lexer": {
            "bg": QColor("#000000"),
            "fg": QColor("#F4F4F5"),
            "caret": QColor("#22D3EE"),
            "caret_line": QColor("#0D0F18"),
            "indent_guide": QColor("#1C1E2A"),
            "line_num_bg": QColor("#000000"),
            "line_num_fg": QColor("#3F3F46"),
            "fold_margin_bg": QColor("#000000"),
            "selection_bg": QColor("#3B0764"),
            "match_brace_bg": QColor("#581C87"),
            "unmatch_brace_bg": QColor("#881337"),
            "tag": QColor("#22D3EE"),
            "attribute": QColor("#E879F9"),
            "keyword": QColor("#C084FC"),
            "string": QColor("#4ADE80"),
            "comment": QColor("#52525B"),
            "number": QColor("#FB7185"),
            "css_prop": QColor("#22D3EE"),
            "css_val": QColor("#4ADE80"),
            "json_key": QColor("#C084FC"),
        }
    },

    "FluxDev Light": {
        "name": "FluxDev Light",
        "bg_main": "#F8FAFC",
        "bg_surface": "#FFFFFF",
        "bg_surface_elevated": "#F1F5F9",
        "bg_surface_hover": "#E2E8F0",
        "bg_input": "#FFFFFF",
        "border": "rgba(0, 0, 0, 0.08)",
        "border_focus": "#7C3AED",
        "text_main": "#0F172A",
        "text_muted": "#64748B",
        "text_dim": "#94A3B8",
        "accent_start": "#7C3AED",  # Deep Violet
        "accent_end": "#0891B2",    # Deep Cyan
        "pill_active_bg": "#FFFFFF",
        "pill_active_border": "rgba(124, 58, 237, 0.4)",
        "scrollbar_thumb": "rgba(0, 0, 0, 0.15)",
        "scrollbar_thumb_hover": "rgba(124, 58, 237, 0.5)",

        "lexer": {
            "bg": QColor("#FFFFFF"),
            "fg": QColor("#0F172A"),
            "caret": QColor("#7C3AED"),
            "caret_line": QColor("#F1F5F9"),
            "indent_guide": QColor("#E2E8F0"),
            "line_num_bg": QColor("#FFFFFF"),
            "line_num_fg": QColor("#94A3B8"),
            "fold_margin_bg": QColor("#FFFFFF"),
            "selection_bg": QColor("#DDD6FE"),
            "match_brace_bg": QColor("#EDE9FE"),
            "unmatch_brace_bg": QColor("#FFE4E6"),
            "tag": QColor("#0369A1"),
            "attribute": QColor("#6D28D9"),
            "keyword": QColor("#7C3AED"),
            "string": QColor("#059669"),
            "comment": QColor("#94A3B8"),
            "number": QColor("#DB2777"),
            "css_prop": QColor("#0369A1"),
            "css_val": QColor("#059669"),
            "json_key": QColor("#6D28D9"),
        }
    }
}


def generate_qss(theme_name: str = "FluxDev Dark") -> str:
    """
    Generates strict Qt-compliant QSS without any browser-only CSS properties
    to prevent 'Unknown property' warnings.
    """
    t = THEMES.get(theme_name, THEMES["FluxDev Dark"])

    qss = f"""
/* ==========================================================================
   FLUXDEV DESIGN SYSTEM — STRICT QT-COMPLIANT STYLESHEET
   ========================================================================== */

* {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}}

/* Frameless Window Root Container */
#root-container {{
    background-color: {t["bg_main"]};
    border-radius: 12px;
    border: 1px solid {t["border"]};
}}

QWidget {{
    background-color: transparent;
    color: {t["text_main"]};
    font-size: 13px;
}}

/* Custom Title Bar */
#title-bar {{
    background-color: {t["bg_main"]};
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    border-bottom: 1px solid {t["border"]};
    min-height: 42px;
    max-height: 42px;
    padding-left: 12px;
    padding-right: 12px;
}}

/* Window Control Buttons (Minimal Dots) */
#btn-win-close {{
    background-color: #EF4444;
    min-width: 13px;
    max-width: 13px;
    min-height: 13px;
    max-height: 13px;
    border-radius: 6px;
    border: none;
}}
#btn-win-close:hover {{
    background-color: #DC2626;
}}

#btn-win-min {{
    background-color: #F59E0B;
    min-width: 13px;
    max-width: 13px;
    min-height: 13px;
    max-height: 13px;
    border-radius: 6px;
    border: none;
}}
#btn-win-min:hover {{
    background-color: #D97706;
}}

#btn-win-max {{
    background-color: #10B981;
    min-width: 13px;
    max-width: 13px;
    min-height: 13px;
    max-height: 13px;
    border-radius: 6px;
    border: none;
}}
#btn-win-max:hover {{
    background-color: #059669;
}}

/* Command Palette Search Trigger */
#btn-cmd-palette-trigger {{
    background-color: {t["bg_surface"]};
    border: 1px solid {t["border"]};
    border-radius: 8px;
    color: {t["text_muted"]};
    padding: 5px 14px;
    font-size: 12px;
    font-weight: 500;
}}
#btn-cmd-palette-trigger:hover {{
    background-color: {t["bg_surface_elevated"]};
    border-color: {t["border_focus"]};
    color: {t["text_main"]};
}}

/* Pill Tabs */
QTabWidget::pane {{
    border: none;
    background-color: {t["bg_main"]};
}}

QTabBar {{
    background-color: {t["bg_main"]};
    border: none;
    padding: 4px 8px;
}}

QTabBar::tab {{
    background-color: transparent;
    color: {t["text_muted"]};
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 6px 14px;
    margin-right: 4px;
    font-size: 12px;
    font-weight: 500;
    min-width: 90px;
}}

QTabBar::tab:hover:!selected {{
    background-color: {t["bg_surface"]};
    color: {t["text_main"]};
}}

QTabBar::tab:selected {{
    background-color: {t["pill_active_bg"]};
    color: {t["text_main"]};
    border: 1px solid {t["pill_active_border"]};
    border-bottom: 2px solid {t["accent_start"]};
    font-weight: bold;
}}

QTabBar::close-button {{
    subcontrol-position: right;
    margin-left: 8px;
    padding: 2px;
    border-radius: 4px;
}}
QTabBar::close-button:hover {{
    background-color: rgba(239, 68, 68, 0.7);
    color: #FFFFFF;
}}

/* Sidebar (Project Explorer Glass Panel) */
#sidebar-panel {{
    background-color: {t["bg_surface"]};
    border-right: 1px solid {t["border"]};
}}

QTreeView {{
    background-color: transparent;
    color: {t["text_main"]};
    border: none;
    font-size: 13px;
}}

QTreeView::item {{
    padding: 5px 8px;
    border-radius: 6px;
    margin: 1px 4px;
}}

QTreeView::item:hover {{
    background-color: {t["bg_surface_hover"]};
}}

QTreeView::item:selected {{
    background-color: {t["pill_active_bg"]};
    color: #FFFFFF;
    border: 1px solid {t["border"]};
}}

/* Live Preview Toolbar (Fixed 38px) */
#preview-header {{
    background-color: {t["bg_surface"]};
    border-bottom: 1px solid {t["border"]};
    min-height: 38px;
    max-height: 38px;
    padding: 0 10px;
}}

/* Status Bar */
QStatusBar {{
    background-color: {t["bg_main"]};
    border-top: 1px solid {t["border"]};
    color: {t["text_muted"]};
    font-size: 11px;
    min-height: 26px;
    max-height: 26px;
    padding: 0 10px;
}}

QStatusBar QLabel {{
    color: {t["text_muted"]};
    padding: 0 8px;
}}

/* Modern Glass Buttons */
QPushButton {{
    background-color: {t["bg_surface"]};
    color: {t["text_main"]};
    border: 1px solid {t["border"]};
    border-radius: 8px;
    padding: 6px 14px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {t["bg_surface_hover"]};
    border-color: {t["border_focus"]};
}}

QPushButton:pressed {{
    background-color: {t["pill_active_bg"]};
}}

/* Primary Accent Gradient Button */
QPushButton.btn-primary {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t["accent_start"]}, stop:1 {t["accent_end"]});
    color: #FFFFFF;
    font-weight: bold;
    border: none;
}}
QPushButton.btn-primary:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t["accent_start"]}, stop:1 {t["accent_end"]});
}}

/* Inputs */
QLineEdit {{
    background-color: {t["bg_input"]};
    color: {t["text_main"]};
    border: 1px solid {t["border"]};
    border-radius: 8px;
    padding: 6px 12px;
}}

QLineEdit:focus {{
    border: 1px solid {t["border_focus"]};
}}

QCheckBox {{
    color: {t["text_muted"]};
    spacing: 6px;
}}

/* Slim 6px Custom Scrollbars */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: {t["scrollbar_thumb"]};
    min-height: 24px;
    border-radius: 3px;
}}

QScrollBar::handle:vertical:hover {{
    background: {t["scrollbar_thumb_hover"]};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
    margin: 0px;
}}

QScrollBar::handle:horizontal {{
    background: {t["scrollbar_thumb"]};
    min-width: 24px;
    border-radius: 3px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {t["scrollbar_thumb_hover"]};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: none;
}}

/* 1px Splitter Handles with Hover Highlight (Issue 8) */
QSplitter::handle {{
    background-color: {t["border"]};
}}

QSplitter::handle:horizontal {{
    width: 1px;
}}

QSplitter::handle:vertical {{
    height: 1px;
}}

QSplitter::handle:hover {{
    background-color: {t["accent_start"]};
}}
"""
    return qss


def save_active_qss(theme_name: str = "FluxDev Dark", output_path: str = None) -> str:
    """Generates and writes editor/style.qss to disk."""
    if not output_path:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(base_dir, "style.qss")

    content = generate_qss(theme_name)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return output_path
