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

def tree_attrs(node, parent):
    
    sub = []
    for i in node.iterchildren():
        s = [_t for _t in tree_attrs(i, node)]
        sub.append(s[0])

    
    if sub:
        w = {"tag":node.tag  , "children": sub}
    else:
        w = {"tag":node.tag }
    w.update(dict(node.attrib))
    yield  w
    

def tree_text(node, parent, cur=0):
    sub = []
    for i in node.iterchildren():
        s = [_t for _t in tree_text(i, node, cur=cur+4)]
        sub.append(s[0])

    t =  {"tag": node.tag, "text": "", "sub":sub, 'space': cur}
    if node.text and node.text.strip():
        if 'id' in node.attrib:
            t['id'] = node.attrib['id']
        t["text"] = node.text
        
    yield  t


def tree_text_draw(tree, line=''):
    
    if tree['text']:
        tt = tree['text'].strip().split("\n")
        tag =  (colored(tree['tag'].strip() + "#" + tree.get('id'), 'yellow')) if 'id' in tree  else (colored(tree['tag'].strip() , 'yellow'))
        tag = tag[-tree['space']:]

        tag_l = len(tag)
        if tree['space'] > tag_l:
            tag +=  ' ' * (tree['space'] - tag_l)
        ss = '\n'.join([' ' * tree['space'] + "|" + colored(i, 'green') if n > 0 else tag + "|" + colored(i, 'green') for n,i in enumerate(tt)])
        
        print(ss)

    
    for i in tree['sub']:
        
        yield  from tree_text_draw(i, line=line + '/' + i['tag'].strip() )


def reverse_search(ele:etree.Element, p, text_field='text()'):
    p = p.strip()

    if "@" in p:
        tag,__p  = p.split("@",1)
        p = __p
    else:
        tag = "*"

    if ' and ' in p:
        ps = p.split("and")
        op = ' and '
    else:
        ps = [p]
    cmds = []
    for _p in ps:
        if 'in' in _p:
            _val, _field = _p.split("in")
            _field = "@" + _field.strip()
        else:
            _val = _p
            _field = text_field
        _val = _val.strip()
        cmd = 'contains(%s,\'%s\')' % (_field, _val)
        cmds.append(cmd)
    __p = './/%s[%s]'% (tag, ' and '.join(cmds))
    # print(__p)
    return ele.xpath(__p)



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
        elif _parse.startswith("?"):
            p = _parse[1:]
            ps = []
            for i in res:
                ps += reverse_search(i, p)
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

def to_html(ele, subpre='', subnext='') -> str:
    if ele != None:
        attr = " ".join([ "%s=\"%s\"" % (k,v) for k,v in ele.items()])
        return '<{tag} {attr} >{pre}{text}{next}</{tag}>'.format(tag=ele.tag, text=ele.text, attr=attr, pre=subpre, next=subnext)
    return  ""

def nearby(ele:etree.Element):
    
    pa = ele.getparent()
    ch = ele.getchildren()
    nt = ele.getnext()
    pr = ele.getprevious()
    
    ch = to_html(ch[0]) if ch else ""
    nt = to_html(nt)
    pr = to_html(pr)
    self = to_html(ele, subnext=ch)

    pa = to_html(pa, subnext=pr+self+nt)
    # print(pa)
    
    return  html.fromstring(pa)
    
    



def show(res, tp =None, tree=False):
    alls = []
    for i in res:
        
        if tp == 'json':
            if tree:
                print(json.dumps(list(tree_attrs(i,i))[0]))
            else:
                u = dict(i.attrib)
                u['tag'] = i.tag
                if i.text and  i.text.strip():
                    u['text'] = i.text.strip().encode().decode()
                print(json.dumps(u))
        elif tp == 'text':
            if tree:
                res_s = list(tree_text(i, i))
                list(tree_text_draw(res_s[0]))
            
            else:
                if i.text:
                    ts = [" "*(len(i.tag) +3 ) + colored(q,'green') if qn > 0 else colored(q,'green')  for qn,q in  enumerate(i.text.split("\n"))]
                    print(i.tag, ":", '\n'.join(ts))
        else:
            w = etree.tostring(i, encoding='utf-8')
            if isinstance(w, bytes):
                w = w.decode('utf-8')
            print(w)
    # if tp =="json":
        # try:
            # print(json.dumps(alls))

        # except Exception as e:
            # print(alls)
            # raise  e


