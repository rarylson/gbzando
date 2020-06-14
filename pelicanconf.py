# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# Site
SITENAME = 'GBzando'
SITESUBTITLE = u'Programação, infraestrutura e redes na prática'
SITE_DESCRIPTION = (u'Blog de programação, infraestrutura e redes na prática. '
        'Artigos sobre Python, C, Shell Script (Bash), Linux, servidores web, email, redes '
        'e muito mais.')
SITE_KEYWORDS = u'programação, computação, servidores, linux, python, shell, bash, redes, gbzando'
SITEURL = ''
TIMEZONE = 'America/Sao_Paulo'
DEFAULT_LANG = 'pt_BR'
LOCALE = 'pt_BR.UTF-8'
AUTHOR = 'Rarylson Freitas'
AUTHOR_EMAIL = 'rarylson@gmail.com'

# Disable feed generation when developing
# Ignore also the borring warning that appears in development mode.
import logging
LOG_FILTER = [(logging.WARN, 'Feeds generated without SITEURL set properly may not be valid'), ]
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None

# Social widget
SOCIAL = (
    ('LinkedIn', 'https://www.linkedin.com/in/rarylson/'),
    ('GitHub', 'https://github.com/rarylson'),
    ('Stack Overflow', 'http://stackoverflow.com/users/2530295/rarylson-freitas'),
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
PAGINATION_PATTERNS = (
    (1, '{base_name}/', '{base_name}/index.html'),
    (2, '{base_name}/page/{number}/', '{base_name}/page/{number}/index.html'),
)
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
DISPLAY_PAGES_ON_MENU = True

# Markdown extensions
# See: http://pythonhosted.org/Markdown/extensions/code_hilite.html
#      http://pythonhosted.org/Markdown/extensions/toc.html
#      http://pythonhosted.org/Markdown/extensions/attr_list.html
MARKDOWN = {
    'extension_configs': {
        'markdown.extensions.codehilite': {
            'css_class': 'highlight',
            'guess_lang': False
        },
        'markdown.extensions.extra': {},
        'markdown.extensions.meta': {},
        'markdown.extensions.toc': {'anchorlink': True},
        'markdown.extensions.attr_list': {},
    },
}
 
# Vars for Notmyidea GBzando template
CREATIVE_COMMONS = True

# Plugins
PLUGIN_PATHS = ['pelican-plugins', ]
PLUGINS = ['assets', 'tag_cloud', ]
WEBASSETS = False

# Static content
STATIC_PATHS = ['images', ]
EXTRA_PATH_METADATA = {}
