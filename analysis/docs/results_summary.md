# WRF-GC Pilot Simulation: Results Summary and Scientific Takeaways

**Simulation:** January 2025, South/Southeast Asia, 27 km single domain  
**Model:** WRF-GC v2.0 (WRF 4.x + GEOS-Chem 12.x, online two-way coupled)  
**Analysis period:** Jan 10–28, 2025 (19 days; Jan 3–9 discarded as spin-up)  
**All snapshots:** 00:00 UTC = 07:00 Bangkok local time (early morning)  
**Document prepared:** May 2026

---

## 1. Simulation Setup and Regime Classification

The domain covers South/Southeast Asia at 179 × 149 mass points (27 km Mercator grid), centred at 13.75°N, 100.50°E. The Bangkok grid point is at j=74, i=89 (13.750°N, 100.500°E). Chemistry runs every 10 minutes; WRF time step is 120 s.

### Stagnation Classification

The ventilation coefficient (VC) is defined as:

> **VC = PBLH × |Wind₁₀ₘ|** (units: m²/s)

VC integrates the two main drivers of surface pollutant dilution — boundary layer depth and horizontal transport. Low VC means pollutants are trapped near the surface.

The Thailand-mean VC was computed daily over the Thailand box (5.5–20.5°N, 98.0–106.0°E). The **median VC over the 19-day analysis window was 1800 m²/s**, and this was used as the stagnation threshold:

- **Stagnation days (VC ≤ 1800 m²/s):** Jan 19–28 — 10 days
- **Ventilated days (VC > 1800 m²/s):** Jan 10–18 — 9 days

The classification is internally consistent: the two regimes fall into a clear early-period (ventilated) vs late-period (stagnant) split, consistent with the typical seasonal meteorological transition in the region during January.

---

## 2. Meteorological Characterization

### Boundary Layer and Wind

| Variable | Stagnation | Ventilated | Ratio |
|---|---|---|---|
| PBLH at Bangkok (m) | 105 ± 38 | 307 ± 89 | 0.34× |
| VC at Bangkok (m²/s) | 190 ± 120 | 1166 ± 480 | 0.16× |
| Thailand-mean VC (m²/s) | ~1100 | ~3800 | 0.29× |

During stagnation, the planetary boundary layer collapses to roughly one-third of its ventilated depth. With a shallower mixing layer and weaker surface winds, the effective atmospheric volume available for pollutant dilution decreases by a factor of ~6 at the Bangkok point.

### Physical Interpretation

Stagnation in January over Thailand is driven by the strengthening of the subtropical high-pressure system over the South China Sea, which suppresses vertical mixing and reduces low-level wind. The result is a shallow, stable nocturnal boundary layer that does not fully erode during the day — a textbook wintertime inversion scenario in tropical/subtropical Southeast Asia.

---

## 3. PM₂.₅ Response to Stagnation — Hypothesis 1

**H1:** *Meteorological stagnation (low VC) causes significant accumulation of fine particulate matter (PM₂.₅) over Thailand.*

### Result: **CONFIRMED**

| Metric | Stagnation | Ventilated | Ratio | p-value |
|---|---|---|---|---|
| Bangkok PM₂.₅ (µg/m³) | 125 ± 32 | 46 ± 18 | **2.73×** | 0.002 |
| Thailand-mean PM₂.₅ (µg/m³) | elevated | baseline | significant | < 0.01 |

PM₂.₅ during stagnation events exceeds 100 µg/m³ at Bangkok, well above the Thai NAAQS standard of 37.5 µg/m³ (24-hr average) and WHO guideline of 15 µg/m³. During ventilated periods, PM₂.₅ remains near 46 µg/m³ — unhealthy by WHO standards but substantially lower.

The VC–PM₂.₅ scatter (figP4) shows a clear inverse relationship: as VC drops below ~2000 m²/s, PM₂.₅ spikes sharply. This nonlinear response is consistent with the theoretical expectation that pollutant concentration scales approximately as the inverse of the mixing volume.

### What Drives the PM₂.₅ Increase?

PM₂.₅ accumulation under stagnation is not simply proportional — it reflects the combined effects of:
1. Reduced dilution (shallower mixing layer, weaker winds)
2. Increased chemical production (longer residence times allow more secondary formation)
3. Reduced wet/dry removal (stagnant conditions correlate with lower precipitation)

The relative contributions of these three effects cannot be separated from daily snapshots alone — this is a key motivation for the full research design.

---

## 4. Aerosol Composition and Organic Aerosol — Hypothesis 2 (Part 1)

**H2:** *Stagnation enhances secondary organic aerosol (SOA) formation, increasing the OA fraction of PM₂.₅.*

### Aerosol Composition Method

PM₂.₅ total is taken directly from the WRF-GC diagnostic `PM2_5_DRY` (µg/m³). Individual inorganic components are computed from ppmv tracers using:

> C (µg/m³) = ppmv × N_air (mol/m³) × MW (g/mol)

where N_air ≈ 41.2 mol/m³ at the surface (1 atm, ~295 K). Organic aerosol (OA) is computed as the residual:

> **OA = PM₂.₅ − SO₄ − NIT − NH₄ − BC**

This residual approach avoids the overcounting that results from directly summing all organic tracers with uncertain molecular weights. It captures POA + SOA combined.

### Composition Results

| Component | Stagnation (µg/m³) | Ventilated (µg/m³) | Ratio | p-value |
|---|---|---|---|---|
| PM₂.₅ total | 125 | 46 | 2.73× | 0.002 |
| OA (residual) | ~98 | ~30 | **3.28×** | 0.001 |
| BC | ~8 | ~2 | **3.85×** | — |
| SO₄ | ~5 | ~7 | 0.73× | — |
| NIT | ~6 | ~4 | ~1.5× | — |
| NH₄ | ~3 | ~2 | ~1.5× | — |

**OA fraction of PM₂.₅:**
- Stagnation: **~79%**
- Ventilated: **~65%**
- Ratio: **1.2× increase in OA fraction** (not just absolute OA — the composition shifts toward organics)

### What This Means

During stagnation, organics dominate PM₂.₅ even more strongly than during ventilated periods. The absolute OA increase (3.28×) outpaces the total PM₂.₅ increase (2.73×), meaning secondary organic chemistry is amplified under stagnation beyond what simple accumulation would predict.

The SO₄ decrease during stagnation (0.73×) is noteworthy: sulfate is highest during ventilated conditions, likely reflecting more efficient photochemical SO₂ oxidation and/or transport of regional SO₂ when atmospheric circulation is active. Under stagnation, local emissions dominate but SO₂-to-SO₄ conversion may be limited by suppressed OH at longer timescales (despite elevated dawn OH — see Section 6).

BC increases 3.85× under stagnation, closely tracking total PM₂.₅, and confirms that stagnation accumulates primary emissions in addition to promoting secondary formation.

---

## 5. SOA Precursor Analysis — Hypothesis 2 (Part 2)

### GEOS-Chem SOA Scheme in This Run

WRF-GC v2.0 with GEOS-Chem 12.x uses a **2-product simplified SOA scheme** (Henze & Seinfeld, 2006) with two active tracers:

| Tracer | Phase | MW (g/mol) | Role |
|---|---|---|---|
| SOAP | Gas | 150 | Semi-volatile SOA precursor pool (gas-phase) |
| SOAS | Aerosol | 150 | Non-volatile SOA aerosol (in PM₂.₅) |

TSOA0–3 and ASOA1–N are structurally declared in the species table but are **inactive in this run** (concentrations at machine epsilon, ~8.7×10⁻¹⁷ ppmv). The 2-product scheme is the operative SOA mechanism.

Terpene and aromatic tracers (MTPA, MTPO, LIMO for monoterpenes/sesquiterpenes; AROMP4, AROMP5 for aromatic oxidation products) are the upstream precursors feeding SOAP production.

### SOA Precursor Results

| Variable | Stagnation | Ventilated | Ratio | p-value |
|---|---|---|---|---|
| SOAP (gas precursor, pptv) | elevated | baseline | **3.27×** | significant |
| SOAS (aerosol, µg/m³) | elevated | baseline | **2.44×** | significant |
| Biogenic terpenes (MTPA+MTPO+LIMO, pptv) | elevated | baseline | **14.88×** | — |
| Anthropogenic aromatics (AROMP4+AROMP5, pptv) | elevated | baseline | **10.50×** | — |

### Spatial Pattern: SOAS ratio ≈ 0.99×

The **spatial** pattern of SOAS (stagnation vs ventilated mean map) shows nearly equal concentrations (ratio ~0.99×), in contrast to the **time-series** result (2.44× at Bangkok point). This apparent contradiction is physically meaningful:

SOAS is **non-volatile** — once formed, it does not evaporate back to the gas phase. It also has a long atmospheric lifetime and is spatially distributed by advection during ventilated conditions. The spatial mean map captures the broad background of SOAS advected across the domain during ventilated periods. The point time-series captures the local accumulation at Bangkok during stagnation events. These are complementary views of the same tracer.

### Biogenic vs Anthropogenic Precursors

The much larger enhancement of biogenic terpene precursors (14.88×) compared to anthropogenic aromatics (10.50×) during stagnation may reflect:
- Stronger boundary layer trapping of forest-emitted terpenes (low-altitude biogenic sources in central/northern Thailand)
- The seasonal vegetation phenology in January (dry season — lower biogenic emissions overall, but what is emitted is trapped efficiently)
- The non-linear response of terpene accumulation to shallow mixing layers

The anthropogenic aromatic enhancement (10.50×) is consistent with urban Bangkok emissions accumulating under the stagnant boundary layer.

### Interpretation for H2

H2 is **supported**. SOAP and SOAS both increase substantially under stagnation. The OA residual increases 3.28× and its fraction of PM₂.₅ rises from 65% to 79%. Both biogenic terpene and anthropogenic aromatic precursors show large stagnation-driven accumulation. The 2-product scheme collapses the precursor diversity into SOAP→SOAS, so exact attribution to biogenic vs anthropogenic SOA is not possible from this run — this is a stated motivation for the full research design using source-tagged chemistry.

---

## 6. Oxidant Chemistry Under Stagnation — Hypothesis 3

**H3:** *Nighttime NO₃ radical chemistry plays a meaningful role in SOA formation during stagnation events.*

### OH Results (Dawn Chemistry)

| Variable | Stagnation | Ventilated | Ratio | p-value |
|---|---|---|---|---|
| OH (pptv, 07:00 LST) | elevated | baseline | **3.5×** | significant |
| NOx (NO+NO₂, ppb) | ~71 | ~19 | **3.64×** | significant |
| NO₂ (ppb) | elevated | baseline | ~3× | — |

**OH is HIGHER during stagnation** — counterintuitive at first glance. The mechanism is:

> **HO₂ + NO → OH + NO₂** (fast reaction at high [NO])

At 07:00 Bangkok local time (the wrfout snapshot time), the night-to-day photochemical transition is underway. During stagnation, accumulated NOx means very high NO concentrations. The HO₂ radical (present from overnight chemistry and early photolysis) rapidly converts to OH via the above reaction. The result is enhanced dawn OH despite the reduced mixing.

This finding is important: it means that during stagnation, daytime SOA formation via OH + VOC pathways is also enhanced, compounding the OA increase.

### NO₃ Results

| Variable | Stagnation | Ventilated | Ratio |
|---|---|---|---|
| NO₃ (pptv, 07:00 LST) | very low | baseline | **0.06×** |

**NO₃ is LOWER during stagnation** — also counterintuitive for H3. The mechanism:

> **NO + NO₃ → 2 NO₂** (titration reaction, fast)

High NO concentrations during stagnation (accumulated NOx overnight) rapidly destroy NO₃ via this titration. At 07:00 LST — the precise moment the wrfout file is written — NO is still high from overnight accumulation, and NO₃ is near zero.

**This does NOT disprove Hypothesis 3.** Nighttime NO₃ accumulation peaks during 20:00–02:00 LST, when NO has been depleted by oxidation and the NO₃ production by O₃+NO₂ proceeds without titration. The 07:00 LST snapshot completely misses this window.

### What Hypothesis 3 Actually Requires

H3 cannot be tested from daily 00:00 UTC snapshots. To test it, the full research design requires:
1. **Hourly WRF-GC output** (or at minimum 6-hourly), capturing the 20:00–02:00 LST NO₃ accumulation window
2. A full month or longer simulation period (seasonality matters)
3. Potentially: diagnostic output of nighttime NO₃ + VOC reaction rates directly

This is the most important structural limitation of the pilot simulation for the dissertation.

### NOx–OA Correlation

The scatter of daily NOx vs OA at Bangkok (figP5) shows **r = 0.987 (p ≈ 0)** — essentially perfect correlation across the 19 analysis days. This is a co-accumulation signal: under stagnation, both primary NOx and secondary OA accumulate together because the same meteorological forcing (low VC) drives both. The correlation does not prove causation (NOx → OA), but it shows that the meteorological forcing coherently affects both chemistry tracers — supporting H2 mechanistically.

---

## 7. Hypothesis-by-Hypothesis Assessment

| Hypothesis | Status | Key Evidence |
|---|---|---|
| **H1:** Stagnation (low VC) → PM₂.₅ accumulation | ✅ **Confirmed** | 2.73× PM₂.₅ (p=0.002), strong VC–PM₂.₅ inverse relationship |
| **H2:** Stagnation → enhanced SOA, higher OA fraction | ✅ **Confirmed** | OA 3.28× (p=0.001), OA fraction 65→79%, SOAP 3.27×, SOAS 2.44× |
| **H3:** Nighttime NO₃ chemistry drives stagnation-period SOA | ⚠️ **Cannot be tested** | NO₃ suppressed at 07:00 LST by NO titration; peak NO₃ window (20:00–02:00 LST) not observed |

---

## 8. Synthesis: What the Pilot Tells Us

The January 2025 WRF-GC pilot simulation provides a clear and internally consistent picture of how meteorological stagnation drives PM₂.₅ and organic aerosol variability over Thailand:

1. **The VC framework works.** The simple product of PBLH and wind speed captures the regime contrast effectively. A VC threshold of ~1800–4000 m²/s separates two meteorologically and chemically distinct populations of days.

2. **Organics dominate PM₂.₅ and are disproportionately enhanced.** OA is already 65% of PM₂.₅ during ventilated periods — unusually high and consistent with Southeast Asia's strong biogenic and biomass-burning influence. Under stagnation this rises to 79%. The implication is that SOA chemistry is more responsive to stagnation than inorganic chemistry (sulfate actually decreases).

3. **Both biogenic and anthropogenic SOA pathways respond.** MTPA/MTPO/LIMO (terpene precursors) increase 14.88× and AROMP4/5 (aromatic products) increase 10.50× under stagnation. Both pathways are active; the relative contributions to the OA residual require source tagging (a full research design objective).

4. **Daytime OH is enhanced during stagnation, not suppressed.** This is a critical nuance: the HO₂+NO→OH mechanism at dawn makes stagnation periods more oxidatively active in the morning. This enhances daytime SOA production via OH+VOC pathways on top of the accumulation effect. The full oxidant budget (24-hour) during stagnation vs ventilation cannot be resolved from daily snapshots.

5. **Nighttime chemistry is a gap, not a disproof.** The NO₃ result is physically consistent with the 07:00 LST snapshot time — NO titration destroys NO₃ at dawn. The nighttime NO₃ hypothesis requires hourly data and remains scientifically plausible. This gap motivates the most important methodological upgrade for the full research.

6. **NOx and OA are tightly correlated (r=0.987).** This co-accumulation signal shows that stagnation meteorology coherently forces the entire pollution chemistry system, not just individual species. The meteorology–chemistry coupling is real and measurable.

---

## 9. Limitations of the Pilot Simulation

| Limitation | Impact | How the Full Research Addresses It |
|---|---|---|
| Daily snapshots (07:00 LST only) | Cannot test H3 (nighttime NO₃); misses diurnal OA cycle | Hourly output planned for full simulation |
| 2-product simplified SOA scheme | SOAP→SOAS collapses biogenic/anthropogenic; no volatility distribution | Full research uses more complete scheme or diagnostic tagging |
| No source tagging | Cannot attribute OA to biogenic vs anthropogenic vs fire | Source-tagged tracers (e.g., ISORROPIA tags, tagged VOC oxidation) |
| Single month (January only) | Cannot assess seasonality (biomass burning, monsoon) | Full research spans multiple seasons |
| Pilot = no observation validation | Cannot assess model accuracy vs surface PM₂.₅ networks | Full research validates against AQMTHAI, PCD, MERRA-2 |
| 27 km resolution | Bangkok urban emissions smeared over large grid cell | Nested 9 km domain planned (WRF_GC_2 configuration) |

---

## 10. Implications for the Full Research Design

The pilot confirms three things that shape the dissertation:

1. **The meteorological forcing (VC) is the right organizing variable.** Build the full analysis around VC-classified composites. The threshold may need refinement (percentile-based rather than median) across a multi-year record.

2. **Hourly output is non-negotiable for H3.** The pilot demonstrates that daily snapshots cannot observe nocturnal NO₃ chemistry. The full simulation must output at least 3-hourly (preferably 1-hourly) chemistry fields.

3. **SOA attribution requires source tagging.** The pilot identifies that organics dominate the PM₂.₅ response and that both biogenic and anthropogenic precursor pathways amplify under stagnation. Separating their contributions is a core dissertation objective and requires either (a) a more complex SOA scheme with explicit biogenic/anthropogenic tracers or (b) sensitivity runs with emissions perturbed.

---

*Document generated from WRF-GC pilot simulation analysis. All statistics computed from Jan 10–28, 2025 analysis window (spin-up excluded). Bangkok grid point: j=74, i=89. Analysis script: `analysis/scripts/plot_proposal_defense.py`. Figures: `analysis/figures/proposal/`.*
