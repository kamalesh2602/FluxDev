"""
Backwards-compatibility re-export from themes.py.
"""

from .themes import generate_qss, THEMES

DARK_STYLESHEET = generate_qss("Aether Dark")
LIGHT_STYLESHEET = generate_qss("Aether Light")
LEXER_THEMES = {k: v["lexer"] for k, v in THEMES.items()}
