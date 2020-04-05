import json
from django.contrib.sessions.middleware import SessionMiddleware


class WLSessionMiddleware(SessionMiddleware):
    USER_SESSION_KEY = 'user_sid'
    POST_TYPES = {
        'POST', 'DELETE', 'PATCH', 'PUT'
    }

    def process_request(self, request):
        super(WLSessionMiddleware, self).process_request(request)
        # Seek for user session
        session_key = request.GET.get(self.USER_SESSION_KEY, None)
        if session_key is None:
            try:
                if request.method in self.POST_TYPES and 'application/json' in request.META.get('CONTENT_TYPE', []):
                    body = json.loads(request.body.decode('utf-8'))
                    session_key = body.get(self.USER_SESSION_KEY) or body['data'].get(self.USER_SESSION_KEY)

            except (AttributeError, KeyError, ValueError):
                pass

        if session_key is not None:
            request.session = self.SessionStore(session_key)
