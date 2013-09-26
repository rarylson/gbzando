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
    pip install pelican markdown
    # optional module for deploy
    pip install fabric


How to
------

Build static content and serve in a simple python webserver:

    pelican content -s settings.py
    cd output && python -m SimpleHTTPServer

To automate this task using `make`:

    # generate the first time
    make html
    # regenerate (using in the following times)
    make regenerate
    # serve
    make serve


License
-------

This blog is open and free (both source code and articles content).

The blog source code is licensed under [BSD 2 Clause License](LICENSE). The articles content are written under [Creative Commons Attribution-NonCommercialLicense](http://creativecommons.org/licenses/by-nc/3.0/deed.en_US).

So, you're free to fork this project, or to reuse the articles quoting the original author and don't using them for commercial purposes.
