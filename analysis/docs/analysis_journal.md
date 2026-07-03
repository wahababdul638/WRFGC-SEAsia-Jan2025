# Analysis Journal — WRF-GC SEAsia January 2025
**Author:** Abdul Wahab  
**Period covered:** Proposal defense preparation through updated proposal submission  
**Simulation:** WRF-GC v2.0, January 3–28 2025, 27 km single domain, Southeast Asia  
**Analysis window:** January 10–28 (19 days post spin-up)

---

## 1. Starting Point

The simulation was complete with 26 daily wrfout files (`wrfout_d01_2025-01-*`) covering
January 3–28, 2025. The first 7 days (Jan 3–9) were discarded as spin-up, leaving 19 days
for analysis starting Jan 10. The Bangkok grid point was identified at j=74, i=89
(13.750°N, 100.500°E), the closest model cell to central Bangkok.

A single monolithic script (`plot_wrfgc.py`) existed. It was replaced during this work
with a modular system: `precompute.py` loads all time series once, and individual
`fig01.py`–`fig14.py` scripts each produce one figure.

A comprehensive CSV (`bangkok_comprehensive_jan2025.csv`) was extracted covering 37
variables at the Bangkok point for all 19 days, enabling fast re-plotting without
re-reading the 148 GB of wrfout files.

---

## 2. Model Configuration Audit

Before any analysis, the model configuration was checked against the simulation design
to confirm what chemistry was actually active.

### SOA Scheme
Reading `WRF/run/geoschem_config.yml`:
```
complex_SOA: false
```
This confirmed the simulation uses the **2-product simplified SOA scheme** (Henze &
Seinfeld, 2006), not the Volatility Basis Set (VBS). The implications are significant:

- **SOAP** (MW=150 g/mol, `Is_Gas=true`): the lumped gas-phase SOA precursor pool.
  All oxidation channels — OH, O₃, and NO₃ — feed into a single SOAP reservoir.
- **SOAS** (MW=150 g/mol, `Is_Aerosol=true`, non-volatile): the condensed SOA product
  counted in PM₂.₅_DRY.
- **VBS tracers inactive:** `tsoa0`–`tsoa3`, `tsog0`–`tsog3`, `asoa1`–`asoa4`,
  `asog1`–`asog3` are all at machine epsilon (~8.7×10⁻¹⁷ ppmv). These are not
  suppressed — they are genuinely not active in this configuration.

**Consequence established early:** The model cannot attribute SOA to specific oxidant
channels (OH vs O₃ vs NO₃). Any hypothesis requiring pathway-resolved SOA
attribution cannot be tested from this simulation alone.

### Other active SOA tracers
Beyond SOAP/SOAS, three additional minor SOA tracers carry real values:
- `soaie` — IEPOX-SOA (isoprene epoxydiol pathway)
- `soagx` — glyoxal SOA (aqueous-phase)
- `lvoc` / `lvocoa` — low-volatility organic compounds

These were included in `soatot_ppb` but are small relative to SOAS.

---

## 3. Regime Classification

### Ventilation Coefficient
VC is defined as:
```
VC = PBLH × |Wind₁₀m|     [m² s⁻¹]
```

**Two distinct VC diagnostics** were extracted and compared:

| Diagnostic | Median | What it represents |
|---|---|---|
| `VC_TH_Mean` (Thailand domain-mean) | **1800 m² s⁻¹** | Spatial average over full 179×149 domain. Captures synoptic-scale dispersion capacity. |
| `VC_BKK` (Bangkok point) | **268 m² s⁻¹** | Single grid cell at 13.75°N 100.50°E. Captures local urban BL at 07:00 LST (pre-sunrise). |

The Bangkok point VC is consistently 5–7× lower than the domain mean because:
1. PBLH at 07:00 LST (= 00:00 UTC, the wrfout snapshot time) captures the nocturnal
   stable boundary layer before daytime convective growth. Bangkok mean PBLH at this
   time is only **105–307 m** depending on regime.
2. Urban surface roughness reduces 10 m wind speed at the city grid cell.

**Classification decision:** The stagnation threshold of 1800 m² s⁻¹ is applied to
`VC_TH_Mean` (domain mean). This captures synoptic-scale stagnation events as intended
by Jacob & Winner (2009). Using the Bangkok-point VC would classify nearly all 19 days
as stagnant (since VC_BKK median = 268 m² s⁻¹).

**17 of 19 days classify the same** under both metrics. Two days differ:
- Jan 13: VC_BKK = 268 (STAG by BKK threshold), VC_TH = 2462 (vent by TH threshold)
- Jan 22: VC_BKK = 476 (vent by BKK threshold), VC_TH = 1800 (exactly at TH median → STAG)

### Regime days
| Regime | Days | Period |
|---|---|---|
| **Ventilated** (VC > 1800) | 9 days | Jan 10–18 |
| **Stagnation** (VC ≤ 1800) | 10 days | Jan 19–28 |

---

## 4. Diagnostic Exploration — What Was Probed and Found

Diagnostics were extracted in sequence, with each result informing the next question.

### 4.1 PM₂.₅ — The Primary Signal

| Metric | Stagnation | Ventilated |
|---|---|---|
| Mean (µg m⁻³) | **125.1** | 45.8 |
| Maximum (µg m⁻³) | **197.0** (Jan 25) | 70.3 |
| Thailand NAAQS (37.5 µg m⁻³) exceeded? | Yes, all 10 days | Mostly no |
| WHO 24-hr guideline (15 µg m⁻³) exceeded? | Yes, all 10 days | Yes, all 9 days |

The stagnation–ventilated contrast in PM₂.₅ is large and clear (2.7× mean difference).
Peak values of 185–197 µg m⁻³ occur on Jan 21 and Jan 25, both deep stagnation days.

### 4.2 Boundary Layer Height — The Compression Mechanism

| Metric | Stagnation | Ventilated |
|---|---|---|
| Mean PBLH at Bangkok (m) | **105** | 307 |
| Minimum PBLH (m) | 40 (Jan 21) | 125 |

PBLH collapses to 40 m on the worst stagnation day — a factor of ~7 compression
relative to the ventilated mean. This is the primary physical mechanism: the same
mass of pollutants is compressed into a much shallower mixing volume, raising surface
concentrations even without any additional emission or chemistry.

### 4.3 SOAS and the Column Burden Test

SOAS (the condensed SOA aerosol) rises substantially under stagnation:

| Metric | Stagnation | Ventilated |
|---|---|---|
| SOAS surface (µg m⁻³) | **14.55** | 5.96 |
| SOAS ratio | 2.4× | — |

**Column burden proxy** (surface SOAS × PBLH, a rough integral):

| | Stagnation | Ventilated | Change |
|---|---|---|---|
| SOAS × PBLH (ppb·m) | 221.8 | 284.9 | **−22.2%** |

**Interpretation:** The column burden is actually *lower* during stagnation by 22%.
This means the PBLH compression fully explains — and more than accounts for — the
surface SOAS increase. The total atmospheric column of SOA does not increase under
stagnation. The surface concentration enhancement is a **dilution/compression effect**,
not net new chemical production.

*Caveat:* This proxy assumes vertically uniform SOAS within the BL, which is not
strictly valid. Definitive attribution requires 3D column integrals from wrfout,
which were not computed here.

### 4.4 SOAP/SOAS Ratio — Formation State

| Metric | Stagnation | Ventilated |
|---|---|---|
| SOAP/SOAS (molar ratio) | **5.78** | 4.33 |

Both regimes show a high SOAP/SOAS ratio (>4), indicating a precursor-rich environment
where gas-phase SOAP pool remains large relative to the condensed SOAS product. The
ratio is somewhat higher during stagnation, consistent with precursor accumulation
outpacing condensation at the 07:00 LST snapshot time.

### 4.5 SOA Precursors — Biogenic and Anthropogenic

Both biogenic terpenes and anthropogenic aromatics accumulate dramatically under stagnation:

| Precursor | Stagnation | Ventilated | Ratio |
|---|---|---|---|
| Terpenes (MTPA+MTPO+LIMO, ppb) | **0.269** | 0.018 | **14.8×** |
| Aromatics (AROMP4+AROMP5, ppb) | **0.0147** | 0.0014 | **10.5×** |
| Terpene/Aromatic ratio | **18.3** | 12.9 | — |

Both precursor classes accumulate due to reduced ventilation. The terpene/aromatic
ratio is higher during stagnation (18.3 vs 12.9), suggesting biogenic precursors
accumulate proportionally more — consistent with the H2 hypothesis about biogenic
fraction increasing under stagnation. However, since SOAP lumps both into a single
pool, the separate SOA contributions cannot be quantified from this simulation.

### 4.6 Oxidant Chemistry — The Most Surprising Findings

| Oxidant | Stagnation | Ventilated | Ratio | Interpretation |
|---|---|---|---|---|
| OH (pptv) | 0.007 | 0.002 | **3.5× higher** during stagnation | Recycled from HO₂ + NO → OH + NO₂ |
| NO (ppb) | 28.3 | 0.68 | **41.5× higher** during stagnation | Traffic NOx trapped, no ventilation |
| NO₂ (ppb) | 43.5 | 19.0 | **2.3× higher** during stagnation | NO oxidation product |
| NO₃ radical (pptv) | 0.177 | 2.94 | **0.06× — 94% lower** during stagnation | Titrated by accumulated NO |
| N₂O₅ (pptv) | 3.94 | 42.68 | **0.09× — 91% lower** during stagnation | Follows NO₃ suppression |

These results were initially counterintuitive and drove significant hypothesis revision:

**OH is higher during stagnation** despite high NOx. The mechanism is
HO₂ + NO → OH + NO₂: the 41.5× accumulated NO efficiently recycles HO₂ back to OH
at dawn (07:00 LST), when HO₂ is produced by early photolysis. This creates a
"super-photochemical" morning environment under stagnation.

**NO₃ is 94% lower during stagnation.** The 41.5× elevated NO directly consumes
the nighttime NO₃ radical via NO + NO₃ → 2NO₂. Bangkok's chronic high-NOx urban
environment eliminates the nighttime biogenic pathway. This is the "urban NOx
penalty" on NO₃-radical chemistry.

---

## 5. Hypothesis Evolution

### 5.1 Original Hypotheses (before analysis)

| # | Statement |
|---|---|
| H1 | WRF-GC improves PM₂.₅ simulation versus offline GEOS-Chem |
| H2 | Stagnation increases locally formed SOA relative to regional transport by suppressing dispersion and increasing precursor residence times |
| H3 | Stagnation enhances SOA through nonlinear interactions: BL suppression, pollutant accumulation, and aerosol-radiation feedback |
| **Old H3** (also considered) | Stagnation enhances SOA through the NO₃ radical + biogenic VOC nighttime pathway |

### 5.2 What the Diagnostics Showed — and What Changed

**Old H3 (NO₃ pathway) — Dropped for two independent reasons:**

*Reason 1 — Chemistry:* NO₃ radical is 94% lower during stagnation (0.177 vs
2.94 pptv) because accumulated traffic NO (41.5× higher) titrates it. Bangkok is
too NOx-saturated for the nighttime biogenic pathway to be significant at the urban
grid cell. The hypothesis predicted enhancement; the data shows suppression.

*Reason 2 — Scheme:* Even if NO₃ were elevated, `complex_SOA: false` lumps all
oxidant channels into SOAP. NO₃-initiated SOA cannot be distinguished from OH- or
O₃-initiated SOA in this output. Pathway-level attribution requires `complex_SOA: true`.

Both reasons are independent disqualifiers. The old H3 was withdrawn.

**H2 — Refined based on precursor evidence:**

The original H2 focused on "locally formed SOA vs regional transport." This framing
was revised because the 2-product scheme cannot separate local from transported SOA
(no GC budget output, no sensitivity runs). The column burden test also showed that
stagnation does not increase the total SOA column — compression explains the surface
signal.

H2 was reframed around what IS testable: whether biogenic SOA increases relative to
anthropogenic SOA under stagnation, using precursor accumulation as a proxy. Data
supports the precursor side of this claim: terpenes increase 14.8× and aromatics
increase 10.5×, with terpenes increasing proportionally more (terpene/aromatic ratio
rises from 12.9 to 18.3). The 2-product scheme prevents direct SOA attribution.

**H3 — Confirmed directionally:**

SOAS surface concentration rises 2.4× under stagnation, PBLH collapses from 307 m
to 105 m, and OH shows the stagnation-driven recycling mechanism (3.5× higher).
The aerosol-radiation feedback (the "stove effect") cannot be directly quantified
from available output but the PBLH suppression during stagnation is consistent with
the expected signature.

### 5.3 Current Hypotheses (updated proposal)

| # | Statement | Data support from this simulation |
|---|---|---|
| H1 | WRF-GC performance improvement is regime-dependent: bias reduction and correlation improvement vs Thai PCD observations will be greater during stagnant days | Requires PCD observational data for evaluation |
| H2 | Under stagnation, the biogenic SOA fraction of total PM₂.₅ increases relative to anthropogenic SOA (terpene precursors accumulate proportionally more than aromatics); locally formed secondary inorganic nitrate increases more than sulfate | Terpene/aromatic ratio rises 18.3 vs 12.9 ✓ (precursor proxy only; SOA attribution requires complex_SOA: true) |
| H3 | Stagnation enhances SOA accumulation through nonlinear BL suppression, pollutant accumulation, and aerosol-radiation feedback | SOAS 2.4× higher, PBLH 2.9× shallower, OH recycling confirmed; aerosol-radiation direct feedback not quantified (AOD output not activated) |

---

## 6. Key Numerical Summary

All values at the Bangkok grid point (13.75°N, 100.50°E), 07:00 LST (00:00 UTC),
Jan 10–28 2025, surface level.

| Variable | Stagnation (n=10) | Ventilated (n=9) | Ratio or change |
|---|---|---|---|
| VC_TH_Mean (m² s⁻¹) | ≤ 1800 (by definition) | > 1800 | — |
| VC_BKK (m² s⁻¹) | median 268 | median 268 | Both urban, both low |
| PBLH (m) | 105 | 307 | −66% |
| PM₂.₅ (µg m⁻³) | 125.1 | 45.8 | +2.7× |
| SOAS (µg m⁻³) | 14.55 | 5.96 | +2.4× |
| SOAS × PBLH column (ppb·m) | 221.8 | 284.9 | −22% |
| SOAP/SOAS ratio | 5.78 | 4.33 | Higher stag = more precursor-rich |
| Terpenes (ppb) | 0.269 | 0.018 | +14.8× |
| Aromatics (ppb) | 0.0147 | 0.0014 | +10.5× |
| Terpene/Aromatic ratio | 18.3 | 12.9 | Biogenic fraction larger under stag |
| OH (pptv) | 0.007 | 0.002 | +3.5× (recycling mechanism) |
| NO (ppb) | 28.3 | 0.68 | +41.5× (traffic trapped) |
| NO₂ (ppb) | 43.5 | 19.0 | +2.3× |
| NO₃ radical (pptv) | 0.177 | 2.94 | −94% (NO titration) |
| N₂O₅ (pptv) | 3.94 | 42.68 | −91% (follows NO₃) |

---

## 7. Known Limitations of This Analysis

### Snapshot timing
All wrfout files are at 00:00 UTC = **07:00 Bangkok LST**. This is pre-sunrise,
capturing the nocturnal/dawn chemistry state. Daytime photochemical peaks, afternoon
boundary layer development, and sea-breeze ventilation are not represented. All
oxidant values (OH, O₃, NO₃) reflect the early-morning state, not daily averages.

### VC_BKK vs VC_TH_Mean
The Bangkok-point VC (median 268 m² s⁻¹) is 6.7× lower than the Thailand domain-mean
VC used for classification (median 1800 m² s⁻¹). The classification is based on the
domain mean (correct for synoptic-scale stagnation events). The Bangkok point is
chronically under-ventilated even on "ventilated" days — this is an expected feature
of an urban grid cell at dawn, not an error.

### Column burden proxy
SOAS_surface × PBLH is a rough proxy, not a true column integral. It assumes the BL
is vertically well-mixed for SOAS, which is not exactly true. The result (−22% column
burden during stagnation) should be interpreted cautiously.

### No GC budget output
GCCHEMPBL, GCMIXINGPBL, GCEMISDRYDEPPBL, and related budget terms output all zeros.
These fields were not activated in `HISTORY.rc`. Direct chemical tendency attribution
is therefore not possible from this output.

### Aerosol-radiation feedback
AOD2D_OUT and PBLMIXFRAC are not output. The aerosol-radiation feedback (H3) cannot
be directly quantified. The PBLH suppression during stagnation is consistent with
the expected feedback but cannot be causally attributed to aerosol effects without
a sensitivity run.

---

## 8. What Further Simulations Would Unlock

| What you need | What to change | What it enables |
|---|---|---|
| NO₃-SOA pathway attribution | `complex_SOA: true` in geoschem_config.yml | Activates TSOA/ASOA/TSOG/ASOG; separates terpene-SOA from aromatic-SOA; enables biogenic vs anthropogenic SOA comparison for H2 |
| GC chemistry budgets | Add GCCHEMPBL, GCMIXINGPBL to HISTORY.rc | Chemical tendency in BL; quantify how much SOA forms vs how much is transported |
| Biogenic emission fluxes | Add EBIO_ISO, EBIO_API, EBIO_MT to HISTORY.rc | Direct measurement of what is emitted vs what accumulates |
| N₂O₅ heterogeneous chemistry | Add KN2O5, CN2O5, GAMN2O5, SAC to HISTORY.rc | Quantify aerosol uptake pathway even though NO₃ is suppressed |
| Aerosol-radiation feedback | Add AOD2D_OUT, PBLMIXFRAC to HISTORY.rc | Directly quantify the stove effect for H3 |
| Local vs regional SOA separation | Zero-emission sensitivity run | Remove anthropogenic emissions → SOAS difference = local anthropogenic contribution |
| Nocturnal chemistry | Additional wrfout at 18:00 UTC (01:00 LST) | Capture nighttime NO₃ before dawn traffic destroys it |

---

## 9. Figure Inventory

| Figure | File | What it shows | Objective |
|---|---|---|---|
| fig01 | `fig01_timeseries.png` | PM₂.₅, SOAP/SOAS, oxidants, VC time series | Overview |
| fig02 | `fig02_aerosol_composition.png` | Aerosol component breakdown (SO₄, NIT, NH₄, BC, OA) | Obj 1, 2 |
| fig03 | `fig03_oxidants.png` | OH, O₃, NOx oxidant time series | Obj 3 |
| fig04 | `fig04_vc_scatter.png` | VC vs PM₂.₅ scatter | Obj 2 |
| fig05 | `fig05_nox_oh_chemistry.png` | NOx–OH relationship and regime | Obj 3 |
| fig06 | `fig06_spatial_pm25_soa.png` | Spatial PM₂.₅ and SOAS maps stag vs vent | Obj 2 |
| fig07 | `fig07_summary_bars.png` | Mean species comparison stag vs vent with t-tests | Obj 2, 3 |
| fig08 | `fig08_soa_precursors.png` | Spatial SOA precursor maps (stagnation composite) | Obj 2 |
| fig09 | `fig09_soa_formation_state.png` | SOAP/SOAS ratio, column burden, VC vs SOAS | Obj 2 |
| fig10 | `fig10_no3_pathway_assessment.png` | NO₃ suppression, titration curve, data limitation | Old H3 assessment |
| fig11 | `fig11_soa_chemistry_drivers.png` | SOA vs OH, SOA vs NO₃, VOC vs SOA | Obj 2, 3 |
| fig12 | `fig12_mechanism_proof.png` | Oxidant seesaw, HO₂/OH recycling, OA fraction shift | Obj 3 |
| fig13 | `fig13_intuitive_summary.png` | Stagnation multiplier summary | Overview |
| fig14 | `fig14_vertical_mechanisms.png` | SOAS + W + PBLH + column burden time series | Obj 3 |
| — | `fig_bangkok_pm25_vc.png` | Bangkok PM₂.₅ and VC on one twin-axis panel | Proposal Fig 5 |
