# -*- coding: utf-8 -*-
"""
Created on Mon May 13 16:00:13 2019

@author: msh
"""

#Impoting
from cosmilog import env
from cosmilog import image

logger = env.Logger(verb=False)
fop = env.File(verb=False)

fts = image.Fits()
d = fts.data("V523_Cas-002V.fit")

s = d.shape
#ps = ((1024, 0), (2048, 1024), (1024, 2048), (0, 1024))
msk = image.Mask()
circ = msk.circular(s, rev=False)
#pol = msk.polygon(s, ps, rev=False)

masked_data = msk.apply(d, circ)

print(fts.cosmic_count(d, la=True))
print(fts.cosmic_count(masked_data, la=True))