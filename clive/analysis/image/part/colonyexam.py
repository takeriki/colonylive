#!/usr/bin/python

import math
import cPickle

import numpy as np
import matplotlib.pylab as plt

from scipy.ndimage import imread
from scipy.ndimage.filters import *
from scipy.ndimage.morphology import *
from scipy.ndimage.filters import gaussian_filter
from scipy.ndimage.filters import median_filter
from scipy.ndimage.morphology import binary_fill_holes
from scipy.ndimage.morphology import binary_closing
from scipy.ndimage.morphology import binary_opening


class ColonyRegionExaminer():
    def __init__(self, shape, r):
        self.shape = shape
        self.cx = int(shape[0]/2)
        self.cy = int(shape[1]/2)
        self.r = r
        self._make_masks()

    def _make_masks(self):
        ary = np.zeros(self.shape)
        n = int(2 * np.pi * self.r) * 2
        self.xyss = []
        for i in range(n):
            deg = (360/float(n)) * i
            xys = []
            for j in np.arange(self.r):
                rad = math.radians(deg)
                x = int(round(j * math.cos(rad) - 0 * math.sin(rad)))
                y = int(round(j * math.sin(rad) - 0 * math.cos(rad)))
                xys += [(x+self.cx, y+self.cy)]
            self.xyss += [xys]

    def get_colony_region(self, ary, bg_cut):
        mary = np.zeros(ary.shape)
        #ary = ary.copy()
        #ary = gaussian_filter(ary, 1)
        #ary = median_filter(ary, 3)
        for xys in self.xyss:
            vs = np.array([ary[x,y] for x,y in xys])
            tmp = np.where(vs>=bg_cut)
            if len(tmp[0]) == 0:
                tmp = np.where(vs==max(vs))
                ind = tmp[0][0]
            else:
                ind = tmp[0][0]
            x,y = xys[ind]
            mary[x,y] = 1
        
        mary = binary_closing(mary)
        mary = binary_fill_holes(mary)
        mary = binary_opening(mary)
        return mary


if __name__ == "__main__":
    ary = imread('../sample/colony.tif')
    r = 28
    exam = ColonyRegionExaminer(ary.shape, r)
    mary = exam.get_colony_region(ary, 180)
    plt.subplot(211)
    plt.imshow(ary)
    plt.subplot(212)
    plt.imshow(mary)
    plt.show()

