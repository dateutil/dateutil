#!/usr/bin/python
from distutils.sysconfig import get_python_lib
from distutils.core import setup
import glob
import os
from os.path import isfile, join

if isfile("MANIFEST"):
    os.unlink("MANIFEST")

# Get PYTHONLIB with no prefix so --prefix installs work.
PYTHONLIB = join(get_python_lib(standard_lib=1, prefix=''), 'site-packages')
ZONEINFO = join("dateutil", "zoneinfo")

setup(name="python-dateutil",
      version = "1.1",
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
      data_files = [(join(PYTHONLIB, ZONEINFO),
                     glob.glob(join(ZONEINFO, "zoneinfo*.tar.*")))],
      )
