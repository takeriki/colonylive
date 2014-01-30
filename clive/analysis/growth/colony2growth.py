"""
Compute conventional growth value and three growth values (LTG, MGR, SPG) based on the growth curve.

"""

import csv
import sys

import numpy as np
import matplotlib.pylab as plt

from clive.core.conf import Configure
from clive.db.handler import ColonyHandler
from clive.db.manager import ExpManager
from lib.modelfit import get_growth_parameters

cfg = Configure()
MINUTES_FIXED = int(cfg[('growth','min_fixed_time_point')])


# index to get conventional growth value
def get_ind_con(times):
    difs = np.array(times) - MINUTES_FIXED
    ind_con = np.where(abs(difs) == min(abs(difs)))[0]
    if len(ind_con) > 0:
        ind_con = ind_con[0]
    return ind_con


# Growth parameters: LTG, MGR, SPG
def get_growthpack(poss, times, areass, vss):
    """
    poss: list(column, row)
    colony position

    times: list(...)
    measurement minutes

    areass: list2(list1(...))
    list1: colony areas (time order)
    list2: colony position order, correspond to poss
    
    vss: list2(list1(...))
    list1: colony growth value, area or mass or cmass (time order)
    list2: colony position order, correspond to poss
    """ 
    ind_con = get_ind_con(times)
    gp = GrowthPack(poss)
    n = len(vss)
    for i, (pos, areas, vs) in enumerate(zip(poss,areass,vss)):
        sys.stdout.write("\r")
        sys.stdout.write("Fitting.\t[%-30s]" % ("="*int((i+1)*30/n)))
        sys.stdout.flush()
        con = areas[ind_con]
        ltg, mgr, spg = get_growth_parameters(times, vs)
        gp.add(pos, con, ltg, mgr, spg)
    print 
    return gp


class GrowthPack():
    def __init__(self, poss):
        poss = sorted(poss, key=lambda x:(x[1],x[0]))
        self.poss = poss
        self.pos2data = {}
        for pos in poss:
            self.pos2data[pos] = []

    def add(self, pos, con, ltg, mgr, spg):
        data = [con, ltg, mgr, spg]
        self.pos2data[pos] = data


def test():
    times = "0|30|60|90|120|150|180|210|240|270|300|330|360|390|420|450|480|510|540|570|600|630|660|690|720|750|780|810|840|870|900|930|960|990|1020|1050|1080|1110|1140|1170|1200|1230|1261|1291|1321"
    gcs = "0.35|0.46|0.41|0.38|0.41|0.42|0.51|0.77|1.1|1.68|2.65|4.03|6.07|8.11|10.14|12.1|14.25|16.05|17.75|19.17|20.49|21.74|22.76|23.68|24.53|25.3|26.0|26.68|27.3|27.84|28.36|28.85|29.58|29.8|30.23|30.66|31.06|31.44|31.88|32.04|32.59|32.85|33.18|33.52|33.96"
    poss = [(1,1) for i in range(3)]
    times = [int(i) for i in times.split("|")]
    vs = [float(i) for i in gcs.split("|")]
    vss = [vs for i in range(3)]
    gp = get_growthpack(poss, times, vss, vss)
    assert(gp.poss[0] == (1,1))
    assert(gp.pos2data[(1,1)] == [32.59, 278.7, 0.06748, 28.941])


if __name__ == '__main__':
    test()
