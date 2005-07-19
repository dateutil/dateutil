#!/usr/bin/python
from distutils.sysconfig import get_python_lib
from distutils.core import setup
import glob
import os

if os.path.isfile("MANIFEST"):
    os.unlink("MANIFEST")

PYTHONLIB = get_python_lib(1)

setup(name="python-dateutil",
      version = "1.0",
      description = "Extensions to the standard python 2.3+ datetime module",
      author = "Gustavo Niemeyer",
      author_email = "niemeyer@conectiva.com",
      url = "https://moin.conectiva.com.br/DateUtil",
      license = "PSF License",
      long_description =
"""\
The dateutil module provides powerful extensions to the standard
datetime module, available in Python 2.3+.
""",
      packages = ["dateutil", "dateutil.zoneinfo"],
      data_files = [(PYTHONLIB+"/dateutil/zoneinfo", 
                     glob.glob("dateutil/zoneinfo/zoneinfo*.tar.*"))],
      )
