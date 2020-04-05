# coding=utf-8
from __future__ import unicode_literals

import django_filters

from django.db import transaction
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from base.exceptions import WLException
from base.serializers import ApiSerializer, serializers
from base.util.pages import get_page_info
from base.util.thread import LocalThreadContextMixin


class AbstractPermission(LocalThreadContextMixin):
    FAIL = {"code": 401, "message": "Permission Denied"}
    EXCEPTION = WLException

    def fail(self):
        raise self.EXCEPTION(**self.FAIL)

    def check(self, **kwargs):
        func = kwargs.pop('func', None)
        request = kwargs.pop('request', None)
        user = kwargs.pop('user', None)
        serializer = kwargs.pop('serializer', None)
        if not self.check_permission(func=func, request=request, user=user, serializer=serializer, **kwargs):
            self.fail()

    def check_permission(self, func, request, user, serializer, **kwargs):
        raise NotImplementedError

    def __or__(self, other):
        return LogicOrPermissions((self, other))


class ConditionalPermission(AbstractPermission):

    def __init__(self, cond_func, permission):
        if callable(cond_func):
            self._cond_func = cond_func
        else:
            raise TypeError("cond_func of Conditional Permission must be callable.")

        self._permission = permission

    def check(self, **kwargs):
        if self._cond_func(**kwargs):
            self._permission.check(**kwargs)
        else:
            pass

    def check_permission(self, func, request, user, serializer, **kwargs):
        # Do nothing because we override check method.
        pass


class LogicOrPermissions(AbstractPermission):
    def __init__(self, permissions):
        if isinstance(permissions, (list, tuple, set)):
            self._permissions = list(permissions)
        else:
            raise TypeError("permissions must be list, tuple or set")

    def check(self, **kwargs):
        last_exc = None
        for perm in self._permissions:
            try:
                perm.check(**kwargs)
            except perm.EXCEPTION as e:
                last_exc = e
            else:
                return

        raise last_exc

    def check_permission(self, func, request, user, serializer, **kwargs):
        # Do nothing because we override check method.
        pass


class RequireUserLoginPermission(AbstractPermission):
    FAIL = {
        "code": 404,
        "message": u"用户不存在或未登录"
    }

    def check_permission(self, func, request, user, **kwargs):
        return isinstance(user, get_user_model()) and user.is_active


class AbstractFuncClass(LocalThreadContextMixin):
    PERMISSIONS = []
    DB_TRANSACTION = False

    def __call__(self, request, user, args_and_serializer_getter):
        self.clean_context()
        kwargs, serializer = args_and_serializer_getter()
        if self.DB_TRANSACTION:
            with transaction.atomic():
                return self.real_call(request=request, user=user, serializer=serializer, kwargs=kwargs)
        else:
            return self.real_call(request=request, user=user, serializer=serializer, kwargs=kwargs)

    def real_call(self, request, user, serializer, kwargs):
        self.check_permission(request=request, user=user, serializer=serializer, kwargs=kwargs)
        return self.run(request=request, user=user, serializer=serializer, **kwargs)

    def get_permissions(self, request, user, serializer, kwargs):
        return self.PERMISSIONS

    def check_permission(self, request, user, serializer, kwargs):
        for permission in self.get_permissions(request=request, user=user, serializer=serializer, kwargs=kwargs):
            permission.check(func=self, request=request, user=user, serializer=serializer, **kwargs)

    def run(self, request, user, serializer, **kwargs):
        raise NotImplementedError


class MethodRoutedFuncClass(AbstractFuncClass):

    def __init__(self, *args, **kwargs):
        self._cached_permission_dict = {}
        super(MethodRoutedFuncClass, self).__init__(*args, **kwargs)

    def get_permissions_for_method(self, method):
        perms = []
        for perm in self.PERMISSIONS:
            if isinstance(perm, (tuple, list)):
                if perm[0] == method:
                    perms.append(perm[1])
            else:
                perms.append(perm)
        return perms

    def get_permissions(self, request, user, serializer, kwargs):
        method = request.method.lower()
        if method not in self._cached_permission_dict:
            self._cached_permission_dict[method] = \
                self.get_permissions_for_method(method)

        return self._cached_permission_dict[method]

    def run(self, request, user, serializer, **kwargs):
        func = getattr(self, request.method.lower(), None)
        if callable(func):
            return func(request=request, user=user, serializer=serializer, **kwargs)
        else:
            raise AssertionError("Method {} not implemented.".format(request.method.lower()))


class PageApiSerializer(ApiSerializer):
    page = serializers.IntegerField(min_value=0)
    count_per_page = serializers.IntegerField(min_value=1, max_value=100)


class PagedAbstractFuncClass(AbstractFuncClass):

    filter_set_class = None  # Integrated with django-filter
    default_count_per_page = None
    page_api_serializer_class = PageApiSerializer

    def run(self, request, **kwargs):
        page, count_per_page = self.get_page_info(request)
        qs, field_name, extra = self.get_paged_qs(page=page, count_per_page=count_per_page, **kwargs)

        if extra is None:
            extra = {}

        qs = self.filter_queryset(request, self.filter_set_class, qs, **kwargs)

        start, end, n_pages = get_page_info(
            qs, count_per_page, page,
            index_error_excepiton=self.out_of_range_exception(page=page, count_per_page=count_per_page, **kwargs)
        )
        qs_paged = qs[start:end]
        qs_transformed = self.transform_queryset(qs_paged, page=page, count_per_page=count_per_page, **kwargs)
        return dict({
            field_name: [
                self.transform_element(obj=obj, page=page, count_per_page=count_per_page, index=index, **kwargs)
                for index, obj in enumerate(qs_transformed)
            ],
            'n_pages': n_pages,
            'count': qs.count(),
        }, **extra)

    def get_page_info(self, request):
        page = request.GET.get('page', 0)
        count_per_page = self.get_count_per_page(request)
        page_serializer = self.page_api_serializer_class(
            data={'page': page, 'count_per_page': count_per_page}
        )
        if not page_serializer.is_valid():
            raise WLException(400, u"页码有误")
        page = page_serializer.validated_data['page']
        count_per_page = page_serializer.validated_data['count_per_page']
        return page, count_per_page

    def get_count_per_page(self, request):
        count_per_page = request.GET.get('count_per_page', None)
        if count_per_page:
            return count_per_page
        else:
            return self.default_count_per_page or settings.COUNT_PER_PAGE

    def get_paged_qs(self, **kwargs):
        """

        :param kwargs:
        :return: queryset, field name, extra fields.
        """
        raise NotImplementedError

    def out_of_range_exception(self, **kwargs):
        return WLException(400, u"页码超出范围")

    def transform_element(self, obj, **kwargs):
        return obj

    def transform_queryset(self, queryset, **kwargs):
        return queryset

    @staticmethod
    def _filter_queryset(request, filter_set_class, queryset, **kwargs):
        return filter_set_class(data=request.GET, queryset=queryset).qs

    def filter_queryset(self, request, filter_set_class, queryset, **kwargs):
        if isinstance(filter_set_class, type) and issubclass(filter_set_class, django_filters.FilterSet):
            if request.method.lower() == 'get':
                return self._filter_queryset(request, filter_set_class, queryset, **kwargs)
            else:
                raise AssertionError("Method of http must be get to use filter_set_class")
        elif filter_set_class is None:
            return queryset
        else:
            raise TypeError("filter_set_class must be subclass of FilterSet or None")


class ModelMethodFunc(AbstractFuncClass):
    model_class = None
    model_name = None
    allow_methods = None
    DB_TRANSACTION = True

    def real_call(self, request, user, serializer, kwargs):
        try:
            instance = self.model_class.objects.get(pk=kwargs['id'])
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            raise WLException(400, "目标{}不存在".format(self.get_model_name()))

        kwargs['instance'] = instance
        return super(ModelMethodFunc, self).real_call(request=request, user=user, serializer=serializer, kwargs=kwargs)

    def run(self, request, user, serializer, instance, method, args, **kwargs):
        self.validate_method(instance, method)

        extra = self.call_method(
            prefix='pre_',
            request=request,
            user=user,
            serializer=serializer,
            instance=instance,
            method=method,
            args=args,
            **kwargs
        )

        if extra:
            args.update(extra)

        result = getattr(instance, method)(**args)

        return self.call_method(
            prefix='post_',
            request=request,
            user=user,
            serializer=serializer,
            instance=instance,
            method=method,
            args=args,
            result=result,
            **kwargs
        )

    def get_model_name(self):
        if self.model_name:
            return self.model_name
        else:
            return self.model_class._meta.verbose_name

    def validate_method(self, instance, method):
        def raise_error():
            raise WLException(400, "不支持该方法")

        if not self._method_valid(instance, method):
            raise_error()

        if self.allow_methods is not None:
            if method in self.allow_methods:
                pass
            else:
                raise_error()
        else:
            raise_error()

    @staticmethod
    def _method_valid(instance, method):
        return callable(getattr(instance, method, None))

    def call_method(self, prefix, method, **kwargs):
        method_name = prefix + method
        method_to_call = getattr(self, method_name, None)
        if callable(method_to_call):
            return method_to_call(method=method, **kwargs)
