"""
Determine colony grid position based on object map

"""

import cPickle

import numpy as np
import matplotlib.pylab as plt


class PlateGrid:
    def __init__(self, ncol, nrow, xy_init, x_dif, y_dif):
        self.ncol = ncol
        self.nrow = nrow
        self.xy_init = xy_init
        self.x_dif = x_dif
        self.y_dif = y_dif
        self.poss = [(col,row) 
            for row in range(1,nrow+1) 
            for col in range(1,ncol+1)]

        self._calc_pos2xy_center()
        self._calc_crippos()


    def _calc_pos2xy_center(self):
        self.pos2xy_center = {}
        for col, row in self.poss:
            cx = int(self.xy_init[0] + 
                    self.x_dif * (col-1))
            cy = int(self.xy_init[1] + 
                    self.y_dif * (row-1))
            self.pos2xy_center[(col,row)] = (cx,cy)


    def _calc_crippos(self):
        rx = self.x_dif
        ry = self.y_dif
        x_tl = int(self.xy_init[0] - self.x_dif)
        y_tl = int(self.xy_init[1] - self.y_dif)
        x_br = int(self.xy_init[0] + 
                    self.x_dif * self.ncol)
        y_br = int(self.xy_init[1] + 
                    self.y_dif * self.nrow)
        self.xy_tl = (x_tl,y_tl)
        self.xy_br = (x_br,y_br)

if __name__ == "__main__":
    ncol = 48
    nrow = 32
    grid = PlateGrid(ncol, nrow, (1,1), 30, 30)
    print grid
