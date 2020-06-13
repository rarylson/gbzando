# Makefile for GBzando
# Based on the default pelican Makefile (`pelican-quickstart`), but improved.

PY=python
PELICAN=pelican
PELICANOPTS=

BASEDIR=$(CURDIR)
INPUTDIR=$(BASEDIR)/content
OUTPUTDIR=$(BASEDIR)/output
DEPLOYDIR=$(BASEDIR)/deploy
CONFFILE=$(BASEDIR)/pelicanconf.py
PUBLISHCONF=$(BASEDIR)/publishconf.py
HOMOLOGCONF=$(BASEDIR)/homologconf.py

DEBUG ?= 0
ifeq ($(DEBUG), 1)
	PELICANOPTS += -D
endif

all: help

help:
	@echo 'Makefile for GBzando (a pelican Web site)                               '
	@echo
	@echo 'Usage:                                                                  '
	@echo
	@echo '   make clean_html                  remove the generated files          '
	@echo '   make clean_deploy                remove files generated for deploy   '
	@echo '   make clean                       remove all temporary files          '
	@echo '   make html                        (re)generate the web site           '
	@echo '   make regenerate                  regenerate files upon modification  '
	@echo '   make serve [PORT=8000]           serve site at http://localhost:8000 '
	@echo '   make devserver [PORT=8000]       start/restart develop_server.sh     '
	@echo '   make stopserver                  stop local server                   '
	@echo '   make html_publish                generate using production settings  '
	@echo '   make html_publish_homolog        generate using homolog settings     '
	@echo
	@echo 'Set the DEBUG variable to 1 to enable debugging, e.g. make DEBUG=1 html.'
	@echo


# Development tasks

clean_html:
	[ ! -d $(OUTPUTDIR) ] || rm -rf $(OUTPUTDIR)

clean_deploy:
	[ ! -d $(DEPLOYDIR) ] || rm -rf $(DEPLOYDIR)

clean: clean_html clean_deploy
	find $(BASEDIR) -name \*.pyc -delete

html:
	$(PELICAN) $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)

regenerate:
	$(PELICAN) -r $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)

serve:
ifdef PORT
	cd $(OUTPUTDIR) && $(PY) -m pelican.server $(PORT)
else
	cd $(OUTPUTDIR) && $(PY) -m pelican.server
endif

devserver:
ifdef PORT
	$(BASEDIR)/develop_server.sh restart $(PORT)
else
	$(BASEDIR)/develop_server.sh restart
endif

stopserver:
	kill -9 `cat pelican.pid`
	kill -9 `cat srv.pid`
	@echo 'Stopped Pelican and SimpleHTTPServer processes running in background.'


# Deploy tasks

html_publish:
	$(PELICAN) $(INPUTDIR) -o $(DEPLOYDIR) -s $(PUBLISHCONF) $(PELICANOPTS)

html_publish_homolog:
	$(PELICAN) $(INPUTDIR) -o $(DEPLOYDIR) -s $(HOMOLOGCONF) $(PELICANOPTS)


.PHONY: html help clean clean_deploy clean_all regenerate serve devserver
