"""
fig04_vc_scatter.py — Scatter plots of ventilation coefficient (VC) vs
PM2.5 and total SOA proxy, coloured by stagnation / ventilated regime.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from config import C_STAG, C_VENT
from plot_helpers import savefig
from precompute import load_all


def plot(d):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.subplots_adjust(wspace=0.30, top=0.85, bottom=0.14)
    fig.suptitle('Ventilation Coefficient vs Aerosol Loading — Bangkok (13.75°N, 100.50°E)\n'
                 'WRF-GC January 2025  |  Jan 10–28 analysis window', fontsize=11)

    pairs = [
        (d.vc_bkk_ts, d.pm25_bkk,    'PM$_{2.5}$ (µg m$^{-3}$)',  'Surface PM$_{2.5}$'),
        (d.vc_bkk_ts, d.soatot_ppb,  'SOA precursor (ppb)',
         'SOAP + SOAS + SOAIE + SOAGX'),
    ]

    for ax, (x, y, ylabel, title) in zip(axes, pairs):
        ax.scatter(x[d.vent_mask], y[d.vent_mask],
                   c=C_VENT, s=60, label='Ventilated', edgecolors='white', lw=0.5,
                   alpha=0.9, zorder=3)
        ax.scatter(x[d.stag_mask], y[d.stag_mask],
                   c=C_STAG, s=60, marker='D', label='Stagnation',
                   edgecolors='white', lw=0.5, alpha=0.9, zorder=3)

        slope, intercept, r, p, _ = stats.linregress(x, y)
        xfit = np.linspace(x.min() * 0.95, x.max() * 1.05, 100)
        ax.plot(xfit, slope * xfit + intercept, 'k--', lw=1.2, alpha=0.7)
        ax.text(0.97, 0.95, f'r = {r:.3f}\np = {p:.4f}\nn = {len(x)}',
                transform=ax.transAxes, ha='right', va='top', fontsize=9,
                bbox=dict(facecolor='white', alpha=0.85, pad=3, lw=0.5, edgecolor='#bbb'))

        ax.set_xlabel('Ventilation Coefficient (m² s$^{-1}$)', fontsize=9)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.set_title(title, fontsize=10, pad=6)
        ax.legend(fontsize=8, framealpha=0.8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.25)

    savefig(fig, 'fig04_vc_scatter.png')


if __name__ == '__main__':
    plot(load_all())
