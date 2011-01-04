from _parse_ext import *
from _sandbox import _open

def parse_inlines(s):
    if ':' not in s:
        return s, ()
    
    l = []
    inline = parse_inline(s, 0)
    i = 0
    while inline != u'':
        s = s.replace(':'+inline, '{'+str(i)+'}')
        l.append(inline)
        inline = parse_inline(s, 0)
        i += 1
    return s, l

def expand_line(ws, l, i, f):
    el, attr = parse_attr(l)
    tag, txt = split_space(el)
    
    # Check for inlined tag hashes
    if txt != u'' and (is_directive(txt[0]) or txt[-1] == u':'):
        l = l.replace(txt, u'')
        f[i] = ws+l
        f.insert(i+1, ws+u' '+txt)
    return l

txt_cmd = u'globals()["__py_parse__"]["{0}_{1}"] = {2}'
txt_fmt = u'globals()["__py_parse__"]["{0}_{1}"] = fmt.format("""{2}""", {3})'

def _parse_pre(_f):
    f = _f[:]
    
    py_queue = []
    py_id = id(py_queue)
    py_count = 0
    
    mixed_ws = None
    mixed_ws_last = None
    get_new_ws = False
    
    i = 0
    
    while i < len(f):
        ws, l = parse_ws(f[i])
        
        if not l:
            del f[i]
            continue
        
        ### maybe something better?
        if l[:8] == 'extends(':
            del f[i]
            _f = _open(l.split("'")[1]).readlines()
            for j, x in enumerate(_f):
                f.insert(i+j, x)
            continue
        elif l[:8] == 'include(':
            del f[i]
            _f = _open(l.split("'")[1]).readlines()
            for j, x in enumerate(_f):
                f.insert(i+j, ws+x)
            continue
        ###
        
        if l[0] in directives:
            l = expand_line(ws, l, i, f)
        elif l[0] == '[' and l[-1] == ']': # else if list comprehension
            py_queue.append(txt_cmd.format(py_id, py_count, l))
            f[i] = ws+'{{{0}}}'.format(py_count)
            py_count += 1
            i += 1
            continue
        # else if not a filter or mixed content
        elif l[0] != ':' and l[-1] != ':':
            if is_assign(l):
                py_queue.append(l)
                del f[i]
            else:
                py_queue.append(txt_cmd.format(py_id, py_count, l))
                f[i] = ws+u'{{{0}}}'.format(py_count)
                py_count += 1
                i += 1
            continue
        
        # check for continued lines
        while l[-1] == '\\':
            _ws, _l = parse_ws(f.pop(i+1))
            l = l[:-1] + _l
        
        # inspect for format variables
        if '{' in l: # and mixed is None:
            l, inlines = parse_inlines(l)
            py_queue.append(txt_fmt.format(py_id, py_count, l, u','.join(inlines)))
            f[i] = ws+u'{{{0}}}'.format(py_count)
            py_count += 1
            i += 1
            continue
        
        # handle filter
        if l[0] == ':':
            func, sep, args = l[1:].partition(' ')
            filter = [func+'(u"""'+args]
            j = i+1
            fl_ws = None # first-line whitespace
            while j < len(f):
                _ws, _l = parse_ws(f[j])
                if _ws <= ws:
                    break
                fl_ws = fl_ws or _ws
                del f[j]
                filter.append(sub_str(_ws, fl_ws)+_l)
            filter.append('""")')
            
            if func == 'block':
                f[i] = ws+u'{{block}}{{{0}}}'.format(args)
                py_queue.append(u'globals()["__py_parse__"]["{0}_{1}"] = {2}'.format(py_id, py_count, u'\n'.join(filter)))
            else:
                f[i] = ws+u'{{{0}}}'.format(py_count)
                py_queue.append(u'globals()["__py_parse__"]["{0}_{1}"] = {2}'.format(py_id, py_count, u'\n'.join(filter)))
                py_count += 1
        
        # handle mixed content
        elif l[-1] == ':':
            mixed_ws = mixed_ws_last = ws
            get_new_ws = True
            py_queue.append(u'__mixed_content__ = []')
            py_queue.append(l)
            del f[i]
            mixed_closed = False
            while i < len(f):
                _ws, _l = parse_ws(f[i])
                if not _l:
                    del f[i]
                    continue
                
                if _ws <= mixed_ws and _l[:4] not in ['else', 'elif']:
                    py_queue.append(u'globals()["__py_parse__"]["{0}_{1}"] = list(__mixed_content__)'.format(py_id, py_count))
                    f.insert(i, mixed_ws+u'{{{0}}}'.format(py_count))
                    py_count += 1
                    mixed_closed = True
                    break
                elif _l[0] in directives:
                    _l = expand_line(_ws, _l, i, f)
                    ws_diff = sub_str(_ws, mixed_ws)
                    if get_new_ws or ws_diff <= mixed_ws_last:
                        mixed_ws_last = ws_diff
                        get_new_ws = False
                    _l, inlines = parse_inlines(_l)
                    py_queue.append(mixed_ws_last+u'__mixed_content__.append(fmt.format("""{0}{1}""", {2}))'.format(sub_str(sub_str(_ws, mixed_ws_last), mixed_ws), _l, ','.join(inlines)))
                    del f[i]
                    continue
                # is this a list comprehension?
                elif _l[0] == '[' and _l[-1] == ']':
                    py_queue.append(mixed_ws_last+u'__mixed_content__.extend({0})'.format(_l))
                    del f[i]
                else:
                    if _l[-1] == ':':
                        get_new_ws = True
                    py_queue.append(sub_str(_ws, mixed_ws)+_l)
                    del f[i]
                    continue
            # maybe this could be cleaner? instead of copy and paste
            if not mixed_closed:
                py_queue.append(u'globals()["__py_parse__"]["{0}_{1}"] = list(__mixed_content__)'.format(py_id, py_count))
                f.insert(i, mixed_ws+u'{{{0}}}'.format(py_count))
                py_count += 1
        # handle standalone embedded function calls
        elif ':' in l:
            l, inlines = parse_inlines(l)
            if len(inlines) != 0:
                py_queue.append(txt_fmt.format(py_id, py_count, l, ','.join(inlines)))
                f[i] = ws+u'{{{0}}}'.format(py_count)
                py_count += 1
                i += 1
                continue
        
        i += 1
    
    
    return f, py_queue

