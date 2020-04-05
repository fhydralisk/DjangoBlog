import six


class AbstractReader(object):
    content = None

    def __init__(self, path=None, mode=None, encoding=None, stream=None):
        if path is not None:
            if mode is None:
                mode = 'rb'
            self.open_path(path, mode, encoding)
        elif stream is not None:
            self.open_stream(stream)
        else:
            pass

    def open_path(self, path, mode, encoding):
        if encoding:
            if six.PY2:
                import codecs
                with codecs.open(path, mode, encoding=encoding) as f:
                    self.content = f.read()
            elif six.PY3 or six.PY34:
                with open(path, mode, encoding=encoding) as f:
                    self.content = f.read()
        else:
            with open(path, mode) as f:
                self.content = f.read()

    def open_stream(self, stream):
        self.content = stream.read()

    def to_tables(self):
        # type: () -> list
        """
        Subclass should implement to_tables to convert content to list of Tables
        :return: list of Tables.
        """
        raise NotImplementedError
