#!/usr/bin/python
from os.path import isfile
import codecs
import os
import re

from setuptools import setup


if isfile("MANIFEST"):
    os.unlink("MANIFEST")


TOPDIR = os.path.dirname(__file__) or "."
VERSION = re.search('__version__ = "([^"]+)"',
                    codecs.open(TOPDIR + "/dateutil/__init__.py",
                                encoding='utf-8').read()).group(1)


setup(name="python-dateutil",
      version=VERSION,
      description="Extensions to the standard Python datetime module",
      author="Yaron de Leeuw",
      author_email="me@jarondl.net",
      url="https://dateutil.readthedocs.org",
      license="Simplified BSD",
      long_description="""
The dateutil module provides powerful extensions to the
datetime module available in the Python standard library.
""",
      packages=["dateutil", "dateutil.zoneinfo"],
      package_data={"dateutil.zoneinfo": ["dateutil-zoneinfo.tar.gz"]},
      zip_safe=True,
      requires=["six"],
      install_requires=["six >=1.5"],  # XXX fix when packaging is sane again
      classifiers=[
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
          'Programming Language :: Python :: 3.4',
          'Topic :: Software Development :: Libraries',
      ],
      test_suite="dateutil.test.test"
      )
