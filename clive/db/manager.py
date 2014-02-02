#!/usr/bin/python

import datetime
import numpy as np

from handler import ExpHandler, PlateHandler, GrowthHandler, GrowthRawHandler, ImgHandler, ColonyHandler
from sqlalchemy import and_, or_, distinct


exp_handler = ExpHandler()
plate_handler = PlateHandler()
growth_raw_handler = GrowthRawHandler()
growth_handler = GrowthHandler()
colony_handler = ColonyHandler()
img_handler = ImgHandler()


class ExpManager():
    def __init__(self, exp_id):
        self.exp = exp_handler.load(exp_id)
        self.plate = plate_handler.load(self.exp.plate_id)
        self.init_plate()
        self.img = img_handler.load_by_expid(exp_id)

    def init_plate(self):
        self.gary = np.zeros((self.plate.nrow, self.plate.ncol))
        self.plate.poss = [(col+1,row+1) \
            for row in range(self.plate.nrow) \
            for col in range(self.plate.ncol)]
        self.plate.pos2cind = {}
        for cind, pos in enumerate(self.plate.poss):
            self.plate.pos2cind[pos] = cind 
       
    def get_colonys(self):
        return colony_handler.get_by_exp_id(self.exp.id)
    
    def put_raw_growthpack(self, growthpack):
        growth_raw_handler.delete_by_exp_id(self.exp.id)
        gp = growthpack
        for pos in gp.poss:
            col, row = pos
            con, ltg, mgr, spg = gp.pos2data[pos]
            growth_raw_handler.create(self.exp.id,
                 col, row, con, ltg, mgr, spg)


    def put_colonys(self, colonypack):
        colony_handler.delete_by_exp_id(self.exp.id)
        cp = colonypack
        for pos in cp.poss:
            colony_handler.create(
                self.exp.id,
                pos[0],
                pos[1],
                cp.pos2location[pos],
                cp.pos2areas[pos],
                cp.pos2masss[pos],
                cp.pos2cmasss[pos]
            )

    def get_raw_growth_ary(self):
        ary = np.zeros((self.plate.nrow, self.plate.ncol, 4))
        growths = growth_raw_handler.load_by_exp_id(self.exp.id)
        for g in growths:
            ary[g.row-1, g.col-1, :] = [g.con, g.ltg, g.mgr, g.spg]
        return ary
    
    def put_growth_ary(self, ary):
        growth_handler.delete_by_exp_id(self.exp.id)
        for pos in self.plate.poss:
            col, row = pos
            con, ltg, mgr, spg = ary[row-1, col-1, :]
            growth_handler.create(self.exp.id,
                 col, row, con, ltg, mgr, spg)
    
    def get_growth(self):
        return growth_handler.load_by_exp_id(self.exp.id)

    def set_step_done(self, value):
        self.exp.step_done = value
        exp_handler.update()
    
    def set_in_process(self, value):
        self.exp.in_process = value
        exp_handler.update()
    
    def set_failure(self, value):
        self.exp.failure = value
        exp_handler.update()


if __name__ == "__main__":
    expm = ExpManager(1)
    ary = expm.get_growth_ary()
    print ary
