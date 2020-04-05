# coding=utf-8
from __future__ import unicode_literals

import urllib
import json
import logging
import functools

from django_fsm import TransitionNotAllowed
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.exceptions import MethodNotAllowed, UnsupportedMediaType, ParseError
from rest_framework.views import APIView
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http.response import (
    HttpResponseNotAllowed,
    HttpResponseBadRequest,
    HttpResponse,
    FileResponse,
)
from django.conf import settings
from base.exceptions import WLException
from base.util.serializer_helper import errors_summery
from base.funcs import AbstractFuncClass
from base.authentication import SessionAuthenticationWoCsrf
from base.choices.common import serializer_type_choice
from base.session.utils import get_extended_session_model, ExtendedSessionNotSet
from base.serializers.model_method import ModelMethodSerializer


logger = logging.getLogger(__name__)


class WLAPIView(object):
    API_VERSION = "0.1"
    parser_classes = (JSONParser, )
    DEFAULT_VALIDATE_EXC_CODE = 400
    ERROR_HTTP_STATUS = False
    http_method_names = ['get', 'post', 'options']

    authentication_classes = [
        SessionAuthenticationWoCsrf
    ]

    def generate_response(self, data, context):
        return Response(data={
            "response": dict(
                {"result": 200},
                **data
            ),
            "version": self.API_VERSION,
            "context": context
        })

    def get_request_data(self, request):
        if MultiPartParser in self.parser_classes:
            return request.data
        else:
            return request.data['data']

    def get_request_obj(self, request, method=None):
        if method is None:
            method = request.method

        if method in {"POST", "PUT", "PATCH"}:
            try:
                context = request.data.get("context", None)
                data = self.get_request_data(request)
                return data, context
            except KeyError:
                raise WLException(code=400, message="Request format incorrect, data field is missing.")
        elif method in {"GET", "DELETE"}:
            objs = request.GET
            if "context" in objs:
                context = objs.pop("context")
                try:
                    context = json.loads(urllib.unquote(context))
                except ValueError:
                    context = None
            else:
                context = None

            data = objs
            return data, context
        else:
            raise WLException(code=500, message="Unexpected call of get request object method.")

    def validate_serializer(self, serializer, exc_code=None):

        if not serializer.is_valid():
            message = errors_summery(serializer)

            raise WLException(
                message=message,
                code=exc_code if exc_code is not None else self.DEFAULT_VALIDATE_EXC_CODE
            )

    def exception_map(self, exc):
        """
        对接口抛出的Exception进行映射
        :param exc: 原Exception
        :return: 映射后Exception
        """
        return exc

    def handle_exception(self, exc):
        exc = self.exception_map(exc)
        if isinstance(exc, WLException):
            reason = exc.message
            code = exc.code
            if exc.code == 500:
                logger.exception("WLException 500", extra={"request": self.request})
            else:
                logger.warn("WLException: %d, %s" % (code, reason), extra={"request": self.request})
        elif isinstance(exc, DjangoValidationError):
            # Django filter raises this kind of exception.
            reason = str(exc.message)
            code = 400
            logger.info('DjangoValidation caught: %s, %s' % (exc.message, getattr(exc, 'code', None)))
        elif isinstance(exc, MethodNotAllowed):
            return HttpResponseNotAllowed(self.http_method_names)
        elif isinstance(exc, (UnsupportedMediaType, ParseError)):
            logger.warn("Exception %s of bad request caught." % repr(exc), exc_info=1)
            return HttpResponseBadRequest(repr(exc))
        else:
            if settings.DEBUG:
                reason = "%s %s" % (str(exc.__class__), str(exc))
            else:
                reason = "Internal Error"

            code = 500
            # Log the detailed exception
            logger.exception("Exception not handled", extra={"request": self.request})

        if self.ERROR_HTTP_STATUS:
            return HttpResponse(content=reason, status=code)
        else:
            return Response(data={
                "response": {
                    "result": code,
                    "reason": reason
                },
                "version": self.API_VERSION,
            })


class WLBinaryView(WLAPIView):

    ERROR_HTTP_STATUS = True

    def get(self, request):
        data, context = self.get_request_obj(request)

        io_stream, content_type = self.get_io_stream(data, context)

        return FileResponse(io_stream, content_type=content_type)

    def get_io_stream(self, data, context):
        """

        :param data:
        :param context:
        :return: BinaryIO, content_type
        """
        raise NotImplementedError


class WLAPIGenericView(WLAPIView, APIView):
    API_VERSION = "2.0"
    API_SERIALIZER = None
    RESULT_SERIALIZER = None
    FUNC_CLASS = None
    EXTRA_ARGS = None
    USE_VALIDATE_DATA = True
    USER_SESSION_KEY = 'user_sid'
    CHECK_SESSION = True

    authentication_classes = [
        SessionAuthenticationWoCsrf
    ]

    def __init__(self, **kwargs):
        super(WLAPIGenericView, self).__init__(**kwargs)
        self._func = self.init_func_class()

    @staticmethod
    def _check_func_class(clz):
        if not issubclass(clz, AbstractFuncClass):
            raise TypeError("FUNC_CLASS must be subclass of AbstractFuncClass")

    def init_func_class(self):

        def check_and_return(c):
            self._check_func_class(c)
            return c

        set_http_methods = set(self.http_method_names)
        if isinstance(self.FUNC_CLASS, dict):
            class_dict = {
                k: v() for k, v in self.FUNC_CLASS.items() if k in set_http_methods and check_and_return(v) is not None
            }

            for method in set_http_methods:
                if method != "options" and method not in self.FUNC_CLASS:
                    raise KeyError("FUNC_CLASS dict must contain a key of %s" % method)

            return class_dict
        elif isinstance(self.FUNC_CLASS, type):
            self._check_func_class(self.FUNC_CLASS)
            fc = self.FUNC_CLASS()
            return {
                k: fc
                for k in set_http_methods if k != "options"
            }

    def __getattr__(self, item):
        if item == 'options':
            return self.options
        elif item in self.http_method_names:
            return self.proceed
        else:
            return super(WLAPIGenericView, self).__getattribute__(item)

    @staticmethod
    def check_session(request):
        # Check whether session is kicked or killed.
        session = getattr(request, 'session', None)
        if session is None:
            return
        if "kicked" in session and session["kicked"]:
            raise WLException(499, "用户已被强制下线，可能因其在另外的终端登录。")
        # Check whether session extension is marked as invalid.
        try:
            extended_session_model = get_extended_session_model()
        except ExtendedSessionNotSet:
            pass
        else:
            try:
                ext_session = extended_session_model.objects.get(session=session.session_key)
                if not ext_session.is_valid:
                    request.session.flush()
                    raise WLException(404, "当前会话已经失效，请重新登录")
            except extended_session_model.DoesNotExist:
                pass

    def get_user(self, request):
        user = getattr(request, 'user', None)
        if isinstance(user, AnonymousUser):
            user = None
        return user

    def get_args(self, request, data):
        if hasattr(self, '_func_args') and hasattr(self, '_api_serializer'):
            return self._func_args, self._api_serializer
        else:
            api_serializer = self.get_api_serializer(request)
            if api_serializer is not None:
                serializer = api_serializer(data=data)
                self.validate_serializer(serializer)

                if self.USE_VALIDATE_DATA:
                    args = serializer.validated_data
                else:
                    args = serializer.data
            else:
                serializer = None
                args = {}

            extra_args = self.get_extra_args(request)

            if extra_args is not None:
                args = dict(args, **extra_args)

            setattr(self, '_func_args', args)
            setattr(self, '_api_serializer', serializer)

            return args, serializer

    def run_func(self, request, user, args_and_serializer_getter):
        # We do not directly gives args and serializer because we need to control the database query action, e.g.
        # transaction, inside the function.
        result = self._func[request.method.lower()](request, user, args_and_serializer_getter)

        return result

    def generate_data(self, request, result, context, serializer, **kwargs):
        result_serializer = self.get_result_serializer(request=request, **kwargs)
        if result_serializer is not None:
            data = result_serializer(result).data
        elif isinstance(result, dict):
            data = result
        else:
            data = {}

        return data

    def http_response(self, request, result, data, context, serializer, **kwargs):
        return self.generate_response(
            data=data,
            context=context
        )

    def proceed(self, request, *args, **kwargs):
        if self.CHECK_SESSION:
            self.check_session(request)

        data, context = self.get_request_obj(request)

        user = self.get_user(request)

        args_and_serializer_getter = functools.partial(self.get_args, request, data)

        result = self.run_func(request, user, args_and_serializer_getter)

        # As we have cached args and serializers, it is no problem to call it here.
        kwargs, serializer = args_and_serializer_getter()

        data = self.generate_data(request=request, result=result, context=context, serializer=serializer, **kwargs)

        return self.http_response(
            request=request, result=result, data=data, context=context, serializer=serializer, **kwargs
        )

    def get_api_serializer(self, request):
        return self.determine_serializer_by_request(request, serializer_type_choice.ST_API)

    def get_result_serializer(self, request, **kwargs):
        return self.determine_serializer_by_request(request, serializer_type_choice.ST_RESULT)

    def get_extra_args(self, request):
        return self.EXTRA_ARGS

    @classmethod
    def determine_serializer_by_request(cls, request, serializer_type):
        return cls.determine_serializer_by_request_method(request.method.lower(), serializer_type)

    @classmethod
    def determine_serializer_by_request_method(cls, method, serializer_type):
        if serializer_type == serializer_type_choice.ST_API:
            s = cls.API_SERIALIZER
        elif serializer_type == serializer_type_choice.ST_RESULT:
            s = cls.RESULT_SERIALIZER
        else:
            raise ValueError("Invalid serializer_type")

        if callable(s):
            return s
        elif isinstance(s, dict):
            return s.get(method, None)
        else:
            return None


class WLModelMethodView(WLAPIGenericView):
    http_method_names = ['post', 'options']
    API_SERIALIZER = ModelMethodSerializer
    METHOD_ARG_SERIALIZER = None

    def __init__(self, **kwargs):
        super(WLModelMethodView, self).__init__(**kwargs)
        if self.METHOD_ARG_SERIALIZER is None:
            self.METHOD_ARG_SERIALIZER = {}

    def get_args(self, request, data):
        if hasattr(self, '_func_args') and hasattr(self, '_api_serializer'):
            return self._func_args, self._api_serializer
        else:
            args, serializer = super(WLModelMethodView, self).get_args(request, data)
            method = args['method']
            arg_serializer_class = self.METHOD_ARG_SERIALIZER.get(method, None)
            if arg_serializer_class:
                arg_serializer = arg_serializer_class(data=args['args'])
                self.validate_serializer(arg_serializer)
                if self.USE_VALIDATE_DATA:
                    args['args'] = arg_serializer.validated_data
                else:
                    args['args'] = arg_serializer.data
            else:
                args['args'] = {}
            return args, serializer

    def get_result_serializer(self, request, **kwargs):
        method = kwargs['method']
        if callable(self.RESULT_SERIALIZER):
            return self.RESULT_SERIALIZER
        elif isinstance(self.RESULT_SERIALIZER, dict):
            return self.RESULT_SERIALIZER.get(method, None)
        else:
            return None

    def exception_map(self, exc):
        if isinstance(exc, TransitionNotAllowed):
            return WLException(453, "非法操作")
        else:
            return exc
