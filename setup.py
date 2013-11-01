#!/usr/bin/python
from os.path import isfile, join
import codecs
import glob
import os
import re

from setuptools import setup


if isfile("MANIFEST"):
    os.unlink("MANIFEST")


TOPDIR = os.path.dirname(__file__) or "."
VERSION = re.search('__version__ = "([^"]+)"',
                    codecs.open(TOPDIR + "/dateutil/__init__.py", encoding='utf-8').read()).group(1)


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
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Topic :: Software Development :: Libraries',
      ]
      )
