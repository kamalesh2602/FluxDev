"""
Syntax Highlighting Lexers and Autocomplete APIs for FluxDev.
Provides QScintilla lexers for HTML, CSS, JavaScript, JSON, and Markdown.
"""

import os
from PyQt6.QtGui import QFont, QColor
from PyQt6.Qsci import (
    QsciLexerHTML,
    QsciLexerCSS,
    QsciLexerJavaScript,
    QsciLexerJSON,
    QsciLexerMarkdown,
    QsciAPIs
)

from .themes import THEMES

HTML_TAGS = [
    "html", "head", "body", "title", "meta", "link", "style", "script",
    "div", "span", "p", "a", "img", "ul", "ol", "li", "table", "thead",
    "tbody", "tr", "th", "td", "form", "input", "button", "textarea",
    "select", "option", "label", "header", "footer", "nav", "section",
    "article", "aside", "main", "figure", "figcaption", "canvas", "svg",
    "audio", "video", "source", "iframe", "h1", "h2", "h3", "h4", "h5", "h6",
    "strong", "em", "code", "pre", "blockquote", "hr", "br"
]

HTML_ATTRIBUTES = [
    "class", "id", "style", "src", "href", "alt", "title", "width", "height",
    "type", "name", "value", "placeholder", "rel", "target", "charset",
    "content", "action", "method", "enctype", "disabled", "required",
    "readonly", "checked", "selected", "autofocus", "autocomplete",
    "data-", "role", "aria-label", "aria-hidden", "tabindex", "onclick"
]

CSS_PROPERTIES = [
    "color", "background", "background-color", "background-image", "background-size",
    "background-position", "display", "flex", "flex-direction", "flex-wrap",
    "justify-content", "align-items", "align-content", "gap", "grid",
    "grid-template-columns", "grid-template-rows", "grid-column", "grid-row",
    "margin", "margin-top", "margin-bottom", "margin-left", "margin-right",
    "padding", "padding-top", "padding-bottom", "padding-left", "padding-right",
    "border", "border-radius", "border-color", "border-width", "border-style",
    "font-size", "font-family", "font-weight", "font-style", "line-height",
    "text-align", "text-decoration", "text-transform", "letter-spacing",
    "width", "height", "min-width", "max-width", "min-height", "max-height",
    "position", "top", "bottom", "left", "right", "z-index", "overflow",
    "overflow-x", "overflow-y", "opacity", "box-shadow", "text-shadow",
    "cursor", "transition", "transform", "animation", "user-select", "box-sizing"
]

JS_KEYWORDS = [
    "const", "let", "var", "function", "return", "if", "else", "switch",
    "case", "break", "default", "for", "while", "do", "continue", "try",
    "catch", "finally", "throw", "class", "extends", "new", "this", "super",
    "import", "export", "from", "as", "async", "await", "yield", "typeof",
    "instanceof", "in", "of", "null", "undefined", "true", "false"
]

JS_BUILTINS = [
    "console", "console.log", "console.warn", "console.error", "console.table",
    "document", "document.getElementById", "document.querySelector", "document.querySelectorAll",
    "document.createElement", "document.body", "window", "window.addEventListener",
    "window.localStorage", "window.sessionStorage", "fetch", "Promise",
    "setTimeout", "setInterval", "clearTimeout", "clearInterval",
    "addEventListener", "removeEventListener", "preventDefault", "stopPropagation",
    "JSON", "JSON.stringify", "JSON.parse", "Math", "Math.floor", "Math.random",
    "Math.max", "Math.min", "Array", "Object", "String", "Number", "Boolean"
]


def create_lexer_for_extension(ext: str, parent=None, theme_name: str = "FluxDev Dark", font_size: int = 14):
    """Factory function returning the appropriate QScintilla lexer with comfortable typography."""
    ext = ext.lower().strip()

    code_font = QFont("JetBrains Mono", font_size)
    if not code_font.exactMatch():
        code_font = QFont("Fira Code", font_size)
        if not code_font.exactMatch():
            code_font = QFont("Consolas", font_size)

    lexer = None
    lang_name = "Plain Text"

    if ext in [".html", ".htm", ".xhtml"]:
        lexer = QsciLexerHTML(parent)
        lang_name = "HTML"
        api = QsciAPIs(lexer)
        for tag in HTML_TAGS:
            api.add(tag)
        for attr in HTML_ATTRIBUTES:
            api.add(attr)
        api.prepare()

    elif ext in [".css", ".scss", ".sass"]:
        lexer = QsciLexerCSS(parent)
        lang_name = "CSS"
        api = QsciAPIs(lexer)
        for prop in CSS_PROPERTIES:
            api.add(prop)
        api.prepare()

    elif ext in [".js", ".mjs", ".ts", ".jsx"]:
        lexer = QsciLexerJavaScript(parent)
        lang_name = "JavaScript"
        api = QsciAPIs(lexer)
        for kw in JS_KEYWORDS:
            api.add(kw)
        for builtin in JS_BUILTINS:
            api.add(builtin)
        api.prepare()

    elif ext in [".json"]:
        lexer = QsciLexerJSON(parent)
        lang_name = "JSON"

    elif ext in [".md", ".markdown"]:
        lexer = QsciLexerMarkdown(parent)
        lang_name = "Markdown"

    if lexer:
        lexer.setFont(code_font)
        apply_theme_to_lexer(lexer, theme_name)

    return lexer, lang_name


def apply_theme_to_lexer(lexer, theme_name: str = "FluxDev Dark"):
    """Configures lexer styles according to the chosen FluxDev theme."""
    if not lexer:
        return

    t = THEMES.get(theme_name, THEMES["FluxDev Dark"])
    colors = t["lexer"]

    bg = colors["bg"]
    fg = colors["fg"]

    lexer.setDefaultPaper(bg)
    lexer.setDefaultColor(fg)

    for style_id in range(128):
        lexer.setPaper(bg, style_id)

    if isinstance(lexer, QsciLexerHTML):
        lexer.setColor(colors["tag"], QsciLexerHTML.Tag)
        lexer.setColor(colors["tag"], QsciLexerHTML.UnknownTag)
        lexer.setColor(colors["attribute"], QsciLexerHTML.Attribute)
        lexer.setColor(colors["attribute"], QsciLexerHTML.UnknownAttribute)
        lexer.setColor(colors["comment"], QsciLexerHTML.HTMLComment)
        lexer.setColor(colors["string"], QsciLexerHTML.HTMLDoubleQuotedString)
        lexer.setColor(colors["string"], QsciLexerHTML.HTMLSingleQuotedString)
        lexer.setColor(colors["number"], QsciLexerHTML.HTMLNumber)

    elif isinstance(lexer, QsciLexerCSS):
        lexer.setColor(colors["tag"], QsciLexerCSS.Tag)
        lexer.setColor(colors["tag"], QsciLexerCSS.ClassSelector)
        lexer.setColor(colors["tag"], QsciLexerCSS.IDSelector)
        lexer.setColor(colors["css_prop"], QsciLexerCSS.Property)
        lexer.setColor(colors["css_val"], QsciLexerCSS.Value)
        lexer.setColor(colors["comment"], QsciLexerCSS.Comment)
        lexer.setColor(colors["string"], QsciLexerCSS.DoubleQuotedString)
        lexer.setColor(colors["string"], QsciLexerCSS.SingleQuotedString)

    elif isinstance(lexer, QsciLexerJavaScript):
        lexer.setColor(colors["keyword"], QsciLexerJavaScript.Keyword)
        lexer.setColor(colors["string"], QsciLexerJavaScript.DoubleQuotedString)
        lexer.setColor(colors["string"], QsciLexerJavaScript.SingleQuotedString)
        lexer.setColor(colors["comment"], QsciLexerJavaScript.Comment)
        lexer.setColor(colors["comment"], QsciLexerJavaScript.CommentLine)
        lexer.setColor(colors["comment"], QsciLexerJavaScript.CommentDoc)
        lexer.setColor(colors["number"], QsciLexerJavaScript.Number)

    elif isinstance(lexer, QsciLexerJSON):
        lexer.setColor(colors["json_key"], QsciLexerJSON.Property)
        lexer.setColor(colors["string"], QsciLexerJSON.String)
        lexer.setColor(colors["number"], QsciLexerJSON.Number)
        lexer.setColor(colors["keyword"], QsciLexerJSON.Keyword)
        lexer.setColor(colors["comment"], QsciLexerJSON.CommentLine)

    elif isinstance(lexer, QsciLexerMarkdown):
        lexer.setColor(colors["keyword"], QsciLexerMarkdown.Header1)
        lexer.setColor(colors["keyword"], QsciLexerMarkdown.Header2)
        lexer.setColor(colors["keyword"], QsciLexerMarkdown.Header3)
        lexer.setColor(colors["string"], QsciLexerMarkdown.Link)
        lexer.setColor(colors["comment"], QsciLexerMarkdown.BlockQuote)
        lexer.setColor(colors["number"], QsciLexerMarkdown.CodeBlock)
