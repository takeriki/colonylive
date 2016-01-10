#!/usr/bin/env python2
# -*- coding:utf-8 -*-

"""
観測用プログラム

データベースのScanner表の情報を基に
経時的スキャンをおこなう
"""

import os
import time
import datetime

from clive.db.schema import Scanner, Imgscan, Exp
from clive.scan.gui_scan import gui_scan
from clive.scan.prep import prep_gui
from clive.scan.imgcrip import clip_scanimg
from clive.core.conf import Configure


TEST_MODE = 1


cfg = Configure()
MIN_CYCLE = int(cfg[('scan','min_cycle')])
SCANNER_IDS = map(int,cfg[('scan','scanner_ids')].split(","))
VERSION = cfg[('core','version')]
FOLDER_SCAN = cfg[('folder','img_scan')]
#FOLDER_TMP = cfg[('folder','img_tmp')]
FOLDER_IMG = cfg[('folder','img_store')]


def main():
    prep_gui()

    if TEST_MODE:
        while True:
            print '[test-mode]'
            #time.sleep(100)
            time.sleep(5)
            run()
    while True:
        dt_now = datetime.datetime.now()
        min_wait = MIN_CYCLE - (dt_now.minute % MIN_CYCLE)
        sec_past = dt_now.second
        time.sleep(min_wait*60 - sec_past)
        run()


def run():
    dt_now = datetime.datetime.now()
    dt_next = dt_now + datetime.timedelta(minutes=MIN_CYCLE)

    os.system('clear')
    print " cycle_scan.py     VERSION = " + VERSION
    print "---------------------------------------"
    print "DATE     : " + dt_now.strftime('%a, %d %b %Y')
    print "SCANNED  : " + dt_now.strftime('%H:%M')
    print "Next SCAN: " + dt_next.strftime('%H:%M')
    print 

    for sid in SCANNER_IDS:
        scanner = Scanner(sid)
        print "scanner%2d: " % int(scanner.id),

        # スキャンの判定
        if scanner.dt_finish == None:
            print "None"
            continue

        dt_now = datetime.datetime.now()
        expids = map(int, scanner.exp_ids.split("|"))

        # ストップ判定と処理
        if scanner.dt_finish < dt_now:
            print "Complete!!"
            for expid in expids:
                exp = Exp(expid)
                exp.in_process = 0
                exp.step_done = 1
                exp.update()
            scanner.clean()
            continue
        
        # imgscanの発行
        imgscan = make_new_imgscan(scanner)
        path_scanimg = "%s%d.tif" % (FOLDER_SCAN, imgscan.id)
        
        # scan
        print "%s; " % scanner.person_name,
        print "until %s " % scanner.dt_finish.strftime('%a, %d %b %Y'),
        ind = SCANNER_IDS.index(scanner.id) + 1
        fail = gui_scan(ind, path_scanimg, cfg) 
        if fail:
            print "[Faild]"
            continue
        print "[Success]"

        min_grows = scanner.min_grows.split("|")
        min_grows += [imgscan.min_grow]
        scanner.min_grows = "|".join(map(str,min_grows))
        n_scan = len(min_grows)

        path_outs = [get_path(i, n_scan) for i in expids]
        clip_scanimg(path_scanimg, path_outs, cfg)
    
    print
    print "DONE"


def get_path(expid, n_scan):
    fld = "%s%d" % (FOLDER_IMG, expid)
    if not os.path.isdir(fld):
        os.system("mkdir -p %s" % fld)
    path = "%s/%d-%04d.tif" % (fld, expid, n_scan)
    return path


def make_new_imgscan(scanner):
    dt_now = datetime.datetime.now()
    imgscan = Imgscan()
    imgscan.set_maxid()
    imgscan.dt_scan = dt_now
    imgscan.scanner_id = scanner.id
    imgscan.exp_ids = scanner.exp_ids
    imgscan.min_grow = _get_min_grow(scanner, dt_now)
    imgscan.insert()
    return imgscan


def _get_min_grow(scanner, dt_now):
    dif = dt_now - scanner.dt_start
    min_grow = (dif.days * 86400 + dif.seconds) / 60
    return min_grow


if __name__ == "__main__":
    main()
