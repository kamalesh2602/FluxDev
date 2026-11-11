"""
Unit tests for the Mini Code Editor.
Tests Emmet expansion, formatters, project templates, and AST syntax validity of all modules.
"""

import os
import ast
import unittest

from editor.emmet_engine import expand_emmet
from editor.formatters import format_html, format_javascript, format_css, format_json_doc, format_document
from editor.templates import HTML5_BOILERPLATE, create_starter_project


class TestEmmetEngine(unittest.TestCase):
    """Tests Emmet abbreviation expansion."""

    def test_boilerplate_expansion(self):
        result = expand_emmet("!")
        self.assertIn("<!DOCTYPE html>", result)
        self.assertIn("<meta charset=\"UTF-8\">", result)

        result_html5 = expand_emmet("html:5")
        self.assertEqual(result, result_html5)

    def test_single_tag(self):
        self.assertEqual(expand_emmet("p"), "<p></p>")
        self.assertEqual(expand_emmet("div.container"), '<div class="container"></div>')
        self.assertEqual(expand_emmet("div#app"), '<div id="app"></div>')
        self.assertEqual(expand_emmet("a"), '<a href=""></a>')
        self.assertEqual(expand_emmet("img"), '<img src="" alt="">')

    def test_child_operator(self):
        result = expand_emmet("ul>li")
        self.assertIn("<ul>", result)
        self.assertIn("<li></li>", result)
        self.assertIn("</ul>", result)

    def test_multiplication_operator(self):
        result = expand_emmet("li*3")
        lines = [line.strip() for line in result.splitlines() if line.strip()]
        self.assertEqual(len(lines), 3)
        for line in lines:
            self.assertEqual(line, "<li></li>")

    def test_combined_emmet(self):
        result = expand_emmet("ul.nav>li.item*3>a")
        self.assertIn('<ul class="nav">', result)
        self.assertIn('<li class="item">', result)
        self.assertIn('<a href=""></a>', result)
        self.assertIn("</ul>", result)

    def test_sibling_operator(self):
        result = expand_emmet("h1+p")
        self.assertIn("<h1></h1>", result)
        self.assertIn("<p></p>", result)


class TestFormatters(unittest.TestCase):
    """Tests code formatters using BeautifulSoup4, jsbeautifier, and cssbeautifier."""

    def test_format_html(self):
        dirty = "<div><p>Hello<span>World</span></p></div>"
        formatted = format_html(dirty)
        self.assertIn("<div>\n", formatted)
        self.assertIn(" <p>\n", formatted)

    def test_format_javascript(self):
        dirty = "function test(){const x=1;return x+2;}"
        formatted = format_javascript(dirty)
        self.assertIn("function test()", formatted)
        self.assertIn("const x = 1;", formatted)
        self.assertIn("return x + 2;", formatted)

    def test_format_css(self):
        dirty = "body{margin:0;padding:0;color:red;}"
        formatted = format_css(dirty)
        self.assertIn("body {", formatted)
        self.assertIn("margin: 0;", formatted)
        self.assertIn("color: red;", formatted)

    def test_format_json(self):
        dirty = '{"name":"editor","version":1}'
        formatted = format_json_doc(dirty)
        self.assertIn('"name": "editor"', formatted)
        self.assertIn('"version": 1', formatted)

    def test_dispatcher(self):
        code, ok, msg = format_document("const a=1;", ".js")
        self.assertTrue(ok)
        self.assertIn("const a = 1;", code)


class TestTemplates(unittest.TestCase):
    """Tests template generation."""

    def test_html5_boilerplate(self):
        self.assertIn("<!DOCTYPE html>", HTML5_BOILERPLATE)
        self.assertIn("<title>New Web Page</title>", HTML5_BOILERPLATE)

    def test_starter_project_creation(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            created = create_starter_project(tmpdir)
            self.assertEqual(len(created), 3)
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "index.html")))
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "style.css")))
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "script.js")))


class TestCodebaseSyntax(unittest.TestCase):
    """AST syntax validation for every python file in the project."""

    def test_all_modules_ast_valid(self):
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for root, _, files in os.walk(project_dir):
            if "venv" in root or ".git" in root or "__pycache__" in root:
                continue
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    with open(full_path, "r", encoding="utf-8") as f:
                        source = f.read()
                    try:
                        ast.parse(source, filename=file)
                    except SyntaxError as e:
                        self.fail(f"Syntax error in {file}: {e}")


if __name__ == "__main__":
    unittest.main()
