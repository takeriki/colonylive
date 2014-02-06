"""
setup scan layout

"""

import sys
import math
import cv2
import numpy as np
import matplotlib.pylab as plt
from matplotlib import interactive
interactive(True)

from clive.core.conf import Configure
cfg = Configure()

def main(fpath):
    ary = cv2.imread(fpath)
    contours = get_red_contours(ary)
    n_plates = len(contours)
    print "Detected plate number:", n_plates
    while True:
        ans = raw_input("Correct? [yes, no]: ")
        if ans == "yes":
            break
        if ans == "no":
            quit("Please check layout image")
    print "-----------------"
    
    selects = ['top', 'left', 'right', 'bottom']
    sel2num_rot = {
        'top':0,
        'right':1,
        'bottom':2,
        'left':3
    }
    plt.imshow(ary)
    print "Which direction is the upper side of plate?"
    while True:
        ans = raw_input("%s: " % selects)
        if ans in selects:
            num_rot = sel2num_rot[ans]
            break
    print "-----------------"

    posids = set(range(1,n_plates+1))
    cfg[('scanlayout','number')] = n_plates
    for contour in contours:
        tary = ary.copy()
        xy_center = get_center(contour)
        xy_corners = get_corners(contour)
        deg = get_adj_degree(xy_corners)
       
        xypos = tuple(map(int,xy_center))
        cv2.circle(tary, xypos, 50, (255,0,0), -1)
        plt.imshow(tary)
        while True:
            ans = raw_input("Input position ID  %s: " % list(posids))
            try:
                posid = int(ans)
            except: 
                continue
            if posid in posids:
                posids.remove(posid)
                break
        tmp = ["-".join(map(str,i))
                for i in xy_corners]
        xy_corners_str = "/".join(tmp)
        layout = "|".join(map(str, 
            [xy_corners_str, num_rot, deg]))
        cfg[('scanlayout','%d'%posid)] = layout
    cfg.update()
    print "-----------------"


def get_red_contours(ary):
    # get RED channel specific value
    tmp = np.array(ary,dtype=int)
    tary = tmp[:,:,2]-tmp[:,:,1]-tmp[:,:,0]
    tary[tary!=255] = 0
    tary = np.array(tary,dtype=np.uint8)

    # find contours
    t, bary = cv2.threshold(
        tary, 230, 255, cv2.THRESH_BINARY)
    contours, hie = cv2.findContours(
        bary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    return contours

    
def get_center(contour):
    m = cv2.moments(contour)
    cx = m['m10']/m['m00']
    cy = m['m01']/m['m00']
    return (cx,cy)

def get_corners(contour):
    cx, cy = get_center(contour)
    xys = [list(i[0]) for i in contour]
    xmin = min([x for x,y in xys])
    ymin = min([y for x,y in xys])
    xmax = max([x for x,y in xys])
    ymax = max([y for x,y in xys])
    
    ys = [y for x,y in xys if x == xmin]
    # not inclined plate
    if len(ys) > 100:
        ys = [y for x,y in xys if x == xmin]
        xy_lt = (xmin, min(ys))
        xy_lb = (xmin, max(ys))
        ys = [y for x,y in xys if x == xmax]
        xy_rt = (xmax, min(ys))
        xy_rb = (xmax, max(ys))
        return xy_lt, xy_lb, xy_rt, xy_rb
    # inclined plate
    yleft = int(np.median([y for x,y in xys if x==xmin]))
    yright = int(np.median([y for x,y in xys if x==xmax]))
    xtop = int(np.median([x for x,y in xys if y==ymin]))
    xbottom = int(np.median([x for x,y in xys if y==ymax]))
    if yleft < yright:
        xy_rt = (xtop, ymin)
        xy_lt = (xmin, yleft)
        xy_lb = (xbottom, ymax)
        xy_rb = (xmax, yright)
    else:
        xy_lt = (xtop, ymin)
        xy_rt = (xmax, yright)
        xy_lb = (xmin, yleft)
        xy_rb = (xbottom, ymax)
    return xy_lt, xy_lb, xy_rt, xy_rb


def get_adj_degree(xy_corners):
    xy_lt, xy_lb, xy_rt, xy_rb = xy_corners
    x_len = (xy_rt[0] - xy_lt[0])
    y_len = (xy_rb[1] - xy_rt[1])
    dx = xy_rb[0] - xy_rt[0]
    dy = xy_rt[1] - xy_lt[1]
    if x_len > y_len:
        deg = math.degrees(math.atan2(dy,x_len))
    else:
        deg = math.degrees(math.atan2(dx,y_len))
    return round(deg,2)


if __name__ == "__main__":
    argvs = sys.argv
    if len(argvs) != 2:
        quit("%s [layout image file]" % argvs[0])
    fpath = argvs[1]
    main(fpath)

#cv2.putText(tary, "test", xypos, cv2.FONT_HERSHEY_SIMPLEX, 5, (0,0,0), 10)
#cv2.imwrite('test.png', ary)

