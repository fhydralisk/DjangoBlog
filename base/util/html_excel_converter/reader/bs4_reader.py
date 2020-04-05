import decimal

from bs4 import BeautifulSoup
from .reader import AbstractReader
from ..core.table import Table


class BS4Reader(AbstractReader):
    @staticmethod
    def number_fallback_to_text(maybe_integer):
        x = maybe_integer
        try:
            x = decimal.Decimal(maybe_integer)
            x = int(maybe_integer)
        except (ValueError, decimal.InvalidOperation):
            pass
        finally:
            return x

    def to_tables(self):
        html = BeautifulSoup(self.content, 'html.parser')
        tables_html = html.find_all('table')
        tables = []
        for table_html in tables_html:
            table = Table(style=table_html.attrs)
            for row_html in table_html.find_all('tr'):
                row_style = row_html.attrs
                row = table.start_new_row(row_style)
                for cell_html in row_html.find_all(('th', 'td')):
                    try:
                        cell_style = cell_html.attrs
                        if cell_html.name == 'th':
                            cell_style.update({'text-align': 'center'})
                        rowspan = int(cell_style.pop('rowspan')) if 'rowspan' in cell_html.attrs else 1
                        colspan = int(cell_style.pop('colspan')) if 'colspan' in cell_html.attrs else 1
                    except ValueError:
                        raise TypeError("rowspan or colspan is not type of integer.")

                    row.append_new_cell(
                        self.number_fallback_to_text(cell_html.text),
                        cell_html.attrs,
                        rowspan=rowspan,
                        colspan=colspan,
                    )
            tables.append(table.resolve(None, None))

        return tables
