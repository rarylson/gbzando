#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

SITEURL = 'http://www.gbzando.com.br'
RELATIVE_URLS = False
DEBUG_DISQUS = False

FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/%s.atom.xml'

DELETE_OUTPUT_DIRECTORY = True 
# Don't publish future date articles
WITH_FUTURE_DATES = False
# Don't process vim swap files
IGNORE_FILES = ['.*.swp', ]

# Adding production plugins
PLUGINS.extend(['sitemap', 'gzip_cache', ])

# Plugin configurations
WEBASSETS = True
SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 1,
        'indexes': 0.4,
        'pages': 0.4
    },
    'changefreqs': {
        'articles': 'monthly',
        'indexes': 'daily',
        'pages': 'monthly'
    },
}

# Google Analytics
GOOGLE_ANALYTICS = "UA-44485503-1"

