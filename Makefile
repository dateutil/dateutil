
PYTHON := python
SETUP_EXTRA_ARGS =

.PHONY: pytest
pytest:
	$(PYTHON) -m pytest

.PHONY: test
test: pytest

.PHONY: tox
tox:
	tox

.PHONY: fetch_tzmeta
fetch_tzmeta:
	curl -sO https://dateutil.github.io/tzdata/zonefile_metadata/zonefile_metadata.json

.PHONY: sdist
sdist:
	$(PYTHON) setup.py sdist

.PHONY: bdist_wheel
bdist_wheel:
	$(PYTHON) setup.py bdist_wheel

.PHONY: upload
upload:
	python setup.py register $(SETUP_EXTRA_ARGS)
	python setup.py sdist bdist upload $(SETUP_EXTRA_ARGS)

.PHONY: test-upload
test-upload: SETUP_EXTRA_ARGS = -r https://test.pypi.org/legacy/
test-upload: upload

.PHONY: release
release: test fetch_tzmeta sdist bdist_wheel

.PHONY: clean
clean:
	-rm -rf *.egg-info
	find . -name '*.pyc' -exec rm {} \;

.PHONY: clean_build
clean_build:
	-rm -rf *.egg-info build dist
