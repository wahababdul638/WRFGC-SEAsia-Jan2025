"""
fig05_nox_oh_chemistry.py — Two scatter plots exploring NOx–OH–OA relationships.

Left:  NO2 vs OH  (OH is HIGHER during stagnation via HO2 + NO → OH + NO2)
Right: NOx vs OA  (tight co-accumulation, r ≈ 0.987, supports Hypothesis 2)
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from config import C_STAG, C_VENT
from plot_helpers import savefig
from precompute import load_all


def plot(d):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.subplots_adjust(wspace=0.32, top=0.85, bottom=0.14)
    fig.suptitle('NOx – OH Chemistry: Stagnation vs Ventilation Regimes\n'
                 'WRF-GC January 2025  |  Bangkok grid point', fontsize=11)

    # Left: NO2 vs OH
    ax = axes[0]
    ax.scatter(d.no2_ppb[d.vent_mask], d.oh_pptv[d.vent_mask],
               c=C_VENT, s=70, label='Ventilated', edgecolors='white', lw=0.5, zorder=3)
    ax.scatter(d.no2_ppb[d.stag_mask], d.oh_pptv[d.stag_mask],
               c=C_STAG, s=70, marker='D', label='Stagnation',
               edgecolors='white', lw=0.5, zorder=3)
    ax.set_xlabel('NO$_2$ (ppb)', fontsize=9)
    ax.set_ylabel('OH (pptv)', fontsize=9)
    ax.set_title('NO$_2$ vs OH — regime colour', fontsize=10, pad=6)
    ax.legend(fontsize=8, framealpha=0.8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, alpha=0.25)
    ax.text(0.97, 0.05,
            'At 07:00 LST: high NO during stagnation\n'
            'promotes OH via HO₂ + NO → OH + NO₂\n'
            '(NOx 3.6× and OH 3.5× higher during stagnation)',
            transform=ax.transAxes, ha='right', fontsize=7.5, color='#333',
            style='italic',
            bbox=dict(facecolor='#fffde7', alpha=0.85, pad=2, lw=0.5, edgecolor='#bbb'))

    # Right: NOx vs OA
    ax = axes[1]
    ax.scatter(d.nox_ppb[d.vent_mask], d.oa_ugm3[d.vent_mask],
               c=C_VENT, s=70, label='Ventilated', edgecolors='white', lw=0.5, zorder=3)
    ax.scatter(d.nox_ppb[d.stag_mask], d.oa_ugm3[d.stag_mask],
               c=C_STAG, s=70, marker='D', label='Stagnation',
               edgecolors='white', lw=0.5, zorder=3)

    slope, intercept, r, p, _ = stats.linregress(d.nox_ppb, d.oa_ugm3)
    xfit = np.linspace(d.nox_ppb.min() * 0.9, d.nox_ppb.max() * 1.05, 100)
    ax.plot(xfit, slope * xfit + intercept, 'k--', lw=1.2, alpha=0.7)
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
            'NOx and OA co-accumulate under stagnation:\ncombustion emissions '
            'trapped in shallow PBL\n→ supports Hypothesis 2',
            transform=ax.transAxes, ha='right', fontsize=7.5, color='#8e44ad',
            style='italic',
            bbox=dict(facecolor='#fef9f0', alpha=0.85, pad=2, lw=0.5, edgecolor='#bbb'))

    savefig(fig, 'figP5_nox_oh_chemistry.png')


if __name__ == '__main__':
    plot(load_all())
