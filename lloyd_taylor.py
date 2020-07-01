#!/usr/bin/env python

"""
Model Reco assuming an Arrhenius-type model following Lloyd & Taylor (1994)

Reference:
----------
* Lloyd J, Taylor JA (1994) On the temperature dependence of soil respiration.
  Functional Ecology, 8, 315–323.

That's all folks.

"""
__author__ = "Martin De Kauwe"
__version__ = "1.0 (07.05.2020)"
__email__ = "mdekauwe@gmail.com"

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import sys




def Resp_Lloyd_Taylor(Tair, rb, E0):
    """
    Arrhenius-type model of respiration

    Paramaters:
    ----------
    Tair : float
        air temperature (deg C)
    rb : float
        base respiration at the reference temp (umol C m-2 s-1) - fitted
    E0 : float
        temperature sensitivity (deg C) - fitted

    Reference:
    ----------
    * Lloyd J, Taylor JA (1994) On the temperature dependence of soil
      respiration. Functional Ecology, 8, 315–323.

    Returns:
    --------
    Respiration : float
        respiration rate, umol m-2 s-1
    """
    DEG_2_K = 273.15
    Tref = 288.15 # Reference temperature, 15 deg C
    T0 = 227.13   # -46.02 (deg C)
    Tk = Tair + DEG_2_K
    Resp = rb * np.exp(E0 * (1.0 / (Tref - T0) - 1.0 / (Tk - T0)))

    return Resp
