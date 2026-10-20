#!/usr/bin/python
import io

from setuptools import setup

###
# Load metadata

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


setup(
      use_scm_version={
          'write_to': 'src/dateutil/_version.py',
      },
      ## Needed since doctest not supported by PyPA.
      long_description = README,
      )
