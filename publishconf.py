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


FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/%s.atom.xml'

DELETE_OUTPUT_DIRECTORY = True 
# Don't publish future date articles
WITH_FUTURE_DATES = False
# Don't process vim swap files
IGNORE_FILES.extend(['.*.swp', ])

# Adding production plugins
PLUGINS.extend(['sitemap', 'gzip_cache', ])

# Plugin configurations
WEBASSETS = True
SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.5,
        'indexes': 0.5,
        'pages': 0.5
    },
    'changefreqs': {
        'articles': 'monthly',
        'indexes': 'daily',
        'pages': 'monthly'
    },
}

# Google Analytics
GOOGLE_ANALYTICS = "UA-44485503-1"

# Disqus must to have tested in a homolog server with a trusted domain
# See: http://help.disqus.com/customer/portal/articles/472098
#      http://help.disqus.com/customer/portal/articles/472007-i-m-receiving-the-message-%22we-were-unable-to-load-disqus-%22
