#!/usr/bin/python

import os
import sys
import getpass

from clive.core.manager import ExpManager


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


def remove_img_files(path):
    cmd = "rm -rf %s" % (path)
    os.system(cmd)


if __name__ == "__main__":
    exp_id = 1

    exp = ExpManager(exp_id)
    
    img_ids = [i.id for i in exp.imgs]
    get_image_files(exp_id, img_ids)

