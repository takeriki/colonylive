#!/usr/bin/python
#

import sys
import csv
import numpy as np

from clive.db.manager import ExpManager
from clive.io.tmp import DIR_TMP


def make_growth_csv(exp_id):
    expman = ExpManager(exp_id)
    growths = expman.get_growth()
    path = "%s/%d.csv" % (DIR_TMP, exp_id)
    #w = csv.writer(open(path,'wb'))
    txt = ''
    outs = [['Exp ID','Plate','Col','Row','Con','LTG','MGR','SPG']]
    txt = "\t".join(['Exp ID','Plate','Col','Row','Con','LTG','MGR','SPG'])
    txt += "\n"
    #w.writerow(head)
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
        txt += "\t".join(map(str,out))
        txt += "\n"
        #outs += [out]
        #w.writerow(out)
    
    #return outs
    return txt



if __name__ == "__main__":
    argvs = sys.argv
    if len(argvs) != 2:
        quit("usage: %s [exp_id] ['growth' or 'image']" % argvs[0])
    exp_id = int(argvs[1])
    make_growth_csv(exp_id)
