
PYPACKAGE=torweb
PY_SOURCES=$(shell find $(PYPACKAGE)/ -type f -name '*.py')
STATIC_DIR=app

VERSION=$(shell python setup.py --version)

JADE_SRC=$(wildcard $(STATIC_DIR)/*.jade) $(wildcard $(STATIC_DIR)/partials/*.jade)
HTML=${JADE_SRC:%.jade=%.html}

NPM := $(shell which npm)
GPG := $(shell which gpg)

ifeq ($(NPM),)
  $(error NPM not found)
endif

ifeq ($(GPG),)
  $(error GnuPG not found)
endif

VENV_DIR:=venv

# NPM packages binary folder
NODE_BIN := node_modules/.bin/
NPM_TARGET := node_modules/.installed

PIP_SOURCE:=requirements.txt
PIP_DEV_SOURCE:=dev-requirements.txt
PIP_DOC_SOURCE:=doc-requirements.txt

PYTHON_PACKAGES:=$(VENV_DIR)/.$(PIP_SOURCE)
PYTHON_DEV_PACKAGES:=$(VENV_DIR)/.$(PIP_DEV_SOURCE)
PYTHON_DOC_PACKAGES:=$(VENV_DIR)/.$(PIP_DOC_SOURCE)

PYLINT:=python -m pylint 

PIP := pip

SETUP_PY=setup.py
DIST_FOLDER        := dist
BDIST_WHEEL        := $(DIST_FOLDER)/${PYPACKAGE}-$(VERSION)-py2-none-any.whl
BDIST_WHEEL_SIGNED := ${BDIST_WHEEL}.asc
SDIST              := $(DIST_FOLDER)/${PYPACKAGE}-$(VERSION).tar.gz
SDIST_SIGNED       := $(SDIST).asc
ifndef PRODUCTION
	JADE_ARGS=--pretty
endif

JADE=$(NODE_BIN)/jade $(JADE_ARGS)

BOWER=$(NODE_BIN)/bower --allow-root  --config.interactive=false


BOWER_COMPONENTS=torweb/app/components/.installed
BOWER_SOURCE=bower.json


PYTHON=python

SPHINXBUILD="${PYTHON} -m sphinx"
export SPHINXBUILD

GIT_HOOK_DIR=.git/hooks
GIT_PRECOMMIT_HOOK=$(GIT_HOOK_DIR)/pre-commit

.PHONY: all
all: $(HTML) $(BOWER_COMPONENTS) $(PYTHON_PACKAGES)

# Print version
.PHONY: _version
_version:
	@echo ${VERSION}

.PHONY: dev_requirements
dev_requirements: $(NPM_TARGET) $(PYTHON_PACKAGES) $(PYTHON_DEV_PACKAGES)

.PHONY: html
html: $(HTML)
# Render HTML
%.html: $(NPM_TARGET) %.jade
	$(JADE) $^


.PHONY: doc
doc: $(PYTHON_DOC_PACKAGES)
	$(MAKE) -C doc/ html

open-doc: doc
	firefox doc/_build/html/index.html

# Bower components
.PHONY: components
components: $(BOWER_COMPONENTS)

$(BOWER_COMPONENTS): $(NPM_TARGET) $(BOWER_SOURCE)
	$(BOWER) install
	touch $@

# Node modules
.PHONY: node_modules
node_modules: $(NPM_TARGET)

$(NPM_TARGET):
	$(NPM) install
	touch $@

# Python dependencies
.PHONY: python_packages python_dev_packages
python_packages: $(PYTHON_PACKAGES)
python_dev_packages: $(PYTHON_DEV_PACKAGES)

.PHONY: force_python_dev_packages
force_python_dev_packages: $(PIP_DEV_SOURCE)
	touch $^
	$(MAKE) python_dev_packages

venv/.%: %
	pip install -r $^
	mkdir -p $(@D)
	touch $@

# cleanup
.PHONY: clean
clean: clean_html clean_npm clean_components
	rm -rf .tox 

.PHONY: clean_html
clean_html:
	rm -f $(HTML)

.PHONY: clean_components
clean_components:
	rm -rf $(dir $(BOWER_COMPONENTS))

.PHONY: clean_npm
clean_npm:
	rm -rf $(dir $(NPM_TARGET))


.PHONY: test
test: pep8 trial_test

.PHONY: trial_test
trial_test:
	trial --reporter=text test

.PHONY: githook
githook: $(GIT_PRECOMMIT_HOOK)
$(GIT_PRECOMMIT_HOOK):
	echo "#/bin/bash">$@
	echo "make precommit_test">>$@
	chmod +x $@

.PHONY: clean_githook
clean_githook:
	rm -f $(GIT_PRECOMMIT_HOOK)

precommit_test: pep8

.PHONY: proper
proper: clean
	rm -rf $(DIST_FOLDER)

.phony: bdist_wheel
bdist_wheel: $(BDIST_WHEEL)
bdist_wheel_signed: $(BDIST_WHEEL_SIGNED)

.PHONY: sdist sdist_signed
sdist: $(SDIST)
sdist_signed: $(SDIST_SIGNED)


$(SDIST):
	$(PYTHON) $(SETUP_PY) sdist

$(BDIST_WHEEL): $(SETUP_PY) $(PYTHON_DEV_PACKAGES)
	$(PYTHON) $(SETUP_PY) bdist_wheel


%.asc: %
	$(GPG) --verify $@ || $(GPG) --no-version --detach-sign --armor --local-user l34k@bk.ru $<

.PHONY: pep8
pep8: $(PY_SOURCES) $(PYTHON_DEV_PACKAGES)
	@ pep8 $^

.PHONY: pylint
pylint: $(PY_SOURCES) $(PYTHON_DEV_PACKAGES)
	$(PYLINT) $(PYPACKAGE)
	
.PHONY: pyflakes
pyflakes: $(PY_SOURCES) $(PYTHON_DEV_PACKAGES)
	pyflakes $(PYPACKAGE)

