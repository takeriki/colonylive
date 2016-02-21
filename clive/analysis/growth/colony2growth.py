#!/usr/bin/env python2
# -*- coding:utf-8 -*-

"""
Compute conventional growth value and three growth values (LTG, MGR, SPG) based on the growth curve.

"""

import numpy as np

from clive.core.conf import Configure
from part.modelfit import get_growth_parameters

cfg = Configure()
MINUTES_FIXED = int(cfg[('growth','min_fixed_time_point')])


def get_ind(times, min_fixed):
    """
    min_fixedに最も近いtimes配列のindexを返す
    """
    difs = np.array(times) - min_fixed
    ind_con = np.where(abs(difs) == min(abs(difs)))[0]
    if len(ind_con) > 0:
        ind_con = ind_con[0]
    return ind_con


# Growth parameters: LTG, MGR, SPG
def get_growth_pars(times, vs):
    """
    経時的な増速データからLTG, MGR, SPGを計算する

    timesは測定した培養時間の配列
    vsは測定した増殖値の配列
    """ 
    ltg, mgr, spg = get_growth_parameters(times, vs)
    return (ltg, mgr, spg)



def test():
    times = "0|30|60|90|120|150|180|210|240|270|300|330|360|390|420|450|480|510|540|570|600|630|660|690|720|750|780|810|840|870|900|930|960|990|1020|1050|1080|1110|1140|1170|1200|1230|1261|1291|1321"
    gcs = "0.35|0.46|0.41|0.38|0.41|0.42|0.51|0.77|1.1|1.68|2.65|4.03|6.07|8.11|10.14|12.1|14.25|16.05|17.75|19.17|20.49|21.74|22.76|23.68|24.53|25.3|26.0|26.68|27.3|27.84|28.36|28.85|29.58|29.8|30.23|30.66|31.06|31.44|31.88|32.04|32.59|32.85|33.18|33.52|33.96"
    times = [int(i) for i in times.split("|")]
    vs = [float(i) for i in gcs.split("|")]
    ltg, mgr, spg = get_growth_pars(times, vs)
    assert((ltg,mgr,spg) == (278.7, 0.06748, 28.941))


if __name__ == '__main__':
    test()
