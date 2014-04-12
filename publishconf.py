#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

# Production changes
SITEURL = 'http://www.gbzando.com.br'
RELATIVE_URLS = False
DEBUG_DISQUS = False
FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/%s.atom.xml'
DELETE_OUTPUT_DIRECTORY = True 
WITH_FUTURE_DATES = False   # Don't publish future date articles
IGNORE_FILES = ['.*.swp', ] # Don't process vim swap files

# Adding production plugins
PLUGINS.extend(['sitemap', 'gzip_cache', 'optimize_images', ])

# Plugin configurations
WEBASSETS = True
WEBASSETS_VERSION_IN_FILENAME = True    # Custom template var
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
# Custom template vars
GOOGLE_ANALYTICS_UNIVERSAL = True
GOOGLE_ANALYTICS_DISPLAYFEATURES = True

# Static files
STATIC_PATHS.extend([
    'extra/robots.txt',
])
EXTRA_PATH_METADATA.update({
    'extra/robots.txt': {'path': 'robots.txt'},
})

