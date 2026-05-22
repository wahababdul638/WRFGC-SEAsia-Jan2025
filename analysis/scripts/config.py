"""
config.py — Shared constants, paths, and style settings.
All other scripts import from here.
"""

import os

# ── Paths ─────────────────────────────────────────────────────────────────────
WRF_RUN = '/home/abdul/TESTs/WRFGC_SEAsia_Jan2025/WRF/run'
FIG_DIR  = '/home/abdul/TESTs/WRFGC_SEAsia_Jan2025/analysis/figures'
os.makedirs(FIG_DIR, exist_ok=True)

# ── Domain and region ─────────────────────────────────────────────────────────
DOM_EXT = [90, 115, 0, 25]     # map extent: zoomed to mainland SEA
TH_LAT  = (5.5, 20.5)          # Thailand latitude bounds
TH_LON  = (98.0, 106.0)        # Thailand longitude bounds
BKK_J, BKK_I = 74, 89          # Bangkok grid point (13.75°N, 100.50°E)

# ── Unit conversion ───────────────────────────────────────────────────────────
N_AIR_SFC = 41.2   # representative surface dry air density (mol m⁻³) at ~1 atm, ~295 K

# ── Regime colours ────────────────────────────────────────────────────────────
C_STAG = '#c0392b'   # red  — stagnant
C_VENT = '#2980b9'   # blue — ventilated
ALPHA_SHADE = 0.18

# ── Projection (cartopy) ──────────────────────────────────────────────────────
import cartopy.crs as ccrs
PROJ = ccrs.PlateCarree()
