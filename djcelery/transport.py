"""

This module is an alias to :mod:`kombu.transport.django`

"""
from __future__ import absolute_import

import sys

import kombu.transport.django as transport
# need to keep reference to old module so that it's not garbage collected
old_module = sys.modules[__name__]
sys.modules[__name__] = transport
