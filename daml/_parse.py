#! /usr/bin/env python
# -*- coding: utf-8 -*-
from _pre_parse import _pre_parse
import _py_parse
#from _doc_parse import _doc_parse
from _cdoc import _doc_parse
from _build import _build
import _sandbox
from lxml import etree
from time import time
import codecs

def _post(s):
    return '<!DOCTYPE html>'+s.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')

def parse(_f, context={}):
    #f = codecs.open(_f, 'r', encoding='utf-8').read().splitlines()
    f = _sandbox._open(_f).read().splitlines()
    _py_parse.sandbox = _sandbox.new()
    _py_parse.sandbox.update(_py_parse.ext)
    _py_parse.sandbox.update(context)
    f = _pre_parse(f)
    f = _py_parse._py_parse(f, _f)
    f = _doc_parse(f)
    #f = _build(f)

    return _post(etree.tostring(f))

class Template(object):
    def __init__(self, f):
        import codecs
        f = codecs.open(f, encoding='utf-8').readlines()
        self.p = _py_parse.PyParse(_pre_parse(f))

    def render(self, context):
        a = time()
        _py_parse.sandbox = self.p.sandbox
        _py_parse.sandbox.update(context)
        print 'init', time()-a
        a = time()
        f = _py_parse._py_parse(self.p.doc[:])
        print 'py  ', time()-a
        a = time()
        f = _doc_parse(f)
        print 'doc ', time()-a

        return _post(etree.tostring(f))

if __name__ == '__main__':
    import sys
    import codecs
    from time import time
    _f = sys.argv[1]
    t = sys.argv[2]

    #f = codecs.open(_f, 'r', encoding='utf-8').read().splitlines()
    if t is 'y':
        times=[]
        for x in range(100):
            a = time()
            r = parse(_f)
            times.append(time()-a)
        print min(times)
    else:
        print parse(_f)


