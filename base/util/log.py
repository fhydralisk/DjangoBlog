import logging
from rest_framework.request import Request


class RequestDetailFormatter(logging.Formatter):

    def format(self, record):
        request = getattr(record, 'request', None)  # type: Request
        if request is None:
            record.request_method = 'N/A'
            record.request_uri = 'N/A'
            record.request_body = 'N/A'
        else:
            record.request_method = request.method
            record.request_uri = request.get_full_path()
            content_type = getattr(request, 'content_type', '')
            if content_type.lower().startswith('application/json'):
                record.request_body = str(request.data)
            else:
                record.request_body = 'Not determined.'

        return super(RequestDetailFormatter, self).format(record)
