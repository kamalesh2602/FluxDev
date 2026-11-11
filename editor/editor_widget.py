"""
Custom QScintilla Code Editor Widget for FluxDev.
Comfort-focused: font size 14, 1.5 line height, 12px gutter padding,
visible current-line highlight, thin indent guides, and Emmet expansion.
"""

import os
import re
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QFont, QKeyEvent
from PyQt6.Qsci import QsciScintilla

from .lexers import create_lexer_for_extension, apply_theme_to_lexer
from .emmet_engine import expand_emmet, SELF_CLOSING_TAGS
from .themes import THEMES

PAIR_CHARS = {
    "(": ")",
    "[": "]",
    "{": "}",
    '"': '"',
    "'": "'",
    "`": "`"
}


class CodeEditorWidget(QsciScintilla):
    """Enhanced QScintilla code editor for FluxDev."""

    cursor_info_changed = pyqtSignal(int, int)
    file_status_changed = pyqtSignal()

    def __init__(self, file_path: str = None, theme_name: str = "FluxDev Dark", parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.encoding = "utf-8"
        self.theme_name = theme_name
        self.language_name = "Plain Text"

        # Editor configuration
        self._init_editor_settings()
        self._setup_margins()
        self._setup_caret_and_selection()

        # Connect signals
        self.cursorPositionChanged.connect(self._on_cursor_changed)
        self.linesChanged.connect(self._update_line_number_margin)
        self.modificationChanged.connect(lambda _: self.file_status_changed.emit())

        # Load file if provided
        if self.file_path and os.path.exists(self.file_path):
            self.load_file(self.file_path)
        else:
            self.set_lexer_by_extension(".html" if not self.file_path else os.path.splitext(self.file_path)[1])

        self.apply_theme(self.theme_name)

    def _init_editor_settings(self):
        """Sets general editor behaviors for comfortable reading and typing."""
        self.setUtf8(True)
        self.setAutoIndent(True)
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setBackspaceUnindents(True)
        self.setScrollWidth(1)
        self.setScrollWidthTracking(True)

        # 1. Comfortable Font (14pt) & 1.5 Line Height
        code_font = QFont("JetBrains Mono", 14)
        if not code_font.exactMatch():
            code_font = QFont("Fira Code", 14)
            if not code_font.exactMatch():
                code_font = QFont("Consolas", 14)
        self.setFont(code_font)

        # Extra line spacing to produce exact 1.5 line height ratio
        self.setExtraAscent(4)
        self.setExtraDescent(3)

        # 2. Thin Indent Guides
        self.setIndentationGuides(True)

        # 3. Bracket matching
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)

        # 4. Autocomplete
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionReplaceWord(True)

    def _setup_margins(self):
        """
        Configures margins:
        - Margin 0: 12px left gutter spacer padding
        - Margin 1: Line numbers
        - Margin 2: Code folding
        """
        # Margin 0: 12px left padding in the gutter
        self.setMarginType(0, QsciScintilla.MarginType.SymbolMargin)
        self.setMarginWidth(0, 12)
        self.setMarginSensitivity(0, False)

        # Margin 1: Line numbers
        self.setMarginType(1, QsciScintilla.MarginType.NumberMargin)
        self.setMarginLineNumbers(1, True)
        self.setMarginWidth(1, " 000 ")

        # Margin 2: Code Folding
        self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle, 2)
        self.setMarginWidth(2, 16)
        self.setMarginSensitivity(2, True)

    def _setup_caret_and_selection(self):
        """Configures cursor and prominent line highlight."""
        self.setCaretLineVisible(True)
        self.setCaretWidth(2)

    def _update_line_number_margin(self):
        """Dynamically adjusts line number margin width with comfortable padding."""
        num_lines = max(self.lines(), 1)
        digits = max(len(str(num_lines)) + 1, 3)
        self.setMarginWidth(1, " " + ("0" * digits) + " ")

    def _on_cursor_changed(self, line, col):
        self.cursor_info_changed.emit(line + 1, col + 1)

    def apply_theme(self, theme_name: str):
        """Updates editor colors according to theme."""
        self.theme_name = theme_name
        t = THEMES.get(theme_name, THEMES["FluxDev Dark"])
        colors = t["lexer"]

        self.setPaper(colors["bg"])
        self.setColor(colors["fg"])
        self.setCaretForegroundColor(colors["caret"])
        self.setCaretLineBackgroundColor(colors["caret_line"])
        self.setSelectionBackgroundColor(colors["selection_bg"])

        # Indent guides color
        self.setIndentationGuidesBackgroundColor(colors["bg"])
        self.setIndentationGuidesForegroundColor(colors.get("indent_guide", QColor("#22283D")))

        # Margins (including 12px padding gutter)
        self.setMarginsBackgroundColor(colors["line_num_bg"])
        self.setMarginsForegroundColor(colors["line_num_fg"])
        self.setFoldMarginColors(colors["fold_margin_bg"], colors["fold_margin_bg"])

        # Braces
        self.setMatchedBraceBackgroundColor(colors["match_brace_bg"])
        self.setUnmatchedBraceBackgroundColor(colors["unmatch_brace_bg"])

        # Lexer
        cur_lexer = self.lexer()
        if cur_lexer:
            apply_theme_to_lexer(cur_lexer, theme_name)

    def set_lexer_by_extension(self, ext: str):
        """Instantiates and binds the appropriate syntax lexer."""
        lexer, lang = create_lexer_for_extension(ext, self, self.theme_name, font_size=14)
        self.setLexer(lexer)
        self.language_name = lang
        self.file_status_changed.emit()

    def load_file(self, path: str):
        """Loads file content and determines syntax highlighting."""
        self.file_path = os.path.abspath(path)
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.encoding = "UTF-8"
        except UnicodeDecodeError:
            with open(self.file_path, "r", encoding="latin-1") as f:
                content = f.read()
                self.encoding = "ISO-8859-1"

        self.setText(content)
        self.setModified(False)
        _, ext = os.path.splitext(self.file_path)
        self.set_lexer_by_extension(ext)
        self._update_line_number_margin()

    def save_file(self, target_path: str = None) -> bool:
        """Saves current buffer to disk."""
        if target_path:
            self.file_path = os.path.abspath(target_path)

        if not self.file_path:
            return False

        with open(self.file_path, "w", encoding=self.encoding) as f:
            f.write(self.text())

        self.setModified(False)
        _, ext = os.path.splitext(self.file_path)
        self.set_lexer_by_extension(ext)
        self.file_status_changed.emit()
        return True

    def get_file_name(self) -> str:
        if self.file_path:
            return os.path.basename(self.file_path)
        return "Untitled"

    def get_file_size_str(self) -> str:
        size = len(self.text().encode(self.encoding, errors="replace"))
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        return f"{size / (1024 * 1024):.1f} MB"

    def duplicate_line(self):
        if self.hasSelectedText():
            sel_text = self.selectedText()
            line_from, col_from, line_to, col_to = self.getSelection()
            self.insertAt(sel_text, line_to, col_to)
        else:
            line, col = self.getCursorPosition()
            line_text = self.text(line)
            if not line_text.endswith("\n"):
                line_text += "\n"
            self.insertAt(line_text, line + 1, 0)
            self.setCursorPosition(line + 1, col)

    def toggle_comment(self):
        lang = self.language_name.lower()
        line_from, col_from, line_to, col_to = self.getSelection()
        if not self.hasSelectedText():
            line_from = line_to = self.getCursorPosition()[0]

        if line_from > line_to:
            line_from, line_to = line_to, line_from

        self.beginUndoAction()
        try:
            for l_idx in range(line_from, line_to + 1):
                raw = self.text(l_idx)
                has_newline = raw.endswith("\n")
                clean = raw[:-1] if has_newline else raw

                if "html" in lang or "markdown" in lang:
                    if clean.strip().startswith("<!--") and clean.strip().endswith("-->"):
                        clean = re.sub(r"^\s*<!--\s*", "", clean)
                        clean = re.sub(r"\s*-->$", "", clean)
                    else:
                        clean = f"<!-- {clean} -->"
                elif "css" in lang:
                    if clean.strip().startswith("/*") and clean.strip().endswith("*/"):
                        clean = re.sub(r"^\s*/\*\s*", "", clean)
                        clean = re.sub(r"\s*\*/$", "", clean)
                    else:
                        clean = f"/* {clean} */"
                else:
                    if clean.lstrip().startswith("//"):
                        clean = clean.replace("// ", "", 1) if "// " in clean else clean.replace("//", "", 1)
                    else:
                        clean = f"// {clean}"

                nl = "\n" if has_newline else ""
                line_len = len(self.text(l_idx))
                self.setSelection(l_idx, 0, l_idx, line_len)
                self.replaceSelectedText(clean + nl)
        finally:
            self.endUndoAction()

    def goto_line(self, line_num: int):
        target = max(1, min(self.lines(), line_num)) - 1
        self.setCursorPosition(target, 0)
        self.ensureLineVisible(target)

    def keyPressEvent(self, e: QKeyEvent):
        key = e.key()
        text = e.text()
        line, col = self.getCursorPosition()

        # 1. Emmet Expansion on Tab
        if key == Qt.Key.Key_Tab and not e.modifiers() and not self.hasSelectedText():
            line_text = self.text(line)
            prefix = line_text[:col]
            match = re.search(r"([a-zA-Z0-9_#.*+>!-]+)$", prefix)
            if match and self.language_name in ["HTML", "Plain Text"]:
                abbrev = match.group(1)
                expanded = expand_emmet(abbrev)
                if expanded and expanded != abbrev:
                    start_col = col - len(abbrev)
                    self.setSelection(line, start_col, line, col)
                    self.replaceSelectedText(expanded)
                    if ">" in expanded and "</" in expanded:
                        first_close = expanded.find(">") + 1
                        self.setCursorPosition(line, start_col + first_close)
                    return

        # 2. Overtype check for closing characters
        if text in [")", "]", "}", '"', "'", "`"]:
            line_text = self.text(line)
            if col < len(line_text) and line_text[col] == text:
                self.setCursorPosition(line, col + 1)
                return

        # 3. Auto-close brackets and quotes
        if text in PAIR_CHARS and not self.hasSelectedText():
            close_char = PAIR_CHARS[text]
            self.insert(text + close_char)
            self.setCursorPosition(line, col + 1)
            return

        # 4. Auto-close HTML tags on typing '>'
        if text == ">" and self.language_name in ["HTML", "Plain Text"]:
            line_text = self.text(line)
            prefix = line_text[:col]
            tag_match = re.search(r"<([a-zA-Z0-9_-]+)(?:\s+[^>]*)?$", prefix)
            if tag_match:
                tag_name = tag_match.group(1).lower()
                if tag_name not in SELF_CLOSING_TAGS and not prefix.endswith("/"):
                    self.insert(f"></{tag_name}>")
                    self.setCursorPosition(line, col + 1)
                    return

        # 5. Backspace pair deletion
        if key == Qt.Key.Key_Backspace and not self.hasSelectedText() and col > 0:
            line_text = self.text(line)
            if col < len(line_text):
                char_before = line_text[col - 1]
                char_after = line_text[col]
                if char_before in PAIR_CHARS and PAIR_CHARS[char_before] == char_after:
                    self.setSelection(line, col - 1, line, col + 1)
                    self.replaceSelectedText("")
                    return

        super().keyPressEvent(e)
