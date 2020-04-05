import six
import io
from ..reader.reader import AbstractReader
from ..core.table import Table


class AbstractWriter(object):

    support_multi_tables = True

    def __init__(self, reader=None, table=None, tables=None):
        # type: (AbstractReader, Table, list) -> None
        if reader:
            tables = reader.to_tables()
        else:
            if table and tables:
                raise ValueError("tables parameter must not be used while table is specified.")

            if isinstance(table, Table):
                tables = [table]

        if not isinstance(tables, (tuple, list)):
            raise TypeError("tables must be a list of Table instances.")

        if not self.support_multi_tables:
            if len(tables) > 1:
                raise ValueError("This writer does not support multiple tables writing.")

        self.tables = tables

    def write_to_path(self, path, mode='wb', encoding=None):
        if encoding:
            if six.PY2:
                import codecs
                with codecs.open(path, mode, encoding=encoding) as f:
                    f.write(self.get_content().read())
            elif six.PY3 or six.PY34:
                with open(path, mode, encoding=encoding) as f:
                    f.write(self.get_content().read())
        else:
            with open(path, mode) as f:
                f.write(self.get_content().read())

    def get_stream(self):
        return self.get_content()

    def get_content(self):
        # type: () -> io.BytesIO
        """
        Subclass should implement get_content to convert Table(s) to bytes for writing.
        :return: io stream of file.
        """
        raise NotImplementedError
