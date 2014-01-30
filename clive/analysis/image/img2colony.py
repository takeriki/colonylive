#!/usr/bin/python

import optparse

from clive.core.parameter import Parameter
from core.image import Image
from imgobj import get_objectmap
from grid import get_grid
from colony import get_colony

plate_fmt = 1536

print "object mapping"
img_color = Image()
img_color.load_file('45.tif')
img_gray = img_color.convert_to_gray()
ary_index_map = get_objectmap(img_gray)

print "make grid"
grid = get_grid(ary_index_map, plate_fmt)

print "determine and analyze colony"
gpos2colony = get_colony(ary_index_map, grid)

