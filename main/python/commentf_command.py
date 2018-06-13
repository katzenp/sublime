"""
commentf_command.py

Description:
    tools and utilities for generating comment lines/blocks
"""
# Python standard libraries
import os
import re

# Sublime libraries
import sublime
import sublime_plugin


__VERSION__ = '1.0.1'
LINE = "{indent}{commenter} {text:{fill}{align}{width}}"
INDENT_PATTERN = "^(\s*)"

def convert(text, commenter="#", fill="-", align="<", width=80, empty=True):
    converted = ""
    block_indent = None
    for each in text.split("\n"):
        if not each and not empty:
            continue

        indent = ""
        result = re.search(INDENT_PATTERN, each)
        if result:
            indent = result.groups()[0]
        if block_indent is None:
            block_indent = indent
       
        tmp_width = width - (len(block_indent) + len(commenter) + 1)  

        each = each.replace(block_indent, "", 1)
        if each:
            if align in "<":
                each = "{} ".format(each)
            elif align == "^":
                each = " {} ".format(each)
            elif align == ">":
                each = " {}".format(each)

        line = LINE.format(
            indent=block_indent,
            commenter=commenter,
            text=each,
            fill=fill,
            align=align,
            width=tmp_width,
        )
        converted += line + "\n"
    return converted


def commentLine(line, symbol="-", size=80, align="<"):
    line_len = len(line)
    if line_len >= size:
        return None
    
    # get current indent
    indent_pattern = "^( *).+"
    ws_count = 0
    result = re.findall(indent_pattern, line)
    if result:
        ws_count = len(result[0])
    
    # remove lead/trailing whitespace characters
    line = line.strip()

    # create comment line
    if align == "<":
        size -= (line_len + 3)
        fill = symbol * size
        indent = ' ' * ws_count
        return "{0}# {1} {2}".format(indent, line, fill)
    elif align == ">":
        size -= (line_len + 3)
        fill = symbol * size
        indent = ' ' * ws_count
        return "{0}# {1} {2}".format(indent, fill, line)
    elif align == "^":
        size -= (line_len + 2)
        l_count = int(size / 2) - 2
        l_fill = symbol * l_count
        r_count = int(size / 2)
        r_fill = symbol * r_count
        indent = ' ' * ws_count
        return "{0}# {1} {2} {3}".format(indent, l_fill, line, r_fill)


def commentBlock(line, symbol="=", size=80, align="<"):
    # get current indent
    indent_pattern = "^( *).+"
    ws_count = 0
    result = re.findall(indent_pattern, line)
    if result:
        ws_count = len(result[0])

    line = line.strip()

    indent = ' ' * ws_count
    fill = symbol * (size - 2 - ws_count)
    block = "{0}# {1}\n".format(indent, fill)
    block += "{0}# {1}\n".format(indent, line)
    block += "{0}# {1}".format(indent, fill)
    return block


class CommentfCommand(sublime_plugin.TextCommand):
    def run(self, edit, style="block", symbol="=", align="<"):
        for region in self.view.sel():
            # get the current line text
            line = self.view.line(region)
            text = self.view.substr(line)

            # create the block comment
            if style == "line":
                comment = commentLine(text, symbol, 80, align)
            elif style == "block":
                comment = commentBlock(text, symbol, 80, align)

            # replace current line
            self.view.erase(edit, line)
            self.view.insert(edit, line.begin(), comment)


if __name__ == "__main__":
    foo = [
    """
        "color_scheme":
            "Packages/Color Scheme - Default/Monokai.tmTheme",
        "theme":
            "Default.sublime-theme",
        "font_size":
            12""",
    "help",
    "",
    "    test",
    "    ",
    ]
    for text in foo:
        empty = True
        if "\n" in text:
            empty = False
        print convert(text, align="<", empty=empty)
        print convert(text, align="^", empty=empty)
        print convert(text, align=">", empty=empty)
