"""
precompute.py — Load all shared time series from wrfout files and classify
stagnation / ventilated regimes.

Call `load_all()` to get a namespace with all pre-computed arrays.
This is called once by run_all.py and the result passed to every figure function.
Each individual figure script can also call it directly when run standalone.

Returns a SimpleNamespace with fields:
    dates_late, late_files, stag_files, vent_files
    stag_mask, vent_mask, vc_median
    vc_bkk_ts, vc_th_ts
    pm25_bkk, pm25_th
    oh_pptv, no3_pptv, n2o5_pptv
    no2_ppb, no_ppb, nox_ppb
    so4_ugm3, nit_ugm3, nh4_ugm3, bc_ugm3, oa_ugm3
    soap_ppb, soas_ppb, soatot_ppb
    isop_ppb
    u10_stag, v10_stag, u10_vent, v10_vent
    pm25_stag_map, pm25_vent_map
    LAT, LON, th_mask
    n_air_bkk
"""

import glob
import os
from types import SimpleNamespace
from datetime import datetime

import numpy as np
import netCDF4 as nc

from config import WRF_RUN, TH_LAT, TH_LON, BKK_J, BKK_I, N_AIR_SFC
from loaders import (load_bkk_ts, load_th_ts, load_vc_ts,
                     load_spatial_mean, get_n_air)


def load_all():
    # ── File lists ──────────────────────────────────────────────────────────
    all_files  = sorted(glob.glob(os.path.join(WRF_RUN, 'wrfout_d01_2025-01-*')))
    late_files = [f for f in all_files if int(os.path.basename(f)[19:21]) >= 10]
    print(f"Files total: {len(all_files)}  |  Late (Jan 10+): {len(late_files)}")

    # ── Static grids ────────────────────────────────────────────────────────
    with nc.Dataset(all_files[0]) as ds:
        LAT = ds.variables['XLAT'][0]
        LON = ds.variables['XLONG'][0]

    th_mask = ((LAT >= TH_LAT[0]) & (LAT <= TH_LAT[1]) &
               (LON >= TH_LON[0]) & (LON <= TH_LON[1]))

    # ── Ventilation coefficient and regime classification ────────────────────
    vc_bkk_ts, vc_th_ts = load_vc_ts(late_files, th_mask)
    vc_median = np.median(vc_th_ts)
    stag_mask = vc_th_ts <= vc_median
    vent_mask = ~stag_mask
    stag_files = [late_files[i] for i in np.where(stag_mask)[0]]
    vent_files = [late_files[i] for i in np.where(vent_mask)[0]]
    dates_late = [datetime.strptime(os.path.basename(f)[11:21], '%Y-%m-%d')
                  for f in late_files]

    print(f"VC median = {vc_median:.0f} m²/s  |  "
          f"Stagnation: {stag_mask.sum()} days  |  Ventilated: {vent_mask.sum()} days")

    # ── Bangkok point air density (for ppmv → µg/m³) ───────────────────────
    with nc.Dataset(late_files[10]) as ds_ref:
        n_air_bkk = float(get_n_air(ds_ref)[BKK_J, BKK_I])

    def ugm3(var_ts, mw):
        return var_ts * n_air_bkk * mw

    # ── Core time series at Bangkok ─────────────────────────────────────────
    _, pm25_bkk  = load_bkk_ts(late_files, 'PM2_5_DRY')
    _, oh_bkk    = load_bkk_ts(late_files, 'oh')
    _, no3_bkk   = load_bkk_ts(late_files, 'no3')
    _, n2o5_bkk  = load_bkk_ts(late_files, 'n2o5')
    _, no2_bkk   = load_bkk_ts(late_files, 'no2')
    _, no_bkk    = load_bkk_ts(late_files, 'no')
    _, soap_bkk  = load_bkk_ts(late_files, 'soap')
    _, soas_bkk  = load_bkk_ts(late_files, 'soas')
    _, soaie_bkk = load_bkk_ts(late_files, 'soaie')
    _, soagx_bkk = load_bkk_ts(late_files, 'soagx')
    _, isop_bkk  = load_bkk_ts(late_files, 'isop')
    _, so4_bkk   = load_bkk_ts(late_files, 'so4')
    _, nit_bkk   = load_bkk_ts(late_files, 'nit')
    _, nh4_bkk   = load_bkk_ts(late_files, 'nh4')
    _, bcpi_bkk  = load_bkk_ts(late_files, 'bcpi')
    _, bcpo_bkk  = load_bkk_ts(late_files, 'bcpo')

    # Thailand mean PM2.5
    _, pm25_th = load_th_ts(late_files, 'PM2_5_DRY', th_mask)

    # ── Unit conversions ────────────────────────────────────────────────────
    oh_pptv   = oh_bkk   * 1e6
    no3_pptv  = no3_bkk  * 1e6
    n2o5_pptv = n2o5_bkk * 1e6
    no2_ppb   = no2_bkk  * 1e3
    no_ppb    = no_bkk   * 1e3
    nox_ppb   = (no_bkk + no2_bkk) * 1e3
    soap_ppb  = soap_bkk * 1e3
    soas_ppb  = soas_bkk * 1e3
    isop_ppb  = isop_bkk * 1e3
    soatot_ppb = (soap_bkk + soas_bkk + soaie_bkk + soagx_bkk) * 1e3

    so4_ugm3 = ugm3(so4_bkk, 96)
    nit_ugm3 = ugm3(nit_bkk, 62)
    nh4_ugm3 = ugm3(nh4_bkk, 18)
    bc_ugm3  = ugm3(bcpi_bkk + bcpo_bkk, 12)
    oa_ugm3  = np.maximum(pm25_bkk - so4_ugm3 - nit_ugm3 - nh4_ugm3 - bc_ugm3, 0.0)

    # ── Spatial composites for maps ─────────────────────────────────────────
    pm25_stag_map = load_spatial_mean(stag_files, 'PM2_5_DRY')
    pm25_vent_map = load_spatial_mean(vent_files, 'PM2_5_DRY')
    u10_stag = load_spatial_mean(stag_files, 'U10')
    v10_stag = load_spatial_mean(stag_files, 'V10')
    u10_vent = load_spatial_mean(vent_files, 'U10')
    v10_vent = load_spatial_mean(vent_files, 'V10')

    print("Pre-compute complete.")

    return SimpleNamespace(
        late_files=late_files, stag_files=stag_files, vent_files=vent_files,
        dates_late=dates_late,
        stag_mask=stag_mask, vent_mask=vent_mask, vc_median=vc_median,
        vc_bkk_ts=vc_bkk_ts, vc_th_ts=vc_th_ts,
        pm25_bkk=pm25_bkk, pm25_th=pm25_th,
        oh_pptv=oh_pptv, no3_pptv=no3_pptv, n2o5_pptv=n2o5_pptv,
        no2_ppb=no2_ppb, no_ppb=no_ppb, nox_ppb=nox_ppb,
        so4_ugm3=so4_ugm3, nit_ugm3=nit_ugm3, nh4_ugm3=nh4_ugm3,
        bc_ugm3=bc_ugm3, oa_ugm3=oa_ugm3,
        soap_ppb=soap_ppb, soas_ppb=soas_ppb, soatot_ppb=soatot_ppb,
        isop_ppb=isop_ppb,
        u10_stag=u10_stag, v10_stag=v10_stag,
        u10_vent=u10_vent, v10_vent=v10_vent,
        pm25_stag_map=pm25_stag_map, pm25_vent_map=pm25_vent_map,
        LAT=LAT, LON=LON, th_mask=th_mask,
        n_air_bkk=n_air_bkk,
    )
