from lxml import html, etree
import re
from termcolor import colored
from tabulate import tabulate
import  json
from .logs import L
PARSE_SLICE = re.compile(r'(\:\d*\:?\-?\d*)')


def ParseSlice(p) -> (str, slice):
    parse_slice_num = PARSE_SLICE.findall(p)
    if parse_slice_num:
        pp = parse_slice_num[0][1:]
        if ':' in pp:
            start,end = pp.split(":")
            start = int(start)
            if end:
                end = int(end)
            else:
                end = None

        else:
            start = int(pp)
            end = start +1
        new_p = PARSE_SLICE.sub('', p)

        return new_p,slice(start, end)

    return p,slice(None)

def parse(raw, p):
    res = [html.fromstring(raw)]
    parse_strs = p.split("|")
    for parse_str in parse_strs:
        parse_str = parse_str.strip()

        # parse number slice 
        _parse, _slice = ParseSlice(parse_str)
        # print(_slice)
        # xpath parse
        if _parse.startswith("/") or _parse.startswith("./"):
            ps = []
            for x in res:
                for q in x.xpath(_parse):
                    ps.append(q)
            res = ps[_slice]
        # cssselect
        else:
            ps = []
            for x in res:
                try:
                    for q in x.cssselect(_parse):
                        ps.append(q)
                except Exception as e:
                    L(e, e=True)
                    
            res = ps[_slice]
    return  res

def show(res, tp =None):
    alls = []
    for i in res:
        if tp == 'json':
            print(json.dumps(dict(i.attrib)))
        elif tp == 'text':
            print({i.tag: i.text})
        else:
            w = etree.tostring(i)
            if isinstance(w, bytes):
                w = w.decode('utf-8')
            print(w)
    # if tp =="json":
        # try:
            # print(json.dumps(alls))

        # except Exception as e:
            # print(alls)
            # raise  e


