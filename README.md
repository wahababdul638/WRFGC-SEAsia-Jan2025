# WRF-GC Simulation — South/Southeast Asia | January 2025

**Project:** PhD Research — Meteorology–Chemistry Coupling and PM₂.₅/SOA Variability over Thailand  
**Model:** WRF-GC v2.0 (WRF 4.x + GEOS-Chem 12.x, online two-way coupled)  
**Researcher:** Abdul Wahab | Sustainable & Environmental Engineering

> **Note:** Simulation output files (`wrfout_*`, ~148 GB total) are excluded from this repository.  
> This repository contains analysis scripts, figures, and model configuration files only.

---

## Research Hypotheses

| # | Hypothesis | Pilot finding |
|---|-----------|---------------|
| H1 | Meteorological stagnation (low VC) causes significant PM₂.₅ accumulation | ✅ 2.73×, p=0.002 |
| H2 | Stagnation enhances SOA formation, increasing the OA fraction of PM₂.₅ | ✅ OA 3.28×, fraction 65%→79% |
| H3 | Nighttime NO₃ radical chemistry drives stagnation-period SOA | ⚠️ Cannot test from daily 07:00 LST snapshots |

**Ventilation Coefficient:** VC = PBLH × |Wind₁₀ₘ| (m² s⁻¹) — stagnation threshold = 1800 m²/s (median over analysis period)

---

## Repository Structure

```
WRFGC_SEAsia_Jan2025/
├── WRF/run/
│   ├── namelist.input          WRF runtime configuration
│   ├── HEMCO_Config.rc         HEMCO emissions configuration
│   └── geoschem_config.yml     GEOS-Chem runtime options
├── WPS/
│   └── namelist.wps            WPS domain & projection configuration
├── analysis/
│   ├── scripts/
│   │   ├── config.py           Shared paths, constants, colours
│   │   ├── loaders.py          WRF data loading functions
│   │   ├── plot_helpers.py     Cartopy map setup and figure utilities
│   │   ├── precompute.py       Load and classify all shared time series
│   │   ├── fig01_timeseries.py      PM2.5 / SOA / oxidants / VC time series
│   │   ├── fig02_aerosol_composition.py  Stacked composition bars
│   │   ├── fig03_oxidants.py       OH, NO3, N2O5 box plots
│   │   ├── fig04_vc_scatter.py     VC vs PM2.5 and SOA scatter
│   │   ├── fig05_nox_oh_chemistry.py   NO2–OH and NOx–OA scatter
│   │   ├── fig06_spatial_maps.py   2×2 spatial PM2.5 and SOAP+SOAS maps
│   │   ├── fig07_summary_bars.py   Summary bar chart (6 variables)
│   │   ├── fig08_soa_precursors.py 4-panel SOA precursor spatial maps
│   │   └── run_all.py              Master runner (precomputes once, runs all figures)
│   ├── figures/proposal/       Output PNG figures (8 files)
│   ├── data/
│   │   └── bangkok_PM25_jan2025.csv  Daily PM₂.₅ at Bangkok grid point
│   └── docs/
│       └── results_summary.md  Full scientific results narrative
└── README.md
```

---

## Quick Start

```bash
# 1. Activate the post-processing environment
conda activate ewrf

# 2. Move to the analysis directory
cd /path/to/WRFGC_SEAsia_Jan2025/analysis

# 3. Generate all 8 figures (wrfout files must be present in WRF/run/)
python scripts/run_all.py

# 4. Or regenerate a single figure
python scripts/fig01_timeseries.py
```

**Required packages:** `netCDF4`, `numpy`, `matplotlib`, `cartopy`, `cmocean`, `scipy`  
Install with: `conda create -n ewrf -c conda-forge python=3.11 netcdf4 matplotlib cartopy cmocean scipy`

---

## Simulation Configuration

### Domain

| Parameter | Value |
|-----------|-------|
| Projection | Mercator |
| Reference point | 13.75°N, 100.50°E (Bangkok) |
| Grid size | 179 × 149 mass points |
| Horizontal resolution | 27 km |
| Vertical levels | 45 eta levels, p_top = 50 hPa |
| Coverage | ~78°E–123°E, ~5°S–31°N (South & Southeast Asia) |
| Time step | 120 s  |  Chemistry step | 10 min |

### Period

| Item | Value |
|------|-------|
| Simulation | Jan 3 – Jan 28, 2025 (26 days) |
| Spin-up (excluded) | Jan 3–9 (met) / Jan 3–11 (aerosol) |
| Analysis window | Jan 10–28, 2025 (19 days) |
| Output frequency | Daily (00:00 UTC = 07:00 Bangkok local time) |

### Physics

| Scheme | Setting |
|--------|---------|
| Microphysics | Morrison 2-moment (mp_physics = 10) |
| Cumulus | Newer Tiedtke (cu_physics = 16) |
| LW/SW radiation | RRTMG (ra_lw/sw_physics = 4) |
| PBL | YSU (bl_pbl_physics = 1) |
| Land surface | Noah LSM (sf_surface_physics = 2) |

### Chemistry (WRF-GC / GEOS-Chem 12.x)

| Setting | Value |
|---------|-------|
| chem_opt | 233 (WRF-GC full chemistry) |
| Mechanism | fullchem (KPP) |
| SOA scheme | 2-product simplified (Henze & Seinfeld 2006): SOAP → SOAS |
| Emissions | CEDSv2 (anthropogenic), MEGAN (biogenic), online dust & sea salt |
| IC/BC | GEOS-Chem global simulation (0.25° × 0.3125°) |
| Meteorological IC/BC | ERA5 (0.25°, 6-hourly) |

---

## Key Variables

| Variable | Units | Notes |
|----------|-------|-------|
| `PM2_5_DRY` | µg m⁻³ | Dry PM₂.₅ diagnostic |
| `PBLH` | m | Planetary boundary layer height |
| `U10`, `V10` | m s⁻¹ | 10 m wind components |
| `oh`, `no3`, `no2`, `no` | ppmv | Chemistry tracers (×10³ → ppb; ×10⁶ → pptv) |
| `soap`, `soas` | ppmv | SOA tracers (SOAP=gas, SOAS=aerosol in PM₂.₅) |
| `so4`, `nit`, `nh4`, `bcpi`, `bcpo` | ppmv | Inorganic + BC aerosol tracers |
| `mtpa`, `mtpo`, `limo` | ppmv | Monoterpene / sesquiterpene precursors |
| `aromp4`, `aromp5` | ppmv | Anthropogenic aromatic oxidation products |

---

## Key Results

- **Bangkok PM₂.₅:** 125 µg/m³ (stagnation) vs 46 µg/m³ (ventilated) — **2.73×, p=0.002**
- **Organic aerosol fraction:** 79% (stagnation) vs 65% (ventilated) — OA 3.28× higher
- **OH radical:** 3.5× *higher* during stagnation at 07:00 LST (HO₂ + NO → OH + NO₂ mechanism)
- **NO₃ radical:** 0.06× *lower* during stagnation (NO titration: NO + NO₃ → 2NO₂)
- **NOx–OA correlation:** r = 0.987 (p ≈ 0) — co-accumulation under stagnation

Full narrative: [`analysis/docs/results_summary.md`](analysis/docs/results_summary.md)

---

## Air Quality Standards

| Species | WHO 2021 | Thailand NAAQS |
|---------|----------|----------------|
| PM₂.₅ | 15 µg m⁻³ (24-hr) | 37.5 µg m⁻³ (24-hr) |
| NO₂ | 25 µg m⁻³ ≈ 13 ppb (24-hr) | 100 µg m⁻³ ≈ 53 ppb (annual) |
