#!/usr/bin/env python

"""
Fit rb and E0 of the Lloyd Taylor func using night-time Reco flux data

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
from lmfit import minimize, Parameters
import pandas as pd

def residual(params, obs, Tair):
    rb = params['rb']
    E0 = params['E0']

    model = Resp_Lloyd_Taylor(Tair, rb, E0)

    return (obs-model)


def fit_lt(Reco, Tair):

    params = Parameters()
    params.add('rb', value=2., min=0.0)
    params.add('E0', value=100., min=0.0)

    result = minimize(residual, params, args=(Reco, Tair))

    return result

if __name__ == "__main__":

    #fname = "data/Yanco_L6.nc"
    #fname = "data/Tumbarumba_L6.nc"
    fname = "data/Whroo_L6.nc"

    (dates, VPD_day,
     Tair_day, Tair_night,
     VPD_day, SW_day,
     Reco_day, Reco_night, NEE_day) = read_nc_file(fname)

    dates_m = dates[~Tair_night.mask]
    Reco_m = Reco_night[~Tair_night.mask]
    Tair_m = Tair_night[~Tair_night.mask]
    Tair_m = Tair_m[~Reco_m.mask]
    dates_m = dates_m[~Reco_m.mask]
    Reco_m = Reco_m[~Reco_m.mask]

    result = fit_lt(Reco_m, Tair_m)

    rb = result.params['rb'].value
    E0 = result.params['E0'].value

    # Fit all years
    for name, par in result.params.items():
        print('%s = %.8f +/- %.8f ' % (name, par.value, par.stderr))
    print("\n")
    plt.plot(Tair_m, Reco_m, "k.")
    plt.plot(Tair_m, Resp_Lloyd_Taylor(Tair_m, rb, E0))
    plt.show()

    # Fit individual years

    # there is some weird issue with the time thing from the ozflux file,
    # this hacky thing gets us back years we can manipulate
    all_years = []
    for i in dates_m:
        all_years.append(i.values.astype("str")[0:4])
    all_years = np.array(all_years)
    years = np.unique(all_years)

    min_pts = 100
    for year in years[1:]:
        years_data = all_years[all_years == year]
        years_reco = Reco_m[all_years == year]
        years_tair = Tair_m[all_years == year]

        if len(years_data) > min_pts:
            result = fit_lt(years_reco, years_tair)

            for name, par in result.params.items():
                print('%s: %s = %.8f +/- %.8f ' % (year, name, par.value, par.stderr))
            print("\n")
        else:
            print("%s: Not enough data" % (year))
