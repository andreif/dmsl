cdef inline tuple parse_ws2(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c

    for i, c in enumerate(s):
        if c != u' ':
            return s[:i], s[i:].rstrip()
    return u'', s.rstrip()

cdef inline tuple parse_attr(unicode s):
    cdef Py_ssize_t i
    cdef Py_ssize_t j = 0
    cdef Py_UNICODE c

    for i, c in enumerate(s):
        if c == u' ' and j == 0:
            return s[:i]+s[i:], u''
        elif c == u'(':
            j = i
        elif c == u')':
            i += 1
            return s[:j]+s[i:], s[j:i]
    return s, u''

cdef inline tuple parse_attr2(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c

    mark_start = None
    mark_end = None

    key_start = None
    val_start = None
    literal_start = None

    d = {}

    for i, c in enumerate(s):
        if key_start is not None:
            if val_start is not None:
                if i is val_start+1 and (c is u'"' or c is u"'"):
                    literal_start = i
                elif literal_start is not None and c is s[literal_start]:
                    d[s[key_start+1:val_start]] = s[literal_start+1:i]
                    key_start = None
                    val_start = None
                    literal_start = None
                elif literal_start is None and c is u']':
                    d[s[key_start+1:val_start]] = s[val_start+1:i]
                    key_start = None
                    val_start = None
            elif c is u'=':
                val_start = i
        elif c is u'[':
            key_start = i
            if mark_start is None:
                mark_start = i
        elif c is u' ':
            mark_end = i
            break
    
    if mark_start is None:
        return s, d
    if mark_end is None:
        return s[:mark_start], d
    else:
        return s[:mark_start]+s[mark_end:], d


cdef inline tuple split_space(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c

    for i, c in enumerate(s):
        if c == u' ':
            return s[:i], s[i:]
    return s, u''

cdef inline tuple split_pound(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c

    for i, c in enumerate(s):
        if c == u'#':
            return s[:i], s[i:]
    return s, u''

cdef inline tuple split_period(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c

    for i, c in enumerate(s):
        if c == u'.':
            return s[:i], s[i:]
    return s, u''

cdef inline tuple parse_tag2(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c
    cdef unicode r1 = u''
    cdef unicode r2 = u''
    cdef unicode _tag = u''
    cdef unicode _id = u''
    cdef unicode _c1 = u''
    cdef unicode _c2 = u''


    for i, c in enumerate(s):
        if c == u'#':
            r1 = s[:i]
            r2 = s[i:]
            break
    if not r1:
        r1 = s
    for i, c in enumerate(r1):
        if c == u'.':
            _tag = r1[:i]
            _c1 = r1[i:]
            break
    if not _tag:
        _tag = r1

    for i, c in enumerate(r2):
        if c == u'.':
            _id = r2[:i]
            _c2 = r2[i:]
            break
    if not _id:
        _id = r2

    return _tag[1:], _id[1:], (_c1+_c2).replace('.', ' ')[1:]

cdef inline tuple parse_tag(unicode s):
    cdef unicode x

    r = [split_period(x) for x in split_pound(s)]
    return r[0][0][1:], r[1][0][1:], (r[0][1]+r[1][1]).replace(u'.', u' ')[1:]

cdef inline bool not_directive(unicode c):
    cdef Py_UNICODE x = u'%'
    cdef Py_UNICODE y = u'#'
    cdef Py_UNICODE z = u'.'

    if c != x and c != y and c != z:
        return True
    return False

