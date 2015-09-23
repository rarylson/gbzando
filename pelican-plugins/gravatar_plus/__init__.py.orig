from gravatar_plus import add_gravatar
from pelican import signals

def register():
    signals.article_generate_context.connect(add_gravatar)