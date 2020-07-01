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
from summary_stats import rmse
import os


def main(fdir, sites, output_dir):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    dfa = fit_all_dates(sites)
    dfy = fit_individual_years(sites)

    dfa.to_csv(os.path.join(output_dir, "LT_fits_all_timesteps.csv"), index=False)
    dfy.to_csv(os.path.join(output_dir, "LT_fits_annual.csv"), index=False)


def fit_all_dates(sites):

    # Save each year seperately
    dfa = pd.DataFrame(columns=['site','osite','dates','rb','rb_se',\
                                'E0','E0_se','rmse'])

    for j,site in enumerate(sites):
        fname = os.path.join(fdir, "%s_L6.nc" % (site))

        if site == "Gingin":
            osite = "Au-Gin"
        elif site == "GreatWesternWoodlands":
            osite = "Au-Gww"
        elif site == "Calperum":
            osite = "Au-Cal"
        elif site == "Wombat":
            osite = "Au-Wom"
        elif site == "Whroo":
            osite = "Au-Whr"
        elif site == "CumberlandPlain":
            osite = "Au-Cum"
        elif site == "Tumbarumba":
            osite = "Au-Tum"

        (dates, VPD_day,
         Tair_day, Tair_night,
         VPD_day, SW_day,
         Reco_day, Reco_night, NEE_day) = read_nc_file(fname)

        # Screen masked data
        dates_m = dates[~Tair_night.mask]
        Reco_m = Reco_night[~Tair_night.mask]
        Tair_m = Tair_night[~Tair_night.mask]
        Tair_m = Tair_m[~Reco_m.mask]
        dates_m = dates_m[~Reco_m.mask]
        Reco_m = Reco_m[~Reco_m.mask]

        # there is some weird issue with the time thing from the ozflux file,
        # this hacky thing gets us back years we can manipulate
        all_years = []
        for i in dates_m:
            all_years.append(i.values.astype("str")[0:4])
        all_years = np.array(all_years)
        years = np.unique(all_years)

        # Fit all the data together...
        result = fit_lt(Reco_m, Tair_m)
        rb = result.params['rb'].value
        E0 = result.params['E0'].value
        pred = Resp_Lloyd_Taylor(Tair_m, rb, E0)
        rms = rmse(pred, Reco_m)

        dfa.loc[len(dfa), :] = [site, osite,\
                                "%s_%s" % (years[0], years[-1]), \
                                result.params['rb'].value, \
                                result.params['rb'].stderr, \
                                result.params['E0'].value,\
                                result.params['E0'].stderr, rms]

        #plt.plot(Tair_m, Reco_m, "k.")
        #plt.plot(Tair_m, Resp_Lloyd_Taylor(Tair_m, rb, E0))
        #plt.show()

    return dfa

def fit_individual_years(sites):

    # Fit individual years
    min_pts = 100

    # Save each year seperately
    dfy = pd.DataFrame(columns=['site','osite','dates','rb','rb_se',\
                                'E0','E0_se','rmse'])

    cnt = 0
    for j,site in enumerate(sites):

        fname = os.path.join(fdir, "%s_L6.nc" % (site))

        if site == "Gingin":
            osite = "Au-Gin"
        elif site == "GreatWesternWoodlands":
            osite = "Au-Gww"
        elif site == "Calperum":
            osite = "Au-Cal"
        elif site == "Wombat":
            osite = "Au-Wom"
        elif site == "Whroo":
            osite = "Au-Whr"
        elif site == "CumberlandPlain":
            osite = "Au-Cum"
        elif site == "Tumbarumba":
            osite = "Au-Tum"

        (dates, VPD_day,
         Tair_day, Tair_night,
         VPD_day, SW_day,
         Reco_day, Reco_night, NEE_day) = read_nc_file(fname)

        # Screen masked data
        dates_m = dates[~Tair_night.mask]
        Reco_m = Reco_night[~Tair_night.mask]
        Tair_m = Tair_night[~Tair_night.mask]
        Tair_m = Tair_m[~Reco_m.mask]
        dates_m = dates_m[~Reco_m.mask]
        Reco_m = Reco_m[~Reco_m.mask]

        # there is some weird issue with the time thing from the ozflux file,
        # this hacky thing gets us back years we can manipulate
        all_years = []
        for i in dates_m:
            all_years.append(i.values.astype("str")[0:4])
        all_years = np.array(all_years)
        years = np.unique(all_years)

        for year in years:

            years_data = all_years[all_years == year]
            years_reco = Reco_m[all_years == year]
            years_tair = Tair_m[all_years == year]

            if len(years_data) > min_pts:
                result = fit_lt(years_reco, years_tair)

                rb = result.params['rb'].value
                E0 = result.params['E0'].value
                pred = Resp_Lloyd_Taylor(Tair_m, rb, E0)
                rms = rmse(pred, Reco_m)

                dfy.loc[cnt, :] = [site, osite, year, \
                                   result.params['rb'].value, \
                                   result.params['rb'].stderr, \
                                   result.params['E0'].value,\
                                   result.params['E0'].stderr, \
                                   rms]

            else:
                # Not enough data to fit
                dfy.loc[cnt, :] = [site, osite, year, -999.9, -999.9, -999.9,\
                                   -999.9, -999.9]

            cnt += 1

    return dfy

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

    fdir = "data"
    output_dir = "outputs"
    sites = ["Gingin", "GreatWesternWoodlands", "Calperum", \
             "WombatStateForest", "Whroo", "CumberlandPlain", "Tumbarumba"]
    main(fdir, sites, output_dir)
