from __future__ import absolute_import

import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


def python_2_unicode_compatible(cls):
    """Taken from Django project (django/utils/encoding.py) & modified a bit to
    always have __unicode__ method available.
    """
    if '__str__' not in cls.__dict__:
        raise ValueError("@python_2_unicode_compatible cannot be applied "
                         "to %s because it doesn't define __str__()." %
                         cls.__name__)

    cls.__unicode__ = cls.__str__

    if PY2:
        cls.__str__ = lambda self: self.__unicode__().encode('utf-8')

    return cls


if PY3:
    unicode = str
    itervalues = lambda x: x.values()
else:
    unicode = unicode
    itervalues = lambda x: x.itervalues()
