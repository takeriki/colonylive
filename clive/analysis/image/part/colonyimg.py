#!/usr/bin/python

import math
import cPickle

import numpy as np
import matplotlib.pylab as plt

from scipy.ndimage.filters import *
from scipy.ndimage.morphology import *

from clive.core.conf import Configure
from util import clip_img, get_peak_intensity

cfg = Configure()
R_CENTER_MASS = int(cfg[('colony','r_center_mass')])


class ColonyImg():
    def __init__(self, marker, location):
        """
        ary: numpy array
        An image is 8-bit grayscale.
        The taget colony is located on center.

        marker: numpy array
        Indicate the colony & background region.
        same size to img array.
        0 = background
        1 = target colony
        2 = neighbor colony

        location: tuple(x, y, length)
        x = x of left up point
        y = y of left up point
        l = length of crip box
        
        """ 
        self.ary = None
        self.marker = marker
        self.location = location
        self.area = 0
        self.mass = 0
        self.cmass = 0

        self.is_found = 0
        if 1 in list(np.unique(marker)):
            self.is_found = 1
        
        self._set_circular_mask()
        
    def load_img(self, ary_img):
        #ary = clip_img(ary_img, self.cx, self.cy, self.length_ary)
        ary = clip_img(ary_img, self.location)
        self.ary = ary.copy()
        self._set_oi_bg()
        self._quantify()

    def _set_oi_bg(self): 
        ary = self.ary[self.marker==0]
        if ary.size != 0:
            self.oi_bg = get_peak_intensity(ary)
   
    def _set_circular_mask(self):
        # make circular mask
        length = self.location[2]+1
        yp, xp = length/2, length/2
        y,x = np.ogrid[-yp:length-yp, -xp:length-xp]
        mask = x*x + y*y <= R_CENTER_MASS*R_CENTER_MASS
        self.center_mask = mask

    def _quantify(self):
        if not self.is_found:
            return
        # whole region
        search_space = self.marker == 1
        ois_search = self.ary[search_space]
        ois_colony = ois_search[ois_search < self.oi_bg - 10]
        self.area = len(ois_colony)
        ods = -np.log10(ois_colony/self.oi_bg)
        mass = np.sum(ods)
        self.mass = round(mass,2)
        
        # center region
        search_space = np.logical_and(
            self.marker == 1,
            self.center_mask == 1)
        ois_search = self.ary[search_space]
        ois_colony = ois_search[ois_search < self.oi_bg - 10]
        ods = -np.log10(ois_colony/self.oi_bg)
        cmass = np.sum(ods)
        self.cmass = round(cmass,2)


if __name__ == "__main__":
    ary_index_map = np.load('index_map.npy')
    
    f = open('dump-grid.pkl','rb')
    grid = cPickle.load(f)
    f.close()
    
    gpos2colony = get_colony(ary_index_map, grid)

