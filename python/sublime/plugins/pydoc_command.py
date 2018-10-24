"""
pydoc_command.py

Description:
    Plug in for generating docstrings for Python functions and methods
"""
# python libraries
import os
import re

# Sublime libraries
import sublime_plugin


# ==============================================================================
# constants/globals
# ==============================================================================
# block comment start/end symbols
BLOCK_BEGIN_END = {
    "C": ("/*", "*/"),
    "C#": ("/*", "*/"),
    "C++": ("/*", "*/"),
    "HTML": ("<!--", "-->"),
    "Java": ("/*", "*/"),
    "JSON": ("/*", "*/"),
    "Python": ("\"\"\"", "\"\"\""),
}

# copy right template
COPYRIGHT = """
# ==============================================================================
#
# Copyright (c) {year} {author}
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction.
# 
# ==============================================================================
"""


# ==============================================================================
# docstring objects
# ==============================================================================
class BaseDoc(object):
    def __init__(self, syntax, fill="", width=80):
        # formatting
        self._block_begin = ""
        self._block_end = ""
        self.syntax = syntax
        self.fill = fill
        self.width = width

    @property
    def syntax(self):
        return self.__dict__["syntax"]

    @syntax.setter
    def syntax(self, value):
        self.__dict__["syntax"] = value
        self._block_begin, self._block_end = BLOCK_BEGIN_END.get(
            value, ("***", "***")
        )

    def parse_text(self, text):
        data = {
            "indent": "",
            "keyword": "",
            "name": "",
            "parameters": []
        }

        # extract signature components
        text = text.replace("\n", "")   
        results = re.search("^(\s*)(\w+) (\w+)\((.*)\)", text)
        if results:
            data["indent"] = results.groups()[0]
            data["keyword"] = results.groups()[1]
            data["name"] = results.groups()[2]
            # extract parameter names
            if results.groups()[3]:
                csv = re.sub("\s|=\w+", "", results.groups()[3])
                data["parameters"] = csv.split(",")
        return data

    def get_module_doc(self, name):
        # define doc template
        template  = "{block_begin:{fill}<{width}}\n"
        template += "{name}\n"
        template += "{block_end:{fill}>{width}}\n"
       
        doc = template.format(
            block_begin=self._block_begin,
            fill=self.fill,
            width=self.width,
            name=name,
            block_end=self._block_end
        )
        return doc

    def get_func_doc(self, indent, name, parameters=None):
        # define doc template
        template  = "\n"
        template += "{indent}{block_begin:{fill}<{width}}\n"
        template += "{indent}Description of callable < {name} >\n"
        template += "{indent}{block_end:{fill}>{width}}"

        doc = template.format(
            indent=indent,
            name=name,
            block_begin=self._block_begin,
            fill=self.fill,
            width=self.width,
            block_end=self._block_end
        )

        return doc

    def get_class_doc(self, indent, name):
        template  = "\n"
        template += "{indent}{block_begin:{fill}<{width}}\n"
        template += "{indent}Description of class < {name} >\n"
        template += "{indent}{block_end:{fill}>{width}}"

        doc = template.format(
            indent=indent,
            name=name,
            block_begin=self._block_begin,
            fill=self.fill,
            width=self.width,
            block_end=self._block_end
        )
        return doc


class SphinxDoc(BaseDoc):
    def __init__(self, syntax, fill="", width=80):
        super(SphinxDoc, self).__init__(
            syntax=syntax, fill=fill, width=width
        )

    def get_module_doc(self, name):
        # define doc template
        template  = "{block_begin:{fill}<{width}}\n"
        template += "{name}\n"
        template += "\n"
        template += "Description:\n"
        template += "    description of module < {name} >\n"
        template += "{block_end:{fill}>{width}}\n"
       
        doc = template.format(
            block_begin=self._block_begin,
            fill=self.fill,
            width=self.width,
            name=name,
            block_end=self._block_end
        )
        return doc

    def get_func_doc(self, indent, name, parameters):
        # define doc template
        template  = "\n"
        template += "{indent}{block_begin:{fill}<{width}}\n"
        template += "{indent}Description of callable < {name} >\n"
        template += "\n"
        template += "{params}"
        template += "{indent}{block_end:{fill}>{width}}"

        params = ""
        for p in parameters:
            params += "{indent}:param {p}:\n".format(indent=indent, p=p)
            params += "{indent}:type {p}:\n".format(indent=indent, p=p)
        params += "{indent}:return:\n".format(indent=indent)
        params += "{indent}:rtype:\n".format(indent=indent)

        doc = template.format(
            indent=indent,
            name=name,
            params=params,
            block_begin=self._block_begin,
            fill=self.fill,
            width=self.width,
            block_end=self._block_end
        )

        return doc

    def get_class_doc(self, indent, name):
        template  = "\n"
        template += "{indent}{block_begin:{fill}<{width}}\n"
        template += "{indent}Description of class < {name} >\n"
        template += "\n"
        template += "{indent}Public Attributes:\n"
        template += "{indent}    attr1:\n"
        template += "{indent}{block_end:{fill}>{width}}"

        doc = template.format(
            indent=indent,
            name=name,
            block_begin=self._block_begin,
            fill=self.fill,
            width=self.width,
            block_end=self._block_end
        )
        return doc


# ==============================================================================
# Command Class
# ==============================================================================
class PydocCommand(sublime_plugin.TextCommand):
    """
    Auto generates docstrings for Python modules, functions, and methods
    based on the current line in your text file
    """
    def _get_signature(self, region):
            # get the current line text
            line = self.view.line(region)
            text = self.view.substr(line)
            while True:
                if re.search('^\s*def |^\s*class ', text):
                    break
                if region.a == 0:
                    break
                region.a -= 1
                line = self.view.line(region)
                text = self.view.substr(line)
            return text.replace("\n", "")

    def run(self, edit, doc_style="sphinx"):
        """
        Main plugin command

        :param edit: the Sublime edit object
        :type edit: instance of class <class 'Sublime.edit'>
        :param doc_style: the docstring style
        :type doc_style: string
        :return: N/A
        :rtype: N/A
        """
        # get current syntax
        try:
            syntax = re.split("[\\/.]", self.view.settings().get("syntax"))[-2]
        except Exception:
            syntax = "Python"

        # get doc object
        if doc_style == "sphinx":
            doc_obj = SphinxDoc(syntax=syntax, fill="", width=0)
        else:
            doc_obj = BaseDoc(syntax=syntax, fill="", width=0)

        # update view
        for region in self.view.sel():
            # get the current line text
            line = self.view.line(region)
            text = self.view.substr(line)
    
            # get doc string
            doc = ""
            pos = line.end()
            if line.begin() == 0:
                file_path = self.view.file_name()
                file_name = os.path.basename(file_path)
                doc = doc_obj.get_module_doc(file_name)
                if text:
                    pos += 1
            else:
                text = self._get_signature(region)
                tokens = doc_obj.parse_text(text)
                indent = "    "
                if tokens["indent"]:
                    indent = tokens["indent"] * 2
                if tokens["keyword"] == "def":
                    doc = doc_obj.get_func_doc(indent, tokens["name"], tokens["parameters"])
                elif tokens["keyword"] == "class":
                    doc = doc_obj.get_class_doc(indent, tokens["name"])
            
            # insert doc string
            if doc:
                self.view.insert(edit, pos, doc)
