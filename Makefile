
PYPACKAGE=torweb
PY_SOURCES=$(shell find $(PYPACKAGE)/ -type f -name '*.py')
STATIC_DIR=app

JADE_SRC=$(wildcard $(STATIC_DIR)/*.jade) $(wildcard $(STATIC_DIR)/partials/*.jade)
HTML=${JADE_SRC:%.jade=%.html}

NPM := npm

# NPM packages binary folder
NODE_BIN := node_modules/.bin/
NPM_TARGET := node_modules/.installed

PIP_TARGET:=venv/.pip_installed
PIP_SOURCE:=requirements.txt
PIP := pip

ifndef PRODUCTION
	JADE_ARGS=--pretty
endif

JADE=$(NODE_BIN)/jade $(JADE_ARGS)

BOWER=$(NODE_BIN)/bower --allow-root  --config.interactive=false


BOWER_TARGET=app/components/.installed
BOWER_SOURCE=bower.json


.PHONY: all
all: $(HTML) dev_requirements

.PHONY: dev_requirements
dev_requirements: $(BOWER_TARGET) $(PIP_TARGET)

# Render HTML
%.html: $(NPM_TARGET) %.jade
	$(JADE) $^


# Bower components
.PHONY: components
components: $(BOWER_TARGET)

$(BOWER_TARGET): $(NPM_TARGET) $(BOWER_SOURCE)
	$(BOWER) install
	touch $@

# Node modules
.PHONY: node_modules
node_modules: $(NPM_TARGET)

$(NPM_TARGET):
	$(NPM) install
	touch $@

# Python dependencies
.PHONY: python_packages
python_packages: $(PIP_TARGET)
$(PIP_TARGET): $(PIP_SOURCE) $(VENV)
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
	rm -rf $(dir $(BOWER_TARGET))

.PHONY: clean_npm
clean_npm:
	rm -rf $(dir $(NPM_TARGET))


.PHONY: test
test: pep8


.PHONY: pep8
pep8:
	pep8 $(PY_SOURCES)

