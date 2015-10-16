from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

import os
import re

from openpyxl.descriptors import String, Strict
from openpyxl.packaging.relationship import Relationship
from openpyxl.xml.constants import (
    SHEET_MAIN_NS,
    REL_NS,
    PKG_REL_NS,
    EXTERNAL_LINK_NS,
)
from openpyxl.xml.functions import (
    fromstring,
    safe_iterator,
    Element,
    SubElement,
)


"""Manage links to external Workbooks"""


class ExternalBook(Strict):

    """
    Map the relationship of one workbook to another
    """

    Id = String()
    Type = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/externalLinkPath"
    TargetMode = "External"
    Target = String()

    def __init__(self, Id, Target, TargetMode=None, Type=None):
        self.Id = Id
        self.Target = Target
        self.links = []
        self._worksheets = {}
        self.link_index = None
        self._named_ranges = {}

    def get_sheet_names(self):
        return self._worksheets.keys()

    def get_sheet_by_name(self, name):
        return self._worksheets[name]

    def get_named_ranges(self):
        return self._named_ranges

    def resolve_named_range(self, name):
        return self._named_ranges[name]

    def __getitem__(self, name):
        return self.get_sheet_by_name(name)

    def __iter__(self):
      return self._worksheets.itervalues()

    #def __iter__(self):
    #    for attr in ('Id', 'Type', 'TargetMode', 'Target'):
    #        value = getattr(self, attr)
    #        yield attr, value


class ExternalRange(Strict):

    """
    Map external named ranges
    NB. the specification for these is different to named ranges within a workbook
    See 18.14.5
    """

    name = String()
    refersTo = String(allow_none=True)
    sheetId = String(allow_none=True)

    def __init__(self, name, refersTo=None, sheetId=None):
        self.name = name
        self.refersTo = refersTo
        self.sheetId = sheetId


    def __iter__(self):
        for attr in ('name', 'refersTo', 'sheetId'):
            value = getattr(self, attr, None)
            if value is not None:
                yield attr, value

class ExternalCell(object):
    __slots__ = (
      'value',
      'data_type'
    )

    def __init__(self, value, data_type=None):
        self.value = value
        self.data_type = data_type

class ExternalWorksheet(object):
    def __init__(self, title, cells, refreshError):
        self.title = title
        self._cells = cells
        self.refreshError = refreshError

    def __getitem__(self, index):
        assert isinstance(index, (str, unicode)), 'Only string indexing supported at the moment.'
        assert ':' not in index, 'No range indexing supported at the moment.'

        if self.refreshError:
          raise Exception('Cannot access this external worksheet "{}" because the workbook is missing this data.'.format(self.title))

        if index not in self._cells:
          raise KeyError('{}!{} not found.'.format(self.title, index))

        return self._cells[index]

def parse_books(xml):
    tree = fromstring(xml)
    rels = tree.findall('{%s}Relationship' % PKG_REL_NS)
    for r in rels:
        return ExternalBook(**r.attrib)

def parse_ranges(xml):
    tree = fromstring(xml)
    book = tree.find('{%s}externalBook' % SHEET_MAIN_NS)
    names = book.find('{%s}definedNames' % SHEET_MAIN_NS)
    for n in safe_iterator(names, '{%s}definedName' % SHEET_MAIN_NS):
        yield ExternalRange(**n.attrib)

def parse_worksheets(xml):
    tree = fromstring(xml)
    book = tree.find('{%s}externalBook' % SHEET_MAIN_NS)

    sheetNames = book.find('{%s}sheetNames' % SHEET_MAIN_NS)
    sheetDataSet = book.find('{%s}sheetDataSet' % SHEET_MAIN_NS)

    worksheets = {}

    for sheetName, sheetData in zip(sheetNames, sheetDataSet):
        title = sheetName.attrib['val']
        refreshError = sheetData.attrib.get('refreshError') == '1'
        cells = {}

        for cell in sheetData.findall('.//{%s}cell' % SHEET_MAIN_NS):
            data_type = cell.attrib.get('t')
            coordinate = cell.attrib['r']
            value = cell.find('{%s}v' % SHEET_MAIN_NS).text

            if data_type is None:
                value = float(value)

            cells[coordinate] = ExternalCell(value, data_type)

        worksheets[title] = ExternalWorksheet(title, cells, refreshError)
    return worksheets

def extract_external_link_index(f_name):
    match = re.match(r'externalLink(\d+)\.xml', f_name)
    if match:
        return match.group(1)
    else:
        raise Exception('Unrecognized external link filename format {}.'.format(f_name))

def detect_external_links(rels, archive):
    for rId, d in rels:
        if d['type'] == EXTERNAL_LINK_NS:
            pth = os.path.split(d['path'])
            f_name = pth[-1]
            dir_name = "/".join(pth[:-1])
            book_path = "{0}/_rels/{1}.rels".format (dir_name, f_name)
            book_xml = archive.read(book_path)

            ext_link_idx = extract_external_link_index(f_name)
            Book = parse_books(book_xml)
            Book.link_index = ext_link_idx

            range_xml = archive.read(d['path'])
            Book.links = list(parse_ranges(range_xml))
            Book._worksheets = parse_worksheets(range_xml)

            named_ranges = {}

            for range in Book.links:
                sheet, coordinate = range.refersTo.split('!')
                sheet = sheet.strip('=\'')
                coordinate = coordinate.replace('$', '')
                named_ranges[range.name] = '[{}]{}!{}'.format(ext_link_idx, sheet, coordinate)

            Book._named_ranges = named_ranges

            yield Book

def write_external_link(links):
    """Serialise links to ranges in a single external worbook"""
    root = Element("{%s}externalLink" % SHEET_MAIN_NS)
    book =  SubElement(root, "{%s}externalBook" % SHEET_MAIN_NS, {'{%s}id' % REL_NS:'rId1'})
    external_ranges = SubElement(book, "{%s}definedNames" % SHEET_MAIN_NS)
    for l in links:
        external_ranges.append(Element("{%s}definedName" % SHEET_MAIN_NS, dict(l)))
    return root


def write_external_book_rel(book):
    """Serialise link to external file"""
    root = Element("Relationships", xmlns=PKG_REL_NS)
    rel = Relationship("", target=book.Target, targetMode=book.TargetMode, id="rId1")
    rel.type = book.Type
    root.append(rel.to_tree())
    return root
