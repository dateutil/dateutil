#!/usr/bin/python
from distutils.core import setup

setup(name="python-dateutil",
      version = "0.4",
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
      packages = ["dateutil"],
      )
