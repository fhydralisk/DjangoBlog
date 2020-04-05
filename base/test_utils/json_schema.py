import six
import copy


def full_path(path):
    return '.'.join(map(lambda x: str(x), path))


def assert_same_type(value1, value2):
    if value1 is None or value2 is None:
        return
    elif value1.__class__ is value2.__class__:
        return
    elif six.PY2 and issubclass(value1.__class__, basestring) and issubclass(value2.__class__, basestring):
        return
    else:
        raise AssertionError


def check_leaf(v_check, v_schema, path, check_type):
    errors = []
    if check_type:
        try:
            assert_same_type(v_schema, v_check)
        except AssertionError:
            # Type hint
            errors.append(
                (full_path(path), 'should be %s but %s' % (v_schema.__class__, v_check.__class__))
            )
    else:
        pass

    return errors


def check_dict(v_check, v_schema, path, check_type):
    errors = []
    if isinstance(v_check, dict):
        errors.extend(
            check_json_schema(v_check, v_schema, check_type=check_type, path=path)
        )
    else:
        errors.append(
            (full_path(path), 'should be dict but %s' % v_check.__class__)
        )

    return errors


def check_list(v_check, v_schema, path, check_type):
    errors = []
    if isinstance(v_check, list):
        for index, element in enumerate(v_check):
            if isinstance(v_schema[0], list):
                errors.extend(
                    check_list(element, v_schema[0], path=path + [index], check_type=check_type)
                )
            elif isinstance(v_schema[0], dict):
                errors.extend(
                    check_dict(element, v_schema[0], path=path + [index], check_type=check_type)
                )
            else:
                errors.extend(
                    check_leaf(element, v_schema[0], path=path + [index], check_type=check_type)
                )
    else:
        errors.append(
            (full_path(path), 'should be list but %s' % v_check.__class__)
        )

    return errors


def check_json_schema(data, data_schema, check_type, path=None):
    # errors: [ ('key': 'error'), ... ]
    errors = []
    if path is None:
        path = []

    if not isinstance(data, dict):
        return [(full_path(path), 'should be dict but %s' % data.__class__)]

    data_check = copy.copy(data)
    for k, v_schema in data_schema.items():
        if k in data_check:
            v_check = data_check.pop(k)
            if isinstance(v_schema, list):
                errors.extend(
                    check_list(v_check, v_schema, path=path + [k], check_type=check_type)
                )
            elif isinstance(v_schema, dict):
                errors.extend((
                    check_dict(v_check, v_schema, path=path + [k], check_type=check_type)
                ))
            else:
                errors.extend(
                    check_leaf(v_check, v_schema, path=path + [k], check_type=check_type)
                )
        else:
            errors.append(
                (full_path(path + [k]), 'does not exists')
            )

    if data_check:
        for k in data_check:
            errors.append(
                (full_path(path + [k]), 'should not exist')
            )

    return errors
