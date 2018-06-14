"""
commentf_command.py

Description:
    tools and utilities for generating comment lines/blocks
"""
# Python standard libraries
import re

# Sublime libraries
import sublime_plugin


# ==============================================================================
# constants/globals
# ==============================================================================
__VERSION__ = '1.0.1'

LINE = "{indent}{commenter} {text:{fill}{align}{width}}"
BLOCK = "{header}\n{text}{header}"
INDENT_PATTERN = "^(\s*)"
COMMENTERS = {
    "json": "//",
    "html": "<!--|-->",
    "python": "#",
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


def convert(text, commenter="#", fill="-", align="<", width=80, empty=True):
    block_indent = None
    for each in text.split("\n"):
        if not each and not empty:
            continue

        indent = get_indent(each)
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
        yield line


def to_comment(text, commenter="#", fill="-", align="<", width=80, empty=True, add_headers=True):
    block_indent = None
    block_fill = fill
    if "\n" in text or add_headers:
        block_fill = ""

    comment = ""
    for line in convert(text, commenter, block_fill, align, width, empty):
        if block_indent is None:
            block_indent = get_indent(line)
        line += "\n"
        comment += line

    # add headers
    if add_headers:
        header = ""
        for line in convert(block_indent, commenter, fill, align, width, empty=True):
            header = line
            break
        comment = BLOCK.format(header=header, text=comment)

    return comment


# ==============================================================================
# Sublime command object
# ==============================================================================
class CommentfCommand(sublime_plugin.TextCommand):
    def run(self, edit, style="block", commenter="#", fill="-", align="<", width=80):
        for region in self.view.sel():
            # get the current line text
            line = self.view.line(region)
            text = self.view.substr(line)

            # create the block comment
            add_headers = False
            if style == "block":
                add_headers = True
            comment = to_comment(text, commenter, fill, align, width, add_headers=add_headers)

            # replace current line
            self.view.erase(edit, line)
            self.view.insert(edit, line.begin(), comment)


if __name__ == "__main__":
    foo = ["""        color_scheme":
            "Packages/Color Scheme - Default/Monokai.tmThemeDefault/Monokai.tmThemeDefault/Monokai.tmTheme",
        "theme":
            "Default.sublime-theme", """,
    "Packages/Color Scheme - Default/Monokai.tmThemeDefault/Monokai.tmThemeDefault/Monokai.tmTheme",
    "  Packages/Color Scheme",
    ]
    for text in foo:
        print "\n"
        # print comment_line(text, commenter="#", fill="-", align="<", width=80, empty=True)
        # print comment_block(text, commenter="#", fill="-", align="<", width=80, empty=True)
        print to_comment(text, commenter="#", fill="-", align="<", width=80, empty=True, add_headers=False)
        print to_comment(text, commenter="#", fill="-", align="<", width=80, empty=True, add_headers=True)
        print "\n"
