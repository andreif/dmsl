#! /usr/bin/env python
# -*- coding: utf-8 -*-

from collections import deque
from _pre_parse import _pre_parse
import _sandbox
from _sandbox import _open
from _cdoc import parse_ws, sub_str
from time import time
from mako import pyparser

def include(f):
    f = _open(f).readlines()
    f = _pre_parse(f)
    f = _py_parse(f)
    return f

class Block(list):
    def __init__(self, name, value):
        self._name = name
        self._value = value
        self._used = False

    def __iter__(self):
        b = sandbox['__blocks__'][self._name]
        if b._used is False:
            b._used = True
            return iter(sandbox['__blocks__'][self._name]._value)
        else:
            return iter(())

def block(s):
    s = s.splitlines()
    s = _pre_parse(s)
    s = _py_parse(s)
    b = Block(s[0], s[1:])
    sandbox['__blocks__'][s[0]] = b
    return b

ext = {'block': block, 'include': include}

sandbox = {}

DECLARATION = 0
OTHER = 1

def parse_cmd(s, _id, i):
    a = s.find('(')
    b = s.find('=')
    if b != -1 and (b < a or a == -1):
        s = s[1:]
    else:
        s = 'globals()["__{0}_{1}__"] = {2}'.format(_id, i, s[1:])

    if '{__i__}' in s:
        s = s.replace('{__i__}', '"__{0}_{1}__"'.format(_id, i), 1)

    return s

def _py_precompile(f):
    pass

def parse_inline(s):
    if ':' in s:
        a = s.index(':')
    else:
        return None
    if '(' in s:
        b = s.index('(')
    else:
        return None
    if ' ' in s[a:b] or a > b: # check a>b for attributes that have :
        return None

    c = s.index(')')+1
    return s[a+1:c]

class PyParse(object):
    def __init__(self, doc):
        self.doc = doc
        self._id = id(self.doc)

        self.sandbox = _sandbox.new()
        self.sandbox.update(ext)
        self.sandbox['include'] = self.include

        self.queue = deque()

        self.precompile()
        self._eval()
        self.update_doc()

    def include(self, f):
        f = _open(f).readlines()
        f = _pre_parse(f)
        f = PyParse(f)
        return f.doc

    def parse_cmd(self, i, s):
        _type = OTHER
        a = s.find('(')
        b = s.find('=')
        if b != -1 and (b < a or a == -1):
            s = s[1:]
            _type = DECLARATION
        else:
            s = 'globals()["__{0}_{1}__"] = {2}'.format(self._id, i, s[1:])

        if '{__i__}' in s:
            _type = OTHER
            s = s.replace('{__i__}', '"__{0}_{1}__"'.format(self._id, i), 1)

        return (i, u' '+s.replace('\n', '\n '), _type)

    def precompile(self):
        for i, line in enumerate(self.doc):
            ws, l = parse_ws(line)

            if l[0] == ':':
                parsed = self.parse_cmd(i, l)
                self.queue.append((-1, u'try:', OTHER))
                self.queue.append(parsed)
                self.queue.append((-1, u'except: pass', OTHER))
                continue

            if '{' in l:
                self.queue.append((-1, u'try:', OTHER))
                self.queue.append((i, u' '+u'globals()["__{0}_{1}__"] = fmt.format("""{2}""")'.format(self._id, i, l.replace('\n', '\n ')), OTHER))
                self.queue.append((-1, u'except: pass', OTHER))
                continue

            # look to see if :func() is embedded in line
            _inline = parse_inline(l)
            if _inline is None:
                continue
            else:
                self.queue.append((-1, 'try:', OTHER))
                self.queue.append((i, ' '+u'globals()["__{0}_{1}__"] = {2}'.format(self._id, i, _inline), OTHER))
                self.queue.append((-1, 'except: pass', OTHER))

    def _eval(self):
        py_str = '\n'.join([x[1] for x in self.queue])
        eval(compile('fmt.namespace=globals()\n'+py_str, '<string>', 'exec'), self.sandbox)

    def update_doc(self):
        offset = 0
        while self.queue:
            i, l, _type = self.queue.popleft()
            if _type == DECLARATION:
                self.doc.pop(i+offset)
                offset -= 1
                continue
            k = '__{0}_{1}__'.format(self._id, i)

            if k in self.sandbox:
                r = self.sandbox[k]

                if isinstance(r, list):
                    if isinstance(r[0], list):
                        r = [a for b in r for a in b]
                    tmp = self.doc.pop(i+offset).rstrip()
                    ws = tmp[:-len(tmp.lstrip())]
                    #ws, tmp = parse_ws(f.pop(i+offset))
                    r = [ws+x for x in r]
                    self.doc = self.doc[:i+offset] + r + self.doc[i+offset:]
                    offset += len(r)-1
                    '''
                    for x in r:
                        f.insert(i+offset, ws+x)
                        offset += 1
                    offset -= 1
                    '''
                else:
                    tmp = self.doc.pop(i+offset)

                    tmp2 = tmp.strip()
                    if tmp2[0] != '': #ugh
                        tmp3 = ':'+l.split('=')[1].strip() #really ugh
                        if tmp3[:4] != ':fmt': # oh geez
                            r = tmp2.replace(tmp3, r)

                    ws = tmp[:-len(tmp.lstrip())]
                    self.doc.insert(i+offset, ws+r)
            elif i != -1:
                #self.doc.pop(i+offset)
                #offset -= 1
                pass



def _py_parse(f, precompile=True):
    queue = deque()
    _id = id(f)

    for i, line in enumerate(f):
        ws, l = parse_ws(line)

        if l[0] == ':':
            l = parse_cmd(l, _id, i)
            queue.append((i, l))
            continue

        if '{' in l:
            queue.append((i, 'globals()["__{0}_{1}__"] = fmt.format("""{2}""")'.format(_id, i, l)))
            continue

        # look to see if :func() is embedded in line
        _inline = parse_inline(l)
        if _inline is None:
            continue
        else:
            queue.append((i, 'globals()["__{0}_{1}__"] = {2}'.format(_id, i, _inline)))


    py_str = '\n'.join([x[1] for x in queue])
    if py_str == '':
        return f

    try:
        cc = compile('fmt.namespace=globals()\n'+py_str, '<string>', 'exec')
        eval(cc, sandbox)
    except Exception as e:
        print '=================='
        print 'Compilation String'
        print '=================='
        print py_str
        print '------------------'
        raise e

    offset = 0
    while queue:
        i, l = queue.popleft()
        k = '__{0}_{1}__'.format(_id, i)

        if k in sandbox:
            r = sandbox[k]

            if isinstance(r, list):
                if isinstance(r[0], list):
                    r = [a for b in r for a in b]
                tmp = f.pop(i+offset).rstrip()
                ws = tmp[:-len(tmp.lstrip())]
                #ws, tmp = parse_ws(f.pop(i+offset))
                r = [ws+x for x in r]
                f = f[:i+offset] + r + f[i+offset:]
                offset += len(r)-1
                '''
                for x in r:
                    f.insert(i+offset, ws+x)
                    offset += 1
                offset -= 1
                '''
            else:
                tmp = f.pop(i+offset)

                tmp2 = tmp.strip()
                if tmp2[0] != '': #ugh
                    tmp3 = ':'+l.split('=')[1].strip() #really ugh
                    if tmp3[:4] != ':fmt': # oh geez
                        r = tmp2.replace(tmp3, r)

                ws = tmp[:-len(tmp.lstrip())]
                f.insert(i+offset, ws+r)
        else:
            f.pop(i+offset)
            offset -= 1

    return f


if __name__ == '__main__':
    import sys
    from time import time
    import _sandbox
    import codecs

    _f = sys.argv[1]
    _f = codecs.open(_f, encoding='utf-8').readlines()
    t = sys.argv[2]

    if t == 'y':
        times = []
        for x in range(2000):
            a = time()
            sandbox = _sandbox.new()
            sandbox.update(ext)
            _py_parse(_pre_parse(_f))
            times.append(time()-a)
        print min(times)
    elif t == 'pre':
        precomp = PyParse(_pre_parse(_f))
        for x in precomp.doc:
            print `x`
    else:
        sandbox = _sandbox.new()
        sandbox.update(ext)
        f = _pre_parse(_f)
        f = _py_parse(f)

        for x in f:
            print `x`

