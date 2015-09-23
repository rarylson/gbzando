#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# Site
SITENAME = u'GBzando'
SITESUBTITLE = u'Programação, infraestrutura e redes na prática'
SITE_DESCRIPTION = (u'Blog de programação, infraestrutura e redes na prática. '
                    'Artigos sobre Python, C, Shell Script (Bash), Linux, servidores web, '
                    'email, redes, roteamento e muito mais.')
SITE_KEYWORDS = u'programação, computação, servidores, linux, python, shell, bash, redes, gbzando'
SITEURL = ''
TIMEZONE = 'America/Sao_Paulo'
DEFAULT_LANG = 'pt_BR'
LOCALE = 'pt_BR.UTF-8'
AUTHOR = u'Rarylson Freitas'
AUTHOR_EMAIL = u'rarylson@gmail.com'

# Disable feed generation when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None

# Blogroll
LINKS = (
            ('Vialink', 'http://www.vialink.com.br'),
            ('Aprenda Python', 'http://docs.python.org/2/tutorial/'),
            ('Aprenda Linux', 'http://www.linux.com/learn/tutorials'),
        )
# Social widget
SOCIAL = (
            ('Facebook', 'https://facebook.com/rarylson'),
            ('Stack Overflow', 'http://stackoverflow.com/users/2530295/rarylson-freitas'),
            ('GitHub', 'https://github.com/rarylson'),
         )

# Input / output
PATH = 'content/'
OUTPUT_PATH = 'output/'
# URLs - Using permlinks without html
ARTICLE_URL = "{slug}/"
ARTICLE_SAVE_AS = "{slug}/index.html"
PAGE_URL = "{slug}/"
PAGE_SAVE_AS = "{slug}/index.html"
CATEGORY_URL = "category/{slug}/"
CATEGORY_SAVE_AS = "category/{slug}/index.html"
TAG_URL = "tag/{slug}/"
TAG_SAVE_AS = "tag/{slug}/index.html"
TAGS_URL = "tags/"
TAGS_SAVE_AS = "tags/index.html"
# Don't generate archieve pages 
# At least, for now.
DIRECT_TEMPLATES = ['index', 'tags', 'categories', ]
# Don't process 'pages' as articles
ARTICLE_EXCLUDES = ['pages', ]

# Vars for template
THEME = 'themes/notmyidea_gbzando'
DEFAULT_PAGINATION = 10
USE_FOLDER_AS_CATEGORY = False
GITHUB_URL = 'https://github.com/rarylson/gbzando'
DEFAULT_DATE_FORMAT = '%a, %d %b %Y'
TYPOGRIFY = False   # It was confliting with others libraries
DISQUS_SITENAME = "gbzando"
DEBUG_DISQUS = True
TAG_CLOUD_STEPS = 4
TAG_CLOUD_MAX_ITEMS = 1000
TAG_CLOUD_SORTING = "alphabetically"

# Markdown extensions
# See: http://pythonhosted.org/Markdown/extensions/code_hilite.html#usage
#      http://pythonhosted.org/Markdown/extensions/toc.html#usage
MD_EXTENSIONS = ['codehilite(css_class=highlight, guess_lang=False)',
        'extra', 'toc(anchorlink=True)', ]
 
# Vars for Notmyidea GBzando template
CREATIVE_COMMONS = True

# Plugins
PLUGIN_PATHS = ['pelican-plugins', ]
PLUGINS = ['assets', 'tag_cloud', ]
WEBASSETS = False

# Static content
STATIC_PATHS = ['images', ]
EXTRA_PATH_METADATA = {}
