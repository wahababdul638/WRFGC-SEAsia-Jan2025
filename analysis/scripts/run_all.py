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
import fig09_stagnation_chemistry
import fig10_oxidant_chemistry
import fig11_soa_drivers
import fig12_mechanism_proof
import fig13_intuitive_summary
import fig14_vertical_mechanisms

if __name__ == '__main__':
    print("=== WRF-GC January 2025 Analysis Figures ===\n")
    d = load_all()

    fig01_timeseries.plot(d)
    fig02_aerosol_composition.plot(d)
    fig03_oxidants.plot(d)
    fig04_vc_scatter.plot(d)
    fig05_nox_oh_chemistry.plot(d)
    fig06_spatial_maps.plot(d)
    fig07_summary_bars.plot(d)
    fig08_soa_precursors.plot(d)
    fig09_stagnation_chemistry.plot(d)
    fig10_oxidant_chemistry.plot(d)
    fig11_soa_drivers.plot(d)
    fig12_mechanism_proof.plot(d)
    fig13_intuitive_summary.plot(d)
    fig14_vertical_mechanisms.plot(d)

    print("\nAll figures complete.")
