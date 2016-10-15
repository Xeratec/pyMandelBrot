#!/usr/bin/python
'''
@file fractal_func.py
@author Philip Wiese
@date 12 Okt 2016
@brief Calculates Mandelbrot set
'''

import time
import numpy as np

def mandelbrot_v2(re_min, re_max, im_min, im_max, max_betr, max_iter, res=400, cont=False):
    # Save Startime
    start_t = time.time()
    # ix and iy is an 2-dimensional array representing the pixels
    pix_y = int(round(res / (re_max - re_min) * (im_max - im_min)))
    pix_x = res
    px, py = np.mgrid[0:pix_x, 0:pix_y]
    # x, y are the values of the pixels
    x = np.linspace(re_min, re_max, pix_x)[px]
    y = np.linspace(im_min, im_max, pix_y)[py]
    c = x+complex(0,1)*y
    # No need of these variables bacuase we only use c    
    del x,y 
    img = np.zeros(c.shape, dtype= float)
    px.shape = py.shape = c.shape = pix_x*pix_y
    
    z = np.copy(c)
    for i in xrange(max_iter):
        if not len(z): break;
        np.multiply(z, z, z)
        np.add(z, c, z)
        # Create boolean array with all points that are bigger than <max_betr>
        rem = abs(z)>max_betr
        # Saves the value of <i+i> in img array for all escaped points
        if cont: img[px[rem], py[rem]] = (i+ 1) - np.log( np.log(abs(z[rem]) ) / 2 / np.log(2) ) / np.log(2)
        else: img[px[rem], py[rem]] = (i+ 1)
        # invert boolean array
        rem = -rem
        # remove all escaped points
        z = z[rem]
        px, py = px[rem], py[rem]
        c = c[rem]
        
    calc_t = time.time()-start_t
    return (img, calc_t)

def mandelbrot_v1_iter(c, max_betr, max_iter, cont=False):
    z = 0
    for i in xrange(max_iter):
        z = z * z + c
        if abs(z) > max_betr:
            if cont:
                log_zn = np.log(abs(z) ) / 2
                nu = np.log( log_zn / np.log(2) ) / np.log(2)
                return i + 1 - nu
            else:
                return (i + 1)
    return 0

def mandelbrot_v1(re_min, re_max, im_min, im_max, max_betr, max_iter, res=400, cont=False):
    # Save Startime
    start_t = time.time()
    # Setup X and Y Resulution in points
    pix_y = int(round(res / (re_max - re_min) * (im_max - im_min)))
    px = np.arange(res)
    py = np.arange(pix_y)
    # Calculate X and Y Values
    x = np.linspace(re_min, re_max, res)[px]
    y = np.linspace(im_min, im_max, pix_y)[py] 
    # Zero out 2-dim array
    img = np.zeros((len(y), len(x)))

    
    # Call Julia for all
    for ix in px:
        for iy in py:
            c = x[ix] + complex(0, 1 * y[iy])
            z = 0
            for i in xrange(max_iter):
                z *= z
                z += c
                if abs(z) > max_betr:
                    if cont:
                        log_zn = np.log(abs(z) ) / 2
                        nu = np.log( log_zn / np.log(2) ) / np.log(2)
                        img[iy, ix] = i + 1 - nu
                    else:
                        img[iy, ix] = (i + 1)
    
    calc_t = time.time()-start_t
    return (img.T, calc_t)