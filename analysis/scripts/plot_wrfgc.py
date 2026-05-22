"""
WRF-GC January 2025  — Publication-quality figures
Full domain (South/Southeast Asia, 179×149, 27 km)
Environment: wrfgc-postproc  (conda-forge + pip)
"""

import os, glob
import numpy as np
import netCDF4 as nc
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cmocean
from datetime import datetime

# ── Paths ─────────────────────────────────────────────────────────────────────
WRF_RUN = '/home/abdul/TESTs/WRFGC_SEAsia_Jan2025/WRF/run'
FIG_DIR  = '/home/abdul/TESTs/WRFGC_SEAsia_Jan2025/analysis/figures'
os.makedirs(FIG_DIR, exist_ok=True)

PROJ = ccrs.PlateCarree()

# full domain extent + Thailand box
DOM_EXT = [78, 123, -5, 31]
TH_LAT  = (5.5, 20.5)
TH_LON  = (98.0, 106.0)

# ── File lists ─────────────────────────────────────────────────────────────────
all_files  = sorted(glob.glob(os.path.join(WRF_RUN, 'wrfout_d01_2025-01-*')))
# aerosol spin-up: use Jan 10 onwards
# filename: wrfout_d01_2025-01-DD_HH:MM:SS  → day at [19:21]
late_files = [f for f in all_files if
              int(os.path.basename(f)[19:21]) >= 10]

print(f"All files  : {len(all_files)}  ({os.path.basename(all_files[0])[11:21]} – {os.path.basename(all_files[-1])[11:21]})")
print(f"Late files : {len(late_files)} (aerosol, Jan10+)")

# ── Read static grids once ────────────────────────────────────────────────────
with nc.Dataset(all_files[0]) as ds:
    LAT = ds.variables['XLAT'][0]
    LON = ds.variables['XLONG'][0]


# ── IO helpers ────────────────────────────────────────────────────────────────
def load_mean(files, var, lev=0):
    stack = []
    for f in files:
        with nc.Dataset(f) as ds:
            v = ds.variables[var]
            stack.append(v[0, lev] if v.ndim == 4 else v[0])
    return np.mean(stack, axis=0)

def load_col_mean(files, var, p_top_hPa=200):
    """Pressure-weighted tropospheric column mean (surface to p_top_hPa).
    Uses mid-layer averaging: pairs adjacent level-centre pressures to get
    layer thickness dp, then computes Σ(v·dp)/Σ(dp).
    Default p_top=200 hPa keeps only tropospheric layers."""
    p_top_Pa = p_top_hPa * 100.0
    stack = []
    for f in files:
        with nc.Dataset(f) as ds:
            v  = ds.variables[var][0]                           # (lev, lat, lon)
            p  = ds.variables['P'][0] + ds.variables['PB'][0]  # (lev, lat, lon) Pa
        # keep only levels with p > p_top (troposphere)
        tropo_mask = (p > p_top_Pa)                             # (lev, lat, lon) bool
        dp    = np.abs(np.diff(p, axis=0))                      # (lev-1, lat, lon)
        v_mid = 0.5 * (v[:-1] + v[1:])                         # (lev-1, lat, lon)
        # layer is tropospheric if both bounding levels are tropospheric
        lyr_mask = tropo_mask[:-1] & tropo_mask[1:]
        dp_masked = np.where(lyr_mask, dp, 0.0)
        col = np.sum(v_mid * dp_masked, axis=0) / np.maximum(np.sum(dp_masked, axis=0), 1e-6)
        stack.append(col)
    return np.mean(stack, axis=0)

# Bangkok nearest grid point (j=74, i=89  →  lat=13.750, lon=100.500)
BKK_J, BKK_I = 74, 89

def load_ts(files, var, lev=0, point=True):
    """Extract time series.
    point=True  → single Bangkok grid point  (use for validation against stations)
    point=False → spatial mean over Thailand box
    """
    vals, dates = [], []
    for f in files:
        with nc.Dataset(f) as ds:
            v = ds.variables[var]
            data = v[0, lev] if v.ndim == 4 else v[0]
            if point:
                vals.append(float(data[BKK_J, BKK_I]))
            else:
                mask = ((LAT >= TH_LAT[0]) & (LAT <= TH_LAT[1]) &
                        (LON >= TH_LON[0]) & (LON <= TH_LON[1]))
                vals.append(float(np.mean(data[mask])))
        bname = os.path.basename(f)
        dates.append(datetime.strptime(bname[11:21], '%Y-%m-%d'))
    return dates, np.array(vals)

def save(fig, name, dpi=200):
    p = os.path.join(FIG_DIR, name)
    fig.savefig(p, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  ✓ {p}")
    return p


# ── Base-map builder ──────────────────────────────────────────────────────────
def make_map(ax, extent=DOM_EXT, gl_xstep=10, gl_ystep=5,
             left_labels=True, bottom_labels=True):
    """Build a cartopy map.  left_labels / bottom_labels control tick visibility
    — set False for non-edge panels in multi-panel rows to avoid overlap."""
    ax.set_extent(extent, crs=PROJ)
    ax.add_feature(cfeature.LAND,      facecolor='#f2efe9', zorder=0)
    ax.add_feature(cfeature.OCEAN,     facecolor='#d6eaf8', zorder=0)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.55, edgecolor='#333333', zorder=3)
    ax.add_feature(cfeature.BORDERS,   linewidth=0.40, edgecolor='#666666',
                   linestyle='--', zorder=3)
    ax.add_feature(cfeature.RIVERS,    linewidth=0.25, edgecolor='steelblue',
                   alpha=0.5, zorder=2)
    gl = ax.gridlines(draw_labels=True, linewidth=0.35, color='gray',
                      alpha=0.6, linestyle=':', crs=PROJ)
    gl.top_labels   = False
    gl.right_labels = False
    gl.left_labels   = left_labels
    gl.bottom_labels = bottom_labels
    gl.xlocator = mticker.FixedLocator(range(int(extent[0]), int(extent[1])+1, gl_xstep))
    gl.ylocator = mticker.FixedLocator(range(int(extent[2]), int(extent[3])+1, gl_ystep))
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': 7.5, 'color': '#333333'}
    gl.ylabel_style = {'size': 7.5, 'color': '#333333'}
    return ax

def thailand_box(ax, lw=2.2, color='#00c8ff'):
    from matplotlib.patches import Rectangle
    ax.add_patch(Rectangle(
        (TH_LON[0], TH_LAT[0]),
        TH_LON[1]-TH_LON[0], TH_LAT[1]-TH_LAT[0],
        linewidth=lw, edgecolor=color, facecolor='none',
        transform=PROJ, zorder=5))
    ax.text(TH_LON[0]+0.3, TH_LAT[1]+0.4, 'Thailand',
            fontsize=7.5, color=color, transform=PROJ,
            fontweight='bold', zorder=6,
            bbox=dict(facecolor='#1a1a1a', alpha=0.4, pad=1, linewidth=0))

def add_colorbar(fig, ax, im, label, shrink=0.75, pad=0.05, fontsize=9):
    cb = fig.colorbar(im, ax=ax, orientation='horizontal',
                      shrink=shrink, pad=pad)
    cb.set_label(label, fontsize=fontsize)
    cb.ax.tick_params(labelsize=7.5)
    return cb


# ══════════════════════════════════════════════════════════════════════════════
#  PRE-COMPUTE ALL FIELDS
# ══════════════════════════════════════════════════════════════════════════════
print("\n── Loading fields …")

# surface concentrations (lev=0)
o3_ppb   = load_mean(all_files,  'o3')  * 1000
no2_ppb  = load_mean(all_files,  'no2') * 1000
co_ppb   = load_mean(all_files,  'co')  * 1000
pm25     = load_mean(late_files, 'PM2_5_DRY')
pblh     = load_mean(all_files,  'PBLH')
u10      = load_mean(all_files,  'U10')
v10      = load_mean(all_files,  'V10')
ws       = np.sqrt(u10**2 + v10**2)
vc       = pblh * ws           # m²/s

# Bangkok point time-series
dates_all,  o3_bkk   = load_ts(all_files,  'o3')
_,          no2_bkk  = load_ts(all_files,  'no2')
_,          co_bkk   = load_ts(all_files,  'co')
_,          pm25_bkk = load_ts(all_files,  'PM2_5_DRY')

# Thailand spatial-mean time-series
_,          o3_th    = load_ts(all_files,  'o3',        point=False)
_,          no2_th   = load_ts(all_files,  'no2',       point=False)
_,          co_th    = load_ts(all_files,  'co',        point=False)
_,          pm25_th  = load_ts(all_files,  'PM2_5_DRY', point=False)

# Thailand-mean VC — all files for time-series, late_files for stagnation classification
th_mask = ((LAT >= TH_LAT[0]) & (LAT <= TH_LAT[1]) &
           (LON >= TH_LON[0]) & (LON <= TH_LON[1]))
vc_th_ts = []
for _f in late_files:
    with nc.Dataset(_f) as _ds:
        _p  = _ds.variables['PBLH'][0]
        _ws = np.sqrt(_ds.variables['U10'][0]**2 + _ds.variables['V10'][0]**2)
        vc_th_ts.append(float(np.mean((_p * _ws)[th_mask])))
vc_th_ts = np.array(vc_th_ts)

# Bangkok VC for all files (time-series panel)
vc_th_all, vc_bkk_all = [], []
for _f in all_files:
    with nc.Dataset(_f) as _ds:
        _p  = _ds.variables['PBLH'][0]
        _ws = np.sqrt(_ds.variables['U10'][0]**2 + _ds.variables['V10'][0]**2)
        vc_th_all.append(float(np.mean((_p * _ws)[th_mask])))
        vc_bkk_all.append(float((_p * _ws)[BKK_J, BKK_I]))
vc_th_all  = np.array(vc_th_all)
vc_bkk_all = np.array(vc_bkk_all)

# stagnation mask — classified by Thailand-mean VC
stag_idx = np.where(vc_th_ts < 4000)[0]
vent_idx = np.where(vc_th_ts >= 4000)[0]
stag_files = [late_files[i] for i in stag_idx]
vent_files = [late_files[i] for i in vent_idx]
print(f"   Thailand-mean VC:  min={vc_th_ts.min():.0f}  max={vc_th_ts.max():.0f}  median={np.median(vc_th_ts):.0f} m²/s")
print(f"   Stagnant days: {len(stag_files)}  |  Ventilated days: {len(vent_files)}")

pm25_stag = load_mean(stag_files, 'PM2_5_DRY') if stag_files else None
pm25_vent = load_mean(vent_files, 'PM2_5_DRY') if vent_files else None


# ══════════════════════════════════════════════════════════════════════════════
#  FIG 1 — TWO-PANEL: PM₂.₅ + wind  |  O₃ + wind   (full domain)
# ══════════════════════════════════════════════════════════════════════════════
print("\n[Fig 1] PM2.5 + O3 with wind (two-panel)")

fig, axes = plt.subplots(1, 2, figsize=(16, 7),
                         subplot_kw={'projection': PROJ})
fig.subplots_adjust(top=0.83, bottom=0.10, wspace=0.08)
fig.suptitle('WRF-GC January 2025 Mean — Surface Concentrations & 10 m Wind\n'
             'Domain: South/Southeast Asia  |  27 km horizontal resolution',
             fontsize=12, y=0.98)

sk = 9

# Left panel — PM2.5
make_map(axes[0])
im0 = axes[0].pcolormesh(LON, LAT, pm25, transform=PROJ,
                         cmap='YlOrBr', vmin=0, vmax=80,
                         shading='gouraud', zorder=1)
axes[0].quiver(LON[::sk, ::sk], LAT[::sk, ::sk],
               u10[::sk, ::sk], v10[::sk, ::sk],
               transform=PROJ, scale=110, width=0.002,
               color='#1a1a2e', alpha=0.75, zorder=4)
thailand_box(axes[0])
add_colorbar(fig, axes[0], im0, 'PM$_{2.5}$ (µg m$^{-3}$)')
axes[0].set_title('(a)  Surface PM$_{2.5}$ & 10 m Wind', fontsize=10, pad=8)

# Right panel — O3
make_map(axes[1], left_labels=False)
im1 = axes[1].pcolormesh(LON, LAT, o3_ppb, transform=PROJ,
                         cmap='YlOrRd', vmin=15, vmax=75,
                         shading='gouraud', zorder=1)
axes[1].quiver(LON[::sk, ::sk], LAT[::sk, ::sk],
               u10[::sk, ::sk], v10[::sk, ::sk],
               transform=PROJ, scale=110, width=0.002,
               color='#1a1a2e', alpha=0.75, zorder=4)
thailand_box(axes[1])
add_colorbar(fig, axes[1], im1, 'O$_3$ (ppb)')
axes[1].set_title('(b)  Surface O$_3$ & 10 m Wind', fontsize=10, pad=8)

save(fig, 'fig01_fourpanel_species.png', dpi=200)


# ══════════════════════════════════════════════════════════════════════════════
#  FIG 2 — PBLH + VENTILATION COEFFICIENT
# ══════════════════════════════════════════════════════════════════════════════
print("[Fig 2] PBLH and Ventilation Coefficient")

fig, axes = plt.subplots(1, 2, figsize=(14, 6),
                         subplot_kw={'projection': PROJ})
fig.subplots_adjust(wspace=0.08, top=0.90, bottom=0.12)
fig.suptitle('WRF-GC January 2025 Mean — Boundary Layer Mixing Diagnostics',
             fontsize=11)

make_map(axes[0])
im0 = axes[0].pcolormesh(LON, LAT, pblh, transform=PROJ,
                          cmap=cmocean.cm.deep, vmin=0, vmax=1500,
                          shading='gouraud', zorder=1)
sk = 9
axes[0].quiver(LON[::sk, ::sk], LAT[::sk, ::sk],
               u10[::sk, ::sk], v10[::sk, ::sk],
               transform=PROJ, scale=110, width=0.002,
               color='white', alpha=0.85, zorder=4)
thailand_box(axes[0])
add_colorbar(fig, axes[0], im0, 'PBLH (m)')
axes[0].set_title('Planetary Boundary Layer Height  &  10 m Wind', fontsize=10)

make_map(axes[1], left_labels=False)
# Custom diverging: green=ventilated, red=stagnant
cmap_vc = plt.cm.RdYlGn
im1 = axes[1].pcolormesh(LON, LAT, vc, transform=PROJ,
                          cmap=cmap_vc, vmin=0, vmax=6000,
                          shading='gouraud', zorder=1)
# Stagnation threshold contour
cs = axes[1].contour(LON, LAT, vc, levels=[4000], colors='#c0392b',
                     linewidths=1.5, linestyles='--', transform=PROJ, zorder=4)
axes[1].clabel(cs, fmt='VC=4000 m²s⁻¹', fontsize=7, inline=True)
thailand_box(axes[1])
add_colorbar(fig, axes[1], im1, 'Ventilation Coefficient (m² s$^{-1}$)')
axes[1].set_title('Ventilation Coefficient  (VC = PBLH × |Wind$_{10m}$|)', fontsize=10)

save(fig, 'fig02_pblh_vc.png', dpi=200)


# ══════════════════════════════════════════════════════════════════════════════
#  FIG 3 — STAGNATION COMPOSITE: PM₂.₅ / Wind Speed / PBLH
#  Split at median Thailand-mean VC → strong (≤median) vs weak (>median)
# ══════════════════════════════════════════════════════════════════════════════
print("[Fig 3] Stagnation composite — PM2.5, wind speed, PBLH (strong vs weak)")

# classify by Thailand-mean VC, split at median
vc_median = np.median(vc_th_ts)
strong_files = [late_files[i] for i in np.where(vc_th_ts <= vc_median)[0]]
weak_files   = [late_files[i] for i in np.where(vc_th_ts >  vc_median)[0]]
print(f"   Median Thailand VC = {vc_median:.0f} m²/s  |  "
      f"Strong stagnation (≤median): {len(strong_files)} days  |  "
      f"Weak stagnation (>median): {len(weak_files)} days")

pm25_strong = load_mean(strong_files, 'PM2_5_DRY')
pm25_weak   = load_mean(weak_files,   'PM2_5_DRY')
pblh_strong = load_mean(strong_files, 'PBLH')
pblh_weak   = load_mean(weak_files,   'PBLH')

def load_wind_mean(files):
    """Mean 10 m U, V, and wind speed across a list of files."""
    us, vs = [], []
    for f in files:
        with nc.Dataset(f) as ds:
            us.append(ds.variables['U10'][0])
            vs.append(ds.variables['V10'][0])
    u_mean = np.mean(us, axis=0)
    v_mean = np.mean(vs, axis=0)
    return u_mean, v_mean, np.sqrt(u_mean**2 + v_mean**2)

u_strong, v_strong, ws_strong = load_wind_mean(strong_files)
u_weak,   v_weak,   ws_weak   = load_wind_mean(weak_files)

panels = [
    ('fig03a_pm25_composite.png',  'Surface PM$_{2.5}$',
     pm25_strong, pm25_weak, 'PM$_{2.5}$ (µg m$^{-3}$)',    'YlOrBr',       0,   45),
    ('fig03b_wind_composite.png',  '10 m Wind Speed',
     ws_strong,   ws_weak,   '10 m Wind Speed (m s$^{-1}$)', 'Blues',        0,    8),
    ('fig03c_pblh_composite.png',  'Planetary Boundary Layer Height',
     pblh_strong, pblh_weak, 'PBLH (m)',                     cmocean.cm.deep, 0, 1500),
]
col_winds = [(u_strong, v_strong), (u_weak, v_weak)]
sk = 9

for fname, var_title, strong_data, weak_data, cb_label, cmap, vmin, vmax in panels:
    fig, axes = plt.subplots(1, 2, figsize=(13, 6),
                             subplot_kw={'projection': PROJ})
    fig.subplots_adjust(wspace=0.06, top=0.84, bottom=0.10)
    fig.suptitle(
        f'{var_title} — Strong vs Weak Stagnation\n'
        f'Split at median Thailand-mean VC = {vc_median:.0f} m² s$^{{-1}}$  |  '
        f'Strong: n={len(strong_files)}  |  Weak: n={len(weak_files)}  |  Jan 10–28, 2025',
        fontsize=10.5, y=0.98)

    for c, (data, letter, side) in enumerate([
            (strong_data, 'a', 'Strong'), (weak_data, 'b', 'Weak')]):
        ax = axes[c]
        make_map(ax, left_labels=(c == 0))
        im = ax.pcolormesh(LON, LAT, data, transform=PROJ,
                           cmap=cmap, vmin=vmin, vmax=vmax,
                           shading='gouraud', zorder=1)
        u_q, v_q = col_winds[c]
        ax.quiver(LON[::sk, ::sk], LAT[::sk, ::sk],
                  u_q[::sk, ::sk], v_q[::sk, ::sk],
                  transform=PROJ, scale=110, width=0.002,
                  color='#1a1a2e', alpha=0.75, zorder=4)
        thailand_box(ax)
        cb = fig.colorbar(im, ax=ax, orientation='horizontal',
                          shrink=0.78, pad=0.04)
        cb.set_label(cb_label, fontsize=8.5)
        cb.ax.tick_params(labelsize=7.5)
        ax.set_title(f'({letter})  {side} Stagnation', fontsize=10, pad=8)

    save(fig, fname, dpi=200)


# ══════════════════════════════════════════════════════════════════════════════
#  FIG 4 — PM₂.₅ DAILY TIME SERIES — Bangkok grid point
# ══════════════════════════════════════════════════════════════════════════════
print("[Fig 4] PM2.5 time series")

fig, ax = plt.subplots(1, 1, figsize=(9, 5))
fig.subplots_adjust(top=0.80, bottom=0.16)
fig.suptitle('WRF-GC Surface PM$_{2.5}$ — January 2025',
             fontsize=12, y=0.97)

TS_START = datetime(2025, 1, 12)
TS_END   = datetime(2025, 1, 29)

def fmt_ax(ax):
    ax.set_xlim(TS_START, TS_END)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha='right', fontsize=8)
    ax.yaxis.set_tick_params(labelsize=8)
    ax.grid(True, alpha=0.3, linewidth=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# WHO 2021 PM2.5 24-hr: 15 µg/m³ | Thailand NAAQS 24-hr: 37.5 µg/m³
ax_vc = ax.twinx()

ax.plot(dates_all, pm25_bkk, color='#2980b9', lw=1.8,
        marker='D', ms=3, label='PM$_{2.5}$ Bangkok')
ax.axhline(15,   color='#c0392b', lw=1.0, ls='--', alpha=0.85, label='WHO 2021 24-hr (15 µg/m³)')
ax.axhline(37.5, color='#e67e22', lw=1.0, ls=':',  alpha=0.85, label='TH NAAQS (37.5 µg/m³)')
ax_vc.plot(dates_all, vc_bkk_all, color='#27ae60', lw=1.2,
           ls='--', alpha=0.8, label='VC Bangkok')
ax_vc.axhline(4000, color='#16a085', lw=0.9, ls=':', alpha=0.7, label='VC = 4000 m²s⁻¹')

ax.set_ylabel('PM$_{2.5}$ (µg m$^{-3}$)', fontsize=9, color='#2980b9')
ax_vc.set_ylabel('Ventilation Coefficient (m² s$^{-1}$)', fontsize=9, color='#27ae60')
ax.set_title('Bangkok grid point (13.75°N, 100.50°E)', fontsize=9.5,
             pad=6, color='#444444')

pm_handles, pm_labels = ax.get_legend_handles_labels()
vc_handles, vc_labels = ax_vc.get_legend_handles_labels()
leg1 = ax_vc.legend(pm_handles, pm_labels,
                    fontsize=7.5, loc='upper left',
                    framealpha=0.75, edgecolor='#aaaaaa')
leg2 = ax_vc.legend(vc_handles, vc_labels,
                    fontsize=7.5, loc='upper right',
                    framealpha=0.75, edgecolor='#aaaaaa')
ax_vc.add_artist(leg1)
fmt_ax(ax)

save(fig, 'fig04_timeseries.png', dpi=200)


# ══════════════════════════════════════════════════════════════════════════════
#  FIG 5 — O₃ + WIND QUIVERS  (full domain, smooth)
# ══════════════════════════════════════════════════════════════════════════════
print("[Fig 5] O3 + wind")

fig, ax = plt.subplots(1, 1, figsize=(11, 8), subplot_kw={'projection': PROJ})
fig.suptitle('WRF-GC January 2025 Mean — Surface O$_3$ and 10 m Wind\n'
             'Domain: South/Southeast Asia', fontsize=11)

make_map(ax)
im = ax.pcolormesh(LON, LAT, o3_ppb, transform=PROJ,
                   cmap='YlOrRd', vmin=15, vmax=75,
                   shading='gouraud', zorder=1)
sk = 9
ax.quiver(LON[::sk, ::sk], LAT[::sk, ::sk],
          u10[::sk, ::sk], v10[::sk, ::sk],
          transform=PROJ, scale=110, width=0.002,
          color='#1a1a2e', alpha=0.75, zorder=4)
thailand_box(ax)
add_colorbar(fig, ax, im, 'Surface O$_3$ (ppb)', shrink=0.75)

save(fig, 'fig05_o3_wind.png', dpi=200)


# ══════════════════════════════════════════════════════════════════════════════
#  FIG 6 — DOMAIN OVERVIEW (3-panel: CO / PBLH / VC)
# ══════════════════════════════════════════════════════════════════════════════
print("[Fig 6] Domain overview: CO / PBLH / VC")

fig, axes = plt.subplots(1, 2, figsize=(13, 6),
                         subplot_kw={'projection': PROJ})
fig.subplots_adjust(wspace=0.05, top=0.90, bottom=0.12)
fig.suptitle('WRF-GC January 2025 Mean — Boundary Layer Mixing Diagnostics\n'
             'Full Simulation Domain (South/Southeast Asia, 27 km)', fontsize=11)

panels6 = [
    (pblh, 'PBLH (m)',                         cmocean.cm.deep, [0, 1500]),
    (vc,   'Ventilation Coefficient (m² s⁻¹)', 'RdYlGn',        [0, 6000]),
]

for idx, (ax, (data, label, cmap, clim)) in enumerate(zip(axes, panels6)):
    make_map(ax, left_labels=(idx == 0))
    im = ax.pcolormesh(LON, LAT, data, transform=PROJ,
                       cmap=cmap, vmin=clim[0], vmax=clim[1],
                       shading='gouraud', zorder=1)
    thailand_box(ax)
    cb = plt.colorbar(im, ax=ax, shrink=0.75, pad=0.05,
                      orientation='horizontal')
    cb.set_label(label, fontsize=8.5)
    cb.ax.tick_params(labelsize=7.5)
    ax.set_title(label, fontsize=9.5, pad=3)

save(fig, 'fig06_domain_overview.png', dpi=200)


print(f"\nAll figures saved → {FIG_DIR}")
for f in sorted(os.listdir(FIG_DIR)):
    sz = os.path.getsize(os.path.join(FIG_DIR, f)) // 1024
    print(f"  {f}  ({sz} kB)")
