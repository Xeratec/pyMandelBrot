#!/usr/bin/python
'''
@file fractal_func.py
@author Philip Wiese
@date 12 Okt 2016
@brief Calculates Mandelbrot set
'''

import time
import numpy as np

class fractal_data():
        def __init__(self, data, calc_t, shape=(400,400), datatype=np.int):
            self.data = np.zeros(shape, dtype = datatype)
            self.data = data
            self.calc_time = calc_t
            self.max = np.amax(data)
            self.min = np.min(data[data>0])
            
        def info(self):
            print "Data Shape: " + str(self.data.shape) 
            print "Calculation Time: %.3fs" % self.calc_time
            print "Maximum Value: %d" % self.max
            print "Minimum Value >0: %d" % self.min
            
def mandelbrot(re_min, re_max, im_min, im_max, max_betr, max_iter, res=400, cont=False):
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
    img = np.zeros(c.shape, dtype= np.float)
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
    
    data = fractal_data(img, calc_t, shape=img.shape, datatype=img.dtype)
    return data