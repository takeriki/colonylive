#!/usr/bin/python

import os
import sys
import getpass

from clive.db.manager import ExpManager
from clive.core.conf import Configure

cfg = Configure()

FOLDER_SCAN = cfg[('folder','img_scan')]
FOLDER_TMP = cfg[('folder','img_tmp')]
FOLDER_IMG_STORE = cfg[('folder','img_store')]


class ExpImgIO():
    def fetch_img_files(self, path_in):
        if not os.path.exists(path_in):
            cmd = "mkdir -p %s" % path_in
            os.system(cmd)
        
        print "fetching image..."
        if not os.path.exists(path_in+"/%d"%self.exp_id):
            cmd = "scp -q gi-bioserv:/ngs/clive/img/%d.tar %s/" % (exp_id, path_in)
            os.system(cmd)
            
            cwd = os.getcwd()
            os.chdir(path_in)
            fname = "%s/%d" % (path_in, self.exp_id)
            cmd = "tar xf %s.tar && rm %s.tar" % (fname, fname)
            os.system(cmd)
            cmd = "bzip2 -d %s/*" % (fname)
            os.system(cmd)
            os.chdir(cwd)

    def remove_img_files(self, path_in):
        cmd = "rm -rf %s/%d" % (path_in, self.exp_id)
        os.system(cmd)

    def decompress_file(self, path):
        cmd = "bzip2 -d %s.bz2" % (path)
        os.system(cmd)


class ExpTmpImgIO():
    def __init__(self, exp_id):
        self.exp_id = exp_id

    def get_path(self, n_scan):
        fld = "%s%d" % (FOLDER_TMP, self.exp_id)
        if not os.path.exists(fld):
            cmd = "mkdir -p %s" % fld
            os.system(cmd)
        self.path = "%s%d/%d-%04d.tif" % (FOLDER_TMP, 
            self.exp_id, self.exp_id, n_scan)
        return self.path

    def push_folder(self):
        os.chdir(FOLDER_TMP)
        cmd = "tar cf %d.tar --remove-files %d" % (self.exp_id, self.exp_id)
        os.system(cmd)
        cmd = "scp -p %d.tar %s" % (self.exp_id, FOLDER_IMG_STORE)
        os.system(cmd)
        cmd = "rm %d.tar" % (self.exp_id)
        os.system(cmd)

    def compress(self):
        cmd = "bzip2 -9 %s" % (self.path)
        os.system(cmd)


class ScanImgIO():
    def __init__(self, imgscan_id):
        self.imgscan_id = imgscan_id
        self.path = "%s%d" % (FOLDER_SCAN, imgscan_id)


if __name__ == "__main__":
    exp_id = 1

    exp = ExpManager(exp_id)
    
    img_ids = [i.id for i in exp.imgs]
    get_image_files(exp_id, img_ids)

