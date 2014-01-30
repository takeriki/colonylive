"""
Image processing to measure growth kinetics of colony
"""

import os
import sys
import getpass
import numpy as np

from clive.db.manager import ExpManager
from clive.io.tmp import DIR_TMP
from clive.io.imgio import fetch_img_files, remove_img_files
from image.seqimg2colony import get_colonypack
from growth.colony2growth import get_growthpack
from growth.normalize import norm_growth


def image_analysis(expman):
    print "___ Image analysis ___"
    # load
    fetch_img_files(DIR_TMP, expman.exp.id)
    # calc
    path = "%s/%d" % (DIR_TMP, expman.exp.id)
    colonypack = get_colonypack(path, 48, 32)
    # submit to db
    expman.put_colonys(colonypack)
    expman.set_step_done(2)
    remove_img_files(DIR_TMP, expman.exp.id)


def growth_analysis(expman):
    print "___ Growth analysis ___"
    # load
    colonys = expman.get_colonys()
    poss = [(i.col, i.row) for i in colonys]
    times = map(int,expman.img.min_grows.split("|"))
    areas = [map(int,i.areas.split("|")) for i in colonys]
    cmasss = [map(float,i.cmasss.split("|")) for i in colonys]
    # calc
    growthpack = get_growthpack(poss, times, areas, cmasss)
    # upload
    expman.put_raw_growthpack(growthpack)
    expman.set_step_done(3)


def growth_normalize(expman):
    print "___ Growth normalization ___"
    # load
    ary = expman.get_raw_growth_ary()
    # calc
    dim = ary.shape[2]
    for i in range(dim):
        ary[:,:,i] = norm_growth(ary[:,:,i])
    # upload
    expman.put_growth_ary(ary)
    expman.set_step_done(4)


def execute(exp_id, step):
    expman = ExpManager(exp_id)
    try:
        expman.set_in_process(1)
        if step <= 1:
            image_analysis(expman)
        if step <= 2:
            growth_analysis(expman)
        if step <= 3:
            growth_normalize(expman)
        print "Succeed"
    except:
        expman.set_failure(1)
        print "Failed"
    finally:
        expman.set_in_process(0)


if __name__ == "__main__":
    argvs = sys.argv
    if len(argvs) != 3:
        print 'usage: %s [exp_id] [step number]' % argvs[0]
        quit()
    expid = int(argvs[1])
    p_num = int(argvs[2])
    print expid
    execute(expid, p_num)


