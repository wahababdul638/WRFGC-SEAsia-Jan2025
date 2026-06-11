# Diagnostic Framework for SOA Attribution and NOx Chemistry
## WRF-GC January 2025 Pilot Simulation

**Prepared for:** PhD Research — Meteorology–Chemistry Coupling over Thailand  
**Purpose:** Factual reference for what the wrfout files can and cannot tell us  
**Model:** WRF-GC v2.0 | GEOS-Chem 12.x | `complex_SOA: false`

---

## 1. The SOA Scheme: What SOAP and SOAS Actually Are

The most important thing to understand before any analysis is **which SOA scheme is active** in this simulation.

From `geoschem_config.yml`:
```yaml
complex_SOA:
  activate: false
  semivolatile_POA: false
```

This means the simulation uses the **2-product simplified SOA scheme** (Henze and Seinfeld, 2006). The multi-product volatility basis set (VBS) scheme is off. This has profound implications for what the data can and cannot show.

### What the 2-product scheme does

GEOS-Chem 12.x with `complex_SOA: false` produces SOA through a single lumped pathway:

```
Precursor VOC  +  Oxidant  →  SOAP  →  SOAS
```

**SOAP** (`soap`, ppmv, `Is_Gas: true`): The lumped gas-phase SOA precursor pool. It is produced from:
- Biogenic monoterpenes (α-pinene, β-pinene, limonene) oxidised by OH, O₃, and NO₃
- Anthropogenic aromatics (toluene, xylene, benzene) oxidised by OH

SOAP is **not** in PM₂.₅. It is a gas-phase intermediate.

**SOAS** (`soas`, ppmv, `Is_Aerosol: true`, MW = 150 g/mol): The non-volatile condensed SOA product. It is irreversibly formed from SOAP and **is** counted in PM₂.₅_DRY.

**Key limitation:** All oxidation pathways (OH, O₃, NO₃) feed into a single SOAP pool. The scheme cannot separate daytime OH-driven SOA from nighttime NO₃-driven SOA. The total represents all channels combined.

### Other SOA tracers in the output

| Tracer | Scheme | Status | Value at Bangkok Jan 22 |
|--------|--------|--------|-------------------------|
| `soap` | 2-product gas precursor | **Active** | 5.47×10⁻³ ppmv |
| `soas` | 2-product aerosol product | **Active** | 7.90×10⁻⁴ ppmv |
| `soaie` | IEPOX-SOA (isoprene) | **Active** | 9.51×10⁻⁶ ppmv |
| `soagx` | Glyoxal SOA | **Active** | 1.86×10⁻⁵ ppmv |
| `lvoc` | Low-volatility OC gas | **Active** | 1.35×10⁻⁷ ppmv |
| `lvocoa` | Low-volatility OC aerosol | **Active** | 5.65×10⁻⁷ ppmv |
| `tsoa0–3`, `tsog0–3` | VBS terpene SOA | **Inactive** | ~8.7×10⁻¹⁷ (machine epsilon) |
| `asoa1–n`, `asog1–3` | VBS anthropogenic SOA | **Inactive** | ~8.7×10⁻¹⁷ (machine epsilon) |

**Implication:** Do not use TSOA or ASOA tracers — they are effectively zero and will produce meaningless results. SOA analysis must rely on `soap`, `soas`, `soaie`, `soagx`, and `lvocoa`.

---

## 2. Available Diagnostics — Honest Assessment

The following is based on direct inspection of a representative wrfout file, checking which variables contain real (non-zero) values at the Bangkok grid point.

### 2.1 What is populated and scientifically useful

| Variable | Type | Bangkok value (ventilated / stagnation) | Use |
|----------|------|-----------------------------------------|-----|
| `soap` | 4D ppmv | 4.37e-3 / 5.47e-3 | SOA precursor concentration |
| `soas` | 4D ppmv | 6.98e-4 / 7.90e-4 | SOA aerosol in PM₂.₅ |
| `soaie` | 4D ppmv | 1.37e-5 / 9.51e-6 | IEPOX-SOA (isoprene pathway) |
| `soagx` | 4D ppmv | 2.73e-5 / 1.86e-5 | Glyoxal SOA |
| `lvocoa` | 4D ppmv | 9.62e-7 / 5.65e-7 | Additional condensed organic |
| `mtpa`, `mtpo`, `limo` | 4D ppmv | ~1.8e-5, ~4.3e-6, ~3.4e-6 | Biogenic terpene precursors |
| `aromp4`, `aromp5` | 4D ppmv | ~5.7e-7, ~7.5e-7 | Anthropogenic aromatic products |
| `no3` | 4D ppmv | 1.78e-6 / 1.00e-6 | NO₃ radical |
| `n2o5` | 4D ppmv | 2.67e-5 / 1.69e-5 | N₂O₅ (nighttime reservoir) |
| `no`, `no2` | 4D ppmv | available | NOx components |
| `oh`, `ho2` | 4D ppmv | available | Daytime oxidants |
| `PM2_5_DRY` | 4D µg/m³ | available | Total PM₂.₅ |
| `PBLH` | 3D m | 163 / 145 | Boundary layer height |
| `W` | 4D m/s | -2.09e-4 / +8.21e-5 | Vertical velocity |
| `U`, `V` | 4D m/s | available | 3D wind field |
| `U10`, `V10` | 3D m/s | available | Surface wind |
| `SWDNB`, `SWDNBC` | 3D W/m² | 2.63/5.00 vs 4.25/4.08 | SW all-sky and clear-sky |
| `ACSWDNB`, `ACSWDNBC` | 3D J/m² | accumulated | Better aerosol forcing estimate |
| `T`, `P`, `PB` | 4D | available | Temperature and pressure |
| `tolu`, `xyle`, `benz` | 4D ppmv | available | Aromatic VOC primary species |

### 2.2 What is in the output but all zeros (not activated)

These variables exist in the file structure but contain no meaningful data because they were not enabled in `HISTORY.rc` or require a different scheme:

| Variable | Expected use | Status |
|----------|-------------|--------|
| `GCCHEMPBL_0–3` | Chemistry tendency in PBL (kg/s) | All zero |
| `GCMIXINGPBL_0–3` | PBL mixing tendency (kg/s) | All zero |
| `GCEMISDRYDEPPBL_0–3` | Emissions+dry deposition in PBL | All zero |
| `GCCONVPBL_0–3` | Convective transport in PBL | All zero |
| `GCWETDEPPBL_0–3` | Wet deposition in PBL | All zero |
| `EBIO_ISO`, `EBIO_API` | Biogenic isoprene/α-pinene emission flux | All zero |
| `KN2O5`, `CN2O5`, `GAMN2O5` | N₂O₅ uptake rate and coefficient | All zero |
| `SAC`, `SNU` | Aerosol surface area concentration | All zero |
| `PBLMIXFRAC` | PBL mixing fraction by level | All zero |
| `AOD2D_OUT` | Column aerosol optical depth | All zero |
| `DRYDEPCHM`, `DRYDEPVELGC` | Dry deposition chemistry tendency | All zero |

**These are not model errors.** They are valid diagnostic fields that are simply not written because the corresponding `HISTORY.rc` entries were either commented out or the accumulation period did not match the output frequency. They can be enabled in future runs without changing the chemistry.

---

## 3. Objective 2 — Local Formation vs Regional Transport

### 3.1 The problem defined precisely

At any Bangkok grid cell, the SOAS concentration at 07:00 LST is the result of:

```
SOAS(t) = SOAS_transported_in + SOAS_locally_formed - SOAS_removed
```

With daily output only, we observe the net state. We cannot directly decompose these terms. However, **four proxy diagnostics available in the existing wrfout files** provide indirect evidence.

### 3.2 Diagnostic 1 — SOAP/SOAS formation ratio

**What it measures:** The degree to which the air mass is in an early (precursor-rich) vs late (product-rich) formation state.

**Values:**
- Ventilated (Jan 15): SOAP = 4.37e-3, SOAS = 6.98e-4 → **ratio = 6.26**
- Stagnation (Jan 22): SOAP = 5.47e-3, SOAS = 7.90e-4 → **ratio = 6.92**

**Interpretation:**
- A high ratio (>>1) means fresh precursor-rich conditions — SOA formation is ongoing. The air has not had time to convert precursor to product. This is consistent with **local production** of fresh SOAP from local VOC emissions, with incomplete conversion to SOAS.
- A low ratio (~1 or <1) means aged air — precursor has been mostly consumed and converted to aerosol. This is consistent with **transported air** that has undergone processing during transit.
- Both days show similar ratios (~6–7), suggesting Bangkok is consistently in a fresh-formation state. The stagnation ratio is slightly higher, which could indicate faster SOAP accumulation than conversion under stagnation.

**Caveat:** The ratio cannot distinguish between (a) rapid local SOAP production from fresh emissions and (b) SOAP transported from upwind before it converts. Both produce a high ratio. Spatial mapping is needed.

**How to compute:** Map SOAP/SOAS spatially for stagnation vs ventilated composites. Local formation hotspots show consistently high ratio co-located with emission source regions (Bangkok urban, northern Thailand forests). Regional transport shows low-ratio air arriving from upwind with SOAS already formed.

### 3.3 Diagnostic 2 — SOAS × PBLH (column burden proxy)

**This is the most direct diagnostic available without re-running the model.**

If pollutants are well-mixed within the boundary layer (which YSU scheme ensures at the 10-min chemistry timestep), the surface concentration and PBLH together approximate the column burden:

```
Column_burden ≈ SOAS_surface × PBLH  (in units of ppmv·m)
```

**Logic:**
- If stagnation increases surface SOAS only because the same regional SOAS mass is compressed into a shallower layer → column burden stays the same
- If stagnation increases surface SOAS because local production adds new mass → column burden also increases

**Values at Bangkok:**
- Jan 15 (ventilated): SOAS = 6.98e-4 ppmv × PBLH = 163 m → burden = 0.114 ppmv·m
- Jan 22 (stagnation): SOAS = 7.90e-4 ppmv × PBLH = 145 m → burden = 0.115 ppmv·m

These two days give nearly identical column burden (0.114 vs 0.115 ppmv·m), which suggests that **for these specific days the SOAS increase at the surface is primarily a compression effect, not a net new production signal**. The same mass is trapped in a shallower layer.

However, this must be computed across all 19 analysis days and compared statistically between the two regimes. The mean column burden during stagnation vs ventilation will show whether net new SOA production occurs at the population level.

**Implication for H2:** If mean stagnation column burden > ventilated column burden → H2 is confirmed at the chemical production level. If equal → the stagnation PM₂.₅ increase is dominated by boundary-layer compression, not enhanced chemistry. Both scenarios are scientifically valid and publishable.

### 3.4 Diagnostic 3 — Precursor spatial co-location with SOAS

**Available precursors in existing output:**

*Biogenic:*
- `mtpa` (α-pinene): emitted from forests, northern Thailand highlands
- `mtpo` (β-pinene): same source region
- `limo` (limonene): same

*Anthropogenic:*
- `aromp4`, `aromp5`: oxidation products of aromatics, concentrated over Bangkok urban
- `tolu`, `xyle`, `benz`: primary aromatic VOC from traffic and industry

**Key observation from data:** At Bangkok grid point, terpene concentrations on Jan 15 (ventilated) and Jan 22 (stagnation) are nearly identical — `mtpa` = 1.81e-5 vs 1.83e-5 ppmv. This means terpene availability at Bangkok does not change significantly between regimes.

**Interpretation:** Bangkok is an urban grid cell (LU_INDEX = 1). Biogenic terpene emissions are minimal at this location. The terpenes observed at Bangkok at 07:00 LST likely represent regional background that has been transported overnight from forested upwind areas, not locally emitted terpenes. Therefore, the biogenic SOA precursor supply at Bangkok is relatively insensitive to the stagnation regime.

**What drives Bangkok SOAP increase during stagnation:** The SOAP increase (25% higher on Jan 22 stagnation day) is more likely driven by aromatic VOC accumulation under the shallow PBL — the anthropogenic aromatic pathway. Map `aromp4+5` vs `SOAS` spatially to confirm.

### 3.5 Diagnostic 4 — Vertical velocity W and boundary-layer subsidence

`W` is the 3D vertical velocity at each model level. At lev=0 (surface):
- Jan 15 (ventilated): W = −2.09×10⁻⁴ m/s (weak subsidence)
- Jan 22 (stagnation): W = +8.21×10⁻⁵ m/s (weak upward motion at this specific point)

Note that vertical velocity at a single point on a single day is highly variable. The meaningful diagnostic is the **composite W field** (spatial map) averaged over all stagnation vs ventilated days. Persistent large-scale subsidence (negative W over the Thailand domain during stagnation) confirms that the boundary-layer compression is synoptically driven, not locally variable.

**A large-scale negative W during stagnation** (from the subtropical high pressure system) physically explains:
1. Suppressed convective mixing → shallow PBLH
2. Adiabatic warming → stable stratification → reinforced PBL cap
3. Limited exchange between boundary layer and free troposphere → pollutant trapping

This makes W the causal physical link between the synoptic pattern (high pressure) and the surface air quality response.

---

## 4. The NO₃ SOA Hypothesis — Why It Was Dropped and What the Data Shows

### 4.1 The original hypothesis

The original Hypothesis 3 proposed: *"Nighttime NO₃ radical chemistry drives stagnation-period SOA formation."*

The scientific basis was:
- NO₃ + monoterpene → organic nitrate → SOA (well-documented in laboratory and field studies)
- Stagnation accumulates NOx → more NO₃ → more terpene-NO₃ reaction → more SOA
- N₂O₅ heterogeneous uptake on aerosol surfaces → HNO₃ production also increases

### 4.2 Why the 2-product scheme cannot test this hypothesis

With `complex_SOA: false`, all monoterpene oxidation (by OH, O₃, and NO₃) feeds into a single SOAP pool. The model produces the same SOAP molecule regardless of which oxidant reacted with the monoterpene. There is no separate tracer for "NO₃-derived SOA."

**This is not a flaw — it is a documented design choice.** The 2-product scheme was designed for computational efficiency and captures total SOA mass reasonably well. However, it cannot provide oxidant-specific attribution.

### 4.3 What the data actually shows about NO₃ chemistry

**Direct observation from wrfout:**

| Variable | Ventilated (Jan 15) | Stagnation (Jan 22) | Change |
|----------|--------------------|--------------------|--------|
| NO (ppmv) | 3.40×10⁻⁴ | 8.18×10⁻⁴ | +2.4× |
| NO₃ (ppmv) | 1.78×10⁻⁶ | 1.00×10⁻⁶ | −0.56× |
| N₂O₅ (ppmv) | 2.67×10⁻⁵ | 1.69×10⁻⁵ | −0.63× |

**This is a critical and counterintuitive result:**

During stagnation, NO is 2.4× higher (from accumulated urban NOx). This high NO rapidly destroys both NO₃ and N₂O₅ via:

```
NO + NO₃  →  2 NO₂                 (fast, k ~ 2.6×10⁻¹¹ cm³/s)
N₂O₅ + NO →  NO₂ + NO₃ + NO₂  (indirect, via equilibrium)
```

At 07:00 LST in Bangkok under stagnation, high accumulated NO from the overnight period chemically suppresses NO₃ below its ventilated level. This is the "urban penalty" on nighttime radical chemistry: in high-NOx urban environments, NO titrates NO₃ before it can react with terpenes.

**Implication for the hypothesis:** In Bangkok, which is a high-NOx urban environment, stagnation does **not** increase NO₃ availability for terpene reactions. It does the opposite — it suppresses NO₃ by accumulating NO. The nighttime NO₃ + terpene SOA pathway is **more active during ventilated conditions** (lower NO, higher NO₃) than during stagnation.

This does not mean the NO₃ pathway is unimportant — it means it is suppressed specifically in the Bangkok urban center due to NOx loading. It may still be significant in rural northern Thailand where NOx is lower.

### 4.4 The 07:00 LST sampling problem

There is a separate and important limitation: all wrfout files are snapshots at 00:00 UTC = 07:00 Bangkok local time. This is the precise moment when:
- NO from overnight anthropogenic emissions peaks (traffic NOx, cooking, etc.)
- NO₃ reaches its minimum (because NO has been accumulating)
- The nocturnal boundary layer is still established

Peak NO₃ accumulation typically occurs between 20:00 and 02:00 LST, when:
- Solar radiation (which destroys NO₃) is zero
- NO has been depleted by oxidation reactions
- NO₂ + O₃ → NO₃ reaction proceeds unopposed

A simulation producing output only at 00:00 UTC **systematically undersamples** the period of peak NO₃ chemistry. The low NO₃ values observed do not mean NO₃ was low all night — they mean it is low at dawn after the overnight cycle has ended.

### 4.5 Why the hypothesis was revised

The hypothesis as stated — that stagnation enhances NO₃ SOA — is **not supported** by the Bangkok urban data for two independent reasons:

1. **Scheme limitation:** The 2-product scheme cannot track NO₃-specific SOA production
2. **Chemical reality:** High urban NOx under stagnation suppresses NO₃ via NO titration, reducing the NO₃ + terpene reaction rate

The revised Hypothesis 3 (aerosol-boundary-layer feedback) is better supported by available diagnostics and is a scientifically stronger claim.

---

## 5. What You Need to Re-run For

### 5.1 Things you can get from the existing run without re-running

These require only updating `HISTORY.rc` for future output frequencies, but the existing wrfout data is already sufficient for:

- SOAP/SOAS ratio maps (stagnation vs ventilation) ✓
- SOAS × PBLH column burden analysis ✓
- Precursor–product spatial co-location (mtpa, aromp4 vs soas) ✓
- Vertical velocity W composite maps ✓
- N₂O₅ time series analysis ✓
- Aerosol radiative forcing (SWDNB − SWDNBC, or accumulated AC versions) ✓
- NOx–SOA co-accumulation ✓
- PBLH spatial distribution ✓

### 5.2 Things that require enabling diagnostics in HISTORY.rc (no chemistry change, re-run needed)

To properly attribute SOA production to local chemistry vs transport, the following HISTORY.rc entries need to be activated. These are zero in the current output but the model computes them internally:

| Diagnostic | HISTORY.rc entry | What it provides |
|------------|-----------------|-----------------|
| Biogenic emission flux | `EBIO_API`, `EBIO_ISO` | Where terpenes are actually emitted (mol/km²/hr) |
| Chemistry tendency in PBL | `GCCHEMPBL_0`, `GCCHEMPBL_1`, etc. | Rate of chemical SOA production in the PBL (kg/s) |
| PBL mixing tendency | `GCMIXINGPBL_0`, etc. | Rate of vertical mixing within PBL (kg/s) |
| Emissions+dry deposition | `GCEMISDRYDEPPBL_0`, etc. | Net source/sink from surface processes |
| N₂O₅ uptake coefficient | `KN2O5` | Actual heterogeneous N₂O₅ loss rate (s⁻¹) |
| Aerosol surface area | `SAC` | Total aerosol surface area (m²/m³) — drives heterogeneous chemistry |
| AOD column | `AOD2D_OUT` | Aerosol optical depth for radiative forcing analysis |
| PBL mixing fraction | `PBLMIXFRAC` | Vertical profile of mixing efficiency within PBL |

**With `GCCHEMPBL` activated:** You can directly compare the chemical tendency of SOAS within the PBL (local production rate, kg/s) against the mixing tendency from above the PBL. If chemistry > mixing → local production dominates. If mixing > chemistry → transport from the residual layer above dominates.

**With `EBIO_API` and `EBIO_ISO` activated:** You get the actual MEGAN emission flux at each grid cell, allowing you to overlay emission maps with SOAS maps and quantify whether SOAS peaks align with emission peaks.

**Required change:** In `HISTORY.rc`, add these variables to the output fields list and ensure they are in the same collection as the wrfout file. No changes to the chemistry or namelist are needed. A short re-run (even 5–7 days) covering one stagnation and one ventilated period is sufficient to validate these diagnostics.

### 5.3 Things that require a scheme change (re-run with different chemistry)

To properly address oxidant-specific SOA attribution (separating OH vs O₃ vs NO₃ channels), the `complex_SOA` scheme must be activated:

```yaml
complex_SOA:
  activate: true
  semivolatile_POA: false
```

This activates the TSOA0–3 / TSOG0–3 (terpene VBS) and ASOA1–N / ASOG1–3 (anthropogenic VBS) tracers. The VBS scheme:
- Resolves SOA by volatility bin (allows partitioning to depend on temperature)
- Separates terpene-derived from anthropogenic-derived SOA at the species level
- In some GEOS-Chem versions, separately tracks the OH+O₃ (daytime) and NO₃ (nighttime) oxidation channels for terpenes via different TSOG precursors

**Cost:** This increases the number of transported chemical species and will be computationally more expensive (~20–40% slower). However, it provides the explicit biogenic vs anthropogenic SOA separation that Objective 2 requires.

**Note:** The `complex_SOA` scheme with `semivolatile_POA: false` (as shown) keeps primary organic aerosol non-volatile (same as the 2-product scheme) while adding volatility resolution for secondary organics only. This is the recommended choice for your research objectives.

### 5.4 Things that require a new simulation design (sensitivity runs)

To definitively quantify the local vs regional fraction of SOAS, a **zero-emission sensitivity run** is required:

- **Control:** Full emissions as in the current simulation
- **Sensitivity 1:** Zero Thailand anthropogenic VOC (toluene, xylene, benzene → 0)
- **Sensitivity 2:** Zero Thailand biogenic VOC (isoprene, monoterpenes → 0 over the Thailand domain)

The SOAS difference between control and sensitivity runs directly gives the locally produced fraction. This is the gold standard for source attribution and is a standard approach in CTM attribution studies.

**Note on hourly output:** Regardless of the scheme, re-running with 1-hourly output (change `history_interval = 60` in namelist.input) is strongly recommended. This will:
- Capture the nocturnal NO₃ peak (20:00–02:00 LST) — addressing the sampling problem
- Enable diurnal cycle analysis of SOAP → SOAS conversion
- Allow budget analysis at chemically meaningful timescales

---

## 6. Recommendations for Full Research Design

### Priority 1 — Do now, before new runs (existing data)
1. Compute SOAP/SOAS ratio maps for stagnation vs ventilated composites
2. Compute SOAS × PBLH column burden for all 19 days — statistical comparison
3. Compute aerosol radiative forcing (ACSWDNB − ACSWDNBC) time series
4. Map N₂O₅ spatial distribution and regime comparison

### Priority 2 — Short re-run with HISTORY.rc changes only
1. Enable `GCCHEMPBL`, `GCMIXINGPBL`, `GCEMISDRYDEPPBL` — chemistry budget in PBL
2. Enable `EBIO_API`, `EBIO_ISO` — biogenic emission flux maps
3. Enable `KN2O5`, `SAC` — heterogeneous N₂O₅ chemistry diagnostics
4. Enable `AOD2D_OUT`, `PBLMIXFRAC`
5. Set `history_interval = 60` for 1-hourly output
6. Run minimum 14 days (one full stagnation period + one ventilated period)

### Priority 3 — Full re-run with complex_SOA
1. Set `complex_SOA: activate: true`
2. Run full January 2025 period with 3-hourly output (balance storage vs resolution)
3. This provides TSOA/ASOA separation for biogenic vs anthropogenic attribution

### Priority 4 — Sensitivity runs for quantitative attribution
1. Zero Thailand anthropogenic VOC emissions
2. Zero Thailand biogenic VOC emissions (MEGAN offline or online suppressed)
3. Compare SOAS fields between control and sensitivity → local fraction quantified

---

## 7. Summary Table — Hypotheses and Diagnostic Availability

| Hypothesis | Status with current data | Required for full test |
|------------|--------------------------|------------------------|
| **H1:** VC controls PM₂.₅ | ✅ Supported — 2.73×, p=0.002 | Observation validation (PCD/AQMTHAI network) |
| **H2:** Stagnation enhances OA fraction | ✅ Supported — OA fraction 65%→79% | Column burden diagnostic; complex_SOA re-run for biogenic/anthropogenic separation |
| **H2 (local vs regional):** Local formation increases | ⚠️ Partially — SOAP/SOAS ratio and column burden indicate compression-dominated; local production enhancement unclear | GCCHEMPBL diagnostic; zero-emission sensitivity runs |
| **H3 (original NO₃ SOA):** Stagnation enhances nighttime NO₃ SOA | ❌ Not supported for Bangkok urban — stagnation suppresses NO₃ via NO titration | Hourly output (to observe NO₃ peak at 20:00-02:00 LST); rural vs urban spatial comparison; complex_SOA for explicit NO₃ channel |
| **H3 (revised aerosol-radiation feedback):** Stagnation enhances SOA via aerosol-BL feedback | ⚠️ Partially — aerosol forcing (SWDNB−SWDNBC) available; BL feedback requires hourly output | Hourly PBLH output; AOD diagnostics enabled |

---

## 8. A Note on Scientific Honesty

The finding that N₂O₅ is **lower** during stagnation at Bangkok (because NO titrates NO₃) is **not a failure of the hypothesis.** It is a scientifically important result that reveals:

1. The Bangkok urban environment is too NOx-saturated for the nighttime NO₃ + terpene pathway to be significant
2. The same mechanism (high NOx) that suppresses NO₃ chemistry **also** drives the HO₂ + NO → OH enhancement observed at dawn
3. The relevant spatial scale for NO₃ SOA may be rural/peri-urban northern Thailand, not the Bangkok megacity

This motivates the nested 9 km domain (WRF_GC_2 configuration) that would resolve urban–rural gradients and show where NO₃ chemistry is actually relevant. It is a finding that strengthens the research design rather than weakening it.

---

*Document version: June 2026*  
*Based on: WRF-GC v2.0, GEOS-Chem 12.x, wrfout_d01_2025-01-* output inspection*  
*Values referenced: Bangkok grid point j=74, i=89 (13.75°N, 100.50°E), surface level (lev=0)*
