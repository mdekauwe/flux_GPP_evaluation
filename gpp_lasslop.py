#!/usr/bin/env python

"""
Model GPP using a rectangular hyperbolic light-response curve

Reference:
----------
* Lasslop, G. et al. ASSLOP, G. (2010), Separation of net ecosystem exchange
  into assimilation and respiration using a light response curve approach:
  critical issues and global evaluation. Global Change Biology, 16: 187-208.

That's all folks.

"""
__author__ = "Martin De Kauwe"
__version__ = "1.0 (01.07.2020)"
__email__ = "mdekauwe@gmail.com"

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import sys


def calculate_gpp_lasslop(alpha, k, D0, Fsd, D):
    """
    Arrhenius-type model of respiration

    Paramaters:
    ----------
    alpha : float
        canopy light utlisation efficiency (umol C J-1), which represents the
        initial slope of the light-response curve - fitted
    Rg : float
        global radiation (W m-2)
    beta : float
        Exponential decreasing func to limit C uptake at high D - fitted
    k : float
        fitted


    Tair : float
        air temperature (deg C)
    rb : float
        base respiration at the reference temp (umol C m-2 s-1) - fitted

    Reference:
    ----------
    * Lloyd J, Taylor JA (1994) On the temperature dependence of soil
      respiration. Functional Ecology, 8, 315–323.

    Returns:
    --------
    Respiration : float
        respiration rate, umol m-2 s-1
    """

    beta = vpd_func(k, D, D0)
    GPP = alpha * beta * Fsd / (alpha * Fsd + beta)

    return GPP


def vpd_func(k, D, D0):
    """
    Exponential decreasing func for beta at high D following Korner 1995
    """
    beta = np.where(D > D0, beta0 * np.exp(-k * (D - D0)), beta0

    return beta
