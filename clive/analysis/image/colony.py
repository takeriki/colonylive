"""
Make colony objects based on object map and grid.

"""

import cPickle

import numpy as np
import matplotlib.pylab as plt

from scipy.ndimage.filters import *
from scipy.ndimage.morphology import *
from scipy.ndimage.filters import gaussian_filter
from scipy.ndimage.filters import median_filter
from scipy.ndimage.morphology import binary_fill_holes
from scipy.ndimage.morphology import binary_closing
from scipy.ndimage.morphology import binary_opening

from part.colonyimg import ColonyImg
from part.colonyexam import ColonyRegionExaminer
from part.util import clip_img
from part.grid import PlateGrid
from part.image import Image
from objmap import get_objectmap


def get_colony(img_gray, ary_index_map, grid):
    length_ary = int(grid.y_dif) * 2
    lt = length_ary
    shape = (lt, lt)
    exam = ColonyRegionExaminer(shape, 30)

    ary_img = img_gray.get_array()
    gpos2colony = {}
    for gpos in sorted(grid.poss):
        #if gpos != (22,12):
        #    continue
        cx, cy = grid.pos2xy_center[gpos]
        location = [cx-lt/2, cy-lt/2, lt]
        search = [cx-lt/6, cy-lt/6, lt/3]

        colony = make_colony(ary_index_map, location, search)
        colony.load_img(ary_img)

        if not colony.is_found:
            ary_index_map = redetect_colony(colony, ary_index_map, location)
            colony = make_colony(ary_index_map, location, search)
            colony.load_img(ary_img)
        
        if colony.is_found:
            ary = exam.get_colony_region(colony.ary, colony.oi_bg - 5)
            colony.marker[ary==1] = 1
        
        gpos2colony[gpos] = colony
    return gpos2colony


def redetect_colony(colony, ary_index_map, location):
    img_ary = Image()
    img_ary.load_array(colony.ary)
    
    threshold = int(colony.oi_bg - 5)
    tmp = get_objectmap(img_ary, threshold=threshold)
    ind_next = np.max(np.abs(np.unique(ary_index_map))) + 1
    
    x, y, l = location
    ary_index_map[y:y+l+1, x:x+l+1] = tmp * ind_next

    """ 
    fname = "test/C%02dR%02d.png" % (gpos)
    plt.subplot(211)
    plt.imshow(ary_index_map)
    plt.subplot(212)
    plt.imshow(img_ary.get_array())
    plt.savefig(fname)
    plt.clf()
    """ 
    return ary_index_map


def make_colony(ary_index_map, location, search):
    # select id
    ary = clip_img(ary_index_map, search) 
    id_select = _select_id_by_max_area(ary)

    # get offset
    x_off = 0; y_off = 0
    if id_select != 0:
        tmp = np.where(ary==-id_select)
        scy,scx = tmp[0][0], tmp[1][0]
        x_off = scx - (search[2]/2)
        y_off = scy - (search[2]/2)
    location[0] += x_off
    location[1] += y_off
    
    # make marker
    ary = clip_img(ary_index_map, location) 
    marker = ary.copy()
    marker[np.abs(ary) > 0] = 2
    if id_select != 0:
        marker[np.abs(ary) == id_select] = 1
    
    colony = ColonyImg(marker, location)
    return colony


def _select_id_by_max_area(ary):
    ids_center = ary[ary<0]*-1
    id_select = 0
    amax = 0
    for id in set(ids_center):
        area = np.size(ary[np.abs(ary)==id])
        if area > amax:
            id_select = id
            amax = area
    return id_select


if __name__ == "__main__":
    ary_index_map = np.load('index_map.npy')
    f = open('dump-grid.pkl','rb')
    grid = cPickle.load(f)
    f.close()
    
    img_color = Image()
    img_color.load_file('45.tif')
    img_gray = img_color.convert_to_gray()
    gpos2colony = get_colony(img_gray, ary_index_map, grid)

