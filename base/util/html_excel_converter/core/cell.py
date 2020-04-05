import six

from .base import check_positive_integer
from .node import Node


class Position(object):
    def __init__(self, row=None, col=None, rowspan=None, colspan=None):
        self.row = row
        self.col = col
        self.rowspan = rowspan or 1
        self.colspan = colspan or 1

    @property
    def row(self):
        return self._row

    @row.setter
    def row(self, value):
        check_positive_integer(value, 'row')
        self._row = value

    @property
    def col(self):
        return self._col

    @col.setter
    def col(self, value):
        check_positive_integer(value, 'col')
        self._col = value

    @property
    def rowspan(self):
        return self._rowspan

    @rowspan.setter
    def rowspan(self, value):
        check_positive_integer(value, 'rowspan', True)
        self._rowspan = value

    @property
    def colspan(self):
        return self._colspan

    @colspan.setter
    def colspan(self, value):
        check_positive_integer(value, 'colspan', True)
        self._colspan = value

    @property
    def is_merged_row(self):
        return self.rowspan > 1

    @property
    def is_merged_col(self):
        return self.colspan > 1


class Cell(Node):
    def __init__(self, text, position, style=None, parent=None, resolved=False):
        # type: (six.string_types, Position, any, Node, bool) -> None
        self.position = position
        self.text = text
        # Writer should write the cell when is_cell is True
        self.is_cell = True
        super(Cell, self).__init__(parent, None, resolved, style)

    def resolve(self, parent, node_info, *args, **kwargs):
        r = super(Cell, self).resolve(parent, node_info, *args, **kwargs)
        r.position.row = node_info['row']
        r.position.col = node_info['col']
        r._resolved = True
        return r

    @property
    def is_merged_row(self):
        return self.position.is_merged_row

    @property
    def is_merged_col(self):
        return self.position.is_merged_col

    @property
    def columns(self):
        return self.position.colspan

    @property
    def rows(self):
        return self.position.rowspan


class PlaceholderCell(Cell):
    def __init__(self, position, parent=None):
        super(PlaceholderCell, self).__init__(None, position, None, parent, True)
        self.is_cell = False

    def resolve(self, parent, node_info, *args, **kwargs):
        return self
