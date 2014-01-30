"""
Set colony grid on a plate 

"""

import cPickle

import numpy as np
import matplotlib.pylab as plt

from lib.grid import PlateGrid
from lib.image import Image


# max_dif: limit value for diff sequence
# cont len = ratio for contiuous length
OBJECT_RATIO_ON_THE_GRID_LINE = 0.6
PERMIT_PIXEL_GAP = 3


def make_grid(ncol, nrow, m_pos):
    """
    make grid manually base on position info.
    """

    mpos_list = m_pos.split(',')
    (xLT, yLT, xRB, yRB) = [float(int(i)) for i in mpos_list]
    xy_init = (xLT, yLT)
    x_dif = (xRB - xLT) / (ncol - 1)
    y_dif = (yRB - yLT) / (nrow - 1)
    
    grid = PlateGrid(ncol, nrow, xy_init, x_dif, y_dif)
    self.calc_pos2xyCenter()
    grid.make_crippos()
    return grid


def detect_grid(ncol, nrow, ary_index_map):
    """
    detect grid automatically base on object map info
    """
    cys, cxs = np.where(ary_index_map<0)
    xy_centers = [(x,y) for x,y in zip(cxs, cys)]
    
    # x axis
    n_line = ncol # expect line number
    n_point = int(nrow * OBJECT_RATIO_ON_THE_GRID_LINE) # expect point number

    vs = sorted([i[0] for i in xy_centers])
    v_lines = _find_grid_lines(vs, n_point)
    x_dif = np.median(np.diff(v_lines))
    x_init = _get_init(v_lines, n_line)

    # y axis
    n_line = nrow
    n_point = int(ncol * OBJECT_RATIO_ON_THE_GRID_LINE)

    vs = sorted([i[1] for i in xy_centers])
    v_lines = _find_grid_lines(vs, n_point)
    y_dif = np.median(np.diff(v_lines))
    y_init = _get_init(v_lines, n_line)

    xy_init = (x_init, y_init)
    grid = PlateGrid(ncol, nrow, xy_init, x_dif, y_dif)
    return grid



def _find_grid_lines(vs, n_point):
    v_lines = []

    tmp = [vs[0]]
    for ind, d in enumerate(np.diff(vs)):
        if d > PERMIT_PIXEL_GAP:
            if len(tmp) > n_point:
                v_lines += [np.mean(tmp)] 
            tmp = [vs[ind+1]]
            continue
        tmp += [vs[ind+1]]
    if len(tmp) > n_point:
        v_lines += [np.mean(tmp)]
    return v_lines


def _get_init(vs, n_line):
    if len(vs) != n_line:
        '''
        if len(vs) > n:
            n_rm = len(vs) - n 
            vs_resi = np.array(vs)%xyDif[axis]
            vs_resi_ave = np.mean(vs_resi)
            ds = list(abs(vs_resi - vs_resi_ave))
            ds_rm = sorted(ds,reverse=True)[:n_rm]
            for ind, d in enumerate(ds):
                if d in ds_rm:
                    vs.pop(ind)
        '''
        print 'error of grid number:'
        print "expect: %d" % n
        print "actual: %d" % len(vs)
        quit()
    v_init = vs[0]
    return int(v_init)



def draw_grid_lines(grid):
    lines = grid.make_lines()
    img_color = Image()
    img_color.load_file('45.tif')

    x_sta, y_sta = grid.xy_init
    x_end = int(x_init + (grid.ncol-1) * grid.x_dif)
    y_end = int(y_init + (grid.nrow-1) * grid.y_dif)
    x_dif = grid.x_dif
    y_dif = grid.y_dif
    lines = []
    for col in range(1,grid.ncol+1):
        x = int(x_sta + grid.x_dif * (col-1))
        line = ((x, y_sta), (x, y_end))
        lines.append(line)
    for row in range(1,grid_nrow+1):
        y = int(y_sta + grid.y_dif * (row-1))
        line = ((x_sta, y), (x_end, y))
        lines.append(line)

    img_color.draw_lines(lines)
    img_color.save_to_file()


if __name__ == "__main__":
    ncol = 48
    nrow = 32
    ary_index_map = np.load('index_map.npy')
    grid = detect_grid(ncol, nrow, ary_index_map)
    print grid.xy_init
    quit()

    draw_grid_lines(grid)

    f = open('dump-grid.pkl','wb')
    cPickle.dump(grid, f)
    f.close()
