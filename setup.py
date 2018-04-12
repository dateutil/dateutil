#!/usr/bin/python
from os.path import isfile
import os
import sys

import setuptools
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

from build_cmd import BuildCommand

from distutils.version import LooseVersion
import warnings

import io

if isfile("MANIFEST"):
    os.unlink("MANIFEST")

if LooseVersion(setuptools.__version__) <= LooseVersion("24.3"):
    warnings.warn("python_requires requires setuptools version > 24.3",
                  UserWarning)


class Unsupported(TestCommand):
    def run(self):
        print("Running 'test' with setup.py is not supported. "
              "Use 'pytest' or 'tox' to run the tests.")

###
# Load metadata
PACKAGES = find_packages(where='.', exclude=['dateutil.test'])

def README():
    with io.open('README.rst', encoding='utf-8') as f:
        readme_lines = f.readlines()

    # The .. doctest directive is not supported by PyPA
    lines_out = []
    doctest_line_found = False
    for line in readme_lines:
        if line.startswith('.. doctest'):
            doctest_line_found = True
            lines_out.append('.. code-block:: python3\n')
        else:
            lines_out.append(line)

    return ''.join(lines_out)
README = README()

def consume_custom_args():
    """Consumes additional arguments to setup.py"""
    # This is a hack-job because the only way I can tell to add user-specified
    # options to `setup.py` subcommands is to set a cmdclass with user_options
    # set, but user_options only works when added to the directly-invoked
    # subcommand, not indirectly invoked (e.g. when python setup.py install
    # invokes build, and build invokes build_py).
    #
    # To get around this, I'll consume these arguments directly from sys.argv
    # in *all* cases, and use them to modify the inputs to setup()
    #
    # If you know of a better way to do this, please let me know.
    valid_args = {'--no-zoneinfo': False,
                  '--tzfiles': True,
                  '--tzpath': True}

    response = {
        'no_zoneinfo': False,
        'tzfiles': None,
        'tzpath': None
    }

    out_args = sys.argv[0:1]

    for arg in sys.argv[1:]:
        argsplit = arg.split('=', 1)
        key = argsplit[0]

        if key in valid_args:
            resp_key = key.lstrip('-').replace('-', '_')
            if valid_args[key]:
                if len(argsplit) == 0:
                    raise ValueError('Missing argument to %s' % key)
                response[resp_key] = argsplit[1]
            else:
                response[resp_key] = not response[resp_key]
        else:
            out_args.append(arg)

    sys.argv = out_args
    return response


# Load custom arguments from command line independent of subcommand
_custom_args = consume_custom_args()

NO_ZONEINFO = _custom_args.pop('no_zoneinfo')
BUILD_OPTIONS = {k: _custom_args.pop(k) for k in ('tzfiles', 'tzpath')}

if NO_ZONEINFO:
    PKG_DATA = {}
else:
    PKG_DATA = {"dateutil.zoneinfo": ["dateutil-zoneinfo.tar.gz"]}


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
      package_data=PKG_DATA,
      zip_safe=True,
      requires=["six"],
      setup_requires=['setuptools_scm'],
      install_requires=["six >=1.5"],  # XXX fix when packaging is sane again
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
          "test": Unsupported,
          "build_py": BuildCommand,
      },
      # Custom arguments parsed from the command line
      options={
          'build_py': BUILD_OPTIONS,
      }
    )
