#!/usr/bin/python2
"""
one scan image --> several plate images.

"""

import os
import sys
import math
import cv2


def clip_scanimg(fpath_in, fpath_outs, cfg):
    ary = cv2.imread(fpath_in)
    npos = int(cfg[('scanlayout','number')])

    clipinfos = []
    for pos in range(1,npos+1):
        tmp = cfg[('scanlayout','%d' % pos)].split("|")
        xy_corners = [map(int,i.split("-")) for i in tmp[0].split("/")]
        num_rot = int(tmp[1])  
        deg = float(tmp[2])
        clipinfos += [(xy_corners, num_rot, deg)]

    for fpath_out, clipinfo in zip(fpath_outs, clipinfos):
        print fpath_out
        cary = clip_img(ary, clipinfo)
        cv2.imwrite(fpath_out, cary)
        cmd = "touch -r %s %s" % (fpath_in, fpath_out)
        os.system(cmd)


def clip_img(ary, clipinfo):
    xy_corners, num_rot, deg = clipinfo
    xmin = min([x for x,y in xy_corners])
    ymin = min([y for x,y in xy_corners])
    xmax = max([x for x,y in xy_corners])+1
    ymax = max([y for x,y in xy_corners])+1
    
    xy_lt, xy_lb, xy_rt, xy_rb = xy_corners
    xlen = int(math.ceil((xy_rt[0] - xy_lt[0])\
            / math.cos(math.radians(deg))))
    ylen = int(math.ceil((xy_rb[1] - xy_rt[1])\
            / math.cos(math.radians(deg))))
    
    # clip
    cary = ary[ymin:ymax, xmin:xmax]
    
    # rotate
    rcary = cary.copy()
    for i in range(num_rot):
        rcary = cv2.transpose(rcary)

    if deg != 0:
        rmat = cv2.getRotationMatrix2D(
            (rcary.shape[1]/2,rcary.shape[0]/2), deg, 1.0)
        tmp = cv2.warpAffine(rcary, rmat, (rcary.shape[1], rcary.shape[0]))
        dx = (tmp.shape[0] - xlen)/2
        dy = (tmp.shape[1] - ylen)/2
        rcary = tmp[dx:-dx,dy:-dy,:]
    return rcary


if __name__ == '__main__':
    argvs = sys.argv
    if len(argvs) != 3:
        print "Usage %s [scanimg] [plateimg1|..2|..]" % argvs[0]
        quit()
    fpath_in = argvs[1] 
    fpath_outs = [i for i in argvs[2].split("|")]
    clip_scanimg(fpath_in, fpath_outs)

