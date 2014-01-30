#!/usr/bin/python
"""
one scan image -- crip & rotate --> plate images.

"""

import os
import sys
import Image

from clive.core.conf import Configure
cfg = Configure()
NUM_PIX_HOR = int(cfg[('pixel','plate_horizontal')])
NUM_PIX_VER = int(cfg[('pixel','plate_vertical')])
FOLDER_SCAN = cfg['folder','img_scan']
tmp = cfg[('scan','crip_parameter')].split("|")
CRIP_PARS = [map(float, i.split(",")) for i in tmp]

def crip_plate_img(angle, x_crip, y_crip, path_img_in, path_img_out):
    img = Image.open(path_img_in)
    # rotate angle is counter clockwise
    r_img = img.rotate(-angle, Image.NEAREST, 1)
    # crop position need tuple: (left, top, right, down)
    rc_img = r_img.crop((\
        x_crip,\
        y_crip,\
        x_crip + NUM_PIX_HOR,\
        y_crip + NUM_PIX_VER))
    rc_img.save(path_img_out)
    # copy file information to new image from original image
    cmd = "touch -r %s %s" % (path_img_in, path_img_out)
    os.system(cmd)


#def main(img_scan_id, img_ids):
def split_img_scan(img_scan_id, fpaths):
    fname_in  = FOLDER_SCAN + '%d.tif' % img_scan_id
    outs = []
    #for ind_pos, img_id in enumerate(img_ids):
    for ind_pos, fpath_out in enumerate(fpaths):
        (angle, x_crip, y_crip) = CRIP_PARS[ind_pos]
        crip_plate_img(angle, int(x_crip), int(y_crip), fname_in, fpath_out)
        outs += [fpath_out]
    return outs


if __name__ == '__main__':
    argvs = sys.argv
    if len(argvs) != 3:
        print "Usage:"
        print "%s [img_scan_id] [img_id1|img_id2|..]" % argvs[0]
        print
        quit()
    
    img_scan_id = int(argvs[1])
    img_ids = [int(i) for i in argvs[2].split("|") if i != '']
    split_img_scan(img_scan_id, img_ids)

