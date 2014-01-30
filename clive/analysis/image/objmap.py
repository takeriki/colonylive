"""
Make map of colony-like image objects

"""

import cv
import numpy as np
import cPickle

import matplotlib.pylab as plt

from clive.core.conf import Configure
from lib.image import Image
from lib.imageobj import get_all_imgobjs
from lib.motsu import get_thresholds

COLONY_AREA_LOWER_LIMIT = 20
COLONY_AREA_UPPER_LIMIT = 2000
ASPECTRATIO_UPPER_LIMIT = 0.6
CIRCULARITY_UPPER_LIMIT = 0.6


def get_objectmap(img_gray, threshold=0, cut_level=2, n_unsharp_mask=2):
    # get threshold
    if threshold == 0:
        ts = get_thresholds(img_gray.iplimg, cut_level)
        threshold = ts[-1] 

    # make binary_img
    tmp = img_gray.copy()
    for i in range(n_unsharp_mask):
        tmp.unsharp_mask()
    
    img_binary = tmp.convert_to_binary(threshold)
    #img_binary.save_to_file('test')

    # find & select objects
    imgobjs_all = get_all_imgobjs(img_binary)
    imgobjs = [imgobj for imgobj in imgobjs_all if imgobj.is_colony]
    #imgobjs = get_imgobjs_like_colony(img_binary)

    # make index map
    ary_indexmap = make_index_map(img_binary.size, imgobjs)
    return ary_indexmap


def make_index_map(size, imgobjs):
    xys_edges = [i.xys_edge for i in imgobjs]
    nx, ny = size
    ary_index_map = np.zeros((ny, nx), dtype=int)

    # labeling
    for i, xys in enumerate(xys_edges):
        xs = np.array([j[0] for j in xys])
        ys = np.array([j[1] for j in xys])
        for x in set(xs):
            sys = ys[xs==x]
            ary_index_map[min(sys):max(sys)+1,x] = i+1
        for y in set(ys):
            sxs = xs[ys==y]
            ary_index_map[y,min(sxs):max(sxs)+1] = i+1
    
    # make center = negative value
    xy_centers = [i.xy_center for i in imgobjs]
    for i, (x, y) in enumerate(xy_centers):
        ary_index_map[y][x] *= -1
    return ary_index_map


def test():
    img_color = Image()
    img_color.load_file('sample/plate.jpg')
    img_gray = img_color.convert_to_gray()
    ary_index_map = get_objectmap(img_gray)
    n_obj = len(np.unique(np.abs(ary_index_map)))
    assert(n_obj == 1537)
    #np.save('index_map', ary_index_map)
    """
    a = ary_index_map
    a[np.abs(a)>0] = 1
    plt.imshow(a)
    plt.colorbar()
    plt.show()
    """

if __name__ == "__main__":
    test()
