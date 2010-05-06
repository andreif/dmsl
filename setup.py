# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='DAML',
    version='0.1',
    author='Daniel Skinner',
    author_email='dasacc22@gmail.com',
    url='http://daml.dasa.cc',
    license = "MIT License",
    py_modules=['daml'],
    requires = ["lxml"],
    description='Python implementation of HAML, extended.',
    long_description = """\
Features CSS selectors and indention for declaring page layout. Embed
python in your documents such as functions, lambda's, variable declarations,
for loops, list comprehensions, etc, writing it just as you would normally.
Filters that are linked to python function calls. First use of this is a
Django-style "block" and "extends". Easy to write custom filters and functions.
Still under heavy development. Parses your documents extremely fast!
    """,
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Environment :: Web Environment",
        ],
    )