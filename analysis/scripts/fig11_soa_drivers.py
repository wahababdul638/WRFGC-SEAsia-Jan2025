
"""
fig11_soa_drivers.py — Investigating OH vs NO3 drivers of SOA production.
(a) SOA vs OH scatter
(b) SOA vs NO3 scatter
(c) VOC consumption vs SOA loading
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from config import C_STAG, C_VENT
from plot_helpers import savefig
from precompute import load_all

def plot(d):
    # MW of SOAS = 150. Convert to ug/m3
    soas_ugm3 = d.soas_ppb * d.n_air_bkk * 150.0 / 1e3 # soas_ppb is already ppmv*1e3

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.subplots_adjust(wspace=0.45, top=0.82, bottom=0.15)
    fig.suptitle('Chemical Drivers of Secondary Organic Aerosol (SOA) — Bangkok (13.75°N, 100.50°E)\n'
                 'WRF-GC January 2025  |  Analyzing OH (Daytime) vs NO3 (Stagnation/Nighttime) pathways', fontsize=13)

    # (a) SOA vs OH
    ax = axes[0]
    ax.scatter(d.oh_pptv[d.vent_mask], soas_ugm3[d.vent_mask], 
               c=C_VENT, s=60, edgecolors='white', lw=0.5, label='Ventilated', zorder=3)
    ax.scatter(d.oh_pptv[d.stag_mask], soas_ugm3[d.stag_mask], 
               c=C_STAG, s=60, marker='D', edgecolors='white', lw=0.5, label='Stagnation', zorder=3)
    
    slope, _, r, p, _ = stats.linregress(d.oh_pptv, soas_ugm3)
    ax.plot(np.linspace(0, d.oh_pptv.max()*1.05, 100), slope*np.linspace(0, d.oh_pptv.max()*1.05, 100), 'k--', alpha=0.5)
    
    ax.set_xlabel('OH (pptv)', fontsize=9)
    ax.set_ylabel('SOA in PM$_{2.5}$ (µg m$^{-3}$)', fontsize=9)
    ax.set_title('OH-driven Pathway (Photochemical)', fontsize=10, pad=8)
    ax.text(0.05, 0.95, f'r = {r:.3f}', transform=ax.transAxes, va='top', fontweight='bold')
    ax.legend(fontsize=7.5)
    ax.grid(True, alpha=0.2)

    # (b) SOA vs NO3
    ax = axes[1]
    ax.scatter(d.no3_pptv[d.vent_mask], soas_ugm3[d.vent_mask], 
               c=C_VENT, s=60, edgecolors='white', lw=0.5, label='Ventilated', zorder=3)
    ax.scatter(d.no3_pptv[d.stag_mask], soas_ugm3[d.stag_mask], 
               c=C_STAG, s=60, marker='D', edgecolors='white', lw=0.5, label='Stagnation', zorder=3)
    
    # We expect a weaker correlation at 07:00 LST due to NO titration
    slope, _, r, p, _ = stats.linregress(d.no3_pptv, soas_ugm3)
    ax.plot(np.linspace(0, d.no3_pptv.max()*1.05, 100), slope*np.linspace(0, d.no3_pptv.max()*1.05, 100), 'k--', alpha=0.5)

    ax.set_xlabel('NO$_3$ (pptv)', fontsize=9)
    ax.set_ylabel('SOA in PM$_{2.5}$ (µg m$^{-3}$)', fontsize=9)
    ax.set_title('NO$_3$-driven Pathway (Stagnation/Night)', fontsize=10, pad=8)
    ax.text(0.05, 0.95, f'r = {r:.3f}', transform=ax.transAxes, va='top', fontweight='bold')
    ax.grid(True, alpha=0.2)
    ax.text(0.95, 0.05, 'Correlation weakened at 07:00 LST\nby NO titration of NO$_3$', 
            transform=ax.transAxes, ha='right', va='bottom', fontsize=7.5, style='italic', color='#555')

    # (c) VOC Consumption: Precursors (MTP + Aromatics) vs SOA
    ax = axes[2]
    total_voc = d.mtp_ppb + d.arom_ppb
    ax.scatter(total_voc[d.vent_mask], soas_ugm3[d.vent_mask],
               c=C_VENT, s=60, edgecolors='white', lw=0.5, label='Ventilated', zorder=3)
    ax.scatter(total_voc[d.stag_mask], soas_ugm3[d.stag_mask],
               c=C_STAG, s=60, marker='D', edgecolors='white', lw=0.5, label='Stagnation', zorder=3)

    slope_c, intercept_c, r_c, p_c, _ = stats.linregress(total_voc, soas_ugm3)
    xfit_c = np.linspace(total_voc.min(), total_voc.max() * 1.05, 100)
    ax.plot(xfit_c, slope_c * xfit_c + intercept_c, 'k--', alpha=0.5)

    ax.set_xlabel('VOC Precursors (MTP + Aromatics, ppb)', fontsize=9)
    ax.set_ylabel('SOA in PM$_{2.5}$ (µg m$^{-3}$)', fontsize=9)
    ax.set_title('Precursor Co-accumulation', fontsize=10, pad=8)
    ax.grid(True, alpha=0.2)
    ax.text(0.05, 0.95, f'r = {r_c:.3f}', transform=ax.transAxes, va='top', fontweight='bold')
    ax.text(0.05, 0.05,
            'Stagnation co-accumulates precursors\nand aerosol — both regimes on the\nsame regression line suggests\ncommon transport/accumulation control.',
            transform=ax.transAxes, ha='left', va='bottom', fontsize=7.5, style='italic', color='#8e44ad')

    savefig(fig, 'fig11_soa_chemistry_drivers.png')

if __name__ == '__main__':
    plot(load_all())
