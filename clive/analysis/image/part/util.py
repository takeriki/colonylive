#!/usr/bin/python

import numpy as np

def clip_img(ary, cripinfo):
    x, y, length = cripinfo
    return ary[y:y+length+1, x:x+length+1]

def get_peak_intensity(ary):
    binary = np.bincount(ary)
    ind_max = np.where(binary==max(binary))[0][0]
    ary = np.array(ary, dtype=int)
    oi = np.mean(np.sort(ary[np.abs(ary-ind_max)<=1]))
    return oi


def get_bg(ary_img, ary_index_map, grid):
    reg = np.zeros(ary_img.shape)
    reg[grid.xyTL[1]:grid.xyBR[1],grid.xyTL[0]:grid.xyBR[0]] = 1
    ind = (ary_index_map==0) * (reg==1)
    ary = ary_img[ind]
    
    oi_bg = get_peak_intensity(ary)
    #n = np.size(ary)
    #bg = np.mean(np.sort(ary)[n*0.2:n*0.8])
    return oi_bg
