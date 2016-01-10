#!/usr/bin/env python2
# -*- coding:utf-8 -*-


from clive.scan.imgcrip import clip_scanimg
from clive.core.conf import Configure

cfg = Configure()

path_scanimg = "sample.tif"
path_outs = ['1.tif','2.tif','3.tif','4.tif']
clip_scanimg(path_scanimg, path_outs, cfg)

