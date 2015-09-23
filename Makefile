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

FTP_HOST=localhost
FTP_USER=anonymous
FTP_TARGET_DIR=/

SSH_HOST=localhost
SSH_PORT=22
SSH_USER=root
SSH_TARGET_DIR=/var/www

S3_BUCKET=my_s3_bucket

CLOUDFILES_USERNAME=my_rackspace_username
CLOUDFILES_API_KEY=my_rackspace_api_key
CLOUDFILES_CONTAINER=my_cloudfiles_container

DROPBOX_DIR=~/Dropbox/Public/

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
	@echo '   make ssh_upload                  upload the web site via SSH         '
	@echo '   make rsync_upload                upload the web site via rsync+ssh   '
	@echo '   make dropbox_upload              upload the web site via Dropbox     '
	@echo '   make ftp_upload                  upload the web site via FTP         '
	@echo '   make s3_upload                   upload the web site via S3          '
	@echo '   make cf_upload                   upload the web site via Cloud Files '
	@echo '   make github                      upload the web site via gh-pages    '
	@echo
	@echo 'Set the DEBUG variable to 1 to enable debugging, e.g. make DEBUG=1 html.'
	@echo


# Development tasks

clean_html:
	[ ! -d $(OUTPUTDIR) ] || rm -rf $(OUTPUTDIR)

clean_html_deploy:
	[ ! -d $(DEPLOYDIR) ] || rm -rf $(DEPLOYDIR)

clean: clean_html clean_html_deploy
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

ssh_upload: publish
	scp -P $(SSH_PORT) -r $(DEPLOYDIR)/* $(SSH_USER)@$(SSH_HOST):$(SSH_TARGET_DIR)

rsync_upload: publish
	rsync -e "ssh -p $(SSH_PORT)" -P -rvz --delete $(DEPLOYDIR)/ $(SSH_USER)@$(SSH_HOST):$(SSH_TARGET_DIR) --cvs-exclude

dropbox_upload: publish
	cp -r $(DEPLOYDIR)/* $(DROPBOX_DIR)

ftp_upload: publish
	lftp ftp://$(FTP_USER)@$(FTP_HOST) -e "mirror -R $(DEPLOYDIR) $(FTP_TARGET_DIR) ; quit"

s3_upload: publish
	s3cmd sync $(DEPLOYDIR)/ s3://$(S3_BUCKET) --acl-public --delete-removed

cf_upload: publish
	cd $(DEPLOYDIR) && swift -v -A https://auth.api.rackspacecloud.com/v1.0 -U $(CLOUDFILES_USERNAME) -K $(CLOUDFILES_API_KEY) upload -c $(CLOUDFILES_CONTAINER) .

github: publish
	ghp-import $(DEPLOYDIR)
	git push origin gh-pages


.PHONY: html help clean clean_deploy clean_all regenerate serve devserver publish publish_homolog ssh_upload rsync_upload dropbox_upload ftp_upload s3_upload cf_upload github
