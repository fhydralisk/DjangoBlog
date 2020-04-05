from .node import Node
from .cell import PlaceholderCell, Position
from .row import Row


class Table(Node):
    def __init__(self, parent=None, children=None, resolved=False, style=None):
        super(Table, self).__init__(parent, children, resolved, style)

    def resolve(self, parent, node_info, *args, **kwargs):
        if parent is not None:
            self.parent = parent

        self.node_info = node_info

        next_placeholders = []
        for row_index, row in enumerate(self.children):
            r = row.resolve(parent, {'row_index': row_index, 'placeholders': next_placeholders})
            self.children[row_index] = r
            next_placeholders = [
                PlaceholderCell(
                    Position(
                        row=rp.position.row,
                        col=rp.position.col,
                        rowspan=rp.position.rowspan-1,
                        colspan=rp.position.colspan,
                    )
                )
                for rp in r.get_rows_merging_next_row()
            ]

        self._resolved = True

        return self

    def start_new_row(self, style):
        if self.is_resolved:
            raise AttributeError("start_new_row cannot be called on resolved table.")
        row = Row(len(self.children), style=style)
        self.append_child(row)
        return row

    def get_all_cells_to_write(self):
        if self.is_resolved:
            return self._get_all_cells_to_write()
        else:
            return self.resolve(None, None).get_all_cells_to_write()

    def _get_all_cells_to_write(self):
        cells = []
        for row in self.children:
            for cell in row.children:
                if cell.is_cell:
                    cells.append(cell)

        return cells
