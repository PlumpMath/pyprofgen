# $Id$

# You MUST not leave trailing '/' in PREFIX.
ifndef PREFIX
	PREFIX=/usr/local
endif

INSTALL=/usr/bin/install
# DO NOT TOUCH LINES BELOW --------------------------------------------------


PPG_BIN_DIR = $(PREFIX)/bin
PPG_LIB_DIR = $(PREFIX)/share/pyprofgen-0.2

ESC_PREFIX=$(shell echo $(PREFIX) | sed -e 's/\//\\\//g')

all: pyprofgen.py
	echo $(ESC_PREFIX)
	sed -e 's/^PREFIX = .*$$/PREFIX = \"$(ESC_PREFIX)\"/' \
		pyprofgen.py > pyprofgen
	chmod +x pyprofgen

install:
	$(INSTALL) -d $(PPG_BIN_DIR)
	$(INSTALL) -d $(PPG_LIB_DIR)
	$(INSTALL) pyprofgen $(PPG_BIN_DIR)
	$(INSTALL) lib/pyprofgen.css $(PPG_LIB_DIR)
	$(INSTALL) lib/pyprofgen.png $(PPG_LIB_DIR)

clean:
	rm -f pyprofgen
