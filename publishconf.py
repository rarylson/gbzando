#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

# Production changes
SITEURL = 'https://www.gbzando.com.br'
RELATIVE_URLS = False
DEBUG_DISQUS = False
FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/%s.atom.xml'
DELETE_OUTPUT_DIRECTORY = True 
WITH_FUTURE_DATES = False   # Don't publish future date articles

# Adding production plugins
PLUGINS.extend(['sitemap', 'gzip_cache', 'optimize_images', ])

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

# Vars for Notmyidea GBzando template
WEBASSETS_VERSION_IN_FILENAME = True
GOOGLE_ANALYTICS_UNIVERSAL = True
GOOGLE_ANALYTICS_DISPLAYFEATURES = True
GOOGLE_ANALYTICS_DOMAIN = "gbzando.com.br"

# Robots file
# Using tip from Pelican Wiki - Tips-n-Tricks - Generate sitemap.xml
# See: https://github.com/getpelican/pelican/wiki/Tips-n-Tricks#generate-sitemapxml
DIRECT_TEMPLATES.extend(['robots'])
ROBOTS_SAVE_AS = 'robots.txt'
