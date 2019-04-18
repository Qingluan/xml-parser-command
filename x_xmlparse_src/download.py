from tqdm import tqdm
import requests
import math
import  os
from concurrent.futures.thread import ThreadPoolExecutor
from termcolor import  colored
from lxml import html
import  urllib.parse as up
import pdb
if not os.path.exists("/tmp/downloads"):
    os.mkdir("/tmp/downloads")

DOWN_ROOT = "/tmp/downloads"

exe = ThreadPoolExecutor(max_workers=12)

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'

Process = None
DIR_URLS = set()

requests.packages.urllib3.disable_warnings()

def init_process(total, desc=' no desc'):
    global Process
    Process = tqdm(total=total, desc=desc)

def update():
    global Process
    if not Process:
        Process = tqdm()
    Process.update()


def mkdir_p(root):
    if root.endswith("/"):
        root = os.path.dirname(root)
    if os.path.isdir(root):
        return
    try:
        os.mkdir(root)
    except FileNotFoundError:
        # print(root)
        d = os.path.dirname(root)
        mkdir_p(d)
        mkdir_p(root)

def download(url, proxy=None, name=None):
    # Streaming, so we can iterate over the response.
    
    sess = requests.Session()

    # pdb.set_trace()
    if proxy:
        sess.proxies['https'] = proxy
        sess.proxies['http'] = proxy

    if not name:
        PP = up.urlparse(os.path.dirname(url))
        parsent = PP.netloc
        dirs = os.path.join(parsent, PP.path[1:])
        PRE = os.path.join(DOWN_ROOT, dirs)
        mkdir_p(PRE)
        name = os.path.basename(url)
    else:
        PRE = DOWN_ROOT

    sess.headers.update({'User-agent':UA})
    sess.verify = False
    # tqdm.write(url)
    # if url.endswith("html") or url.endswith("htm"):
    #     r = sess.get(url)
    #     with open(os.path.join(PRE, name), 'wb') as f:
    #         f.write(r.content)
    #     return
    r = sess.get(url, stream=True, verify=False)
    block_size = 1024

    
    # Total size in bytes.
    total_size = int(r.headers.get('content-length', 0)); 
    wrote = 0 
    with open(os.path.join(PRE, name), 'wb') as f:
        for data in tqdm(r.iter_content(block_size), total=math.ceil(total_size//block_size) , unit='KB', unit_scale=True):
            wrote = wrote  + len(data)
            f.write(data)
    if total_size != 0 and wrote != total_size:
        print("ERROR, something went wrong")


def get(url, parser, show, proxy=''):

    sess = requests.Session()
    if proxy:
        sess.proxies['https'] = proxy
        sess.proxies['http'] = proxy
    sess.headers.update({'User-agent':UA})
    try:
        res = sess.get(url)
    except requests.exceptions.SSLError:
        print(colored("[!]", 'red'), colored('%s retry', 'yellow'))
        res = get(url, parser, show, proxy=proxy)
    if res.status_code == 200:
        if parser:
            e = parser(res.text)
        if show:
            e = show(e)
        else:
            e = res.text
        return  e
    else:
        tqdm.write(colored("[!] ", 'red') + colored(url + " %d" % res.status_code))    
        
    return  ''
    

def add_url_to_download(url, proxy):
    exe.submit(download, url, proxy=proxy)



def linesprint(res):
    for l in res:
        print(l)

def add_url(url, proxy, parser, show,callback=None):
    f = exe.submit(get, url, parser, show, proxy=proxy)
    if callback:
        f.add_done_callback(callback)

    return  f

def parse_sub_dir(url, proxy, parent=None, host=None):
    global DIR_URLS
    if not parent:
        parent = up.urlparse(url)
        parent = parent.scheme + "://" + parent.netloc
    else:
        if up.urlparse(url).netloc != up.urlparse(host).netloc:
            return
        if url.startswith("http"):
            if not url.startswith(parent):
                return
            else:
                if url in DIR_URLS:
                    return
        elif url.endswith("#"):
            return 
        else:
            # print(parent, url)
            url = up.urljoin(parent, url)
    if url in DIR_URLS:
        return
    xml = get(url, None, None, proxy=proxy)
    DIR_URLS.add(url)
    
    if isinstance(xml, str):
        if len(xml)> 1:
            xml = html.fromstring(xml)
        else:
            
            return
    if isinstance(xml, str):
        tqdm.write(colored("[!] ", 'red') + colored(url + " not get ok"))
        return
    tqdm.write(colored("[+]" ,'green') + colored(url, 'blue'))
    parent = url
    for a in xml.xpath("//a[@href]"):
        u = a.attrib['href']
        if u.endswith("/"):
            if u.startswith("/"):
                continue
            elif u.startswith("http") and not u.startswith(parent):
                continue    
            elif u.startswith(".."):continue
            else:
                pass
            # print(u, parent)
            parse_sub_dir(u, proxy, parent=parent, host=host)
        else:
            # pass
            
            
            uu = up.urljoin(parent, u)
            if not uu.startswith(parent):continue
            # print(proxy)
            # download(uu, proxy=proxy)
            add_url_to_download(uu, proxy)
            tqdm.write(colored("[✓] " ,'green') + colored(u, attrs=['bold', 'underline']), end='\r')
            # break
