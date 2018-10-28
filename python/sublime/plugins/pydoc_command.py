"""
pydoc_command.py

Description:
    Plug in for generating docstrings for Python functions and methods
"""
# python libraries
import datetime
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


# ==============================================================================
# docstring objects
# ==============================================================================
class BaseDoc(object):
    """
    Object for generating module, function, class, and method doc strings

    Public Attributes:
        :attr syntax: syntax / programming language this object is assoiated with
        :typ syntax: string
        :attr parse_text(): parses given text into function, method, or class 
            signature components
        :rtype parse_text: string
        :attr get_copyright_public(): returns a public copyright header
        :rtype get_copyright_public: string
        :attr get_copyright_private(): returns a private copyright header
        :rtype get_copyright_private: string
        :attr get_module_doc(): returns a module doc string
        :rtype get_module_doc: string
        :attr get_func_doc(): returns a function or method doc string
        :rtype get_func_doc: string
        :attr get_class_doc(): returns a class object doc string
        :rtype get_class_doc: string
    """
    def __init__(self, syntax, fill="", width=80):
        """
        Initializes all object properties/attributes

        :param syntax: name of the syntax / programming language this object is
            associated with
        :type syntax: string
        :param fill: block comment fill character
        :type fill: string
        :param width: fill width
        :type width: int
        :return: n/a
        :rtype: n/a
        """
        # formatting
        self._block_begin = ""
        self._block_end = ""
        self.syntax = syntax
        self.fill = fill
        self.width = width

    @property
    def syntax(self):
        """
        Returns the syntax / programming language this object is assoiated with.
        The syntax is used to determine appropriate block comment symbols

        :return: the syntax this object is assoiated with 
        :rtype: string
        """
        return self.__dict__["syntax"]

    @syntax.setter
    def syntax(self, value):
        """
        Sets the syntax / programming language this object is associated with.
        Setting the syntax auto calculates the appropriate block comment symbols
        from the module level constant: `BLOCK_BEGIN_END`

        :param value: name of the syntax to set like: "Python"
        :type value: string
        :return: n/a
        :rtype: n/a
        """
        self.__dict__["syntax"] = value
        self._block_begin, self._block_end = BLOCK_BEGIN_END.get(
            value, ("***", "***")
        )

    def parse_text(self, text):
        """
        Attempts to parses the given text into function, method, or class
        signature components.A block of text is considered a signature if it
        adheres to the following format:
            {indent}{keyword} {name}({parameters})
        Example - Python method signature:
            '    def log(message, level="warning"):'
        Result:
            {
                "indent": '    ',
                "keyword": 'def',
                "name": 'log',
                "parameters": ['message', 'level'],
            }

        :param text: block of text to parse
        :type text: string
        :return: signature components
        :rtype: dict
        """
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
                # csv = re.sub("\s|=[^,]+", "", results.groups()[3])
                csv = re.sub("\s|=[^,]+", "", results.groups()[3])
                data["parameters"] = csv.split(",")
        return data

    def get_copyright_public(self, company):
        """
        Returns a public copyright header for the specified company.

        :param company: name of the company/person owning the copyright
        :type company: name
        :return: public copyright header
        :rtype: string
        """
        text  = "#===============================================================================\n"
        text += "#\n"
        text += "# Copyright (c) {year} {company}\n"
        text += "#\n"
        text += "# Permission is hereby granted, free of charge, to any person obtaining a copy\n"
        text += "# of this software and associated documentation files (the \"Software\"), to deal\n"
        text += "# in the Software without restriction.\n"
        text += "#\n"
        text += "#===============================================================================\n"

        text = text.format(
            year=datetime.datetime.today().year,
            company=company
        )

        return text

    def get_copyright_private(self, company):
        """
        Returns a private copyright header for the specified company.

        :param company: name of the company/person owning the copyright
        :type company: name
        :return: private copyright header
        :rtype: string
        """
        text  = "#===============================================================================\n"
        text += "#\n"
        text += "# Copyright (c) {year} {company}\n"
        text += "#\n"
        text += "#  This file contains confidential and proprietary source code, belonging to\n"
        text += "#  {company}. Its contents may not be disclosed to third parties, copied or\n"
        text += "#  duplicated in any form, in whole or in part, without prior permission.\n"
        text += "#\n"
        text += "#===============================================================================\n"

        text = text.format(
            year=datetime.datetime.today().year,
            company=company
        )

        return text

    def get_module_doc(self, name):
        """
        Returns a formatted module level docstring

        :param name: name of the module
        :type name: string
        :return: formatted module doc string
        :rtype: string
        """
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
        """
        Returns a formatted function or method docstring

        :param indent: white space indentation characters
        :type indent: string
        :param name: name of the function or method
        :type name: string
        :param parameters: list of parameter names
        :type parameters: list, None
        :return: formated function or method doc string
        :rtype: string
        """
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
        """
        Returns a formatted class object docstring

        :param indent: white space indentation characters
        :type indent: string
        :param name: name of the class object
        :type name: string
        :return: formatted class object docstring
        :rtype: string
        """
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
    """
    Object for generating Spyhnx style module, function, class, and method doc strings

    Inherited Public Attributes:
        :attr syntax: syntax / programming language this object is assoiated with
        :typ syntax: string
        :attr parse_text(): parses given text into function, method, or class 
            signature components
        :rtype parse_text: string
        :attr get_copyright_public(): returns a public copyright header
        :rtype get_copyright_public: string
        :attr get_copyright_private(): returns a private copyright header
        :rtype get_copyright_private: string

    Overridden Public Attributes:
        :attr get_module_doc(): returns a module doc string
        :rtype get_module_doc: string
        :attr get_func_doc(): returns a function or method doc string
        :rtype get_func_doc: string
        :attr get_class_doc(): returns a class object doc string
        :rtype get_class_doc: string
    """

    def __init__(self, syntax, fill="", width=80):
        """
        Initializes all object properties/attributes

        :param syntax: name of the syntax / programming language this object is
            associated with
        :type syntax: string
        :param fill: block comment fill character
        :type fill: string
        :param width: fill width
        :type width: int
        :return: n/a
        :rtype: n/a
        """
        super(SphinxDoc, self).__init__(
            syntax=syntax, fill=fill, width=width
        )

    def get_module_doc(self, name):
        """
        Returns a formatted module level docstring

        :param name: name of the module
        :type name: string
        :return: formatted module doc string
        :rtype: string
        """
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
        """
        Returns a formatted function or method docstring

        :param indent: white space indentation characters
        :type indent: string
        :param name: name of the function or method
        :type name: string
        :param parameters: list of parameter names
        :type parameters: list, None
        :return: formated function or method doc string
        :rtype: string
        """
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
        """
        Returns a formatted class object docstring

        :param indent: white space indentation characters
        :type indent: string
        :param name: name of the class object
        :type name: string
        :return: formatted class object docstring
        :rtype: string
        """
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
        """
        Attempts to fetch a function, method, or class signature from the given region
        :param region: the region operate on
        :type region: instance of < class 'Sublime.region'>
        :return: a function, method, or class signature line
        :rtype: string
        """
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

    def run(self, edit, doc_style="sphinx", copyright=True, copyright_private=True, company="***"):
        """
        Main plugin command

        :param edit: the Sublime edit object
        :type edit: instance of class <class 'Sublime.edit'>
        :param doc_style: the style of docstrings to generate
        :type doc_style: string
        :param copyright: option to add copyrighting to module docstrings
        :type copyright: bool
        :param copyright_private: option to add strict copyrighting
        :type copyright_private: bool
        :param company: company or person owning the copyrights
        :type company: string
        :return: n/a
        :rtype: n/a
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
                if copyright:
                    if copyright_private:
                        doc = doc_obj.get_copyright_private(company=company)
                    else:
                        doc = doc_obj.get_copyright_public(company=company)
                file_path = self.view.file_name()
                file_name = os.path.basename(file_path)
                doc += doc_obj.get_module_doc(file_name)
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
