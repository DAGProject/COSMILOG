# -*- coding: utf-8 -*-
"""
Created on Mon May 13 16:00:13 2019

@author: msh
"""

#Impoting
from cosmilog import env
from cosmilog import image

logger = env.LOGGER(verb=False)
fop = env.FILE(verb=False)

img = image.IMAGE("file/file2.fits", verb=True, def_layer=2)
if img.data is not None:
    mask = image.MASK(img.data.shape, verb=True)
    cmask = mask.circular()
    points = ((0, 0), (0, 1024), (2048, 1024), (2048, 0))
    bmask = mask.polygon(points)
    img.apply_mask(cmask, bkg=True)
    img.apply_mask(bmask, bkg=True)
    
    img.show()
    cosm = image.COSMIC.LA(img.data, verb=True)
    
    print("{} Cosmic rays found".format(cosm.count()))
    mask_data = cosm.cosmask()
    
    img.show(mask_data)
    