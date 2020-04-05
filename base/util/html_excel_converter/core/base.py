import six


def check_positive_integer(obj, obj_name, nonzero=False):
    if obj is None:
        return

    if not isinstance(obj, six.integer_types):
        raise TypeError('Type of %s must be integer.' % obj_name)
    if nonzero:
        check = 1
    else:
        check = 0

    if obj < check:
        raise ValueError('%s must >= %d' % (obj_name, check))
