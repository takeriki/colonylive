#!/usr/bin/python

import optparse

from part.image import Image
from objmap import get_objectmap
from setgrid import detect_grid
from colony import get_colony

ncol = 48
nrow = 32

print "object mapping"
img_color = Image()
img_color.load_file('sample/plate.jpg')
img_gray = img_color.convert_to_gray()
ary_index_map = get_objectmap(img_gray)

print "make grid"
grid = detect_grid(ncol, nrow, ary_index_map)

print "determine and analyze colony"
gpos2colony = get_colony(img_gray, ary_index_map, grid)

for gpos, colony in gpos2colony.items():
    print gpos, colony.area
