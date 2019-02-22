#!/usr/bin/python
from os.path import isfile
import os

import setuptools
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

from distutils.version import LooseVersion
import warnings

import io
import sys

if isfile("MANIFEST"):
    os.unlink("MANIFEST")

if LooseVersion(setuptools.__version__) <= LooseVersion("24.3"):
    warnings.warn("python_requires requires setuptools version > 24.3",
                  UserWarning)


class Unsupported(TestCommand):
    def run(self):
        sys.stderr.write("Running 'test' with setup.py is not supported. "
                         "Use 'pytest' or 'tox' to run the tests.\n")
        sys.exit(1)


###
# Load metadata
PACKAGES = find_packages(where='.', exclude=['dateutil.test'])


def README():
    with io.open('README.rst', encoding='utf-8') as f:
        readme_lines = f.readlines()

    # The .. doctest directive is not supported by PyPA
    lines_out = []
    for line in readme_lines:
        if line.startswith('.. doctest'):
            lines_out.append('.. code-block:: python3\n')
        else:
            lines_out.append(line)

    return ''.join(lines_out)
README = README()  # NOQA


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
      license="Dual License",
      long_description=README,
      long_description_content_type='text/x-rst',
      packages=PACKAGES,
      python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*",
      package_data={"dateutil.zoneinfo": ["dateutil-zoneinfo.tar.gz"]},
      zip_safe=True,
      setup_requires=['setuptools_scm'],
      install_requires=["six >=1.5"],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'License :: OSI Approved :: Apache Software License',
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
