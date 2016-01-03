
PYPACKAGE=torweb
PY_SOURCES=$(shell find $(PYPACKAGE)/ -type f -name '*.py')
STATIC_DIR=app

JADE_SRC=$(wildcard $(STATIC_DIR)/*.jade) $(wildcard $(STATIC_DIR)/partials/*.jade)
HTML=${JADE_SRC:%.jade=%.html}

NPM := npm

VENV_DIR:=venv

# NPM packages binary folder
NODE_BIN := node_modules/.bin/
NPM_TARGET := node_modules/.installed

PIP_SOURCE:=requirements.txt
PIP_DEV_SOURCE:=dev-requirements.txt


PYTHON_PACKAGES:=$(VENV_DIR)/.$(PIP_SOURCE)
PYTHON_DEV_PACKAGES:=$(VENV_DIR)/.$(PIP_DEV_SOURCE)

PYLINT:=python -m pylint 

PIP := pip


ifndef PRODUCTION
	JADE_ARGS=--pretty
endif

JADE=$(NODE_BIN)/jade $(JADE_ARGS)

BOWER=$(NODE_BIN)/bower --allow-root  --config.interactive=false


BOWER_COMPONENTS=app/components/.installed
BOWER_SOURCE=bower.json


SPHINXBUILD="python -m sphinx"
export SPHINXBUILD

GIT_HOOK_DIR=.git/hooks
GIT_PRECOMMIT_HOOK=$(GIT_HOOK_DIR)/pre-commit

.PHONY: all
all: $(HTML) $(BOWER_COMPONENTS) $(PYTHON_PACKAGES)

.PHONY: dev_requirements
dev_requirements: $(NPM_TARGET) $(PYTHON_PACKAGES) $(PYTHON_DEV_PACKAGES)

.PHONY: html
html: $(HTML)
# Render HTML
%.html: $(NPM_TARGET) %.jade
	$(JADE) $^


.PHONY: doc
doc:
	$(MAKE) -C doc/ html

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

.PHONY: pep8
pep8: $(PY_SOURCES) $(PYTHON_DEV_PACKAGES)
	@ pep8 $^

.PHONY: pylint
pylint: $(PY_SOURCES) $(PYTHON_DEV_PACKAGES)
	$(PYLINT) $(PYPACKAGE)
	$(PYLINT) $(PYPACKAGE)
	$(PYLINT) $(PYPACKAGE)
	$(PYLINT) $(PYPACKAGE)
	$(PYLINT) $(PYPACKAGE)
	$(PYLINT) $(PYPACKAGE)
	$(PYLINT) $(PYPACKAGE)
	$(PYLINT) $(PYPACKAGE)
	
.PHONY: pyflakes
pyflakes: $(PY_SOURCES) $(PYTHON_DEV_PACKAGES)
	pyflakes $(PYPACKAGE)

