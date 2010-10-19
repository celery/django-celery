try:
    import unittest
    unittest.skip
except AttributeError:
    import unittest2 as unittest
