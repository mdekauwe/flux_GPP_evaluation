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

    # Save all years results
    dfa = pd.DataFrame(columns=['site','dates','rb','rb_se','E0','E0_se','rmse'],
                       index=range(len(sites)))

    # Save each year seperately
    dfy = pd.DataFrame(columns=['site','dates','rb','rb_se','E0','E0_se','rmse'],
                       index=range(len(sites)))

    for j,site in enumerate(sites):
        fname = os.path.join(fdir, "%s_L6.nc" % (site))

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

        #print("RMSE = %.2f" % rms)
        #for name, par in result.params.items():
        #    print('%s = %.8f +/- %.8f ' % (name, par.value, par.stderr))
        #print("\n")

        dfa.loc[j,"site"] = site
        dfa.loc[j,"dates"] = "%s_%s" % (years[0], years[-1])
        dfa.loc[j,"rb"] = result.params['rb'].value
        dfa.loc[j,"rb_se"] = result.params['rb'].stderr
        dfa.loc[j,"E0"] = result.params['E0'].value
        dfa.loc[j,"E0_se"] = result.params['E0'].stderr
        dfa.loc[j,"rmse"] = rms



        #plt.plot(Tair_m, Reco_m, "k.")
        #plt.plot(Tair_m, Resp_Lloyd_Taylor(Tair_m, rb, E0))
        #plt.show()

    # Fit individual years
    min_pts = 100
    
    # Save each year seperately
    dfy = pd.DataFrame(columns=['site','dates','rb','rb_se','E0','E0_se','rmse'],
                       index=range(len(sites*len(years))))

    cnt = 0
    for j,site in enumerate(sites):

        for year in years:
            print(year)
            years_data = all_years[all_years == year]
            years_reco = Reco_m[all_years == year]
            years_tair = Tair_m[all_years == year]

            if len(years_data) > min_pts:
                result = fit_lt(years_reco, years_tair)

                rb = result.params['rb'].value
                E0 = result.params['E0'].value
                pred = Resp_Lloyd_Taylor(Tair_m, rb, E0)
                rms = rmse(pred, Reco_m)

                dfy.loc[cnt,"site"] = site
                dfy.loc[cnt,"dates"] = "%s" % (year)
                dfy.loc[cnt,"rb"] = result.params['rb'].value
                dfy.loc[cnt,"rb_se"] = result.params['rb'].stderr
                dfy.loc[cnt,"E0"] = result.params['E0'].value
                dfy.loc[cnt,"E0_se"] = result.params['E0'].stderr
                dfy.loc[cnt,"rmse"] = rms


                #print("RMSE = %.2f" % rms)
                #for name, par in result.params.items():
                #    print('%s: %s = %.8f +/- %.8f ' % (year, name, par.value, par.stderr))
                #print("\n")
            else:
                # Not enough data to fit
                dfy.loc[j,"site"] = site
                dfy.loc[j,"dates"] = "%s" % (year)

            cnt += 1

    dfa.to_csv(os.path.join(output_dir, "LT_fits_all_timesteps.csv"), index=False)
    dfy.to_csv(os.path.join(output_dir, "LT_fits_annual.csv"), index=False)

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
    sites = ["Whroo"]
    main(fdir, sites, output_dir)
