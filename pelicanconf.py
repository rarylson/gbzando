#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# Site
SITENAME = u'GBzando'
SITESUBTITLE = u'Programação e infraestrutura na prática'
SITE_DESCRIPTION = u'Blog de programação e infraestrutura na prática. Conceitos e problemas do dia-a-dia sobre Python, C, Perl, Shell Script, Servidores, Linux, Nginx e outros'
SITE_KEYWORDS = u'programação, computação, servidores, linux, python, shell, bash, nginx, gbzando'
SITEURL = ''
TIMEZONE = 'America/Sao_Paulo'
DEFAULT_LANG = 'pt_BR'
LOCALE = 'pt_BR.UTF-8'

# Default author and category
AUTHOR = u'Rarylson Freitas'
AUTHOR_EMAIL = u'rarylson@gmail.com'
DEFAULT_CATEGORY = u'Geral'

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
# Don't generate archieve pages
DIRECT_TEMPLATES = ['index', 'tags', 'categories', 'authors', ]
GITHUB_URL = 'https://github.com/rarylson/gbzando'
DEFAULT_DATE_FORMAT = '%a, %d %b %Y'
TYPOGRIFY = True
DISQUS_SITENAME = "gbzando"
DEBUG_DISQUS = True
MENUITEMS = [('Sobre o autor', '/author/rarylson-freitas.html'), ]
 
# Custom template vars
CREATIVE_COMMONS = True

# Plugins
PLUGIN_PATH = 'plugins'
PLUGINS = ['gravatar_plus', 'assets', 'author_plus']
WEBASSETS = False
AUTHOR_PLUS_DIR = 'author'

# Static content
#STATIC_PATHS = [
#    'extra/robots.txt',
#]
#EXTRA_PATH_METADATA = {
#    'extra/robots.txt': {'path': 'robots.txt'},
#}

