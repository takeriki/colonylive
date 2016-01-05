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
from clive.scan.imgcrip import clip_scanimg
from clive.core.conf import Configure


TEST_MODE = 1

cfg = Configure()
SCANNER_IDS = map(int,cfg[('scan','scanner_ids')].split(","))
VERSION = cfg[('core','version')]
FOLDER_SCAN = cfg[('folder','img_scan')]
FOLDER_TMP = cfg[('folder','img_tmp')]
FOLDER_IMG_STORE = cfg[('folder','img_store')]


def main(imgscanid, n_scan):
    # imgscanの発行
    imgscan = Imgscan(imgscanid)
    path_scanimg = "%s%d.tif" % (FOLDER_SCAN, imgscan.id)
    
    # Split image
    tmpimgs = []
    for expid in map(int,imgscan.split("|")):
        fld_tmpimg = "%s%d.tif" % (FOLDER_TMP, expid)
        prep_fld(fld_tmpimg)
        path_tmpimg = "%s%d/%d-%04d.tif" % (
            FOLDER_TMP, expid, expid, n_scan)
        path_tmpimgs += [path_tmpimg]
        
    tmpimgs = [ExpTmpImgIO(i) for i in exp_ids]
    n_scan = len(min_grows) - 1
    path_outs = [i.get_path(n_scan) for i in tmpimgs]
    clip_scanimg(path_scanimg, path_outs, cfg)
    
    print
    print "DONE"


def make_new_img(scanner):
    dt_now = datetime.datetime.now()
    imgscan = Imgscan()
    imgscan.set_maxid()
    imgscan.dt_scan = dt_now
    imgscan.scanner_id = scanner.id
    imgscan.exp_ids = scanner.exp_ids
    imgscan.insert()
    return imgscan


def store_images(scanner):
    exp_ids = map(int, scanner.exp_ids.split("|"))
    for exp_id in exp_ids:
        store_tmp_images(exp_id)
        img_handler.create(
            exp_id, scanner.id, scanner.min_grows)
        expman = ExpManager(exp_id)
        expman.set_in_process(0)
        expman.set_step_done(1)


if __name__ == "__main__":
    main()
