
"""
fig12_mechanism_proof.py — The ultimate proof for the thesis objective.
(a) The Oxidant Seesaw: NO3 suppression vs OH enhancement.
(b) Photochemical Recycling Evidence: HO2/OH ratio vs NO.
(c) Regime Impact: Organic Aerosol (OA) mass fraction shift.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

from config import C_STAG, C_VENT
from plot_helpers import savefig
from precompute import load_all

def plot(d):
    # Calculations
    oa_fraction = (d.oa_ugm3 / np.maximum(d.pm25_bkk, 1.0)) * 100
    ho2_oh_ratio = d.ho2_pptv / np.maximum(d.oh_pptv, 1e-10)

    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
    fig.subplots_adjust(wspace=0.45, top=0.82, bottom=0.15)
    fig.suptitle('Objective 3: Boundary Layer–Chemistry Feedback — Stagnation-Induced "Oxidant Seesaw"\n'
                 'Bangkok (07:00 LST) — Elevated NO suppresses NO₃ while recycling OH via HO₂ + NO → OH + NO₂', fontsize=12, fontweight='bold')

    # (a) The Oxidant Seesaw
    ax = axes[0]
    ax2 = ax.twinx()
    
    # Left axis: OH
    l1 = ax.scatter(d.no_ppb, d.oh_pptv, c=d.oh_pptv, cmap='YlOrRd', s=80, edgecolors='k', lw=0.5, label='OH (pptv)', zorder=3)
    ax.set_ylabel('OH (pptv)', color='#c0392b', fontweight='bold')
    
    # Right axis: NO3
    l2 = ax2.scatter(d.no_ppb, d.no3_pptv, marker='D', c=d.no3_pptv, cmap='Greens_r', s=60, edgecolors='k', lw=0.5, label='NO$_3$ (pptv)', zorder=3)
    ax2.set_ylabel('NO$_3$ (pptv)', color='#16a085', fontweight='bold')
    
    ax.set_xlabel('Traffic Emissions: NO (ppb)', fontsize=10)
    ax.set_title('(a)  The Oxidant Seesaw\nHigh NO → destroys NO₃ but produces OH', fontsize=10, pad=8)
    ax.grid(True, alpha=0.15)
    
    ax.text(0.95, 0.95, 'High NO destroys NO$_3$\nbut produces OH', 
            transform=ax.transAxes, ha='right', va='top', fontsize=7.5, style='italic',
            bbox=dict(facecolor='white', alpha=0.8, pad=2))

    # (b) Photochemical Recycling Evidence
    ax = axes[1]
    ax.scatter(d.no_ppb[d.vent_mask], ho2_oh_ratio[d.vent_mask], c=C_VENT, s=70, label='Ventilated', zorder=3)
    ax.scatter(d.no_ppb[d.stag_mask], ho2_oh_ratio[d.stag_mask], c=C_STAG, marker='D', s=70, label='Stagnation', zorder=3)
    
    # Trend line for HO2/OH vs NO
    mask = np.isfinite(ho2_oh_ratio)
    slope, intercept, r, p, _ = stats.linregress(d.no_ppb[mask], ho2_oh_ratio[mask])
    ax.plot(np.sort(d.no_ppb), slope * np.sort(d.no_ppb) + intercept, 'k--', alpha=0.4)
    
    ax.set_yscale('log')
    ax.set_xlabel('NO (ppb)', fontsize=10)
    ax.set_ylabel('HO$_2$ / OH Ratio', fontsize=10)
    ax.set_title('(b)  Photochemical Recycling Efficiency\nHO₂/OH ratio vs traffic NO', fontsize=10, pad=8)
    ax.grid(True, which="both", alpha=0.1)
    ax.text(0.95, 0.05, 'Lower HO$_2$/OH = Faster Recycling\n(HO$_2$ + NO → OH + NO$_2$)', 
            transform=ax.transAxes, ha='right', va='bottom', fontsize=7.5, style='italic',
            bbox=dict(facecolor='#e8f6f3', alpha=0.8, pad=2))

    # (c) Impact on Aerosol Composition
    ax = axes[2]
    # OA fraction vs NO
    ax.scatter(d.no_ppb[d.vent_mask], oa_fraction[d.vent_mask], c=C_VENT, s=70, label='Ventilated', zorder=3)
    ax.scatter(d.no_ppb[d.stag_mask], oa_fraction[d.stag_mask], c=C_STAG, marker='D', s=70, label='Stagnation', zorder=3)
    
    ax.set_xlabel('NO (ppb)', fontsize=10)
    ax.set_ylabel('Organic Mass Fraction of PM$_{2.5}$ (%)', fontsize=10)
    ax.set_title('(c)  Organic Aerosol Fraction Shift\nStagnation effect on PM₂.₅ composition', fontsize=10, pad=8)
    ax.grid(True, alpha=0.2)
    
    # Significance test
    frac_s, frac_v = oa_fraction[d.stag_mask], oa_fraction[d.vent_mask]
    t, p = stats.ttest_ind(frac_s, frac_v)
    ax.text(0.5, 0.92, f'Stagnation shift: +{frac_s.mean()-frac_v.mean():.1f}% OA\np = {p:.4f}', 
            transform=ax.transAxes, ha='center', fontsize=9, fontweight='bold', color='#8e44ad')

    savefig(fig, 'fig12_mechanism_proof.png')

if __name__ == '__main__':
    plot(load_all())
