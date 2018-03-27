"""
commentf_command.py

Description:
    tools and utilities for generating comment lines/blocks
"""
# python libraries
import os
import re

# Sublime libraries
import sublime
import sublime_plugin


__version__ = '1.0.1'


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
