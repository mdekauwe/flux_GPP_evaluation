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

    dfa.to_csv(os.path.join(output_dir, "LT_fits_all_timesteps_NATT.csv"), index=False)
    dfy.to_csv(os.path.join(output_dir, "LT_fits_annual_NATT.csv"), index=False)
    #dfa.to_csv(os.path.join(output_dir, "LT_fits_all_timesteps.csv"), index=False)
    #dfy.to_csv(os.path.join(output_dir, "LT_fits_annual.csv"), index=False)

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

                """
                fig = plt.figure(figsize=(9,6))
                fig.subplots_adjust(hspace=0.1)
                fig.subplots_adjust(wspace=0.05)
                plt.rcParams['text.usetex'] = False
                plt.rcParams['font.family'] = "sans-serif"
                plt.rcParams['font.sans-serif'] = "Helvetica"
                plt.rcParams['axes.labelsize'] = 12
                plt.rcParams['font.size'] = 12
                plt.rcParams['legend.fontsize'] = 12
                plt.rcParams['xtick.labelsize'] = 12
                plt.rcParams['ytick.labelsize'] = 12

                almost_black = '#262626'
                # change the tick colors also to the almost black
                plt.rcParams['ytick.color'] = almost_black
                plt.rcParams['xtick.color'] = almost_black

                # change the text colors also to the almost black
                plt.rcParams['text.color'] = almost_black

                # Change the default axis colors from black to a slightly lighter black,
                # and a little thinner (0.5 instead of 1)
                plt.rcParams['axes.edgecolor'] = almost_black
                plt.rcParams['axes.labelcolor'] = almost_black

                ax = fig.add_subplot(111)
                ax.plot(Tair_m, Reco_m, "k.")
                ax.plot(Tair_m, pred)
                ax.set_ylabel("R$_{eco}$ (\u03BCmol m$^{-2}$ s$^{-1}$)")
                ax.set_xlabel("T$_{air}$ ($^{\circ}\mathrm{C}$)")

                plot_dir = "plots"
                if not os.path.exists(plot_dir):
                    os.makedirs(plot_dir)

                plt.savefig(os.path.join(plot_dir,
                                         "%s_%s_Reco.pdf" % (osite, year)),
                            bbox_inches='tight', pad_inches=0.1)
                """


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
    #sites = ["Gingin", "GreatWesternWoodlands", "Calperum", \
    #         "WombatStateForest", "Whroo", "CumberlandPlain", "Tumbarumba"]
    sites = ["AdelaideRiver", "DalyUncleared", "DryRiver", "HowardSprings", \
             "SturtPlains"]
    main(fdir, sites, output_dir)
