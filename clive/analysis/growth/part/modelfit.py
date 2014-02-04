"""
Compute three growth parameters by regression to growth model.

Growth parameters:
  LTG = lag time of growth
  MGR = maximum growth rate
  SPG = saturation point of growth
"""

import sys
import numpy as np
import matplotlib.pylab as plt
import rpy2.robjects as robj
import rpy2.robjects.numpy2ri

from clive.core.conf import Configure

cfg = Configure()
OD_LIM_QUANT = int(cfg[('growth','od_limit')])
NUM_POINTS = int(cfg[('growth','point_number_use')])
FRAC_LIM_IP = float(cfg[('growth','frac_limit_ip')])

# to avoid messages
np.seterr(invalid='raise')
r = robj.r
r('options(warn=-1)')


def model_fitting(xs, ys, plot=0):
    """
    Perform nonlinear regression with R function (via rpy2).
    
    xs: times
    ys: growth values

    """
    robj.globalenv['x'] = robj.IntVector(xs)
    robj.globalenv['y'] = robj.FloatVector(ys)
    r('res <- NULL')
    #r('tryCatch(res <- nls(y~SSlogis(x, a, b, c)), error=function(e) stop)')
    r('tryCatch(res <- nls(y~SSgompertz(x, a, b, c)), error=function(e) stop)')
    a, b, c = r('coef(res)')
    ltg = (np.log(1/b)+1)/np.log(c)
    mgr = -a * np.log(c) / np.exp(1)
    spg = a
    
    # Is the inflection point in measured period?
    ti = np.log(1/b)/np.log(c)
    t_sta, t_fin = xs[0], xs[-1]
    t_cut = t_sta + ((t_fin-t_sta)*FRAC_LIM_IP)
    if ti > t_cut:
        mgr, spg = 0, 0

    ltg = round(ltg,1)
    mgr = round(mgr,5)
    spg = round(spg,3)
    
    if plot:
        r('px <- seq(0,1200,by=1)')
        pxs = np.array(list(r('px')))
        pys = np.array(list(r('predict(res, list(x=px))')))
        plt.plot(xs, ys, 'o')
        plt.plot(pxs, pys, '-k')
        plt.show()
    return (ltg, mgr, spg)


def prep_for_fitting(times, gcs):
    if sum(gcs) == 0:
        return [], []
    ts = np.array(times)
    vs = np.array(gcs)
    vs = vs - np.min(vs) 

    fts = ts[vs>OD_LIM_QUANT][:NUM_POINTS]
    fvs = vs[vs>OD_LIM_QUANT][:NUM_POINTS]
    return fts, fvs


def get_growth_parameters(times, gc):
    fts, fgs = prep_for_fitting(times, gc)
    # skip no growth 
    if len(fts) == 0:
        return (0, 0, 0)
    # do fitting
    try:
        return model_fitting(fts, fgs)
    except:
        return (0, 0, 0)
    

def test():
    times = "0|30|60|90|120|150|180|210|240|270|300|330|360|390|420|450|480|510|540|570|600|630|660|690|720|750|780|810|840|870|900|930|960|990|1020|1050|1080|1110|1140|1170|1200|1230|1261|1291|1321"
    gcs = "0.35|0.46|0.41|0.38|0.41|0.42|0.51|0.77|1.1|1.68|2.65|4.03|6.07|8.11|10.14|12.1|14.25|16.05|17.75|19.17|20.49|21.74|22.76|23.68|24.53|25.3|26.0|26.68|27.3|27.84|28.36|28.85|29.58|29.8|30.23|30.66|31.06|31.44|31.88|32.04|32.59|32.85|33.18|33.52|33.96"
    times = [int(i) for i in times.split("|")]
    gcs = [float(i) for i in gcs.split("|")]
    gp = get_growth_parameters(times, gcs)
    print "LTG, MGR, SPG = " + str(gp)
    assert(gp[0]>0)
    assert(gp[1]>0)
    assert(gp[2]>0)


if __name__ == '__main__':
    test()
