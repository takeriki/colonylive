"""
Normalize growth values in a plate

Required module:  numpy, rpy2

The program execute following normalization (in order)
  1) Plate normalization
  2) Spatial normalization
  3) Row/Col normalization

Ref) Nature Methods 7, 1017-1024 (2010) doi:10.1038/nmeth.1534
"""

import numpy as np
import matplotlib.pylab as plt
import scipy.signal

# parameters
SIZE_MED_FILT = 7  # 7x7
SIZE_AVE_FILT = 10 # 10x10

def norm_growth(ary, refary=[]):
    """
    INPUT
      ary: numpy array (row, column, dim)

        sample array. 
        dim = number of types of growth value. e.g.) 2 dim = ltg, mgr

      refary: numpy array (row, column)

        reference ary for spatial normalization. 
        array size should be same to sample array.

    OUTPUT
      nary: numpy array (row, column, dim)
        
        normalized sample array.
    """
    if len(refary) == 0:
        refary = np.ones(ary.shape)
    check_plate(ary)
    ary = np.ma.masked_array(ary, ary==0)
    aryp = plate_norm(ary)
    aryps = spatial_norm(aryp, refary)
    arypsr = rowcol_norm(aryps)
    nary = np.round(arypsr,2)
    return nary


def check_plate(ary):
    if np.sum(ary == 0) > 100:
        print "Bad input: Death number > 100"
        quit()
    if 0 in np.median(ary, axis=1): # row
        print "Bad input: Row median == 0"
        quit()
    if 0 in np.median(ary, axis=0): # col
        print "Bad input: Col median == 0" 
        quit()


# Plate normalization
# PMM: Plate middle mean
def calc_pmm(vs):
    n = len(vs)
    ns = n * 0.2
    ne = n * 0.8
    vs_sort = np.sort(vs)
    pmm = np.mean(vs_sort[ns:ne])
    return pmm


def plate_norm(ary):
    ary_1d = ary.reshape(-1)
    pmm = calc_pmm(ary_1d)
    cary = ary / pmm
    return cary


# Spatial normalization
# for average filter
tmp = np.ones((SIZE_AVE_FILT,SIZE_AVE_FILT))
avgfilt = tmp/tmp.size
def spatial_norm(ary, refary):
    # calc med filt estimetes
    ary_log = np.ma.log(ary/refary)
    # median filter
    ary_m = scipy.signal.medfilt2d(ary_log, SIZE_MED_FILT)
    # average filter
    ary_ma = scipy.signal.convolve(ary_m, avgfilt, "same")
    cary = ary * (1/np.exp(ary_ma))
    return cary


# Row/Col normalization
def rowcol_norm(ary):
    ary[ary<=0] = 0
    # Column fit
    col_meds = np.median(ary, axis=0)
    crs_r = np.median(col_meds) / col_meds
    # Row fit
    row_meds = np.median(ary, axis=1)
    rrs_r = np.median(row_meds) / row_meds
    # normalize
    cary = np.zeros(ary.shape)
    for row in range(32):
        for col in range(48):
            cary[row,col] = ary[row,col] * rrs_r[row] * crs_r[col]
    return cary


def test():
    ary = np.ones((32,48))
    tmp = np.arange(1,33)/32.
    gra = np.repeat(tmp, 48).reshape((32,48))
    ary = ary * gra
    nary = norm_growth(ary)
    """
    plt.subplot(211)
    plt.imshow(ary)
    plt.subplot(212)
    plt.imshow(nary)
    plt.show()
    """
    assert(1)

if __name__ == "__main__":
    test()

