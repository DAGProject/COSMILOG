# -*- coding: utf-8 -*-
"""
Created on Mon May 13 15:50:17 2019

@author: msh
"""
from json import dump
from json import loads

from numpy import ogrid
from numpy import sqrt
from numpy import power
from numpy import float64
from numpy import asarray as ar
from numpy import where
from numpy import histogram as histo
from numpy import argmax
from numpy import std

from sep import Background

from scipy import misc
from scipy.stats import sigmaclip

from astropy.io import fits as fts

from PIL import ImageDraw
from PIL import Image

import matplotlib.pyplot as plt

from . import env
from . import cosm

class IMAGE:
    def __init__(self, file, def_layer=0, verb=False, debugger=False):
        self.verb = verb
        self.debugger = debugger
        self.file = file
        self.def_layer = def_layer
        
        self.logger = env.LOGGER(verb=self.verb, debugger=self.debugger)
        self.fop = env.FILE(verb=self.verb, debugger=self.debugger)
        
        self.data = self.get_data()
        self.bkg = self.background()
        self.pure = self.create_pure_data()
        self._pure_ = self.pure
        
    def header(self, field):
        """Returns wanted header from given file."""
        self.logger.log("Getting Header from {}".format(self.file))
        try:
            if self.fop.is_file(self.file):
                hdu = fts.open(self.file, mode='readonly')
                header = hdu[0].header
                hdu.close()
                return(header[field])
        except Exception as e:
            self.logger.log(e)
        
    def create_pure_data(self):
        if self.data is not None and self.bkg is not None:
            return(self.data - self.bkg)
    
    def get_data_fit(self):
        """Reads FITS files and assign numpy array as data"""
        try:
            if self.fop.is_file(self.file):
                data = fts.getdata(self.file).astype(float64)
                if data.ndim == 2:
                    return(data)
                elif data.ndim >2:
                    return(data[self.def_layer])
        except Exception as e:
            self.logger.log(e)
            
    def get_data_png(self):
        """Reads PNG/JPG files and assign numpy array as data"""
        try:
            if self.fop.is_file(self.file):
                image = misc.imread(self.file).astype(float64)
                if image.ndim == 2:
                    return(image)
                elif image.ndim > 2:
                    return(image[:, :, self.def_layer])
        except Exception as e:
            self.logger.log(e)
        
    def get_data(self):
        """Uses get_data_fit or get_data_png to assign numpy array as data"""
        data = self.get_data_fit()
        if data is None:
            data = self.get_data_png()
            
        return(data)
            
    
            
    def write(self, file_name, header=None, ow=True):
        """Writes a fits file if data is available"""
        if self.data is not None:
            fts.writeto(file_name, self.data, header=header, overwrite=ow)
            
    def background(self):
        """Returns background value of data if data is available"""
        if self.data is not None:
            try:
                return(ar(Background(self.data)))
            except Exception as e:
                self.logger.log(e)
            
    def apply_mask(self, mask, bkg=True):
        self._data_ = self.data
        if bkg:
            self.data[mask] = self.bkg[mask]
            self._pure_[mask] = self.pure[mask]
        else:
            self.data[mask] = 0
            self._pure_[mask] = 0
            
    def show(self, data=None):
        """Displays image if data is available"""
        plt.figure()
        
        if data is not None:
            plt.imshow(data, cmap='gray')
            plt.colorbar()
            plt.xticks([])
            plt.yticks([])
            plt.show()
        elif self.data is not None:
            plt.imshow(self.data, cmap='gray')
            plt.colorbar()
            plt.xticks([])
            plt.yticks([])
            plt.show()
        else:
            self.logger.log("BAD DATA")
            
class COSMIC(IMAGE):
    def __init__(self):
        pass
    
    class FAST():
        def __init__(self, data, nrows=64, ncols=64, verb=False, debugger=False):
            self.verb = verb
            self.debugger = debugger
            self.def_settings = {"gain": 2.2, "readout_noise": 10.0,
                                 "sigma_clip": 5.0, "sigma_fraction": 0.3,
                                 "object_limit": 5.0}
            
            self.logger = env.LOGGER(verb=self.verb, debugger=self.debugger)
            self.fop = env.FILE(verb=self.verb, debugger=self.debugger)
            
            
            self.nrows, self.ncols = nrows, ncols
            self.data = data
            self.h, self.w = self.data.shape
            
            self.do = self.check_n()
            
        def check_n(self):
            return(self.h % self.nrows == 0 and self.w % self.ncols == 0)
            
        def split(self):
            if self.do:
                ret = []
                sclp = []
                sigmas = []
                for x in range(0, self.h, self.ncols):
                    row = []
                    sclp_row = []
                    sgima_row = []
                    for y in range(0, self.w, self.nrows):
                        subar = ar(self.data[x:x+self.ncols, y:y+self.nrows])
                        sc = ar(sigmaclip(subar, low=4, high=4).clipped)
                        sg = ar(std(subar))
                        row.append(subar)
                        sclp_row.append(sc)
                        sgima_row.append(sg)
                        
                    sigmas.append(ar(sgima_row))
                    sclp.append(sclp_row)
                    ret.append(ar(row))
                return(ar(ret), ar(sclp), ar(sigmas))
                
        def higher(self, hist):
            index = argmax(hist[0])
            values = hist[1][:index]
            counts = hist[0][:index]
            return([counts, values])
            
        def find_cosmic_values(self, arr, sgm, mult=3):
            print()
            big_arr = arr[1][:-1][arr[0] > 0]
            for element in range(1, len(big_arr[:-1]) - 1):
                gap = big_arr[element] - big_arr[element - 1]
                print(gap, sgm * mult)
                if gap > sgm * mult:
                    break
            return(big_arr[:-1][element - 1])
                
        def histogram(self):
            if self.do:
                sub_ars, sub_ars_sclp, sgimas = self.split()
                for sub_line, sub_line_scp, sub_line_sigm in zip(sub_ars, sub_ars_sclp, sgimas):
                    for sub_arr, sub_arr_scp, sgm in zip(sub_line, sub_line_scp, sub_line_sigm):

                        hst = histo(sub_arr_scp, bins=200)
                        print(hst)
                        high_hist = self.higher(hst)
                        cosmic_values = self.find_cosmic_values(hst, sgm)
                        print(len(sub_arr[sub_arr > cosmic_values]))
                        plt.bar(high_hist[1], high_hist[0])
                        plt.show()
                        break
            
    class LA:
        def __init__(self, data, verb=False, debugger=False):
            self.verb = verb
            self.debugger = debugger
            self.def_settings = {"gain": 2.2, "readout_noise": 10.0,
                                 "sigma_clip": 5.0, "sigma_fraction": 0.3,
                                 "object_limit": 5.0}
            
            self.logger = env.LOGGER(verb=self.verb, debugger=self.debugger)
            self.fop = env.FILE(verb=self.verb, debugger=self.debugger)
            
            self.cos = None
            self.data = data
        
        def settings(self, gain, readout_noise, sigma_clip,
                           sigma_fraction, object_limit):
            """Writes settings for cosmic cleaner as json file
            in user's home directory in order to be used later."""
            try:
                the_settings = {}
                the_settings['gain'] = gain
                the_settings['readout_noise'] = readout_noise
                the_settings['sigma_clip'] = sigma_clip
                the_settings['sigma_fraction'] = sigma_fraction
                the_settings['object_limit'] = object_limit
                
                with open(self.logger.setting_file, 'w') as set_file:
                    dump(the_settings, set_file)
            except Exception as e:
                self.logger.log(e)
                
        def reset_settingss(self):
            """Writes default settings for cosmic cleaner as json file
            in user's home directory in order to be used later."""
            with open(self.logger.setting_file, 'w') as set_file:
                    dump(self.def_settings, set_file)
                
        def read_settings(self):
            """Reads settings file from user's home directory."""
            try:
                with open(self.logger.setting_file, 'r') as myfile:
                    data=myfile.read()
                    
                settings = loads(data)
                
                for key, value in settings.items():
                    if value is None:
                        settings[value] = self.def_settings[value]
            
                return(settings)
            except Exception as e:
                return(self.def_settings)
                self.logger.log(e)
                
        def do(self):
            """Runs cosmic cleaner and finds cosmic rays. Creates mask file."""
            try:
                if self.data is not None:
                    settings = self.read_settings()
                    self.cos = cosm.cosmicsimage(self.data,
                                                 gain=settings['gain'],
                                                 readnoise=settings[
                                                         'readout_noise'],
                                                 sigclip=settings[
                                                         'sigma_clip'],
                                                 sigfrac=settings[
                                                         'sigma_fraction'],
                                                 objlim=settings[
                                                         'object_limit'],
                                                 verbose=self.verb)
                    self.cos.run(maxiter=1)
            except Exception as e:
                self.logger.log(e)
                
        def count(self, mask=None):
            """Returns cosmic ray number."""
            try:
                if self.cos is None:
                    self.do()
                    
                if mask is not None:
                    self.cos.mask[mask] = 0
                    
                return(self.cos.mask[where(self.cos.mask > 0)].size)
            except Exception as e:
                self.logger.log(e)
                
        def cosmask(self):
            """Returns cosmic ray number."""
            try:
                if self.cos is None:
                    self.do()
#                print(self.cos.mask.sum())
                return(255 * (self.cos.mask + 0))
            except Exception as e:
                self.logger.log(e)
                
class MASK:
    def __init__(self, shape, verb=False, debugger=False):
        self.verb = verb
        self.debugger = debugger
        self.shape = shape
    
    def circular(self, center=None, radius=None, bigger=0, auto=min):
        h, w = self.shape
        if center is None:
            center = [int(w/2), int(h/2)]
            
        if radius is None:
            radius = auto(center[0], center[1], w-center[0], h-center[1])
            
        Y, X = ogrid[:h, :w]
        dist_from_center = sqrt(
                power(X - center[0], 2) + power(Y-center[1], 2))
        return(dist_from_center <= radius + bigger)
        
    def polygon(self, poins):
        h, w = self.shape
        img = Image.new('L', (w, h), 0)
        ImageDraw.Draw(img).polygon(poins, outline=1, fill=1)
        mask = ar(img)
        return(mask == 1)