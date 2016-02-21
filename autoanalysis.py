#!/usr/bin/env python2
# -*- coding:utf-8 -*-

"""
解析用プログラム


Routine analysis (automatic)

"""

import time
import datetime

from clive.db.handler import ExpHandler
from clive.analysis.process import execute

exp_handler = ExpHandler()


def perform():
    while True:
        exps = exp_handler.get_unprocess_exps()
        print "Analysis targets:", exps
        for exp in exps:
            if exp.id != 1:
                continue
            execute(exp.id, exp.step_done)    

        _wait_until_midnight()
    

def _wait_until_midnight():
    dt = datetime.datetime.now()
    tsec_now = dt.hour * 3600 + dt.minute * 60 + dt.second
    tsec_day = 24 * 3600
    sec_wait = tsec_day - tsec_now
    time.sleep(sec_wait)


if __name__ == "__main__":
    perform()

