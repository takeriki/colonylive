#!/usr/bin/env python2
# -*- coding:utf-8 -*-

"""
CRON用 自動解析プログラム

10 Processで並列処理(multiprocessing module)
"""


#import multiprocessing as mp

N_PROC = 10

from clive.db.search import get_unprocessed_exp_ids

exp_ids = get_unprocessed_exp_ids()

print len(exp_ids)

def perform(cmds):
    for cmd in cmds:
        print cmd


"""
def perform(cmds):
    for cmd in cmds:
        print cmd
        try:
            cmd()
        except:
            pass


#pool = mp.Pool(N_PROC)
#pool.map(perform, cmds)
"""
