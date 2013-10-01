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
AUTHOR_EMAIL = 'rarylson@gmail.com'
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
DIRECT_TEMPLATES = ['index', 'tags', 'categories', ]
GITHUB_URL = 'https://github.com/rarylson/gbzando'
DEFAULT_DATE_FORMAT = '%a, %d %b %Y'
TYPOGRIFY = True

# Default syntax highlight
MD_EXTENSIONS = ['codehilite(css_class=highlight,linenums=True)','extra']
DISQUS_SITENAME = "gbzando"

# Custom template vars
CREATIVE_COMMONS = True

# Plugins
PLUGIN_PATH = 'plugins'
PLUGINS = ['gravatar', 'assets', ]
WEBASSETS = False

# Static content
#STATIC_PATHS = [
#    'extra/robots.txt',
#]
#EXTRA_PATH_METADATA = {
#    'extra/robots.txt': {'path': 'robots.txt'},
#}

