# -*- coding: utf-8 -*-
"""
Created on Mon May 13 15:50:17 2019

@author: msh
"""

from json import dump
from json import loads

from sep import Background

import matplotlib.pyplot as plt

from numpy import float64
from numpy import asarray as ar
from numpy import array
from numpy import ogrid
from numpy import sqrt
from numpy import where

from scipy import misc

from astropy.io import fits as fts

from PIL import ImageDraw
from PIL import Image

from . import env
from . import cosm

class FTS:
    def __init__(self, verb=False, debugger=False):
        """Constructor method."""
        self.verb = verb
        self.debugger = debugger
        
        self.logger = env.LOGGER(verb=self.verb, debugger=self.debugger)
        self.fop = env.FILE(verb=self.verb, debugger=self.debugger)
        
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

class COSMIC:
    def __init__(self, data, verb=False, debugger=False):
        """Constructor method.
        Gets data as numpy array."""
        self.verb = verb
        self.debugger = debugger
        
        self.data = data
        
        self.logger = env.LOGGER(verb=self.verb, debugger=self.debugger)
        self.fop = env.FILE(verb=self.verb, debugger=self.debugger)
        self.def_settings = {"gain": 2.2, "readout_noise": 10.0,
                             "sigma_clip": 5.0, "sigma_fraction": 0.3,
                             "object_limit": 5.0}
        
        self.cos = None
        
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
        """Reads settings file from user's home directory and returns it."""
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
            settings = self.read_settings()
            self.cos = cosm.cosmicsimage(self.data, gain=settings['gain'],
                                    readnoise=settings['readout_noise'],
                                    sigclip=settings['sigma_clip'],
                                    sigfrac=settings['sigma_fraction'],
                                    objlim=settings['object_limit'],
                                    verbose=self.verb)
            self.cos.run(maxiter=1)
        except Exception as e:
            self.logger.log(e)
        
    def count(self):
        """Returns cosmic ray number."""
        try:
            if self.cos is None:
                self.do()
                
            return(self.cos.mask[where(self.cos.mask > 0)].size)
        except Exception as e:
            self.logger.log(e)

class IMAGE:
    def __init__(self, file, def_data=0, verb=False, debugger=False):
        """Constructor method.
        Gets file as string."""
        self.verb = verb
        self.debugger = debugger
        
        self.file = file
        self.def_data = def_data
        
        self.fop = env.FILE(verb=self.verb, debugger=self.debugger)
        self.logger = env.LOGGER(verb=self.verb, debugger=self.debugger)
        
        self.data = None
        
    def get_data_fit(self):
        """Reads FITS files and assign numpy array as data"""
        try:
            if self.fop.is_file(self.file):
                hdu = fts.open(self.file)
                data = hdu[0].data.astype(float64)
                if data.ndim == 2:
                    self.data = data
                elif data.ndim >2:
                    self.data = data[self.def_data]
        except Exception as e:
            self.logger.log(e)
            
    def get_data_png(self):
        """Reads PNG/JPG files and assign numpy array as data"""
        try:
            if self.fop.is_file(self.file):
                image = misc.imread(self.file).astype(float64)
                if image.ndim == 2:
                    self.data = image
                elif image.ndim > 2:
                    self.data = image[:, :, self.def_data]
        except Exception as e:
            self.logger.log(e)
        
    def get_data(self):
        """Uses get_data_fit or get_data_png to assign numpy array as data"""
        if self.data is None:
            self.get_data_fit()
            if self.data is None:
                self.get_data_png()
        else:
            self.logger.log("BAD DATA")
            
    def shape(self):
        """Returns shape of data if data is available"""
        if self.data is not None:
            return(self.data.shape)

    def create_circular_mask(self, center=None, radius=None,
                             bigger=0, auto=min):
        
        """Returns a circular mask if data is available"""
        if self.data is not None:
            h, w = self.shape()
            
            if center is None:
                center = [int(w/2), int(h/2)]
                
            if radius is None:
                radius = auto(center[0], center[1], w-center[0], h-center[1])
                
            Y, X = ogrid[:h, :w]
            dist_from_center = sqrt((X - center[0])**2 + (Y-center[1])**2)
            return(dist_from_center <= radius + bigger)
        else:
            self.logger.log("BAD DATA")
            
    def background(self):
        """Returns background value of data if data is available"""
        if self.data is not None:
            try:
                return(ar(Background(self.data)))
            except Exception as e:
                self.logger.log(e)
            
    def create_polygon_mask(self, coordinates):
        """Returns a polygon mask if data is available"""
        if self.data is not None:
            h, w = self.shape()
            img = Image.new('L', (w, h), 0)
            ImageDraw.Draw(img).polygon(coordinates, outline=1, fill=1)
            mask = array(img)
            return(mask == 1)
        else:
            self.logger.log("BAD DATA")
            
    def apply_mask(self, mask, bkg=True):
        """Applies mask to data if data is available"""
        if self.data is not None:
            if bkg:
                backg = self.background()
                if backg is not None:
                    self.data[mask] = backg[mask]
                else:
                    self.data[mask] = 0
            else:
                self.data[mask] = 0
        
    def write(self, file_name, header=None, ow=True):
        """Writes a fits file if data is available"""
        if self.data is not None:
            fts.writeto(file_name, self.data, header=header, overwrite=ow)
            
    def show(self, data=None):
        """Displays image if data is available"""
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