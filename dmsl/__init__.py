# -*- coding: utf-8 -*-
"""
import dmsl
dmsl._sandbox._open.template_dir = 'omg/seriously'
dmsl.parse('index.dmsl', {'content': 'Hello World!'})
"""
__version__ = '0.2'
from _parse import Template
import _sandbox
from _sandbox import extensions

def set_template_dir(value):
    _sandbox._open.template_dir = value

