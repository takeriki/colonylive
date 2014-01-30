#!/usr/bin/env python

"""
Keep reducing file number in the scan image folder

"""

from multiprocessing import Process

from clive.analysis.routine import perform

jobs = []
jobs += [Process(target=perform, )]

for j in jobs:
    j.start()
for j in jobs:
    j.join()

print "stop"
