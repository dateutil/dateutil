#
# Simple wrapper for setup.py script
#

DESTDIR=/
PYTHON=python

prefix=/usr
bindir=$(prefix)/bin

all:
	$(PYTHON) setup.py build

install:
	$(PYTHON) setup.py install \
		--root=$(DESTDIR) \
		--prefix=$(prefix) \
		--install-scripts=$(bindir)

dist:
	$(PYTHON) setup.py sdist

rpm:
	$(PYTHON) setup.py bdist_rpm

