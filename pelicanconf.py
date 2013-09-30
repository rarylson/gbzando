#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# Site
SITENAME = u'GBzando'
SITEURL = ''
TIMEZONE = 'America/Sao_Paulo'
DEFAULT_LANG = 'pt_BR'
LOCALE = 'pt_BR.UTF-8'

# Default author and category
AUTHOR = u'Rarylson Freitas'
DEFAULT_CATEGORY = 'Geral'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS = (
            ('Vialink', 'http://www.vialink.com.br'),
            ('Aprenda Python', 'http://docs.python.org/2/tutorial/'),
            ('Aprenda Linux', 'http://www.linux.com/learn/tutorials'),
        )
# Social widget
SOCIAL = (
            ('Facebook', 'https://facebook.com/rarylson'),
         )

# Vars to template
THEME = 'themes/notmyidea_gbzando'
DEFAULT_PAGINATION = 10
USE_FOLDER_AS_CATEGORY = False
GITHUB_URL = 'https://github.com/rarylson/gbzando'

# Custom template vars
CREATIVE_COMMONS = True

# Static content
#STATIC_PATHS = [
#    'extra/robots.txt',
#]
#EXTRA_PATH_METADATA = {
#    'extra/robots.txt': {'path': 'robots.txt'},
#}

