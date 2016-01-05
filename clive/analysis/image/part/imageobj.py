#!/usr/bin/python

import cv
import numpy as np

import motsu
import cPickle

import matplotlib.pylab as plt

from image import Image

COLONY_AREA_LOWER_LIMIT = 20
COLONY_AREA_UPPER_LIMIT = 2000
ASPECTRATIO_UPPER_LIMIT = 0.6
CIRCULARITY_UPPER_LIMIT = 0.6

def get_all_imgobjs(img_binary):
    tmp = cv.CloneImage(img_binary.iplimg)
    contours = cv.FindContours(tmp,
        cv.CreateMemStorage(),
        method=cv.CV_CHAIN_APPROX_NONE)
    del tmp
    imgobjs = []
    while contours:
        imgobj = Imgobject(contours)
        if imgobj.is_colony:
            imgobjs += [imgobj]
        contours = contours.h_next()
    del contours
    return imgobjs


class Imgobject():
    def __init__(self, contour):
        #self.contour = contour
        self.xys_edge = None
        self.xy_center = None
        try:
            self._calc(contour)
            self.is_colony = self._eval_colony_identity(contour)
        except:
            self.is_colony = 0

    def _calc(self, contour):
        self.xys_edge = [i for i in contour]
        # centroid
        m = cv.Moments(contour)
        m00 = cv.GetSpatialMoment(m,0,0)
        m01 = cv.GetSpatialMoment(m,0,1)
        m10 = cv.GetSpatialMoment(m,1,0)
        cx = int(m10/m00); cy = int(m01/m00)
        self.xy_center = (cx, cy)

    def _eval_colony_identity(self, contour):
        area = cv.ContourArea(contour)
        rect = cv.BoundingRect(contour)
        aspectratio = float(rect[2])/float(rect[3])
        circ = cv.ArcLength(contour)
        circularity = 4 * 3.14 * area / (circ ** 2)
        if area < COLONY_AREA_LOWER_LIMIT:
            return 0
        if area > COLONY_AREA_UPPER_LIMIT:
            return 0
        if abs(1. - aspectratio) > ASPECTRATIO_UPPER_LIMIT:
            return 0
        if abs(1. - circularity) > CIRCULARITY_UPPER_LIMIT:
            return 0
        return 1


if __name__ == "__main__":
    img_color = Image()
    img_color.load_file('45.tif')

    img_gray = img_color.convert_to_gray()
    ary_index_map = get_imgobj(img_gray)
    np.save('index_map', ary_index_map)
    
