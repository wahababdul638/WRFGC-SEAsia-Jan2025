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
import pandas as pd

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

    # ── Try to load time series from precomputed CSV ──
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'bangkok_comprehensive_jan2025.csv')
    
    if os.path.exists(csv_path):
        print(f'Loading Bangkok time series from {csv_path}...')
        df = pd.read_csv(csv_path)
        dates_late = [datetime.strptime(t[:10], '%Y-%m-%d') for t in df['Time']]
        
        vc_bkk_ts = df['VC_BKK'].values
        vc_th_ts  = df['VC_TH_Mean'].values
        
        pm25_bkk = df['PM25_ugm3'].values
        oh_bkk   = df['oh_ppmv'].values
        no3_bkk  = df['no3_ppmv'].values
        n2o5_bkk = df['n2o5_ppmv'].values
        no2_bkk  = df['no2_ppmv'].values
        no_bkk   = df['no_ppmv'].values
        soap_bkk = df['soap_ppmv'].values
        soas_bkk = df['soas_ppmv'].values
        soaie_bkk = df['soaie_ppmv'].values
        soagx_bkk = df['soagx_ppmv'].values
        isop_bkk = df['isop_ppmv'].values
        so4_bkk  = df['so4_ppmv'].values
        nit_bkk  = df['nit_ppmv'].values
        nh4_bkk  = df['nh4_ppmv'].values
        bcpi_bkk = df['bcpi_ppmv'].values
        bcpo_bkk = df['bcpo_ppmv'].values
        o3_bkk   = df['o3_ppmv'].values
        hno3_bkk = df['hno3_ppmv'].values
        ho2_bkk  = df['ho2_ppmv'].values
        mtp_bkk  = df['mtpa_ppmv'].values + df['mtpo_ppmv'].values + df['limo_ppmv'].values
        arom_bkk = df['aromp4_ppmv'].values + df['aromp5_ppmv'].values
        w_bkk    = df['W_m_s'].values
        pblh_bkk = df['PBLH_m'].values
        
        n_air_bkk = df['n_air_mol_m3'].mean()
        _, pm25_th = load_th_ts(late_files, 'PM2_5_DRY', th_mask)

    else:
        print('CSV not found. Loading time series from wrfout files (slow)...')
        vc_bkk_ts, vc_th_ts = load_vc_ts(late_files, th_mask)
        dates_late = [datetime.strptime(os.path.basename(f)[11:21], '%Y-%m-%d')
                      for f in late_files]

        with nc.Dataset(late_files[10]) as ds_ref:
            n_air_bkk = float(get_n_air(ds_ref)[BKK_J, BKK_I])

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
        _, o3_bkk    = load_bkk_ts(late_files, 'o3')
        _, hno3_bkk  = load_bkk_ts(late_files, 'hno3')
        _, ho2_bkk   = load_bkk_ts(late_files, 'ho2')
        _, mtpa      = load_bkk_ts(late_files, 'mtpa')
        _, mtpo      = load_bkk_ts(late_files, 'mtpo')
        _, limo      = load_bkk_ts(late_files, 'limo')
        mtp_bkk = mtpa + mtpo + limo
        _, aromp4    = load_bkk_ts(late_files, 'aromp4')
        _, aromp5    = load_bkk_ts(late_files, 'aromp5')
        arom_bkk = aromp4 + aromp5
        _, pm25_th   = load_th_ts(late_files, 'PM2_5_DRY', th_mask)

    vc_median = np.median(vc_th_ts)
    stag_mask = vc_th_ts <= vc_median
    vent_mask = ~stag_mask
    stag_files = [late_files[i] for i in np.where(stag_mask)[0]]
    vent_files = [late_files[i] for i in np.where(vent_mask)[0]]

    print(f'VC median = {vc_median:.0f} m²/s  |  '
          f'Stagnation: {stag_mask.sum()} days  |  Ventilated: {vent_mask.sum()} days')

    def ugm3(var_ts, mw):
        return var_ts * n_air_bkk * mw

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
        o3_ppb=o3_bkk*1e3, hno3_ppb=hno3_bkk*1e3, ho2_pptv=ho2_bkk*1e6,
        mtp_ppb=mtp_bkk*1e3, arom_ppb=arom_bkk*1e3,
        w_bkk=w_bkk, pblh_bkk=pblh_bkk,
        LAT=LAT, LON=LON, th_mask=th_mask,
        n_air_bkk=n_air_bkk,
    )
