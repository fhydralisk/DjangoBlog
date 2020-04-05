import six
from .base import check_positive_integer
from .node import Node
from .cell import Cell, Position


class Row(Node):
    def __init__(self, row_index, parent=None, children=None, resolved=False, style=None):
        self.row_index = row_index
        self._columns = None

        super(Row, self).__init__(parent, children, resolved, style)

    def resolve(self, parent, node_info, *args, **kwargs):
        if 'row_index' in node_info:
            self.row_index = node_info['row_index']
        if parent is not None:
            self.parent = parent

        placeholders = list(node_info['placeholders'])

        cur_pos = 0
        resolved_row = Row(self.row_index, self.parent, resolved=True, style=self.style)

        for child_cell in self.children:
            while placeholders:
                next_placeholder = placeholders[0]
                if next_placeholder.position.col == cur_pos:
                    resolved_row.append_child(next_placeholder)
                    placeholders.remove(next_placeholder)
                    cur_pos += next_placeholder.position.colspan
                elif next_placeholder.position.col < cur_pos:
                    self.resolve_overlap(next_placeholder, resolved_row, cur_pos)
                else:
                    break

            cell = child_cell.resolve(resolved_row, {"col": cur_pos, 'row': self.row_index})
            cur_pos += cell.position.colspan
            resolved_row.append_child(cell)

        # resolve leaks
        for placeholder in placeholders:
            if placeholder.position.col == cur_pos:
                resolved_row.append_child(placeholder)
                cur_pos += placeholder.position.colspan
            elif placeholder.position.col < cur_pos:
                self.resolve_overlap(placeholder, resolved_row, cur_pos)
            else:
                # Leak
                resolved_row.append_child(placeholder)
                cur_pos = placeholder.col + placeholder.colspan

        resolved_row._columns = cur_pos
        return resolved_row

    @staticmethod
    def resolve_overlap(placeholder, row, cur_pos):
        # TODO: Resolve this kind of issue.
        if row.children[-1].is_cell:
            raise ValueError(
                "Cell at %d,%d has overlapped another cell. please check." %
                (row.row_index, row.children[-1].position.col)
            )
        else:
            raise AssertionError(
                "This case should not happen. Check whether placeholders is sorted by col."
            )

    @property
    def columns(self):
        if not self.is_resolved:
            raise AttributeError("columns must be accessed after resolved.")
        else:
            return self._columns

    @property
    def is_merged_row(self):
        return reduce(lambda c1, c2: c1 | c2, map(lambda c: c.is_merged_row, self.children))

    def get_rows_merging_next_row(self):
        return list(filter(lambda c: c.is_merged_row, self.children))

    def append_new_cell(self, text, style, colspan, rowspan):
        if self.is_resolved:
            raise AttributeError("append_new_cell cannot be called on resolved row.")
        pos = Position(colspan=colspan, rowspan=rowspan)
        cell = Cell(text=text, position=pos, style=style)
        self.append_child(cell)
        return cell

    @property
    def row_index(self):
        return self._row_index

    @row_index.setter
    def row_index(self, value):
        check_positive_integer(value, 'row_index')
        self._row_index = value
