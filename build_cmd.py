"""
Custom build command to allow the use of custom tzpath and tzfile and to
allow builds that do not include the zoneinfo tarball.
"""

import os
import tempfile
import warnings

from setuptools.command.build_py import build_py as BaseBuildCommand


class BuildCommand(BaseBuildCommand):
    """Custom build command to allow distributors to customize zone data"""
    def __requires_tzfile(self):
        return (self.tzpath is not None) or (self.tzfiles is not None)

    def __get_tzvar(self, var):
        tzvar = getattr(self, var)

        if tzvar is None:
            return None

        out = tzvar.split(':')
        out = [x for x in out if x]

        if not out:
            warnings.warn('No locations found in %s' % var)

        return out

    def __fmt_tzvar(self, var):
        varnames = {
            'tzfiles': 'TZFILES',
            'tzpath': 'TZPATHS',
        }
        if var not in varnames:
            raise ValueError('Unknown variable %s' % var)

        tzlist = self.__get_tzvar(var)
        if tzlist is None:
            return []

        varname = varnames[var]
        out_list = ['%s = [' % varname]

        if not tzlist:
            out_list[0] += ']'
        else:
            for line in tzlist:
                out_list.append('    %s,' % repr(line))
            out_list.append(']')

        return out_list

    def __make_tzfile(self, fobj):
        out = [
            '# -*- coding: utf-8 -*-',
            '# This is a file generated at build time to allow ' +
            'for build-time modifications',
            '# of the paths to time zone files by downstream distributors'
        ]

        out += self.__fmt_tzvar('tzfiles')
        out += self.__fmt_tzvar('tzpath')

        out.append('')

        fobj.write('\n'.join(out))

    def initialize_options(self):
        BaseBuildCommand.initialize_options(self)

        self.tzpath = None
        self.tzfiles = None

    def add_tzpaths(self):
        # Create the _tzpaths.py file
        build_loc = self.get_module_outfile(self.build_lib,
                                            ('dateutil', 'tz'),
                                            '_tzpaths')

        tmp_file, tmp_file_path = tempfile.mkstemp(prefix='_tzpaths_',
                                                   suffix='.py')

        with os.fdopen(tmp_file, 'w') as f:
            self.__make_tzfile(f)

        try:
            self.copy_file(tmp_file_path, build_loc)
        except:
            raise
        finally:
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

    def run(self):
        # Before the run, modify the TZ_LOCS if requested
        BaseBuildCommand.run(self)

        if self.__requires_tzfile():
            self.add_tzpaths()
