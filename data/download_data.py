#!/usr/bin/env python

"""
Get OzFlux files

That's all folks.
"""
__author__ = "Martin De Kauwe"
__version__ = "1.0 (01.07.2020)"
__email__ = "mdekauwe@gmail.com"

import sys

import urllib.request


sites = ["Gingin", "GreatWesternWoodlands", "Calperum", "WombatStateForest", \
         "Whroo", "CumberlandPlain", "Tumbarumba"]


for site in sites:
    print(site)
    url = "http://dap.ozflux.org.au/thredds/fileServer/ozflux/sites/%s/L6/default/%s_L6.nc" % (site, site)
    urllib.request.urlretrieve(url, "%s_L6.nc" % (site))
