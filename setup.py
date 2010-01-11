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
      description = "Extensions to the standard python 2.3+ datetime module",
      author = "Gustavo Niemeyer",
      author_email = "gustavo@niemeyer.net",
      url = "http://labix.org/python-dateutil",
      license = "PSF License",
      long_description =
"""\
The dateutil module provides powerful extensions to the standard
datetime module, available in Python 2.3+.
""",
      packages = ["dateutil", "dateutil.zoneinfo"],
      package_data={"": ["*.tar.gz"]},
      include_package_data=True,
      zip_safe=False,
      )
