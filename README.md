GBZando
=======

A nerd blog (pt-BR) about programming and infrastructure.


What is it?
-----------

It's a brazilian blog, written in portuguese, about programming and IT infrastructure. It intends to use a practical aproach.


How it works?
-------------

It's made in [Pelican](https://github.com/getpelican/pelican/), a static site generator written in Python. Articles are written in [Markdown](http://daringfireball.net/projects/markdown/) and themes are written in [Jinja2](http://jinja.pocoo.org).


Install
-------

In Ubuntu:

    apt-get install python python-pip
    pip install pelican
    pip install fabric
    pip instamm markdown cssmin webassets requests six tipogrify
    apt-get install optipng libjpeg8

How to
------

Build static content and serve in a simple python webserver:

    pelican content -o output -s pelicanconf.py
    cd output && python -m SimpleHTTPServer

You can use the dev server to do this:

    ./develop_server.sh start 

The fabfile contains a specific deploy method for GBzando. You can use the `prod_config.py.sample` to generate your `prod_config.py` file:

    # deploy in homolog
    fab publish_homolog
    # deploy
    fab publish

License
-------

This blog is open and free (both source code and articles content).

The blog source code is licensed under [BSD 2 Clause License](LICENSE). The articles content are written under [Creative Commons Attribution-NonCommercialLicense](http://creativecommons.org/licenses/by-nc/3.0/deed.en_US).

So, you're free to fork this project, or to reuse the articles quoting the original author and don't using them for commercial purposes.

TODO
----

- Author plus: Getting author email from authors page metadata (not from article metadata)
- Author plus: Page rendered using the pelican readers (not only a markeddown reader)
- Use i18n in template (http://docs.python.org/2/library/i18n.html)
- Neighbors: https://github.com/getpelican/pelican-plugins/tree/master/neighbors
- http://blog.leonardfactory.com/2013/05/05/code-fenced-blocks-pygments-and-line-numbers-with-jekyll/
- http://pythonhosted.org/Markdown/extensions/tables.html
- http://packages.python.org/Markdown/extensions/admonition.html
- Add all the source code and tests in a .tar.gz version for download. Make a plugin for this too.
- https://github.com/favalex/python-asciimathml
