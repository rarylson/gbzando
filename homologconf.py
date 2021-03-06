from __future__ import unicode_literals

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

# Homolog will use publishconf as base
from publishconf import *

# Disqus must to have tested in a homolog server with a trusted domain
# See: http://help.disqus.com/customer/portal/articles/472098
#      http://help.disqus.com/customer/portal/articles/472007-i-m-receiving-the- \
#          message-%22we-were-unable-to-load-disqus-%22
SITEURL = 'http://homolog.gbzando.com.br'
DISQUSURL = 'http://www.gbzando.com.br'
DEBUG_DISQUS = True
