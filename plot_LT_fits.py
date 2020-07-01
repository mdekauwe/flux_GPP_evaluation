#!/usr/bin/env python

"""
Plot rb and E0 of the Lloyd Taylor by site

That's all folks.
"""
__author__ = "Martin De Kauwe"
__version__ = "1.0 (01.07.2020)"
__email__ = "mdekauwe@gmail.com"

import os
import sys
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def main():

    fname = "outputs/LT_fits_annual.csv"
    df = pd.read_csv(fname)
    df = df[df.rb > -500.]

    sns.set_style("ticks")
    sns.set_style({"xtick.direction": "in","ytick.direction": "in"})

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

    # define outlier properties
    flierprops = dict(marker='o', markersize=3, markerfacecolor="black")
    ax = sns.boxplot(x="site", y="rb", data=df, palette="Set2",
                     flierprops=flierprops)

    ax.set_ylabel("rb (\u03BCmol C m$^{-2}$ s$^{-1}$)")
    ax.set_xlabel(" ")
    ax.set_xticklabels( ax.get_xticklabels(),
                        rotation=45,
                        horizontalalignment='right')

    plot_dir = "plots"
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)

    plt.savefig(os.path.join(plot_dir, "rb.pdf"),
                bbox_inches='tight', pad_inches=0.1)

    plt.show()

if __name__ == "__main__":

    main()
