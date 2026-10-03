"""Analytic fabric tension folds, authored independently of the reference pixels."""
from math import exp, sin, cos, pi

def fold_field(x,z):
    # Each tuple is a tapered diagonal crease: center x/z, slope, length, width, depth.
    lines=[(-.37,4.25,-1.5,.30,.023,.034),(.35,4.28,1.4,.35,.024,.040),
           (-.26,4.77,1.9,.25,.018,.022),(.38,4.92,-1.1,.22,.020,.024),
           (-.12,3.97,-1.6,.17,.018,.025),(.37,3.98,1.3,.21,.022,.024)]
    out=0.0
    for cx,cz,slope,length,width,depth in lines:
        dx=x-cx; dz=z-cz
        norm=(1+slope*slope)**.5
        across=(dz-slope*dx)/norm
        along=(dx+slope*dz)/norm
        taper=exp(-(along/length)**4)
        out+=depth*(exp(-(across/width)**2)-.55*exp(-((across-width*1.25)/(width*1.3))**2))*taper
    return out
