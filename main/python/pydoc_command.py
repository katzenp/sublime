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
SYMBOLS = {
    "C": ("/*", "*/"),
    "C#": ("/*", "*/"),
    "C++": ("/*", "*/"),
    "HTML": ("<!--", "-->"),
    "Java": ("/*", "*/"),
    "JSON": ("/*", "*/"),
    "Python": ("\"\"\"", "\"\"\""),
}

# doc string formats
DOC_MODUE = """{symbol_begin}
{basename}

Description:
    Module description ...
{symbol_begin}"""

DOC_BUILD_UI = """
{indent}\"\"\"
{indent}Defines all ui elements
{indent}
{indent}:return: n/a
{indent}:rtype: n/a
{indent}\"\"\""""

DOC_INITIALIZE_UI = """
{indent}\"\"\"
{indent}Initializes all ui elements to their default state
{indent}
{indent}:return: n/a
{indent}:rtype: n/a
{indent}\"\"\""""

DOC_CONNECT_SIGNALS = """
{indent}\"\"\"
{indent}Defines all SIGNAL/SLOT connections
{indent}
{indent}:return: n/a
{indent}:rtype: n/a
{indent}\"\"\""""


# ==============================================================================
# Doc Classes
# ==============================================================================
class Docstringer(object):
    """
    Base class for all docstring generators
    Generates docstrings for module, class, and function objects
    from a given line of text.
    """
    PATTERN = '^( *)(\w+) (\w+)\((.*)\):'

    def __init__(self, line, tab_size=4):
        """
        Constructor method

        :param line: line to create a docstring for, if necessary
        :type line: string
        :param tab_size: number of white space characters to use as a tab
        :type tab_size: int
        :return: N/A
        :rtype: N/A
        """
        # get the line
        self._line = line

        # determine tab string
        self._tab_size = 4
        if tab_size > 0 and not tab_size % 4:
            self._tab_size = tab_size
        self._tab = ' ' * self._tab_size

        # initialize line tokens
        self._indent = 0
        self._keyword = None
        self._obj_name = None
        self._parameters = None

        # analyze line
        self.__analyze()

    def __analyze(self):
        """
        Attempts to parse function/class header data from `_line`
        and store the results in the following instance attributes:
            _indent, _keyword, _obj_name, _parameters

        :return: N/A
        :rtype: N/A
        """
        result = re.search(Docstringer.PATTERN, self._line)
        if result:
            self._indent = result.groups()[0]
            self._indent += self._tab
            self._keyword = result.groups()[1]
            self._obj_name = result.groups()[2]
            self._parameters = result.groups()[3]

    def module_doc(self, filename=''):
        """
        Creates a module docstring that includes the given filename
        if one is provided

        :param filename: the name of the current file
        :type filename: string
        :return: the module docstring
        :rtype: string
        """
        if filename:
            if os.sep in filename:
                filename = os.path.basename(filename)

        # construct docstring
        if re.search("^\'{3}|^\"{3}", self._line):
            return ''

        doc = '\"\"\"\n'
        if self._line.startswith('#!'):
            doc = '\n\"\"\"\n'
        doc += '{0}\n\n'.format(filename)
        doc += 'Description:\n'
        doc += '\tModule description\n'
        doc += '\"\"\"'

        return doc

    def func_doc(self):
        """
        Creates a docstring for a callable object(function, method)
        that includes parameter names

        :return: docstring for a callable object
        :rtype: string
        """
        doc = ''
        if self._keyword == 'def':
            # construct description template
            doc = '\n{0}"""\n'.format(self._indent)
            doc += '{0}Description of callable <{1}>\n\n'.format(self._indent, self._obj_name)

            # construct parameters template
            if self._parameters:
                doc += '{0}Parameters\n'.format(self._indent)
                doc += '{0}----------\n'.format(self._indent)
                self._parameters = self._parameters.split(',')
                for p in self._parameters:
                    if p == 'self':
                        continue
                    p_name = p.split('=')[0]
                    p_name = p_name.strip()
                    doc += '{0}{1}:\n'.format(self._indent, p_name)

            # construct returns template
            doc += '\n{0}Returns\n'.format(self._indent)
            doc += '{0}-------\nn'.format(self._indent)
            doc += '{0}value\n'.format(self._indent)
            doc += '{0}"""'.format(self._indent)
        return doc

    def class_doc(self):
        """
        Creates a docstring for a class object

        :return: docstring for a class object
        :rtype: string
        """
        doc = ''
        if self._keyword == 'class':
            obj_name = repr(self._obj_name)
            doc = '\n{0}""" Description of <class {1}> """\n'.format(self._indent, obj_name)
        return doc

    def get_doc(self):
        """
        Creates a docstring for a class or callable object based on the
        Python keyword extracted by the __analyze() method

        :return: docstring for a callable object
        :rtype: string
        """
        doc = ''
        if self._keyword == 'def':
            doc = self.func_doc()
        elif self._keyword == 'class':
            doc = self.class_doc()

        return doc


class Sphinx_Docstringer(Docstringer):
    """
    Generates Sphinx style docstrings for module, class, and function objects
    from a given line of text
    """

    def __init__(self, line, tab_size=4):
        """
        Constructor method

        :param line: line to create a docstring for, if necessary
        :type line: string
        :param tab_size: number of white space characters to use as a tab
        :type tab_size: int
        :return: N/A
        :rtype: N/A
        """
        super(Sphinx_Docstringer, self).__init__(line, tab_size)

    def func_doc(self):
        """
        Creates a Sphinx style docstring for a callable object(function, method)
        that includes parameter names

        :return: docstring for a callable object
        :rtype: string
        """
        # validate
        if not self._keyword == 'def':
            return ""

        # special cases
        if self._obj_name == "_build_ui":
            return DOC_BUILD_UI.format(indent=self._indent)
        if self._obj_name == "_initialize_ui":
            return DOC_INITIALIZE_UI.format(indent=self._indent)
        if self._obj_name == "_connect_signals":
            return DOC_CONNECT_SIGNALS.format(indent=self._indent)

        # standard cases
        doc = "\n{0}\"\"\"\n".format(self._indent)
        doc += "{0}Description of callable <{1}>\n\n".format(self._indent, self._obj_name)

        # construct parameters template
        if self._parameters:
            self._parameters = self._parameters.split(",")
            for p in self._parameters:
                if p == "self":
                    continue
                p_name = p.split("=")[0]
                p_name = p_name.strip()
                doc += "{0}:param {1}:\n".format(self._indent, p_name)
                doc += "{0}:type {1}:\n".format(self._indent, p_name)

        # construct returns template
        doc += '{0}:return:\n'.format(self._indent)
        doc += '{0}:rtype:\n'.format(self._indent)
        doc += '{0}\"\"\"'.format(self._indent)
        return doc

    def class_doc(self):
        """
        Creates a Sphinx style docstring for a class object

        :return: docstring for a class object
        :rtype: string
        """
        doc = ''
        if self._keyword == 'class':
            doc = '\n{0}"""\n'.format(self._indent)
            obj_name = repr(self._obj_name)
            doc +='{0}Description of <class {1}>\n\n'.format(self._indent, obj_name)
            doc +='{0}Public Attributes:\n'.format(self._indent)
            doc +='{0}{1}attr1:\n'.format(self._indent, self._tab)
            doc +='{0}"""'.format(self._indent)
        return doc


# ==============================================================================
# Command Class
# ==============================================================================
class PydocCommand(sublime_plugin.TextCommand):
    """
    Auto generates docstrings for Python modules, functions, and methods
    based on the current line in your text file
    """
    @property
    def commenter(self):
        """
        Returns the appropriate block comment symbols based on the curent
        language / syntax

        :return: block comment symbols 
        :rtype: string
        """
        syntax_file = self.view.settings().get('syntax')
        syntax = os.path.basename(syntax_file).rsplit(".", 1)[0]
        return COMMENTERS.get(syntax, "#")

    def run(self, edit, doc_style='sphinx'):
        """
        Main plugin command

        :param edit: the Sublime edit object
        :type edit: instance of class <class 'Sublime.edit'>
        :param doc_style: the docstring style
        :type doc_style: string
        :return: N/A
        :rtype: N/A
        """
        # get the current tab size
        cur_tab_size = int(self.view.settings().get('tab_size', 4))

        for region in self.view.sel():
            # get the current line text
            line = self.view.line(region)
            text = self.view.substr(line)

            # get doc object
            if doc_style == 'sphinx':
                doc_obj = Sphinx_Docstringer(text, cur_tab_size)
            else:
                doc_obj = Docstringer(text, cur_tab_size)

            # get doc string
            doc = ''
            if line.begin() == 0:
                cur_file = self.view.file_name()
                doc = doc_obj.module_doc(cur_file)
            else:
                doc = doc_obj.get_doc()

            # add docstring
            if doc:
                self.view.insert(edit, line.end(), doc)
