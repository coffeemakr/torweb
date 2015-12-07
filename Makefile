
STATIC_DIR=app

JADE_SRC=$(wildcard $(STATIC_DIR)/*.jade) $(wildcard $(STATIC_DIR)/partials/*.jade)
HTML=${JADE_SRC:%.jade=%.html}

ifndef PRODUCTION
	JADE_ARGS=--pretty	
endif

JADE=node_modules/.bin/jade $(JADE_ARGS)



.PHONY: all
all: $(HTML)

%.html: %.jade
	$(JADE) $<

.PHONY: clean clean_html
clean: clean_html

clean_html:
	rm -f $(HTML)
