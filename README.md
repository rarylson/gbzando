GBzando
=======

A blog about programming, infrastructure and networking.

This project contains both the source code (theme and plugins) and the blog content (articles).

It is a brasilian blog (`pt_BR`). Most of the source code is written in English, and the blog content is written in Portuguese.

How it works?
-------------

This project is developed using [Pelican](https://github.com/getpelican/pelican/), a static site generator written in Python.

Some extra plugins are also developed using Python.

Articles are written in [Markdown](http://daringfireball.net/projects/markdown/). Themes are written in [Jinja2](http://jinja.pocoo.org).

Install
-------

In Ubuntu:

```sh
pip install -r requirements.txt
apt-get install optipng libjpeg8
```

Usage
-----

To run the local development server:

```sh
make devserver
```

To stop de local development server:

```sh
make stopserver
```

To publish the blog:

```sh
# Generate config file
# Edit 'deploy_config.py' after.
cp deploy_config.py.sample deploy_config.py
# Publish in homolog
fab publish_homolog
# Publish
fab publish
```

License
-------

The software is released under the [Revised BSD License](LICENSE).

The articles are released under the [Creative Commons Attribution-NonCommercial License](http://creativecommons.org/licenses/by-nc/3.0/deed.en_US).

TODO
----

- Use i18n in template
	- See: http://docs.python.org/2/library/i18n.html
- Neighbors
	- See: https://github.com/getpelican/pelican-plugins/tree/master/neighbors
- Better use of Pygments
	- See: http://blog.leonardfactory.com/2013/05/05/code-fenced-blocks-pygments-and-line-numbers-with-jekyll/
- Admonition:
	- See: http://packages.python.org/Markdown/extensions/admonition.html
