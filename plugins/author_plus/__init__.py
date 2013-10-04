from author_plus import add_author_plus
from pelican import signals

def register():
    signals.article_generator_context.connect(add_author_plus)
