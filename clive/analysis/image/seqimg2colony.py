#!/usr/bin/python

import os
import sys

from part.image import Image
from objmap import get_objectmap
from setgrid import detect_grid
from colony import get_colony


#def get_colonypack(path, ncol, nrow):
def analyze_pos_seqimgs(path, ncol, nrow):
    cwd = os.getcwd()
    os.chdir(path)
    fnames = sorted(os.listdir('.'))
    
    fname = fnames[-1]
    sys.stdout.write("Pre-scanning...")
    sys.stdout.flush()
    img_color = Image()
    img_color.load_file(fname)
    img_gray = img_color.convert_to_gray()

    ary_index_map = get_objectmap(img_gray)
    grid = detect_grid(ncol, nrow, ary_index_map)
    gpos2colony = get_colony(img_gray, ary_index_map, grid)
    
    n = len(fnames)
    mlpos2data = {} # Multilayer
    for pos, colony in gpos2colony.items():
        mlpos2data[pos, 0] = _to_str(colony.location)
        mlpos2data[pos, 1] = []
        mlpos2data[pos, 2] = []
        mlpos2data[pos, 3] = []
    #cp = ColonyPack(gpos2colony)
    for i, fname in enumerate(fnames):
        sys.stdout.write("\r")
        sys.stdout.write("Image analysis\t[%-30s]" % ("="*int((i+1)*30/n)))
        sys.stdout.flush()
        img_color.load_file(fname)
        img_gray = img_color.convert_to_gray()
        ary_img = img_gray.get_array()
        for gpos in sorted(grid.poss):
            #gpos2colony[gpos].load_img(ary_img)
            colony = gpos2colony[gpos]
            colony.load_img(ary_img)
            mlpos2data[gpos,1] += [colony.area]
            mlpos2data[gpos,2] += [colony.mass]
            mlpos2data[gpos,3] += [colony.mass]
            #cp.add(gpos, colony)
    for gpos in sorted(grid.poss):
        mlpos2data[gpos,1] = _to_str(mlpos2data[gpos,1])
        mlpos2data[gpos,2] = _to_str(mlpos2data[gpos,2])
        mlpos2data[gpos,3] = _to_str(mlpos2data[gpos,3])
    print  
    #cp.pack()
    os.chdir(cwd)
    #return cp
    return mlpos2data


def _to_str(vs):
    return "|".join(map(str, vs))

class ColonyPack():
    
    def __init__(self, pos2colony):
        poss = sorted(pos2colony.keys(), key=lambda x:(x[1],x[0]))
        self.poss = poss
        self.pos2location = {}
        self.pos2areas = {}
        self.pos2masss = {}
        self.pos2cmasss = {}
        for pos, colony in pos2colony.items():
            self.pos2location[pos] = self._to_str(colony.location)
            self.pos2areas[pos] = []
            self.pos2masss[pos] = []
            self.pos2cmasss[pos] = []

    def add(self, pos, colony):
        self.pos2areas[pos] += [colony.area]
        self.pos2masss[pos] += [colony.mass]
        self.pos2cmasss[pos] += [colony.cmass]
    
    def pack(self):
        for pos in self.poss:
            self.pos2areas[pos] = self._to_str(self.pos2areas[pos])
            self.pos2masss[pos] = self._to_str(self.pos2masss[pos])
            self.pos2cmasss[pos] = self._to_str(self.pos2cmasss[pos])

    def _to_str(self, vs):
            s = "|".join(map(str, vs))
            return s


if __name__ == "__main__":
    ncol = 48
    nrow = 32
    path = "/tmp/clive-morilab/1"
    cp = get_colonypack(path, ncol, nrow)

    pos = (1,1)
    print cp.pos2location[pos]
    print cp.pos2areas[pos]
    print cp.pos2masss[pos]
    print cp.pos2cmasss[pos]
    print len(cp.pos2cmasss[pos])


