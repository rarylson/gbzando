import os.path
from pelican.utils import slugify
import markdown

from logging import debug

"""
Author plus plugin for Pelican

This plugin add the content of AUTHOR_PLUS_DIR/{author.url} to the ``author_plus`` variable.
"""

#TODO Change the parse behaviour to Pelican readers

AUTHOR_PLUS = {}

def add_author_plus(generator, metadata):

    # Get author if it is not defined on metadata
    if 'author' not in metadata.keys() \
        and 'AUTHOR' in generator.settings.keys():
            metadata['author'] = generator.settings['AUTHOR']
    
    # Then add author content
    if 'author' in metadata.keys() and 'AUTHOR_PLUS_DIR' in generator.settings.keys():
        author_plus_short = slugify(metadata['author'])
        # Trying to get from cache
        author_plus = AUTHOR_PLUS.get(author_plus_short, None)
        # Not in cache
        if not author_plus:
            author_plus_url = "{}/{}.html".format(generator.settings['AUTHOR_PLUS_DIR'], author_plus_short)
            author_plus_url = os.path.abspath(os.path.expanduser(author_plus_url))
            debug("AUTHOR_PLUS: trying to get content from " + author_plus_url)
            # Get content parsing the MarkDown file
            if os.path.isfile(author_plus_url):
                author_plus = markdown.markdownFromFile(author_plus_url)
                with open (author_plus_url, "r") as author_file:
                    author_plus_md = author_file.read().decode('utf-8')
                    author_plus = markdown.markdown(author_plus_md)
                # Caching result
                AUTHOR_PLUS.update({author_plus_short:author_plus})
                debug(u"AUTHOR_PLUS: content about {} generated".format(author_plus_short))
            else:
                debug("AUTHOR_PLUS: file not found " + author_plus_url)
        metadata["author_plus"] = author_plus
