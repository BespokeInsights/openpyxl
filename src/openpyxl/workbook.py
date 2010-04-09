'''
Copyright (c) 2010 openpyxl

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

@author: Eric Gazoni
'''

from openpyxl.worksheet import Worksheet
from openpyxl.namedrange import NamedRange
from openpyxl.style import DocumentStyle

class DocumentProperties(object):

    pass


class DocumentSecurity(object):

    pass


class Workbook(object):

    def __init__(self):

        self.worksheets = [Worksheet(self)]

        self._active_sheet_index = 0

        self._named_ranges = {}

        self.properties = DocumentProperties()

        self.style = DocumentStyle()

        self.security = DocumentSecurity()

    def get_active_sheet(self):

        return self.worksheets[self._active_sheet_index]

    def create_sheet(self, index = None):

        new_ws = Worksheet(parent_workbook = self)

        self.add_sheet(worksheet = new_ws, index = index)

        return new_ws

    def add_sheet(self, worksheet, index = None):

        self.worksheets.insert(index = index, object = worksheet)

    def remove_sheet(self, worksheet):

        self.worksheets.remove(worksheet)

    def get_sheet_by_name(self, name):

        for sheet in self.worksheets:
            if sheet.title == name:
                return sheet

        return None

    def get_index(self, worksheet):

        self.worksheets.index(worksheet)

    def get_sheet_names(self):

        return [s.title for s in self.worksheets]

    def get_named_ranges(self):

        return self._named_ranges

    def add_named_range(self, named_range):

        self._named_ranges['%s!%s' % (named_range.worksheet.title,
                                      named_range.name)] = named_range

    def get_named_range(self, name):

        for nr in self._named_ranges:
            if nr.name == name:
                return nr

        return None

    def remove_named_range(self, named_range):

        del self._named_ranges['%s!%s' % (named_range.worksheet.title,
                                          named_range.name)]


