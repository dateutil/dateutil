#!/usr/bin/python
from os.path import isfile
import os

import setuptools
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

from distutils.version import LooseVersion
import warnings

if isfile("MANIFEST"):
    os.unlink("MANIFEST")

PACKAGES = find_packages(where='.', exclude=['dateutil.test'])

if LooseVersion(setuptools.__version__) <= LooseVersion("24.3"):
    warnings.warn("python_requires requires setuptools version > 24.3",
                  UserWarning)


class Unsupported(TestCommand):
    def run(self):
        print("Running 'test' with setup.py is not supported. "
              "Use 'pytest' or 'tox' to run the tests.")


setup(name="python-dateutil",
      use_scm_version={
          'write_to': 'dateutil/_version.py',
      },
      description="Extensions to the standard Python datetime module",
      author="Gustavo Niemeyer",
      author_email="gustavo@niemeyer.net",
      maintainer="Paul Ganssle",
      maintainer_email="dateutil@python.org",
      url="https://dateutil.readthedocs.io",
      license="Apache 2.0",
      long_description="""
The dateutil module provides powerful extensions to the
datetime module available in the Python standard library.
""",
      packages=PACKAGES,
      python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*",
      package_data={"dateutil.zoneinfo": ["dateutil-zoneinfo.tar.gz"]},
      zip_safe=True,
      requires=["six"],
      setup_requires=['setuptools_scm'],
      install_requires=["six >=1.5"],  # XXX fix when packaging is sane again
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: Software Development :: Libraries',
      ],
      test_suite="dateutil.test",
      cmdclass={
          "test": Unsupported
      }
      )
