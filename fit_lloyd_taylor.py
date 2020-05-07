#!/usr/bin/env python

"""
Blah

That's all folks.
"""
__author__ = "Martin De Kauwe"
__version__ = "1.0 (07.05.2020)"
__email__ = "mdekauwe@gmail.com"

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import sys
from get_data import read_nc_file
from lloyd_taylor import Resp_Lloyd_Taylor

def fit_lt(dates, Reco, Tair):

    plt.plot(Reco)
    plt.show()
    sys.exit()

if __name__ == "__main__":

    fname = "data/Yanco_L6.nc"
    (dates, VPD_day,
     Tair_day, Tair_night,
     VPD_day, SW_day,
     Reco_day, Reco_night, NEE_day) = read_nc_file(fname)

    fit_lt(dates, Reco_night, Tair_night)
