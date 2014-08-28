import sys


PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


def python_2_unicode_compatible(klass):
    """
    Taken from Django project (django/utils/encoding.py) & modified a bit to
    always have __unicode__ method available.
    """
    if '__str__' not in klass.__dict__:
        raise ValueError("@python_2_unicode_compatible cannot be applied "
                         "to %s because it doesn't define __str__()." %
                         klass.__name__)

    klass.__unicode__ = klass.__str__

    if PY2:
        klass.__str__ = lambda self: self.__unicode__().encode('utf-8')

    return klass


if PY3:
    unicode = str
    itervalues = lambda x: x.values()
else:
    unicode = unicode
    itervalues = lambda x: x.itervalues()
