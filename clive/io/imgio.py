#!/usr/bin/python

import os
import sys
import getpass

from clive.db.manager import ExpManager

"""
def get_img_files(path, img_ids):
    if not os.path.exists(path):
        cmd = "mkdir -p %s" % path 
        os.system(cmd)

    n = len(img_ids)
    for i, img_id in enumerate(img_ids):
        sys.stdout.write("\r")
        sys.stdout.write("Fetch images\t[%-30s]" % ("="*int((i+1)*30/n)))
        sys.stdout.flush()
        
        fname = "%d.tif" % img_id
        if os.path.isfile("%s/%s" % (path, fname)):
            continue 
        cmd = "scp -q gi-bioserv:img/%s.bz2 %s/" % (fname, path)
        os.system(cmd)
        cmd = "bzip2 -d %s/%s.bz2" % (path, fname)
        os.system(cmd)
    print
"""


def fetch_img_files(path_in, exp_id):
    if not os.path.exists(path_in):
        cmd = "mkdir -p %s" % path_in
        os.system(cmd)
    
    print "fetching image..."
    if not os.path.exists(path_in+"/%d"%exp_id):
        #cmd = "scp -q gi-bioserv:img/%d.tar %s/" % (exp_id, path_in)
        cmd = "scp -q gi-bioserv:/ngs/clive/img/%d.tar %s/" % (exp_id, path_in)
        os.system(cmd)
        
        cwd = os.getcwd()
        os.chdir(path_in)
        fname = "%s/%d" % (path_in, exp_id)
        cmd = "tar xf %s.tar && rm %s.tar" % (fname, fname)
        os.system(cmd)
        cmd = "bzip2 -d %s/*" % (fname)
        os.system(cmd)
        os.chdir(cwd)


def remove_img_files(path_in, exp_id):
    cmd = "rm -rf %s/%d" % (path_in, exp_id)
    os.system(cmd)


def compress_file(path):
    cmd = "bzip2 -9 %s" % (path)
    os.system(cmd)


def decompress_file(path):
    cmd = "bzip2 -d %s.bz2" % (path)
    os.system(cmd)


if __name__ == "__main__":
    exp_id = 1

    exp = ExpManager(exp_id)
    
    img_ids = [i.id for i in exp.imgs]
    get_image_files(exp_id, img_ids)

