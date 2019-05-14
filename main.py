# -*- coding: utf-8 -*-
"""
Created on Mon May 13 16:00:13 2019

@author: msh
"""

#Impoting
from cosmolog import env
from cosmolog import image

logger = env.LOGGER(verb=False)
fop = env.FILE(verb=True)

#Read list of files
files = fop.list_of_fiels("file/", "*.fits")

#Loop in files
for file in files:
#    Create IMAGE object
    img = image.IMAGE(file, verb=False)
#    Read data form image
    img.get_data()
#    Create COSMIC object
    cos = image.COSMIC(img.data, verb=False)
#    Reset cosmic settings
    cos.reset_settingss()
#    Calculate cosmic rays
    cos.do()
    
#    Create IMAGE object
    img2 = image.IMAGE(file, verb=False)
#    Read data form image
    img2.get_data()
#    Create a circular mask and fill it with background
    mask = img2.create_circular_mask()
#    Apply the mask
    img2.apply_mask(mask, bkg=True)
#    Create COSMIC object
    cos2 = image.COSMIC(img2.data, verb=False)
#    Reset cosmic settings
    cos2.reset_settingss()
#    Calculate cosmic rays and print them
    print(file, cos.count(), cos2.count())