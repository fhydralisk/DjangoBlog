import xlwt
from io import BytesIO
from .writer import AbstractWriter
from ..core.table import Table
from ..core.cell import Position
from .stylemap import html_style_to_xls


class XLWTWriter(AbstractWriter):
    style_dic = {}

    def str_2_style(self, style_str):
        if style_str in self.style_dic:
            return self.style_dic[style_str]
        else:
            style = xlwt.easyxf(style_str)
            self.style_dic[style_str] = style
            return style

    def get_width_px(self, width_str):
        if width_str.endswith('px'):
            width_str = width_str.replace('px', '')

        width_str = width_str.strip()

        try:
            return int(width_str)
        except ValueError:
            return None

    def get_content(self):
        workbook = xlwt.Workbook()
        for table_index, table in enumerate(self.tables):  # type: Table
            sheet = workbook.add_sheet("Sheet%d" % table_index)  # type: xlwt.Worksheet
            cells = table.get_all_cells_to_write()
            for cell in cells:
                cell_style = cell.get_style()
                xls_style_str = html_style_to_xls(cell_style)
                xls_style = self.str_2_style(xls_style_str)
                text = cell.text
                pos = cell.position  # type: Position
                if cell.is_merged_row or cell.is_merged_col:
                    sheet.write_merge(pos.row, pos.row + pos.rowspan - 1, pos.col, pos.col + pos.colspan - 1, text, style=xls_style)
                else:
                    sheet.write(pos.row, pos.col, text, style=xls_style)
                if 'height' in cell_style:
                    height_style_str = 'font: height {}'.format(int(cell_style['height'])*10)
                    tall_style = self.str_2_style(height_style_str)
                    sheet.row(pos.row).set_style(tall_style)

                if 'width' in cell_style:
                    width = self.get_width_px(cell_style['width'])
                    if width:
                        sheet.col(pos.col).width = width * 256
        content = BytesIO()
        workbook.save(content)

        content.seek(0)
        return content
