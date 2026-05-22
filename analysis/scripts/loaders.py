"""
loaders.py — Functions for reading variables from WRF-GC wrfout files.

All chemistry tracers (oh, no, no2, soap, soas, so4, …) are in ppmv.
PM2_5_DRY is in µg m⁻³. Meteorological fields (PBLH, U10, V10) are in SI units.
"""

import os
import numpy as np
import netCDF4 as nc
from datetime import datetime

from config import BKK_J, BKK_I


def get_n_air(ds, lev=0):
    """Dry air number density (mol m⁻³) at a given model level from WRF pressure and temperature."""
    P     = ds.variables['P'][0, lev] + ds.variables['PB'][0, lev]
    theta = ds.variables['T'][0, lev] + 300.0
    T     = theta * (P / 1e5) ** 0.2857
    return P / (8.314 * T)


def ppmv_to_ugm3(ppmv_arr, mw, n_air):
    """Convert ppmv → µg m⁻³.  C = ppmv × n_air (mol/m³) × MW (g/mol)."""
    return ppmv_arr * n_air * mw


def load_spatial_mean(files, var, lev=0):
    """Temporal mean of a 2D spatial field across a list of wrfout files."""
    stack = []
    for f in files:
        with nc.Dataset(f) as ds:
            v = ds.variables[var]
            stack.append(v[0, lev] if v.ndim == 4 else v[0])
    return np.mean(stack, axis=0)


def load_spatial_sum_ppmv(files, var_list, lev=0):
    """Sum multiple ppmv tracers and return their temporal-mean spatial field."""
    stack = []
    for f in files:
        with nc.Dataset(f) as ds:
            total = np.zeros(ds.variables[var_list[0]][0, 0].shape
                             if ds.variables[var_list[0]].ndim == 4
                             else ds.variables[var_list[0]][0].shape)
            for v in var_list:
                arr = ds.variables[v]
                total += arr[0, lev] if arr.ndim == 4 else arr[0]
        stack.append(total)
    return np.mean(stack, axis=0)


def load_bkk_ts(files, var, lev=0):
    """Time series of a variable at the Bangkok grid point (BKK_J, BKK_I)."""
    vals, dates = [], []
    for f in files:
        with nc.Dataset(f) as ds:
            v    = ds.variables[var]
            data = v[0, lev] if v.ndim == 4 else v[0]
            vals.append(float(data[BKK_J, BKK_I]))
        dates.append(datetime.strptime(os.path.basename(f)[11:21], '%Y-%m-%d'))
    return dates, np.array(vals)


def load_th_ts(files, var, th_mask, lev=0):
    """Time series of the Thailand spatial mean for a given variable."""
    vals, dates = [], []
    for f in files:
        with nc.Dataset(f) as ds:
            v    = ds.variables[var]
            data = v[0, lev] if v.ndim == 4 else v[0]
            vals.append(float(np.mean(data[th_mask])))
        dates.append(datetime.strptime(os.path.basename(f)[11:21], '%Y-%m-%d'))
    return dates, np.array(vals)


def load_vc_ts(files, th_mask, bkk_j=BKK_J, bkk_i=BKK_I):
    """Compute ventilation coefficient (VC = PBLH × |Wind10m|) time series."""
    vc_bkk, vc_th = [], []
    for f in files:
        with nc.Dataset(f) as ds:
            pblh = ds.variables['PBLH'][0]
            ws   = np.sqrt(ds.variables['U10'][0]**2 + ds.variables['V10'][0]**2)
            vc   = pblh * ws
            vc_bkk.append(float(vc[bkk_j, bkk_i]))
            vc_th.append(float(np.mean(vc[th_mask])))
    return np.array(vc_bkk), np.array(vc_th)
