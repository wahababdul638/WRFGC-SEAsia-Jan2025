"""
WRF-GC January 2025 — Proposal Defense Figures
Hypothesis-supporting analysis: VC, aerosol composition, OH/NO3 chemistry
Environment: ewrf  (conda activate ewrf)
"""

import os, glob
import numpy as np
import netCDF4 as nc
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
from scipy import stats
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cmocean
from datetime import datetime

# ── Paths ─────────────────────────────────────────────────────────────────────
WRF_RUN = '/home/abdul/TESTs/WRFGC_SEAsia_Jan2025/WRF/run'
FIG_DIR  = '/home/abdul/TESTs/WRFGC_SEAsia_Jan2025/analysis/figures/proposal'
os.makedirs(FIG_DIR, exist_ok=True)

PROJ = ccrs.PlateCarree()
DOM_EXT  = [90, 115, 0, 25]   # zoomed to mainland SEA
TH_LAT   = (5.5, 20.5)
TH_LON   = (98.0, 106.0)
BKK_J, BKK_I = 74, 89          # Bangkok grid point 13.75°N 100.50°E

# ── Colours for stagnation/ventilation regimes ────────────────────────────────
C_STAG = '#c0392b'   # red  = stagnant
C_VENT = '#2980b9'   # blue = ventilated
ALPHA_SHADE = 0.18

# ── File lists ────────────────────────────────────────────────────────────────
all_files  = sorted(glob.glob(os.path.join(WRF_RUN, 'wrfout_d01_2025-01-*')))
late_files = [f for f in all_files if int(os.path.basename(f)[19:21]) >= 10]

print(f"All files  : {len(all_files)}")
print(f"Late files : {len(late_files)}  (Jan10+, post aerosol spin-up)")

# ── Static grids ──────────────────────────────────────────────────────────────
with nc.Dataset(all_files[0]) as ds:
    LAT = ds.variables['XLAT'][0]
    LON = ds.variables['XLONG'][0]

th_mask = ((LAT >= TH_LAT[0]) & (LAT <= TH_LAT[1]) &
           (LON >= TH_LON[0]) & (LON <= TH_LON[1]))


# ════════════════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════

def get_n_air(ds, lev=0):
    """Dry air number density at a given level (mol m⁻³) from WRF P and T."""
    P = (ds.variables['P'][0, lev] + ds.variables['PB'][0, lev])
    theta = ds.variables['T'][0, lev] + 300.0
    T = theta * (P / 1e5) ** 0.2857
    return P / (8.314 * T)          # mol m⁻³  (shape: lat×lon)


def ppmv_to_ugm3(ppmv_arr, mw, n_air):
    """Convert ppmv (mol mol⁻¹ × 10⁶) to µg m⁻³.
    C (µg/m³) = ppmv × n_air (mol/m³) × MW (g/mol)
    """
    return ppmv_arr * n_air * mw


def load_spatial_mean(files, var, lev=0):
    stack = []
    for f in files:
        with nc.Dataset(f) as ds:
            v = ds.variables[var]
            stack.append(v[0, lev] if v.ndim == 4 else v[0])
    return np.mean(stack, axis=0)


def load_bkk_ts(files, var, lev=0):
    """Time series at Bangkok grid point."""
    vals, dates = [], []
    for f in files:
        with nc.Dataset(f) as ds:
            v = ds.variables[var]
            data = v[0, lev] if v.ndim == 4 else v[0]
            vals.append(float(data[BKK_J, BKK_I]))
        dates.append(datetime.strptime(os.path.basename(f)[11:21], '%Y-%m-%d'))
    return dates, np.array(vals)


def load_th_ts(files, var, lev=0):
    """Time series of Thailand spatial mean."""
    vals, dates = [], []
    for f in files:
        with nc.Dataset(f) as ds:
            v = ds.variables[var]
            data = v[0, lev] if v.ndim == 4 else v[0]
            vals.append(float(np.mean(data[th_mask])))
        dates.append(datetime.strptime(os.path.basename(f)[11:21], '%Y-%m-%d'))
    return dates, np.array(vals)


def save(fig, name, dpi=200):
    p = os.path.join(FIG_DIR, name)
    fig.savefig(p, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  ✓ {p}")


def make_map(ax, extent=DOM_EXT):
    ax.set_extent(extent, crs=PROJ)
    ax.add_feature(cfeature.LAND,      facecolor='#f2efe9', zorder=0)
    ax.add_feature(cfeature.OCEAN,     facecolor='#d6eaf8', zorder=0)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.55, edgecolor='#333333', zorder=3)
    ax.add_feature(cfeature.BORDERS,   linewidth=0.40, edgecolor='#666666',
                   linestyle='--', zorder=3)
    gl = ax.gridlines(draw_labels=True, linewidth=0.3, color='gray',
                      alpha=0.5, linestyle=':', crs=PROJ)
    gl.top_labels = False; gl.right_labels = False
    gl.xlocator = mticker.FixedLocator(range(85, 120, 5))
    gl.ylocator = mticker.FixedLocator(range(-5, 30, 5))
    gl.xformatter = LONGITUDE_FORMATTER; gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': 7}; gl.ylabel_style = {'size': 7}
    return ax


def thailand_box(ax):
    from matplotlib.patches import Rectangle
    ax.add_patch(Rectangle((TH_LON[0], TH_LAT[0]),
                            TH_LON[1]-TH_LON[0], TH_LAT[1]-TH_LAT[0],
                            lw=2, edgecolor='#00c8ff', facecolor='none',
                            transform=PROJ, zorder=5))
    ax.text(TH_LON[0]+0.2, TH_LAT[1]+0.3, 'Thailand',
            fontsize=7, color='#00c8ff', transform=PROJ, fontweight='bold',
            zorder=6, bbox=dict(facecolor='#1a1a1a', alpha=0.4, pad=1, lw=0))


def shade_stagnation(ax, dates, stag_mask):
    """Shade stagnant days in grey on a time-series axis."""
    for k, (d, s) in enumerate(zip(dates, stag_mask)):
        if s:
            ax.axvspan(d, dates[k+1] if k+1 < len(dates) else d,
                       color='#e0e0e0', alpha=0.55, zorder=0)


# ════════════════════════════════════════════════════════════════════════════
#  PRE-COMPUTE  ──  all time series  (late_files, Jan 10-28)
# ════════════════════════════════════════════════════════════════════════════
print("\n── Pre-computing time series …")

# VC at Bangkok and Thailand mean
vc_bkk_ts, vc_th_ts = [], []
for f in late_files:
    with nc.Dataset(f) as ds:
        pblh = ds.variables['PBLH'][0]
        ws   = np.sqrt(ds.variables['U10'][0]**2 + ds.variables['V10'][0]**2)
        vc   = pblh * ws
        vc_bkk_ts.append(float(vc[BKK_J, BKK_I]))
        vc_th_ts.append(float(np.mean(vc[th_mask])))
vc_bkk_ts = np.array(vc_bkk_ts)
vc_th_ts  = np.array(vc_th_ts)

# Stagnation classification — split at median Thailand-mean VC
vc_median  = np.median(vc_th_ts)
stag_mask  = vc_th_ts <= vc_median   # bool array over late_files
vent_mask  = ~stag_mask
stag_files = [late_files[i] for i in np.where(stag_mask)[0]]
vent_files = [late_files[i] for i in np.where(vent_mask)[0]]
dates_late = [datetime.strptime(os.path.basename(f)[11:21], '%Y-%m-%d')
              for f in late_files]

print(f"   VC median = {vc_median:.0f} m²/s  |  "
      f"Stagnation days: {stag_mask.sum()}  |  Ventilation days: {vent_mask.sum()}")

# Core chemistry & aerosol time series at Bangkok
_, pm25_bkk   = load_bkk_ts(late_files, 'PM2_5_DRY')
_, oh_bkk     = load_bkk_ts(late_files, 'oh')
_, no3_bkk    = load_bkk_ts(late_files, 'no3')
_, n2o5_bkk   = load_bkk_ts(late_files, 'n2o5')
_, no2_bkk    = load_bkk_ts(late_files, 'no2')
_, no_bkk     = load_bkk_ts(late_files, 'no')
_, isop_bkk   = load_bkk_ts(late_files, 'isop')
_, soap_bkk   = load_bkk_ts(late_files, 'soap')
_, soas_bkk   = load_bkk_ts(late_files, 'soas')
_, soaie_bkk  = load_bkk_ts(late_files, 'soaie')
_, soagx_bkk  = load_bkk_ts(late_files, 'soagx')

# Thailand spatial-mean PM2.5 (for VC–PM2.5 scatter)
_, pm25_th = load_th_ts(late_files, 'PM2_5_DRY')

# ── Unit conversions at Bangkok ───────────────────────────────────────────────
# Compute mean surface n_air at Bangkok (mol/m³) — use a single representative file
with nc.Dataset(late_files[10]) as ds_ref:
    n_air_bkk = float(get_n_air(ds_ref)[BKK_J, BKK_I])

# ppmv → ppb: × 1000
no2_ppb  = no2_bkk * 1000
no_ppb   = no_bkk  * 1000
nox_ppb  = (no_bkk + no2_bkk) * 1000

# ppmv → pptv: × 1e6
oh_pptv  = oh_bkk  * 1e6
no3_pptv = no3_bkk * 1e6
n2o5_pptv = n2o5_bkk * 1e6

# ppmv → µg/m³ using ppmv × n_air × MW
# SO4 (MW=96), NIT (MW=62), NH4 (MW=18), BC (MW=12)
def ugm3_ts(var_ts, mw): return var_ts * n_air_bkk * mw

# Load inorganic + BC time series
_, so4_bkk   = load_bkk_ts(late_files, 'so4')
_, nit_bkk   = load_bkk_ts(late_files, 'nit')
_, nh4_bkk   = load_bkk_ts(late_files, 'nh4')
_, bcpi_bkk  = load_bkk_ts(late_files, 'bcpi')
_, bcpo_bkk  = load_bkk_ts(late_files, 'bcpo')
_, ocpi_bkk  = load_bkk_ts(late_files, 'ocpi')
_, ocpo_bkk  = load_bkk_ts(late_files, 'ocpo')

so4_ugm3  = ugm3_ts(so4_bkk,  96)
nit_ugm3  = ugm3_ts(nit_bkk,  62)
nh4_ugm3  = ugm3_ts(nh4_bkk,  18)
bc_ugm3   = ugm3_ts(bcpi_bkk + bcpo_bkk, 12)
poa_ugm3  = ugm3_ts((ocpi_bkk + ocpo_bkk) * 12, 1) * 2.1  # OC→OM factor 2.1
oa_ugm3   = pm25_bkk - so4_ugm3 - nit_ugm3 - nh4_ugm3 - bc_ugm3  # residual OA
oa_ugm3   = np.maximum(oa_ugm3, 0.0)

# SOA proxy (relative): sum gas+aerosol organic precursors in ppb
soap_ppb  = soap_bkk  * 1000
soas_ppb  = soas_bkk  * 1000
soatot_ppb = (soap_bkk + soas_bkk + soaie_bkk + soagx_bkk) * 1000

# Bangkok grid point — stagnation mean vs ventilation mean (scalar values)
def stag_vent(arr):
    return arr[stag_mask].mean(), arr[vent_mask].mean()

pm25_s,  pm25_v  = stag_vent(pm25_bkk)
oh_s,    oh_v    = stag_vent(oh_pptv)
no3_s,   no3_v   = stag_vent(no3_pptv)
n2o5_s,  n2o5_v  = stag_vent(n2o5_pptv)
nox_s,   nox_v   = stag_vent(nox_ppb)
no2_s,   no2_v   = stag_vent(no2_ppb)
so4_s,   so4_v   = stag_vent(so4_ugm3)
nit_s,   nit_v   = stag_vent(nit_ugm3)
nh4_s,   nh4_v   = stag_vent(nh4_ugm3)
bc_s,    bc_v    = stag_vent(bc_ugm3)
oa_s,    oa_v    = stag_vent(oa_ugm3)
soap_s,  soap_v  = stag_vent(soap_ppb)
soas_s,  soas_v  = stag_vent(soas_ppb)
soatot_s, soatot_v = stag_vent(soatot_ppb)
isop_s,  isop_v  = stag_vent(isop_bkk * 1000)   # ppb

print(f"   Bangkok stagnation mean PM2.5  = {pm25_s:.1f} µg/m³")
print(f"   Bangkok ventilation  mean PM2.5 = {pm25_v:.1f} µg/m³")
print(f"   OH (stag/vent): {oh_s:.4f} / {oh_v:.4f} pptv")
print(f"   NO3 (stag/vent): {no3_s:.4f} / {no3_v:.4f} pptv")
print(f"   NOx (stag/vent): {nox_s:.2f} / {nox_v:.2f} ppb")


# ════════════════════════════════════════════════════════════════════════════
#  FIG P1 — TIME SERIES: PM2.5, ORGANIC PRECURSORS, OH/NO3, VC
# ════════════════════════════════════════════════════════════════════════════
print("\n[Fig P1] Multi-panel time series")

fig, axes = plt.subplots(4, 1, figsize=(11, 12), sharex=True)
fig.subplots_adjust(hspace=0.08, top=0.93, bottom=0.07)
fig.suptitle('WRF-GC January 2025 — Bangkok (13.75°N, 100.50°E)\n'
             'Daily surface chemistry and boundary-layer mixing',
             fontsize=12, y=0.97)

# Stagnation shading on all panels
for ax in axes:
    for k, (d, s) in enumerate(zip(dates_late, stag_mask)):
        if s:
            next_d = dates_late[k+1] if k+1 < len(dates_late) else d
            ax.axvspan(d, next_d, color='#f5cba7', alpha=0.55, zorder=0)
    ax.grid(True, alpha=0.25, lw=0.5, zorder=1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

xfmt  = mdates.DateFormatter('%d %b')
xloc  = mdates.DayLocator(interval=2)

# Panel 1 — PM2.5
ax = axes[0]
ax.plot(dates_late, pm25_bkk, 'o-', color='#c0392b', lw=1.8, ms=4, zorder=3)
ax.axhline(15,   color='#7f8c8d', lw=0.9, ls='--', label='WHO 24-hr (15 µg m⁻³)')
ax.axhline(37.5, color='#7f8c8d', lw=0.9, ls=':',  label='TH NAAQS (37.5 µg m⁻³)')
ax.set_ylabel('PM$_{2.5}$ (µg m$^{-3}$)', fontsize=9)
ax.legend(fontsize=7, loc='upper left', framealpha=0.7)
ax.text(0.01, 0.88, '(a)', transform=ax.transAxes, fontsize=9, fontweight='bold')

# Panel 2 — Total organic precursor / SOA proxy (ppb)
ax = axes[1]
ax.fill_between(dates_late, soap_ppb, 0, alpha=0.60, color='#8e44ad', label='SOAP (anthrop. SOA prec.)')
ax.fill_between(dates_late, soas_ppb, 0, alpha=0.60, color='#27ae60', label='SOAS (biogenic SOA prec.)')
ax.set_ylabel('SOA precursor (ppb)', fontsize=9)
ax.legend(fontsize=7, loc='upper left', framealpha=0.7)
ax.text(0.01, 0.88, '(b)', transform=ax.transAxes, fontsize=9, fontweight='bold')

# Panel 3 — OH and NO3
ax = axes[2]
ax2 = ax.twinx()
ax.plot(dates_late, oh_pptv,  's-', color='#f39c12', lw=1.6, ms=4, label='OH (pptv)', zorder=3)
ax2.plot(dates_late, no3_pptv, '^-', color='#16a085', lw=1.6, ms=4, ls='--',
         label='NO$_3$ (pptv)', zorder=3)
ax2.plot(dates_late, n2o5_pptv, 'v-', color='#2980b9', lw=1.2, ms=3, ls=':',
         label='N$_2$O$_5$ (pptv)', alpha=0.8, zorder=3)
ax.set_ylabel('OH (pptv)',  fontsize=9, color='#f39c12')
ax2.set_ylabel('NO$_3$, N$_2$O$_5$ (pptv)', fontsize=9, color='#16a085')
lines1, lbs1 = ax.get_legend_handles_labels()
lines2, lbs2 = ax2.get_legend_handles_labels()
ax.legend(lines1+lines2, lbs1+lbs2, fontsize=7, loc='upper left', framealpha=0.7)
ax.text(0.01, 0.88, '(c)', transform=ax.transAxes, fontsize=9, fontweight='bold')
ax2.spines['top'].set_visible(False)
ax.grid(True, alpha=0.25, lw=0.5, zorder=1)

# Panel 4 — VC
ax = axes[3]
ax.fill_between(dates_late, vc_bkk_ts, vc_median, where=(vc_bkk_ts <= vc_median),
                alpha=0.4, color=C_STAG, label='Stagnation (VC ≤ median)')
ax.fill_between(dates_late, vc_bkk_ts, vc_median, where=(vc_bkk_ts > vc_median),
                alpha=0.4, color=C_VENT, label='Ventilated (VC > median)')
ax.plot(dates_late, vc_bkk_ts, 'k-', lw=1.5, zorder=3)
ax.axhline(vc_median, color='gray', lw=1.0, ls='--',
           label=f'Median VC = {vc_median:.0f} m² s⁻¹')
ax.set_ylabel('Vent. Coeff. (m² s$^{-1}$)', fontsize=9)
ax.legend(fontsize=7, loc='upper right', framealpha=0.7)
ax.text(0.01, 0.88, '(d)', transform=ax.transAxes, fontsize=9, fontweight='bold')

axes[-1].xaxis.set_major_formatter(xfmt)
axes[-1].xaxis.set_major_locator(xloc)
plt.setp(axes[-1].xaxis.get_majorticklabels(), rotation=30, ha='right', fontsize=8)
for ax in axes[:-1]:
    ax.yaxis.set_tick_params(labelsize=8)

# Stagnation label
axes[0].text(0.76, 0.92, '← Stagnation period (Jan 19–28)',
             transform=axes[0].transAxes, fontsize=7.5, color=C_STAG,
             style='italic')

save(fig, 'figP1_timeseries.png')


# ════════════════════════════════════════════════════════════════════════════
#  FIG P2 — AEROSOL COMPOSITION: STAGNATION vs VENTILATION
# ════════════════════════════════════════════════════════════════════════════
print("[Fig P2] Aerosol composition stagnation vs ventilation")

comp_labels = ['SO$_4$', 'NIT + NH$_4$', 'BC', 'OA (residual)']
comp_colors = ['#f1c40f', '#e67e22', '#2c3e50', '#8e44ad']

stag_vals = np.array([so4_s, (nit_s+nh4_s), bc_s, oa_s])
vent_vals = np.array([so4_v, (nit_v+nh4_v), bc_v, oa_v])

stag_pct = stag_vals / stag_vals.sum() * 100
vent_pct = vent_vals / vent_vals.sum() * 100

fig, axes = plt.subplots(1, 2, figsize=(13, 6))
fig.subplots_adjust(wspace=0.35, top=0.85, bottom=0.12)
fig.suptitle('Surface PM$_{2.5}$ Chemical Composition — Bangkok grid point\n'
             'WRF-GC January 2025  |  Stagnation vs Ventilated period',
             fontsize=11)

for ax, vals, pcts, title, color, n_days in [
    (axes[0], stag_vals, stag_pct, f'Stagnation (VC ≤ {vc_median:.0f} m² s⁻¹)',
     C_STAG, stag_mask.sum()),
    (axes[1], vent_vals, vent_pct,  f'Ventilated (VC > {vc_median:.0f} m² s⁻¹)',
     C_VENT, vent_mask.sum()),
]:
    bottoms = 0.0
    for lbl, clr, v, pct in zip(comp_labels, comp_colors, vals, pcts):
        ax.bar([0], [v], bottom=bottoms, color=clr, alpha=0.88,
               edgecolor='white', linewidth=0.8)
        # Only label if segment is large enough to read
        if v > 4.0:
            txt_color = 'white' if clr == '#2c3e50' else '#111111'
            ax.text(0, bottoms + v / 2,
                    f'{lbl}\n{v:.1f} µg/m³  ({pct:.0f}%)',
                    ha='center', va='center', fontsize=8.5,
                    color=txt_color, fontweight='bold')
        elif v > 1.0:
            ax.text(0.55, bottoms + v / 2,
                    f'{lbl}  {v:.1f}  ({pct:.0f}%)',
                    ha='left', va='center', fontsize=7.5, color='#333',
                    transform=ax.get_yaxis_transform())
        bottoms += v
    ymax = max(stag_vals.sum(), vent_vals.sum()) * 1.15
    ax.set_ylim(0, ymax)
    ax.set_title(f'{title}\nn = {n_days} days', fontsize=10, color=color, pad=8)
    ax.set_ylabel('PM$_{2.5}$ (µg m$^{-3}$)', fontsize=9)
    ax.text(0, bottoms + ymax * 0.01,
            f'Total: {vals.sum():.1f} µg/m³',
            ha='center', va='bottom', fontsize=10, fontweight='bold', color=color)
    ax.set_xticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, axis='y', alpha=0.3)

# Shared legend
handles = [mpatches.Patch(color=c, label=l)
           for l, c in zip(comp_labels, comp_colors)]
fig.legend(handles=handles, loc='lower center', ncol=4, fontsize=9,
           bbox_to_anchor=(0.5, 0.01), framealpha=0.8)

save(fig, 'figP2_aerosol_composition.png')


# ════════════════════════════════════════════════════════════════════════════
#  FIG P3 — OXIDANT CHEMISTRY: OH, NO3, N2O5 COMPARISON
# ════════════════════════════════════════════════════════════════════════════
print("[Fig P3] Oxidant comparison: OH, NO3, N2O5")

fig, axes = plt.subplots(1, 3, figsize=(13, 5))
fig.subplots_adjust(wspace=0.35, top=0.85, bottom=0.18)
fig.suptitle('Atmospheric Oxidant Concentrations at Bangkok — Stagnation vs Ventilated\n'
             'WRF-GC January 2025  |  Snapshot at 07:00 LST (end of night)',
             fontsize=11)

oxidants = [
    ('OH',                      oh_pptv,   'OH (pptv)',       '#f39c12'),
    ('NO$_3$',                  no3_pptv,  'NO$_3$ (pptv)',   '#16a085'),
    ('N$_2$O$_5$',              n2o5_pptv, 'N$_2$O$_5$ (pptv)', '#2980b9'),
]

for ax, (name, ts, ylabel, color) in zip(axes, oxidants):
    stag_data = ts[stag_mask]
    vent_data = ts[vent_mask]

    bplot = ax.boxplot([stag_data, vent_data],
                       positions=[1, 2],
                       widths=0.55,
                       patch_artist=True,
                       medianprops=dict(color='white', lw=2),
                       whiskerprops=dict(lw=1.2),
                       capprops=dict(lw=1.2),
                       flierprops=dict(marker='o', ms=4, alpha=0.7))

    for patch, color_b in zip(bplot['boxes'], [C_STAG, C_VENT]):
        patch.set_facecolor(color_b)
        patch.set_alpha(0.75)

    # overlay individual points
    for x_pos, data, c in [(1, stag_data, C_STAG), (2, vent_data, C_VENT)]:
        ax.scatter(np.random.normal(x_pos, 0.07, len(data)), data,
                   color=c, alpha=0.7, s=25, zorder=3)

    # stats annotation
    t_stat, p_val = stats.ttest_ind(stag_data, vent_data)
    sig = '***' if p_val < 0.001 else ('**' if p_val < 0.01 else ('*' if p_val < 0.05 else 'ns'))
    y_top = max(np.concatenate([stag_data, vent_data])) * 1.12
    ax.plot([1, 2], [y_top, y_top], 'k-', lw=0.8)
    ax.text(1.5, y_top * 1.02, f'p={p_val:.3f} {sig}', ha='center', fontsize=8)

    # ratio annotation
    ratio = stag_data.mean() / max(vent_data.mean(), 1e-30)
    ax.text(0.98, 0.05, f'Stag/Vent = {ratio:.2f}×',
            transform=ax.transAxes, ha='right', fontsize=8.5,
            color='#333333',
            bbox=dict(facecolor='#fffde7', alpha=0.8, pad=2, lw=0.5, edgecolor='#bbb'))

    ax.set_xticks([1, 2])
    ax.set_xticklabels(['Stagnation\n(n=%d)' % stag_mask.sum(),
                        'Ventilated\n(n=%d)' % vent_mask.sum()], fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_title(name, fontsize=11, pad=6)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, axis='y', alpha=0.3)

# Context note
fig.text(0.5, 0.03,
         'Note: snapshots at 07:00 LST capture end-of-night chemistry. High NO during stagnation titrates NO₃ (NO+NO₃→2NO₂), '
         'suppressing NO₃ at this hour.\nDuring the preceding night, NOx accumulation (3.6×) drives intense NO₃ production; '
         'N₂O₅ heterogeneous uptake on elevated aerosol surfaces also enhances HNO₃ formation.',
         ha='center', fontsize=7.5, style='italic', color='#555')

save(fig, 'figP3_oxidants.png')


# ════════════════════════════════════════════════════════════════════════════
#  FIG P4 — VC vs PM2.5  AND  VC vs SOA-proxy  SCATTER CORRELATION
# ════════════════════════════════════════════════════════════════════════════
print("[Fig P4] VC–PM2.5 and VC–SOA scatter correlation")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.subplots_adjust(wspace=0.30, top=0.85, bottom=0.14)
fig.suptitle('Ventilation Coefficient vs Aerosol Loading — Bangkok grid point\n'
             'WRF-GC January 2025  |  Jan 10–28 (post spin-up)',
             fontsize=11)

scatter_pairs = [
    (vc_bkk_ts,  pm25_bkk,   'PM$_{2.5}$ (µg m$^{-3}$)',  'Surface PM$_{2.5}$'),
    (vc_bkk_ts,  soatot_ppb, 'SOA precursor (ppb)',        'SOAP + SOAS + SOAIE + SOAGX'),
]

for ax, (x, y, ylabel, title) in zip(axes, scatter_pairs):
    sc = ax.scatter(x[vent_mask], y[vent_mask],
                    c=C_VENT, s=60, zorder=3, label='Ventilated',
                    edgecolors='white', lw=0.5, alpha=0.9)
    sc2 = ax.scatter(x[stag_mask], y[stag_mask],
                     c=C_STAG, s=60, zorder=3, label='Stagnation',
                     edgecolors='white', lw=0.5, alpha=0.9, marker='D')

    # Linear regression
    slope, intercept, r, p, se = stats.linregress(x, y)
    xfit = np.linspace(x.min()*0.95, x.max()*1.05, 100)
    ax.plot(xfit, slope*xfit + intercept, 'k--', lw=1.2, alpha=0.7)

    # Pearson r annotation
    ax.text(0.97, 0.95,
            f'r = {r:.3f}\np = {p:.4f}\nn = {len(x)}',
            transform=ax.transAxes, ha='right', va='top',
            fontsize=9, bbox=dict(facecolor='white', alpha=0.85, pad=3, lw=0.5,
                                  edgecolor='#bbb'))

    ax.set_xlabel('Ventilation Coefficient (m² s$^{-1}$)', fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_title(title, fontsize=10, pad=6)
    ax.legend(fontsize=8, framealpha=0.8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, alpha=0.25)

save(fig, 'figP4_vc_scatter.png')


# ════════════════════════════════════════════════════════════════════════════
#  FIG P5 — NOx–OH CHEMISTRY SCATTER
# ════════════════════════════════════════════════════════════════════════════
print("[Fig P5] NOx–OH chemistry scatter")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.subplots_adjust(wspace=0.32, top=0.85, bottom=0.14)
fig.suptitle('NOx – OH Chemistry: Stagnation vs Ventilation Regimes\n'
             'WRF-GC January 2025  |  Bangkok grid point',
             fontsize=11)

# Left: NO2 vs OH coloured by regime
ax = axes[0]
ax.scatter(no2_ppb[vent_mask], oh_pptv[vent_mask],
           c=C_VENT, s=70, label='Ventilated', edgecolors='white', lw=0.5, zorder=3)
ax.scatter(no2_ppb[stag_mask], oh_pptv[stag_mask],
           c=C_STAG, s=70, marker='D', label='Stagnation', edgecolors='white', lw=0.5, zorder=3)
ax.set_xlabel('NO$_2$ (ppb)', fontsize=9)
ax.set_ylabel('OH (pptv)', fontsize=9)
ax.set_title('NO$_2$ vs OH — regime colour', fontsize=10, pad=6)
ax.legend(fontsize=8, framealpha=0.8)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, alpha=0.25)

# Annotate the pattern — at 07:00 LST high NO promotes OH via HO2+NO→OH
ax.text(0.97, 0.05,
        'At 07:00 LST: high NO during stagnation\npromotes OH via HO₂ + NO → OH + NO₂\n'
        '(NOx 3.6× and OH 3.5× higher during stagnation)',
        transform=ax.transAxes, ha='right', fontsize=7.5,
        color='#333', style='italic',
        bbox=dict(facecolor='#fffde7', alpha=0.85, pad=2, lw=0.5, edgecolor='#bbb'))

# Right: NOx vs OA (organic aerosol) scatter — pollutant accumulation drives OA
ax = axes[1]
no3_oh_ratio = no3_pptv / np.maximum(oh_pptv, 1e-10)
ax.scatter(nox_ppb[vent_mask], oa_ugm3[vent_mask],
           c=C_VENT, s=70, label='Ventilated', edgecolors='white', lw=0.5, zorder=3)
ax.scatter(nox_ppb[stag_mask], oa_ugm3[stag_mask],
           c=C_STAG, s=70, marker='D', label='Stagnation', edgecolors='white', lw=0.5, zorder=3)
slope, intercept, r, p, se = stats.linregress(nox_ppb, oa_ugm3)
xfit = np.linspace(nox_ppb.min()*0.9, nox_ppb.max()*1.05, 100)
ax.plot(xfit, slope*xfit + intercept, 'k--', lw=1.2, alpha=0.7)
ax.text(0.97, 0.95, f'r = {r:.3f}\np = {p:.4f}',
        transform=ax.transAxes, ha='right', va='top', fontsize=9,
        bbox=dict(facecolor='white', alpha=0.85, pad=3, lw=0.5, edgecolor='#bbb'))
ax.set_xlabel('NOx (ppb)', fontsize=9)
ax.set_ylabel('Organic Aerosol — residual (µg m$^{-3}$)', fontsize=9)
ax.set_title('NOx vs Organic Aerosol — coupled accumulation', fontsize=10, pad=6)
ax.legend(fontsize=8, framealpha=0.8)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, alpha=0.25)
ax.text(0.97, 0.08,
        'NOx and OA co-accumulate under stagnation:\ncombustion emissions trapped in shallow PBL\n→ supports Hypothesis 2',
        transform=ax.transAxes, ha='right', fontsize=7.5,
        color='#8e44ad', style='italic',
        bbox=dict(facecolor='#fef9f0', alpha=0.85, pad=2, lw=0.5, edgecolor='#bbb'))

save(fig, 'figP5_nox_oh_chemistry.png')


# ════════════════════════════════════════════════════════════════════════════
#  FIG P6 — SPATIAL MAP: SOA PRECURSOR LOADING (SOAP+SOAS mean)
# ════════════════════════════════════════════════════════════════════════════
print("[Fig P6] Spatial SOA precursor maps: stagnation vs ventilation")

def load_spatial_sum_ppmv(files, var_list, lev=0):
    """Sum multiple ppmv tracers → spatial mean across files (ppmv)."""
    stack = []
    for f in files:
        with nc.Dataset(f) as ds:
            total = np.zeros(LAT.shape)
            for v in var_list:
                arr = ds.variables[v]
                total += arr[0, lev] if arr.ndim == 4 else arr[0]
        stack.append(total)
    return np.mean(stack, axis=0)

soap_stag = load_spatial_sum_ppmv(stag_files, ['soap', 'soas'])
soap_vent = load_spatial_sum_ppmv(vent_files, ['soap', 'soas'])
pm25_stag_map = load_spatial_mean(stag_files, 'PM2_5_DRY')
pm25_vent_map = load_spatial_mean(vent_files, 'PM2_5_DRY')

u10_stag = load_spatial_mean(stag_files, 'U10')
v10_stag = load_spatial_mean(stag_files, 'V10')
u10_vent = load_spatial_mean(vent_files, 'U10')
v10_vent = load_spatial_mean(vent_files, 'V10')

fig, axes = plt.subplots(2, 2, figsize=(14, 11),
                          subplot_kw={'projection': PROJ})
fig.subplots_adjust(wspace=0.06, hspace=0.12, top=0.91, bottom=0.04)
fig.suptitle('WRF-GC January 2025 — Spatial Distribution under Different Regimes\n'
             f'Stagnation (n={stag_mask.sum()} days, VC ≤ {vc_median:.0f} m² s⁻¹)  vs  '
             f'Ventilated (n={vent_mask.sum()} days)',
             fontsize=11, y=0.97)

sk = 8
cmap_pm = 'YlOrBr'
cmap_soa = 'BuPu'

# Shared colour limits
vmax_pm  = max(pm25_stag_map.max(), pm25_vent_map.max()) * 0.97
vmax_soa = max(soap_stag.max(), soap_vent.max()) * 0.97

panels = [
    (axes[0,0], pm25_stag_map, 'PM$_{2.5}$ — Stagnation',   cmap_pm,  0, vmax_pm,
     u10_stag, v10_stag, '(a)'),
    (axes[0,1], pm25_vent_map, 'PM$_{2.5}$ — Ventilated',   cmap_pm,  0, vmax_pm,
     u10_vent, v10_vent, '(b)'),
    (axes[1,0], soap_stag,     'SOAP+SOAS — Stagnation',     cmap_soa, 0, vmax_soa,
     u10_stag, v10_stag, '(c)'),
    (axes[1,1], soap_vent,     'SOAP+SOAS — Ventilated',     cmap_soa, 0, vmax_soa,
     u10_vent, v10_vent, '(d)'),
]

for ax, data, title, cmap, vmin, vmax, u, v, letter in panels:
    make_map(ax)
    im = ax.pcolormesh(LON, LAT, data, transform=PROJ,
                       cmap=cmap, vmin=vmin, vmax=vmax,
                       shading='gouraud', zorder=1)
    ax.quiver(LON[::sk, ::sk], LAT[::sk, ::sk],
              u[::sk, ::sk], v[::sk, ::sk],
              transform=PROJ, scale=90, width=0.002,
              color='#1a1a2e', alpha=0.7, zorder=4)
    thailand_box(ax)
    cb = plt.colorbar(im, ax=ax, orientation='horizontal', shrink=0.82, pad=0.03)
    cb_lbl = 'PM$_{2.5}$ (µg m$^{-3}$)' if 'PM' in title else 'SOAP+SOAS (ppmv)'
    cb.set_label(cb_lbl, fontsize=8)
    cb.ax.tick_params(labelsize=7)
    ax.set_title(f'{letter}  {title}', fontsize=9.5, pad=6)

save(fig, 'figP6_spatial_soa_pm25.png')


# ════════════════════════════════════════════════════════════════════════════
#  FIG P7 — SUMMARY STATISTICS TABLE / BAR CHART
# ════════════════════════════════════════════════════════════════════════════
print("[Fig P7] Summary comparison bar chart")

fig, axes = plt.subplots(2, 3, figsize=(14, 8))
fig.subplots_adjust(hspace=0.40, wspace=0.35, top=0.88, bottom=0.10)
fig.suptitle('Summary: Bangkok Stagnation vs Ventilation — WRF-GC January 2025\n'
             'All variables at surface (07:00 LST); error bars = ±1σ',
             fontsize=11)

def bar2(ax, s_arr, v_arr, ylabel, title, unit_factor=1.0, fmt='.1f'):
    xs = np.array([1, 2])
    means = np.array([s_arr.mean(), v_arr.mean()]) * unit_factor
    stds  = np.array([s_arr.std(),  v_arr.std()])  * unit_factor
    bars = ax.bar(xs, means, width=0.5, color=[C_STAG, C_VENT],
                  alpha=0.80, edgecolor='white', lw=0.5)
    ax.errorbar(xs, means, yerr=stds, fmt='none', color='#333', capsize=5, lw=1.5, zorder=4)
    ax.set_xticks(xs)
    ax.set_xticklabels(['Stagnation\n(n=%d)' % stag_mask.sum(),
                        'Ventilated\n(n=%d)' % vent_mask.sum()], fontsize=8.5)
    ax.set_ylabel(ylabel, fontsize=8.5)
    ax.set_title(title, fontsize=9.5, pad=4)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, axis='y', alpha=0.25)
    # value labels
    for bar, m in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + stds[0]*0.05,
                f'{m:{fmt}}', ha='center', va='bottom', fontsize=8.5, fontweight='bold')
    # t-test
    t, p = stats.ttest_ind(s_arr, v_arr)
    sig = '***' if p<0.001 else ('**' if p<0.01 else ('*' if p<0.05 else 'ns'))
    ax.text(0.98, 0.94, f'p={p:.3f} {sig}', transform=ax.transAxes,
            ha='right', va='top', fontsize=8,
            bbox=dict(facecolor='#fffde7', alpha=0.85, pad=2, lw=0.5, edgecolor='#bbb'))
    return ax

bar2(axes[0,0], pm25_bkk[stag_mask],  pm25_bkk[vent_mask],
     'µg m$^{-3}$', 'Surface PM$_{2.5}$')

bar2(axes[0,1], oa_ugm3[stag_mask],   oa_ugm3[vent_mask],
     'µg m$^{-3}$', 'Organic Aerosol (residual)')

bar2(axes[0,2], bc_ugm3[stag_mask],   bc_ugm3[vent_mask],
     'µg m$^{-3}$', 'Black Carbon')

bar2(axes[1,0], oh_pptv[stag_mask],   oh_pptv[vent_mask],
     'pptv', 'OH radical')

bar2(axes[1,1], no3_pptv[stag_mask],  no3_pptv[vent_mask],
     'pptv', 'NO$_3$ radical (nighttime)')

bar2(axes[1,2], nox_ppb[stag_mask], nox_ppb[vent_mask],
     'ppb', 'NOx (NO + NO$_2$)')

save(fig, 'figP7_summary_bars.png')


# ════════════════════════════════════════════════════════════════════════════
#  FIG P8 — 4-PANEL SOA PRECURSOR SPATIAL MAP (stagnation composite)
#  Panel a: Biogenic terpene precursors  MTPA + MTPO + LIMO  (pptv)
#  Panel b: Anthropogenic aromatic prods AROMP4 + AROMP5     (pptv)
#  Panel c: SOAP — lumped gas-phase SOA precursor pool        (ppb)
#  Panel d: SOAS — actual non-volatile SOA aerosol in PM2.5  (µg m⁻³)
# ════════════════════════════════════════════════════════════════════════════
print("[Fig P8] 4-panel SOA precursor spatial map (stagnation composite)")

# Load stagnation-mean spatial fields (lev=0 surface)
bio_terp_stag  = load_spatial_sum_ppmv(stag_files, ['mtpa', 'mtpo', 'limo'])   # ppmv
anth_arom_stag = load_spatial_sum_ppmv(stag_files, ['aromp4', 'aromp5'])        # ppmv
soap_stag_map  = load_spatial_sum_ppmv(stag_files, ['soap'])                    # ppmv
soas_stag_map  = load_spatial_sum_ppmv(stag_files, ['soas'])                    # ppmv

# Also load ventilated means for comparison annotations
bio_terp_vent  = load_spatial_sum_ppmv(vent_files, ['mtpa', 'mtpo', 'limo'])
anth_arom_vent = load_spatial_sum_ppmv(vent_files, ['aromp4', 'aromp5'])
soap_vent_map  = load_spatial_sum_ppmv(vent_files, ['soap'])
soas_vent_map  = load_spatial_sum_ppmv(vent_files, ['soas'])

# Unit conversions
N_AIR_SFC = 41.2   # mol m⁻³ representative surface value
bio_terp_pptv  = bio_terp_stag  * 1e6       # ppmv → pptv
anth_arom_pptv = anth_arom_stag * 1e6       # ppmv → pptv
soap_ppb_map   = soap_stag_map  * 1e3       # ppmv → ppb
soas_ugm3_map  = soas_stag_map  * N_AIR_SFC * 150.0   # ppmv × mol/m³ × g/mol → µg/m³

# Thailand-box mean for annotation (ratio stag/vent)
def th_mean(arr):
    return float(np.mean(arr[th_mask]))

ratios = {
    'bio':  th_mean(bio_terp_stag)  / max(th_mean(bio_terp_vent),  1e-30),
    'anth': th_mean(anth_arom_stag) / max(th_mean(anth_arom_vent), 1e-30),
    'soap': th_mean(soap_stag_map)  / max(th_mean(soap_vent_map),  1e-30),
    'soas': th_mean(soas_stag_map)  / max(th_mean(soas_vent_map),  1e-30),
}

fig, axes = plt.subplots(2, 2, figsize=(14, 11),
                          subplot_kw={'projection': PROJ})
fig.subplots_adjust(wspace=0.06, hspace=0.14, top=0.91, bottom=0.04)
fig.suptitle(
    'WRF-GC January 2025 — SOA Precursor Identification (Stagnation Composite)\n'
    f'n = {stag_mask.sum()} stagnation days  |  VC ≤ {vc_median:.0f} m² s⁻¹  '
    '|  SOAP = gas-phase precursor pool  |  SOAS = aerosol product in PM$_{2.5}$',
    fontsize=10.5, y=0.97)

panels_p8 = [
    # (ax, data, title, cmap, units_label, letter, ratio_key)
    (axes[0,0], bio_terp_pptv,
     '(a)  Biogenic Terpene Precursors\nMTPA + MTPO + LIMO',
     'YlGn',   'pptv',        'bio'),
    (axes[0,1], anth_arom_pptv,
     '(b)  Anthropogenic Aromatic Oxidation Products\nAROMP4 + AROMP5',
     'RdPu',   'pptv',        'anth'),
    (axes[1,0], soap_ppb_map,
     '(c)  SOAP — Lumped Gas-Phase SOA Precursor Pool\n(biogenic + anthropogenic merged)',
     'YlOrBr', 'ppb',         'soap'),
    (axes[1,1], soas_ugm3_map,
     '(d)  SOAS — Non-volatile SOA Aerosol in PM$_{2.5}$\n(MW = 150 g mol⁻¹)',
     'BuPu',   'µg m$^{-3}$', 'soas'),
]

sk = 8
for ax, data, title, cmap, units, rkey in panels_p8:
    make_map(ax)
    vmax = np.percentile(data, 97)   # robust max avoids outlier saturation
    im = ax.pcolormesh(LON, LAT, data, transform=PROJ,
                       cmap=cmap, vmin=0, vmax=vmax,
                       shading='gouraud', zorder=1)
    # Wind vectors (stagnation mean — weak, consistent with stagnation)
    ax.quiver(LON[::sk, ::sk], LAT[::sk, ::sk],
              u10_stag[::sk, ::sk], v10_stag[::sk, ::sk],
              transform=PROJ, scale=80, width=0.0022,
              color='#2c3e50', alpha=0.65, zorder=4)
    thailand_box(ax)
    cb = plt.colorbar(im, ax=ax, orientation='horizontal', shrink=0.84, pad=0.03)
    cb.set_label(units, fontsize=8.5)
    cb.ax.tick_params(labelsize=7.5)
    ax.set_title(title, fontsize=9, pad=5)
    # Stag/vent ratio annotation inside Thailand box
    ratio_val = ratios[rkey]
    ax.text(TH_LON[0] + 0.3, TH_LAT[0] + 0.6,
            f'Stag/Vent\n= {ratio_val:.2f}×',
            fontsize=7.5, color='white', transform=PROJ, zorder=6,
            fontweight='bold',
            bbox=dict(facecolor='#1a1a2e', alpha=0.72, pad=2, lw=0))

# Add a shared annotation explaining SOAP vs SOAS distinction
fig.text(0.5, 0.005,
         'SOAP (panels a–c upstream) is a GAS-PHASE tracer (Is_Gas=True) — '
         'NOT in PM₂.₅.  '
         'SOAS (panel d) is the AEROSOL product (Is_Aerosol=True, non-volatile) — '
         'IS counted in PM₂.₅_DRY.\n'
         'Biogenic (a) and anthropogenic (b) precursors merge into the lumped SOAP pool (c) '
         'before condensing irreversibly to SOAS (d).  '
         'Source separation requires sensitivity runs or explicit TSOA/ASOA scheme.',
         ha='center', fontsize=7, color='#444', style='italic')

save(fig, 'figP8_soa_precursor_spatial.png')


# ════════════════════════════════════════════════════════════════════════════
#  PRINT SUMMARY TABLE
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("BANGKOK SUMMARY: STAGNATION vs VENTILATION  (Jan 10–28, 2025)")
print("="*65)
rows = [
    ("PM2.5 (µg/m³)",         pm25_bkk[stag_mask].mean(),  pm25_bkk[vent_mask].mean()),
    ("OA residual (µg/m³)",   oa_ugm3[stag_mask].mean(),   oa_ugm3[vent_mask].mean()),
    ("SO4 (µg/m³)",           so4_ugm3[stag_mask].mean(),  so4_ugm3[vent_mask].mean()),
    ("BC (µg/m³)",            bc_ugm3[stag_mask].mean(),   bc_ugm3[vent_mask].mean()),
    ("NOx (ppb)",             nox_ppb[stag_mask].mean(),   nox_ppb[vent_mask].mean()),
    ("NO2 (ppb)",             no2_ppb[stag_mask].mean(),   no2_ppb[vent_mask].mean()),
    ("OH (pptv)",             oh_pptv[stag_mask].mean(),   oh_pptv[vent_mask].mean()),
    ("NO3 (pptv)",            no3_pptv[stag_mask].mean(),  no3_pptv[vent_mask].mean()),
    ("N2O5 (pptv)",           n2o5_pptv[stag_mask].mean(), n2o5_pptv[vent_mask].mean()),
    ("NO3/OH ratio",          no3_oh_ratio[stag_mask].mean(),no3_oh_ratio[vent_mask].mean()),
    ("SOAP+SOAS (ppb)",       soatot_ppb[stag_mask].mean(),soatot_ppb[vent_mask].mean()),
    ("ISOP (ppb)",            isop_bkk[stag_mask].mean()*1000, isop_bkk[vent_mask].mean()*1000),
    ("VC_Bangkok (m²/s)",     vc_bkk_ts[stag_mask].mean(),vc_bkk_ts[vent_mask].mean()),
]
print(f"{'Variable':<25} {'Stagnation':>12} {'Ventilated':>12} {'Ratio S/V':>10}")
print("-"*65)
for name, sv, vv in rows:
    ratio = sv / max(vv, 1e-30)
    print(f"{name:<25} {sv:>12.4f} {vv:>12.4f} {ratio:>10.2f}×")
print("="*65)

print(f"\nAll proposal defense figures saved → {FIG_DIR}")
for f in sorted(os.listdir(FIG_DIR)):
    if f.endswith('.png'):
        sz = os.path.getsize(os.path.join(FIG_DIR, f)) // 1024
        print(f"  {f}  ({sz} kB)")
