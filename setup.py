#!/usr/bin/python
from os.path import isfile, join
import glob
import os
import re

from setuptools import setup


if isfile("MANIFEST"):
    os.unlink("MANIFEST")


TOPDIR = os.path.dirname(__file__) or "."
VERSION = re.search('__version__ = "([^"]+)"',
                    open(TOPDIR + "/dateutil/__init__.py").read()).group(1)


setup(name="python-dateutil",
      version = VERSION,
      description = "Extensions to the standard Python datetime module",
      author = "Tomi Pievilaeinen",
      author_email = "tomi.pievilainen@iki.fi",
      url = "http://labix.org/python-dateutil",
      license = "Simplified BSD",
      long_description =
"""\
The dateutil module provides powerful extensions to the 
datetime module available in the Python standard library.
""",
      packages = ["dateutil", "dateutil.zoneinfo"],
      package_data = {"": ["*.tar.gz"]},
      include_package_data = True,
      zip_safe = False,
      requires = ["six"],
      install_requires = ["six"], # XXX fix when packaging is sane again
      )
