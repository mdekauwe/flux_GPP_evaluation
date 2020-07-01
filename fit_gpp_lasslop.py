#!/usr/bin/env python

"""
Fit alpha, beta, k of the Lasslop rectangular hyperbolic light-response curve

That's all folks.
"""
__author__ = "Martin De Kauwe"
__version__ = "1.0 (01.07.2020)"
__email__ = "mdekauwe@gmail.com"

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import sys
from get_data import read_nc_file
from lloyd_taylor import Resp_Lloyd_Taylor
from gpp_lasslop import calculate_gpp_lasslop
from lmfit import minimize, Parameters
import pandas as pd
from summary_stats import rmse
import os


def main(fdir, sites, output_dir):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    fname = "outputs/LT_fits_all_timesteps_NATT.csv"
    df_resp = pd.read_csv(fname)


    dfa = fit_all_dates(sites, df_resp)
    #dfy = fit_individual_years(sites)

    dfa.to_csv(os.path.join(output_dir, "LT_fits_all_timesteps_NATT.csv"), index=False)
    #dfy.to_csv(os.path.join(output_dir, "LT_fits_annual_NATT.csv"), index=False)
    #dfa.to_csv(os.path.join(output_dir, "LT_fits_all_timesteps.csv"), index=False)
    #dfy.to_csv(os.path.join(output_dir, "LT_fits_annual.csv"), index=False)

def fit_all_dates(sites, df_resp):

    # Save each year seperately
    dfa = pd.DataFrame(columns=['site','osite','dates','rb','rb_se',\
                                'E0','E0_se','alpha','alpha_se',\
                                'beta0','beta0_se','k','k_se','D0','D0_se',\
                                'rmse'])

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
        elif site == "AdelaideRiver":
            osite = "Au-Ade"
        elif site == "DalyUncleared":
            osite = "Au-Dal"
        elif site == "DryRiver":
            osite = "Au-Dry"
        elif site == "HowardSprings":
            osite = "Au-How"
        elif site == "SturtPlains":
            osite = "Au-Stu"

        # Need to vary rb during the day later.
        rb = df_resp[df_resp.site == site].rb.values[0]
        E0 = df_resp[df_resp.site == site].E0.values[0]
        D0 = 1.0

        (dates, VPD_day,
         Tair_day, Tair_night,
         VPD_day, SW_day,
         Reco_day, Reco_night, NEE_day) = read_nc_file(fname)

        # Screen masked data
        dates_m = dates[~NEE_day.mask]
        Tair_m = Tair_day[~NEE_day.mask]
        SW_day_m = SW_day[~NEE_day.mask]
        VPD_day_m = VPD_day[~NEE_day.mask]
        NEE_day_m = NEE_day[~NEE_day.mask]

        dates_m = dates[~Tair_m.mask]
        SW_day_m = SW_day_m[~Tair_m.mask]
        VPD_day_m = VPD_day_m[~Tair_m.mask]
        NEE_day_m = NEE_day_m[~Tair_m.mask]
        Tair_m = Tair_m[~Tair_m.mask]

        dates_m = dates[~SW_day_m.mask]
        VPD_day_m = VPD_day_m[~SW_day_m.mask]
        NEE_day_m = NEE_day_m[~SW_day_m.mask]
        Tair_m = Tair_m[~SW_day_m.mask]
        SW_day_m = SW_day_m[~SW_day_m.mask]

        dates_m = dates[~VPD_day_m.mask]
        NEE_day_m = NEE_day_m[~VPD_day_m.mask]
        Tair_m = Tair_m[~VPD_day_m.mask]
        SW_day_m = SW_day_m[~VPD_day_m.mask]
        VPD_day_m = VPD_day_m[~VPD_day_m.mask]


        # there is some weird issue with the time thing from the ozflux file,
        # this hacky thing gets us back years we can manipulate
        all_years = []
        for i in dates_m:
            all_years.append(i.values.astype("str")[0:4])
        all_years = np.array(all_years)
        years = np.unique(all_years)

        # Fit all the data together...
        result = fit_gpp(D0, rb, E0, NEE_day, Tair_day, SW_day, VPD_day)
        alpha = result.params['alpha'].value
        beta0 = result.params['beta0'].value
        k = result.params['k'].value

        Reco = Resp_Lloyd_Taylor(Tair_day, rb, E0)
        gpp = calculate_gpp_lasslop(alpha, beta0, k, D0, Fsd, D)
        nee_pred = -1 * gpp + Reco
        pred = Resp_Lloyd_Taylor(Tair_m, rb, E0)
        rms = rmse(nee_pred, NEE_day)

        dfa.loc[len(dfa), :] = [site, osite,\
                                "%s_%s" % (years[0], years[-1]), \
                                result.params['rb'].value, \
                                #result.params['rb'].stderr, \
                                -999.9,\
                                result.params['E0'].value,\
                                #result.params['E0'].stderr,
                                -999.9,\
                                result.params['alpha'].value, \
                                result.params['alpha'].stderr, \
                                result.params['beta0'].value,\
                                result.params['beta0'].stderr, \
                                result.params['k'].value,\
                                result.params['k'].stderr, \
                                result.params['D0'].value,\
                                result.params['D0_se'].value,\
                                -999.9, \
                                rms]

    return dfa



def residual(params, nee_obs, Tair, Fsd, D):
    alpha = params['alpha']
    beta0 = params['beta0']
    k = params['k']
    rb = params['rb']
    E0 = params['E0']
    D0 = params['D0']

    Reco = Resp_Lloyd_Taylor(Tair, rb, E0)
    gpp = calculate_gpp_lasslop(alpha, beta0, k, D0, Fsd, D)
    nee_model = -1 * gpp + Reco
    return (nee_obs - nee_model)


def fit_gpp(D0, rb, E0, NEE, Tair, Fsd, D):

    params = Parameters()
    params.add('rb', value=rb, vary=False)
    params.add('E0', value=E0, vary=False)
    params.add('D0', value=D0, vary=False)
    params.add('alpha', value=0.01, min=0.0, max=1.0)
    params.add('beta0', value=1.0, min=0.0)
    params.add('k', value=0.0, min=0.0)

    result = minimize(residual, params, args=(NEE, Tair, Fsd, D))

    return result

if __name__ == "__main__":

    fdir = "data"
    output_dir = "outputs"
    #sites = ["Gingin", "GreatWesternWoodlands", "Calperum", \
    #         "WombatStateForest", "Whroo", "CumberlandPlain", "Tumbarumba"]
    sites = ["AdelaideRiver", "DalyUncleared", "DryRiver", "HowardSprings", \
             "SturtPlains"]
    main(fdir, sites, output_dir)
