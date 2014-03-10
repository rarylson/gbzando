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

# Input / output
PATH = 'content/'
OUTPUT_PATH = 'output/'
# URLs - Using permlinks without html
ARTICLE_URL = "{slug}/"
ARTICLE_SAVE_AS = "{slug}/index.html"
PAGE_URL = "pages/{slug}/"
PAGE_SAVE_AS = "pages/{slug}/index.html"
CATEGORY_URL = "category/{slug}/"
CATEGORY_SAVE_AS = "category/{slug}/index.html"
TAG_URL = "tag/{slug}/"
TAG_SAVE_AS = "tag/{slug}/index.html"
AUTHOR_URL = "author/{slug}/"
AUTHOR_SAVE_AS = "author/{slug}/index.html"
# With those new configs, pay attention in your article slugs. They can't
# be 'tags', for example
TAGS_URL = "tags/"
TAGS_SAVE_AS = "tags/index.html"
AUTHORS_URL = "authors/"
AUTHORS_SAVE_AS = "authors/index.html"
# Don't generate archieve pages
DIRECT_TEMPLATES = ['index', 'tags', 'categories', 'authors', ]
# Don't process 'pages' and 'authors' as articles
ARTICLE_EXCLUDES = ['pages', 'authors', ]
# Custom menu item URL
MENUITEMS = [('Sobre o autor', '/author/rarylson-freitas/'), ]

# Vars to template
THEME = 'themes/notmyidea_gbzando'
DEFAULT_PAGINATION = 10
USE_FOLDER_AS_CATEGORY = False
GITHUB_URL = 'https://github.com/rarylson/gbzando'
DEFAULT_DATE_FORMAT = '%a, %d %b %Y'
TYPOGRIFY = True
DISQUS_SITENAME = "gbzando"
DEBUG_DISQUS = True

# Markdown extensions
# See: http://pythonhosted.org/Markdown/extensions/code_hilite.html#usage
#      http://pythonhosted.org/Markdown/extensions/toc.html#usage
MD_EXTENSIONS = ['codehilite(css_class=highlight,guess_lang=False)', 
        'extra', 'toc(anchorlink=True)', ]
 
# Custom template vars
CREATIVE_COMMONS = True

# Plugins
PLUGIN_PATH = 'plugins'
PLUGINS = ['gravatar_plus', 'assets', 'author_plus']
WEBASSETS = False
AUTHOR_PLUS_DIR = 'authors'

# Static content
STATIC_PATHS = ['images', ]
EXTRA_PATH_METADATA = {}
