# -*- coding: utf-8 -*-
"""
Created on Mon May 13 15:50:17 2019

@author: msh
"""

from ccdproc import cosmicray_lacosmic as cosla
from ccdproc import cosmicray_median as cosme

from numpy import float64 as f64
from numpy import ogrid
from numpy import sqrt
from numpy import power
from numpy import asarray as ar
from numpy import logical_not as lnot
from numpy import sum as nsum

from PIL import ImageDraw
from PIL import Image

from astropy.io import fits as fts

from sep import Background

from . import env

class Fits:
    def __init__(self, verb=True, debugger=False):
        self.verb = verb
        self.debugger = debugger
        
        self.logger = env.Logger(verb=self.verb, debugger=self.debugger)
        self.fop = env.File(verb=self.verb, debugger=self.debugger)
        
    def header(self, file, field):
        """Returns wanted header from given file."""
        self.logger.log("Getting Header from {}".format(file))
        try:
            if self.fop.is_file(file):
                hdu = fts.open(file, mode='readonly')
                header = hdu[0].header
                hdu.close()
                return(header[field])
        except Exception as e:
            self.logger.log(e)
            
    def data(self, file):
        """Reads FITS files and assign numpy array as data"""
        try:
            if self.fop.is_file(file):
                data = fts.getdata(file).astype(f64)
                if data.ndim == 2:
                    return(data)
                elif data.ndim >2:
                    return(data[self.def_layer])
        except Exception as e:
            self.logger.log(e)
            
    def write(self, file_name, data, header=None, ow=True):
        try:
            fts.writeto(file_name, data, header=header, overwrite=ow)
        except Exception as e:
            self.logger.log(e)
            
    def background(self, data):
        """Returns background value of data if data is available"""
        try:
            return(ar(Background(data)))
        except Exception as e:
            self.logger.log(e)
            
    def lacosmic(self, data, sigclip=12, sigfrac=0.3, objlim=5.0, gain=1.0,
                 readnoise=6.5, satlevel=65535.0, pssl=0.0, iteration=4,
                 sepmed=True, cleantype='meanmask', fsmode='median',
                 psfmodel='gauss', psffwhm=2.5, psfsize=7, psfk=None,
                 psfbeta=4.765, verbose=False):
        try:
            new_data, cos = cosla(data, sigclip=sigclip, sigfrac=sigfrac,
                                  objlim=objlim, gain=gain,
                                  readnoise=readnoise, satlevel=satlevel,
                                  pssl=pssl, niter=iteration,
                                  sepmed=sepmed, cleantype=cleantype,
                                  fsmode=fsmode, psfmodel=psfmodel,
                                  psffwhm=psffwhm, psfsize=psfsize,
                                  psfk=psfk, psfbeta=psfbeta, verbose=verbose)
            
            return(new_data, cos.astype(int))
        except Exception as e:
            self.logger.log(e)
    
    def mecosmic(self, data, error_image=None, thresh=5, mbox=11,
                 gbox=0, rbox=0):
        try:
            new_data, cos = cosme(data, error_image=error_image,
                                  thresh=thresh, mbox=mbox,
                                  gbox=gbox, rbox=rbox)
            return(new_data, cos.astype(int))
        except Exception as e:
            self.logger.log(e)
            
    
    def cosmic_count(self, data, la=True):
        if la:
            _, cos = self.lacosmic(data)
        else:
            _, cos = self.mecosmic(data)
            
        return(nsum(cos))
                
class Mask:
    def __init__(self, verb=True, debugger=False):
        self.verb = verb
        self.debugger = debugger
        self.fits = Fits(verb=self.verb, debugger=self.debugger)
        
    def circular(self, shape, center=None, radius=None, bigger=0,
                 auto=min, rev=False):
        h, w = shape
        if center is None:
            center = [int(w/2), int(h/2)]
            
        if radius is None:
            radius = auto(center[0], center[1], w-center[0], h-center[1])
            
        Y, X = ogrid[:h, :w]
        dist_from_center = sqrt(
                power(X - center[0], 2) + power(Y-center[1], 2))
        
        the_mask = dist_from_center <= radius + bigger
        
        if rev:
            return(lnot(the_mask))
        else:
            return(the_mask)
        
    def polygon(self, shape, points, rev=False):
        img = Image.new('L', shape, 0)
        ImageDraw.Draw(img).polygon(points, outline=1, fill=1)
        mask = ar(img)
        
        the_mask = mask == 1
        
        if rev:
            return(lnot(the_mask))
        else:
            return(the_mask)
            
    def apply(self, data, mask, bkg=True):
        copy_od_data = data.copy()
        if bkg:
            backg = self.fits.background(copy_od_data)
            copy_od_data[mask] = backg[mask]
        else:
            copy_od_data[mask] = 0
            
        return(copy_od_data)
            