#!/usr/bin/python
#

import sys
import commands
import numpy as np

from clive.db.manager import ExpManager
from clive.io.tmp import DIR_TMP


def make_growth_csv(exp_id):
    expman = ExpManager(exp_id)
    growths = expman.get_growth()
    
    txt = ",".join(['Exp ID','Plate','Col','Row','Con','LTG','MGR','SPG']) + "\n"
    for growth in growths:
        out = [
            expman.exp.id,
            expman.plate.id,
            growth.col,
            growth.row,
            growth.con,
            growth.ltg,
            growth.mgr,
            growth.spg
            ]
        txt += ",".join(map(str,out)) + "\n"
    return txt


def make_images_tar(exp_id):
    expman = ExpManager(exp_id)
    data = commands.getoutput("cat /home/morilab/rimg/%d.tar" % exp_id)
    return data


if __name__ == "__main__":
    argvs = sys.argv
    if len(argvs) != 3:
        quit("usage: %s [exp_id] ['growth' or 'image']" % argvs[0])
    exp_id = int(argvs[1])
    vtype = argvs[2]
    if vtype == "growth":
        print make_growth_csv(exp_id)
    if vtype == "image":
        print len(make_images_tar(exp_id))
