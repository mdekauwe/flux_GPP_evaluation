#!/usr/bin/env python

"""
Load OzFlux file and extract nedded vars.

That's all folks.
"""
__author__ = "Martin De Kauwe"
__version__ = "1.0 (07.05.2020)"
__email__ = "mdekauwe@gmail.com"

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import sys

def read_nc_file(fname):

    ds = xr.open_dataset(fname)

    SW = ds.Fsd[:,0,0]
    VPD = ds.VPD[:,0,0]
    Tair = ds.Ta[:,0,0]
    Reco = ds.ER[:,0,0]
    NEE = ds.Fc[:,0,0]

    # Separate the data into morning and afteroon
    VPD_day = np.ma.masked_where(SW <= 10, VPD)
    Tair_day = np.ma.masked_where(SW <= 10., Tair)
    SW_day = np.ma.masked_where(SW <= 10, SW)
    Reco_day = np.ma.masked_where(SW <= 10, Reco)
    NEE_day = np.ma.masked_where(SW <= 10, NEE)
    VPD_night = np.ma.masked_where(SW > 10, VPD)
    Tair_night = np.ma.masked_where(SW > 10., Tair)
    SW_night = np.ma.masked_where(SW > 10, SW)
    Reco_night = np.ma.masked_where(SW > 10, Reco)
    NEE_night = np.ma.masked_where(SW > 10, NEE)
    dates = ds.time

    # Screen some bad data - Peter makes a good argument about this messing
    # with the error statistics. Will do this for now.
    VPD_day = np.ma.masked_where(VPD_day < 0.0, VPD_day)
    Reco_day = np.ma.masked_where(Reco_day < -100.0, Reco_day)
    Reco_night = np.ma.masked_where(Reco_night < -100.0, Reco_night)

    #plt.plot(Reco_day)
    #plt.plot(Reco_night)
    #plt.show()
    #sys.exit()


    return (dates, VPD_day, Tair_day, VPD_day, SW_day,
            Reco_day, Reco_night, NEE_day)




if __name__ == "__main__":

    fname = "data/Yanco_L6.nc"
    (dates, VPD_day,
     Tair_day, VPD_day, SW_day,
     Reco_day, Reco_night, NEE_day) = read_nc_file(fname)

    fig = plt.figure(figsize=(8,10))
    fig.subplots_adjust(hspace=0.1)
    fig.subplots_adjust(wspace=0.2)
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.family'] = "sans-serif"
    plt.rcParams['font.sans-serif'] = "Helvetica"
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['font.size'] = 12
    plt.rcParams['legend.fontsize'] = 12
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12

    ax1 = fig.add_subplot(5,1,1)
    ax2 = fig.add_subplot(5,1,2)
    ax3 = fig.add_subplot(5,1,3)
    ax4 = fig.add_subplot(5,1,4)
    ax5 = fig.add_subplot(5,1,5)


    ax1.plot(dates, SW_day)
    ax2.plot(dates, VPD_day)
    ax3.plot(dates, Tair_day)
    ax4.plot(dates, NEE_day)
    ax5.plot(dates, Reco_night)

    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax2.get_xticklabels(), visible=False)
    plt.setp(ax3.get_xticklabels(), visible=False)
    plt.setp(ax4.get_xticklabels(), visible=False)

    ax1.set_ylabel("SW")
    ax2.set_ylabel("VPD")
    ax3.set_ylabel("Tair")
    ax4.set_ylabel("NEE")
    ax5.set_ylabel("Reco")

    fig.tight_layout()
    plt.show()
