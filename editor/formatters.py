"""
Code Formatting Module using BeautifulSoup4, jsbeautifier, and cssbeautifier.
"""

import json

try:
    import bs4
except ImportError:
    bs4 = None

try:
    import jsbeautifier
except ImportError:
    jsbeautifier = None

try:
    import cssbeautifier
except ImportError:
    cssbeautifier = None


def format_html(code: str) -> str:
    """Formats HTML using BeautifulSoup4."""
    if not bs4:
        raise RuntimeError("beautifulsoup4 is not installed")
    soup = bs4.BeautifulSoup(code, "html.parser")
    # Prettify with 4 spaces indent
    return soup.prettify()


def format_javascript(code: str) -> str:
    """Formats JavaScript using jsbeautifier."""
    if not jsbeautifier:
        raise RuntimeError("jsbeautifier is not installed")
    opts = jsbeautifier.default_options()
    opts.indent_size = 4
    opts.indent_char = " "
    opts.space_after_anon_function = True
    opts.brace_style = "collapse"
    return jsbeautifier.beautify(code, opts)


def format_css(code: str) -> str:
    """Formats CSS using cssbeautifier."""
    if not cssbeautifier:
        raise RuntimeError("cssbeautifier is not installed")
    opts = cssbeautifier.default_options()
    opts.indent_size = 4
    opts.indent_char = " "
    opts.space_around_combinator = True
    return cssbeautifier.beautify(code, opts)


def format_json_doc(code: str) -> str:
    """Formats JSON using the standard json module."""
    data = json.loads(code)
    return json.dumps(data, indent=4)


def format_document(code: str, ext: str) -> tuple[str, bool, str]:
    """
    Main format dispatcher based on file extension.
    Returns: (formatted_code, success_bool, message)
    """
    ext = ext.lower().strip()
    try:
        if ext in [".html", ".htm"]:
            return format_html(code), True, "HTML formatted successfully"
        elif ext in [".js", ".mjs", ".ts", ".jsx"]:
            return format_javascript(code), True, "JavaScript formatted successfully"
        elif ext in [".css", ".scss"]:
            return format_css(code), True, "CSS formatted successfully"
        elif ext in [".json"]:
            return format_json_doc(code), True, "JSON formatted successfully"
        else:
            return code, False, f"No formatter available for '{ext}' files"
    except Exception as exc:
        return code, False, f"Formatting error: {str(exc)}"
