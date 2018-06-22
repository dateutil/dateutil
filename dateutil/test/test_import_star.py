"""Test for the "import *" functionality.

As import * can be only done at module level, it has been added in a separate file
"""
import unittest

prev_locals = list(locals())
from dateutil import *
new_locals = {name:value for name,value in locals().items()
              if name not in prev_locals}
new_locals.pop('prev_locals')

class ImportStarTest(unittest.TestCase):
    """ Test that `from dateutil import *` adds the modules in __all__ locally"""

    def testImportedModules(self):
        import dateutil.easter
        import dateutil.parser
        import dateutil.relativedelta
        import dateutil.rrule
        import dateutil.tz
        import dateutil.utils
        import dateutil.zoneinfo

        self.assertEqual(dateutil.easter, new_locals.pop("easter"))
        self.assertEqual(dateutil.parser, new_locals.pop("parser"))
        self.assertEqual(dateutil.relativedelta, new_locals.pop("relativedelta"))
        self.assertEqual(dateutil.rrule, new_locals.pop("rrule"))
        self.assertEqual(dateutil.tz, new_locals.pop("tz"))
        self.assertEqual(dateutil.utils, new_locals.pop("utils"))
        self.assertEqual(dateutil.zoneinfo, new_locals.pop("zoneinfo"))

        self.assertFalse(new_locals)
