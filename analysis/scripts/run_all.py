"""
run_all.py — Master runner: pre-compute shared data once, then generate all 8 figures.

Usage:
    conda run -n ewrf python analysis/scripts/run_all.py

Individual figures can also be regenerated on their own:
    conda run -n ewrf python analysis/scripts/fig01_timeseries.py
"""

from precompute import load_all

import fig01_timeseries
import fig02_aerosol_composition
import fig03_oxidants
import fig04_vc_scatter
import fig05_nox_oh_chemistry
import fig06_spatial_maps
import fig07_summary_bars
import fig08_soa_precursors

if __name__ == '__main__':
    print("=== WRF-GC Proposal Defense Figures ===\n")
    d = load_all()

    fig01_timeseries.plot(d)
    fig02_aerosol_composition.plot(d)
    fig03_oxidants.plot(d)
    fig04_vc_scatter.plot(d)
    fig05_nox_oh_chemistry.plot(d)
    fig06_spatial_maps.plot(d)
    fig07_summary_bars.plot(d)
    fig08_soa_precursors.plot(d)

    print("\nAll figures complete.")
