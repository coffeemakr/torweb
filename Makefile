
STATIC_DIR=app

JADE_SRC=$(wildcard $(STATIC_DIR)/*.jade) $(wildcard $(STATIC_DIR)/partials/*.jade)
HTML=${JADE_SRC:%.jade=%.html}


JADE=node_modules/.bin/jade

.PHONY: all
all: $(HTML)

%.html: %.jade
	$(JADE) $<

.PHONY: clean clean_html
clean: clean_html

clean_html:
	rm -f $(HTML)
