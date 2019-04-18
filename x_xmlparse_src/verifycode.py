import numpy as np
from PIL import Image
import requests
from io import  BytesIO


PL = 0.33
PO = int(255 * PL)
PW = int(255 * (1-PL))


def move_windows(base_array:np.array, r=3, corp='white'):
    aw,ah = base_array.shape[0:2]
    if corp == 'white':
        exm = np.ones(base_array[0][0].shape) * 255
    else:
        exm = np.zeros(base_array[0][0].shape)
    # corp will be white
    base_array[0:r-1, 0:r-1] = exm
    for i in range(r-1, aw - r):
        for j in range(r-1, ah - r):
            win =  base_array[i-r +1: i+r, j-r+1:j+r]
            yield i, j, win


def simple_filter(arr:np.array) -> np.array:
    a = arr.copy()
    a[a > PO] = 255
    return  a


def clear_point(one,min_value=5):
    cent = one.shape[0] // 2
    w = one[cent, cent]
    if (w < 255 ).any() == True:
        k_p = np.count_nonzero(one < 255)
        if k_p < min_value:
            return np.ones(w.shape) * 255
        else:
            return  w
    else:        
        return w


def complete_windows(win: np.array, check_point= lambda x: if x < 85):
    l = win.shape[0]
    w = win.copy()
    w[check_point(w).any() == True ] = 1
    w[check_point(w).any() == False] = 0
    fil = np.ones((l,1))
    cl = w.dot(fil).sum()
    cw = w.T.dot(fil).sum()
    return cw, cl



def to_gray(url, array=True, *filters):
    if url.startswith("http"):
        img = Image.open(BytesIO(requests.get(url, proxies={'http':'socks5h://127.0.0.1:1080', 'https':'socks5h://127.0.0.1:1080'}).content))
    else:
        img = Image.open(url)
    i = img.convert('LA')
    if filters:
        arr = np.asarray(i).copy()
        for f in filters:
            arr = f(arr)
        return  arr

    
    # return  
    

def from_array(arr, show=False):
    i =  Image.fromarray(arr)
    if show:
        i.show()
    return  i

