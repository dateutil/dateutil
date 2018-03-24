# Contributing

This document outlines the ways to contribute to `python-dateutil`. This is a fairly small, low-traffic project, so most of the contribution norms (coding style, acceptance criteria) have been developed ad hoc and this document will not be exhaustive. If you are interested in contributing code or documentation, please take a moment to at least review the license section to understand how your code will be licensed.

## Types of contribution

### Bug reports
Bug reports are an important type of contribution - it's important to get feedback about how the library is failing, and there's no better way to do that than to hear about real-life failure cases. A good bug report will include:

1. A minimal, reproducible example - a small, self-contained script that can reproduce the behavior is the best way to get your bug fixed. For more information and tips on how to structure these, read [StackOverflow's guide to creating a minimal, complete, verified example](https://stackoverflow.com/help/mcve).

2. The platform and versions of everything involved, at a minimum please include operating system, `python` version and `dateutil` version. Instructions on getting your versions:
    - `dateutil`: `python -c 'import dateutil; print(dateutil.__version__)'`
    - `Python`: `python --version`

3. A description of the problem - what *is* happening and what *should* happen.

While pull requests fixing bugs are accepted, they are *not* required - the bug report in itself is a great contribution.

### Feature requests

If you would like to see a new feature in `dateutil`, it is probably best to start an issue for discussion rather than taking the time to implement a feature which may or may not be appropriate for `dateutil`'s API. For minor features (ones where you don't have to put a lot of effort into the PR), a pull request is fine but still not necessary.

### Pull requests

If you would like to fix something in `dateutil` -  improvements to documentation, bug fixes, feature implementations, fixes to the build system, etc - pull requests are welcome! Where possible, try to keep your coding to [PEP 8 style](https://www.python.org/dev/peps/pep-0008/), with the minor modification that the existing `dateutil` class naming style does not use the CapWords convention, or where the existing style does not follow PEP 8.

The most important thing to include in your pull request are *tests* - please write one or more tests to cover the behavior you intend your patch to improve. Ideally, tests would use only the public interface - try to get 100% difference coverage using only supported behavior of the API.

#### Changelog
To keep users abreast of the changes to the module and to give proper credit, `dateutil` maintains a changelog, which is managed by [towncrier](https://github.com/hawkowl/towncrier). To add a changelog entry, make a new file called `<issue_no>.<type>.rst`, where `<issue_no>` is the number of the PR you've just made (it's easiest to add the changelog *after* you've created the PR so you'll have this number), and `<type>` is one of the following types:

- `feature`: A new feature, (e.g. a new function, method, attribute, etc)
- `bugfix`: A fix to a bug
- `doc`: A change to the documentation
- `deprecation`: Used if deprecating a feature or dropping support for a Python version.
- `misc`: A change that has no interesting effect for end users, such as fixes to the test suite or CI.

PRs that include a feature or bugfix *and* a deprecation should create a separate entry for the deprecation.



> {description of changes}. Reported by @{reporter} (gh issue #{issue\_no}). Fixed by @{patch submitter} (gh pr #{pr\_no})

An example changelog entry might be:

**581.bugfix.rst**
```
Fixed issue where the tz.tzstr constructor would erroneously succeed if passed
an invalid value for tzstr. Reported by @pganssle (gh issue #259). Fixed by
@pablogsal (gh pr #581)
```

For bugs reported and fixed by the same person use "Reported and fixed by @{patch submitter}". It is not necessary to create a github issue just for the purpose of mentioning it in the changelog, if the PR *is* the report, mentioning the PR is enough.

## License

Starting December 1, 2017, all contributions will be assumed to be released under a dual license - the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0) and the [3-Clause BSD License](https://opensource.org/licenses/BSD-3-Clause) unless otherwise specified in the pull request.

All contributions before December 1, 2017 except those explicitly relicensed, are only under the 3-clause BSD license.

## Building and releasing

When you get the source, it does not contain the internal zoneinfo
database. To get (and update) the database, run the updatezinfo.py script. Make sure
that the zic command is in your path, and that you have network connectivity
to get the latest timezone information from IANA, or from [our mirror of the
IANA database](https://dateutil.github.io/tzdata/).

## Development Setup

Install the the dependencies for running the test suite using `pip` or `conda`.

### pip

Run the following commands to create a [virtual environment](https://virtualenv.pypa.io) with all dependencies installed:

    python -m virtualenv .venv       # Create virtual environment in .venv directory
    . .venv/bin/activate             # Activate the virtual environment
    pip install -r requirements.txt  # Install the dependencies

### conda

Run the following commands to create a [conda environment](https://conda.io) with all dependencies installed:

    conda create -n dateutil                # Create a conda environment
    # conda create -n dateutil python=3.6   # or specify a version
    source activate dateutil                # Activate the conda environment
    pip install -r requirements.txt         # Install the dependencies

## Testing

dateutil has a comprehensive test suite, which can be run simply by running
`python -m pytest` in the project root. Note that if you don't have the internal
zoneinfo database, some tests will fail. Apart from that, all tests should pass.

To easily test dateutil against all supported Python versions, you can use
[tox](https://tox.readthedocs.io/en/latest/).

All GitHub pull requests are automatically tested using travis and appveyor.
