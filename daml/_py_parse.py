#! /usr/bin/env python
# -*- coding: utf-8 -*-

from collections import deque
from _pre_parse import _pre_parse
from _sandbox import _open

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

def _py_parse(f):
    queue = deque()
    _id = id(f)
    
    for i, line in enumerate(f):
        line = line.rstrip()
        l = line.strip()
        ws = line[:-len(l)]
        
        if l[0] == ':':
            a = l.find('(')
            b = l.find('=')
            if b != -1 and (b < a or a == -1):
                """
                :mine('asdf')
                :get('func=blah')
                :test = 'tad(a)'
                :title = 'woah'
                """
                l = l[1:]
            else:
                l = 'globals()["__{0}_{1}__"] = {2}'.format(_id, i, l[1:])
            
            if '{__i__}' in l:
                l = l.replace('{__i__}', '"__{0}_{1}__"'.format(_id, i), 1)
            queue.append((i, l))
            continue

        if '{' in l:
            queue.append((i, 'globals()["__{0}_{1}__"] = fmt.format("""{2}""")'.format(_id, i, l)))
            continue

        # look to see if :func() is embedded in line
        if ':' in l:
            a = l.index(':')
        else:
            continue
        if '(' in l:
            b = l.index('(')
        else:
            continue
        if ' ' in l[a:b] or a > b: # check a>b for attributes that have :
            continue

        c = l.index(')')+1
        queue.append((i, 'globals()["__{0}_{1}__"] = {2}'.format(_id, i, l[a+1:c]))) # FIXME embedded needs a line number among other things

    py_str = '\n'.join([x[1] for x in queue])
    if py_str == '':
        return f

    try:
        eval(compile('fmt.namespace=globals()\n'+py_str, '<string>', 'exec'), sandbox)
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
                tmp = f.pop(i+offset).rstrip()
                ws = tmp[:-len(tmp.lstrip())]
                for x in r:
                    f.insert(i+offset, ws+x)
                    offset += 1
                offset -= 1
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
    
    _f = sys.argv[1]
    _f = open(_f).readlines()
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
    else:
        sandbox = _sandbox.new()
        sandbox.update(ext)
        f = _pre_parse(_f)
        f = _py_parse(f)

        for x in f:
            print `x`

