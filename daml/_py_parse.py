#! /usr/bin/env python
# -*- coding: utf-8 -*-

from collections import deque
from _pre_parse import _pre_parse
import __builtin__
from _fmt import DamlFormatter
from time import time

def include(f):
    """
    FIXME this, and all functions need to be made to go to globals() either in pre_parse or in py_parse
    """
    f = open(f).readlines()
    f = _pre_parse(f)
    f = _py_parse(f)
    return f

sandbox = { '__builtins__': None,
            '__blocks__': {},
            '__py_evals__': {}, # need to index by filename, then line number
            'dict': __builtin__.dict,
            'enumerate': __builtin__.enumerate,
            'fmt': DamlFormatter(),
            'globals': __builtin__.globals,
            'len': __builtin__.len,
            'list': __builtin__.list,
            'locals': __builtin__.locals,
            'map': __builtin__.map,
            'max': __builtin__.max,
            'min': __builtin__.min,
            'open': __builtin__.open,
            'range': __builtin__.range,
            'include': include}

def block(s):
    s = s.splitlines()
    s = _py_parse(s)
    globals()['__blocks__'][s[0]] = [s[1:], False] # [content, been-used-yet?]

def _py_parse(f):
    queue = deque()
    _id = id(f)
    
    for i, (ws, l) in enumerate(f):
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
            elif '{__i__}' in l:
                l = l.replace('{__i__}', '"__{0}_{1}__"'.format(_id, i), 1)[1:]
            else:
                l = 'globals()["__{0}_{1}__"] = {2}'.format(_id, i, l[1:])
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
    
    eval(compile('fmt.namespace=globals()\n'+py_str, '<string>', 'exec'), sandbox)

    offset = 0
    while queue:
        i, l = queue.popleft()
        
        k = '__{0}_{1}__'.format(_id, i)
        if k in sandbox:
            r = sandbox[k]
            
            if isinstance(r, list):
                ws, tmp = f.pop(i+offset)
                for x in r:
                    if isinstance(x, list):
                        y_ws, y = x
                        f.insert(i+offset, (ws+y_ws, y))
                        offset += 1
                    else:
                        f.insert(i+offset, (ws, x))
                        offset += 1
                offset -= 1
            else:
                f[i+offset][1] = r
        else:
            f.pop(i+offset)
            offset -= 1
    
    return f


if __name__ == '__main__':
    #from _pre_parse import _pre_parse
    import sys
    from time import time
    
    _f = sys.argv[1]
    t = sys.argv[2]
    f = open(_f).readlines()

    if t == 'yes':
        times = []
        for x in range(2000):
            a = time()
            _py_parse(_pre_parse(f))
            times.append(time()-a)
        print min(times)
    else:
        
        f = open(_f).readlines()
        f = _pre_parse(f)
        f = _py_parse(f)

        for x in f:
            print x
