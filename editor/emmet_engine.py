"""
Emmet-style abbreviation expansion engine for HTML.
Expands patterns like 'ul>li*3', 'div.container>p', '!', and 'html:5' into structured HTML.
"""

import re

SELF_CLOSING_TAGS = {"img", "input", "br", "hr", "meta", "link"}

TAG_DEFAULT_ATTRIBUTES = {
    "a": 'href=""',
    "img": 'src="" alt=""',
    "link": 'rel="stylesheet" href=""',
    "script": 'src=""',
    "input": 'type="text"',
    "form": 'action="" method="post"',
    "button": 'type="button"',
}

HTML5_BOILERPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    
</body>
</html>"""


class EmmetNode:
    """Represents an AST node in an Emmet abbreviation."""

    def __init__(self, tag="div", classes=None, elem_id="", count=1, attributes=""):
        self.tag = tag or "div"
        self.classes = classes or []
        self.elem_id = elem_id
        self.count = max(1, count)
        self.attributes = attributes
        self.children = []
        self.siblings = []

    def to_html(self, indent_level=0, indent_str="    ") -> str:
        res = []
        for _ in range(self.count):
            current_indent = indent_str * indent_level

            # Construct attributes
            attrs = []
            if self.classes:
                attrs.append(f'class="{" ".join(self.classes)}"')
            if self.elem_id:
                attrs.append(f'id="{self.elem_id}"')
            if self.attributes:
                attrs.append(self.attributes)
            elif self.tag in TAG_DEFAULT_ATTRIBUTES:
                attrs.append(TAG_DEFAULT_ATTRIBUTES[self.tag])

            attr_str = (" " + " ".join(attrs)) if attrs else ""

            if self.tag in SELF_CLOSING_TAGS:
                res.append(f"{current_indent}<{self.tag}{attr_str}>")
            elif not self.children:
                res.append(f"{current_indent}<{self.tag}{attr_str}></{self.tag}>")
            else:
                inner_lines = []
                for child in self.children:
                    inner_lines.append(child.to_html(indent_level + 1, indent_str))
                inner_content = "\n".join(inner_lines)
                res.append(f"{current_indent}<{self.tag}{attr_str}>\n{inner_content}\n{current_indent}</{self.tag}>")

        main_html = "\n".join(res)

        # Append siblings at same level
        if self.siblings:
            sibling_lines = [sib.to_html(indent_level, indent_str) for sib in self.siblings]
            main_html = main_html + "\n" + "\n".join(sibling_lines)

        return main_html


def parse_single_item(token: str) -> EmmetNode:
    """Parses a single tag unit such as 'li.item*3' or 'div#app'."""
    # Check count multiplier (*N)
    count = 1
    if "*" in token:
        parts = token.rsplit("*", 1)
        if len(parts) == 2 and parts[1].isdigit():
            token = parts[0]
            count = int(parts[1])

    # Extract ID (#) and Classes (.)
    elem_id = ""
    classes = []

    # Regex to extract tag name and class/id parts
    match = re.match(r"^([a-zA-Z0-9_-]*)", token)
    tag = match.group(1) if match else "div"
    if not tag:
        tag = "div"

    rest = token[len(tag):]

    # Find all .class and #id occurrences
    for m in re.finditer(r"([.#])([a-zA-Z0-9_-]+)", rest):
        symbol, name = m.group(1), m.group(2)
        if symbol == ".":
            classes.append(name)
        elif symbol == "#":
            elem_id = name

    return EmmetNode(tag=tag, classes=classes, elem_id=elem_id, count=count)


def expand_emmet(abbrev: str, base_indent: str = "") -> str:
    """
    Expands an Emmet abbreviation into HTML.
    Returns None if the abbreviation is invalid or cannot be expanded.
    """
    abbrev = abbrev.strip()
    if not abbrev:
        return ""

    # Special boilerplates
    if abbrev in ["!", "html:5"]:
        lines = HTML5_BOILERPLATE.splitlines()
        if base_indent:
            return "\n".join((base_indent + line if line else "") for line in lines)
        return HTML5_BOILERPLATE

    # Handle child operators '>'
    if ">" in abbrev:
        parts = abbrev.split(">")
        root = parse_single_item(parts[0])
        curr = root
        for p in parts[1:]:
            child_node = parse_single_item(p)
            curr.children.append(child_node)
            curr = child_node
        expanded = root.to_html(0, "    ")
    elif "+" in abbrev:
        parts = abbrev.split("+")
        root = parse_single_item(parts[0])
        for p in parts[1:]:
            root.siblings.append(parse_single_item(p))
        expanded = root.to_html(0, "    ")
    else:
        node = parse_single_item(abbrev)
        expanded = node.to_html(0, "    ")

    if base_indent:
        lines = expanded.splitlines()
        return "\n".join((base_indent + line if line else "") for line in lines)

    return expanded
