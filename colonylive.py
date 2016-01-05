#!/usr/bin/env python2
# -*- coding:utf-8 -*-


"""
colonylive

アプリの起動


"""

from subprocess import call
from multiprocessing import Process


def start_scan():
    call(["clive_scan"])

def start_web():
    call(["clive_web"])

def start_analysis():
    call(["clive_analysis"])


jobs = []
jobs += [Process(target=start_web, )]
jobs += [Process(target=start_scan, )]
jobs += [Process(target=start_analysis, )]

for j in jobs:
    j.start()
for j in jobs:
    j.join()

print "stop"
