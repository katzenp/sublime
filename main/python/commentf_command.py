
"""
commentf_command.py

Description:
    tools and utilities for generating comment lines/blocks
"""
# Python standard libraries
import os
import re

# Sublime libraries
import sublime_plugin


# ==============================================================================
# constants/globals
# ==============================================================================
LINE = "{indent}{symbol} {text:{fill}{align}{width}}"
BLOCK = "{header}\n{text}\n{header}"
INDENT_PATTERN = "^(\s*)"
SYMBOLS = {
    "C": "//",
    "C#": "//",
    "C++": "//",
    "HTML": "<!--|-->",
    "Java": "//",
    "JSON": "//",
    "Python": "#",
}


# ==============================================================================
# general
# ==============================================================================
def get_indent(text):
    indent = ""
    result = re.search(INDENT_PATTERN, text)
    if result:
        indent = result.groups()[0]

    return indent


def convert(text, symbol, fill="-", align="<", width=80, empty=True):
    block_indent = None
    for each in text.split("\n"):
        if not each and not empty:
            continue

        indent = get_indent(each)
        if block_indent is None:
            block_indent = indent

        tmp_width = width - (len(block_indent) + len(symbol) + 1)

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
            symbol=symbol,
            text=each,
            fill=fill,
            align=align,
            width=tmp_width,
        )
        line = re.sub("\s+$", "", line)
        yield line


def to_comment(text, symbol, fill="-", align="<", width=80, empty=True, add_headers=True):
    block_indent = None
    block_fill = fill
    if "\n" in text or add_headers:
        block_fill = ""

    comment = []
    for line in convert(text, symbol, block_fill, align, width, empty):
        if block_indent is None:
            block_indent = get_indent(line)
        comment.append(line)
    comment = "\n".join(comment)

    # add headers
    if add_headers:
        header = ""
        for line in convert(block_indent, symbol, fill, align, width, empty=True):
            header = line
            break
        comment = BLOCK.format(header=header, text=comment)

    return comment


# ==============================================================================
# Sublime command object
# ==============================================================================
class CommentfCommand(sublime_plugin.TextCommand):
    def run(self, edit, style="block", fill="-", align="<", width=80):
        # get line comment symbol
        syntax_file = self.view.settings().get('syntax')
        syntax = os.path.basename(syntax_file).rsplit(".", 1)[0]
        symbol = SYMBOLS.get(syntax, "#")

        for region in self.view.sel():
            # get the current line text
            line = self.view.line(region)
            text = self.view.substr(line)

            # create the block comment
            add_headers = False
            if style == "block":
                add_headers = True
            comment = to_comment(
                text,
                symbol,
                fill,
                align,
                width,
                add_headers=add_headers
            )

            # replace current line
            self.view.erase(edit, line)
            self.view.insert(edit, line.begin(), comment)

