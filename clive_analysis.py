#!/usr/bin/env python2
# -*- coding:utf-8 -*-

"""
解析用プログラム

現状では1536のみに対応

"""

import os
import sys
import numpy as np


from clive.db.schema import Exp, Colony, Growth, Ngrowth
from clive.db.pack import mput_colonys, mput_growths
from clive.db.search import get_colonys_by_exp_id, get_growths_by_exp_id
from clive.core.conf import Configure
from clive.analysis.image.seqimg2colony import analyze_pos_seqimgs
from clive.analysis.growth.colony2growth import get_growth_pars, get_ind
from clive.analysis.growth.normalize import norm_growth

cfg = Configure()
FOLDER_IMG_STORE = cfg[('folder','img_store')]
DIR_TMP = "/tmp/colonylive/"
MINUTES_FIXED = int(cfg[('growth','min_fixed_time_point')])


def image_analysis(exp):
    print "___ Image analysis ___"
    # prepare files
    print "fetching image..."
    if not os.path.exists(DIR_TMP):
        cmd = "mkdir -p %s" % DIR_TMP
        os.system(cmd)
    zip_file = "%s%d.zip" % (FOLDER_IMG_STORE, exp.id)
    if not os.path.exists(DIR_TMP+"%d" % exp.id):
        cmd = "unzip -q -d %s %s" % (DIR_TMP, zip_file)
        os.system(cmd)
    # calc
    imgfld = "%s%d" % (DIR_TMP, exp.id)
    ncol = 48; nrow = 32
    mlpos2data = analyze_pos_seqimgs(imgfld, 48, 32)
    colonys = []
    for row in range(1, nrow+1):
        for col in range(1, ncol+1):
            pos = (col, row)
            colony = Colony()
            colony.exp_id = exp.id
            colony.col, colony.row = col, row
            colony.location = mlpos2data[pos, 0]
            colony.areas = mlpos2data[pos, 1]
            colony.masss = mlpos2data[pos, 2]
            colony.cmasss = mlpos2data[pos, 3]
            colonys += [colony]
    # upload to db
    mput_colonys(colonys)
    exp.step_done = 2
    exp.update()
    # cleanup 
    cmd = "rm -rf %s" % (imgfld)
    os.system(cmd)


def growth_analysis(exp):
    print "___ Growth analysis ___"
    # load
    times = map(int,exp.mins_grow.split("|"))
    ind_fix = get_ind(times, MINUTES_FIXED)
    colonys = get_colonys_by_exp_id(exp.id)
    n = len(colonys)
    growths = []
    for i, colony in enumerate(colonys):
        # show progress
        sys.stdout.write("\r")
        sys.stdout.write("Fitting.\t[%-30s]" % ("="*int((i+1)*30/n)))
        sys.stdout.flush()
        # make instance
        growth = Growth()
        growth.exp_id = exp.id
        growth.col, growth.row = colony.col, colony.row
        # calc
        areas = map(int,colony.areas.split("|"))
        growth.con = areas[ind_fix]
        masss = map(float,colony.cmasss.split("|"))
        ltg, mgr, spg = get_growth_pars(times, masss)
        growth.ltg, growth.mgr, growth.spg = ltg, mgr, spg
        growths += [growth]
    sys.stdout.write("\n")
    # upload to db
    mput_growths(growths) 
    exp.step_done = 3
    exp.update()


def growth_normalize(exp):
    print "___ Growth normalization ___"
    # load
    growths = get_growths_by_exp_id(exp.id)
    ncol = 48; nrow = 32; ndim = 4
    ary = np.zeros((nrow, ncol, ndim))
    for growth in growths:
        ary[growth.row-1, growth.col-1, 0] = growth.con
        ary[growth.row-1, growth.col-1, 1] = growth.ltg
        ary[growth.row-1, growth.col-1, 2] = growth.mgr
        ary[growth.row-1, growth.col-1, 3] = growth.spg
    # calc
    for i in range(ndim):
        ary[:,:,i] = norm_growth(ary[:,:,i])
    ngrowths = []
    for growth in growths:
        ngrowth = Ngrowth()
        ngrowth.exp_id = exp.id
        ngrowth.col, ngrowth.row = growth.col, growth.row
        ngrowth.con = ary[growth.row-1, growth.col-1, 0]
        ngrowth.ltg = ary[growth.row-1, growth.col-1, 1]
        ngrowth.mgr = ary[growth.row-1, growth.col-1, 2]
        ngrowth.spg = ary[growth.row-1, growth.col-1, 3]
        ngrowths += [ngrowth]
    # upload to db
    mput_growths(ngrowths)
    exp.step_done = 4
    exp.update()


def execute(exp_id):
    exp = Exp(exp_id)
    try:
        exp.in_process = 1
        exp.update()

        if exp.step_done <= 1:
            image_analysis(exp)
        if exp.step_done <= 2:
            growth_analysis(exp)
        if exp.step_done <= 3:
            growth_normalize(exp)
    except Exception as e:
        exp.failure = 'yes'
        exp.update()
        print str(e)
    finally:
        exp.in_process = 0
        exp.update()
        print "Succeed"


if __name__ == "__main__":
    argvs = sys.argv
    if len(argvs) != 2:
        print 'usage: %s [exp_id]' % argvs[0]
        quit()
    expid = int(argvs[1])
    execute(expid)

