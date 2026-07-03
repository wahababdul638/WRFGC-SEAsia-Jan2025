"""
fig_bangkok_pm25_vc.py — Daily PM2.5 and Ventilation Coefficient at Bangkok grid point.

Both diagnostics are at the Bangkok grid point (13.75°N, 100.50°E, j=74, i=89).
VC = PBLH × |Wind10m|  (m² s⁻¹), computed at the Bangkok cell.
PM2.5 in µg m⁻³.

Output: fig_bangkok_pm25_vc.png
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

from config import FIG_DIR
from plot_helpers import savefig
from precompute import load_all


def plot(d):
    fig, ax1 = plt.subplots(figsize=(10, 5))
    fig.subplots_adjust(top=0.88, bottom=0.22, left=0.10, right=0.90)
    fig.suptitle(
        'WRF-GC January 2025 — Bangkok Grid Point (13.75°N, 100.50°E)\n'
        'Daily surface PM$_{2.5}$ and Ventilation Coefficient',
        fontsize=12)

    ax2 = ax1.twinx()

    # ── PM2.5 (left axis, red) ────────────────────────────────────────────────
    l1, = ax1.plot(d.dates_late, d.pm25_bkk, 'o-', color='#c0392b', lw=2.0, ms=5,
                   label='PM$_{2.5}$ (µg m$^{-3}$)', zorder=3)
    ax1.axhline(15,   color='#c0392b', lw=0.8, ls='--', alpha=0.5,
                label='WHO 24-hr (15 µg m⁻³)')
    ax1.axhline(37.5, color='#c0392b', lw=0.8, ls=':',  alpha=0.5,
                label='TH NAAQS (37.5 µg m⁻³)')
    ax1.set_ylabel('PM$_{2.5}$ (µg m$^{-3}$)', fontsize=10, color='#c0392b')
    ax1.tick_params(axis='y', labelcolor='#c0392b')

    # ── VC at Bangkok (right axis, green) ─────────────────────────────────────
    vc_bkk_median = np.median(d.vc_bkk_ts)
    l2, = ax2.plot(d.dates_late, d.vc_bkk_ts, 's--', color='#27ae60', lw=2.0, ms=5,
                   label=f'VC (m² s$^{{-1}}$)', zorder=3)
    ax2.set_ylabel('Ventilation Coefficient (m² s$^{-1}$)', fontsize=10, color='#27ae60')
    ax2.tick_params(axis='y', labelcolor='#27ae60')

    # ── Formatting ────────────────────────────────────────────────────────────
    ax1.grid(True, alpha=0.20, lw=0.5)
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)

    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=0, ha='center', fontsize=9)
    ax1.set_xlabel('January 2025', fontsize=10)

    lines = [l1, l2,
             plt.Line2D([0], [0], color='#c0392b', lw=0.8, ls='--', alpha=0.5),
             plt.Line2D([0], [0], color='#c0392b', lw=0.8, ls=':',  alpha=0.5)]
    labels = ['PM$_{2.5}$ (µg m$^{-3}$)', 'VC (m² s$^{-1}$)',
              'WHO 24-hr guideline (15 µg m⁻³)', 'Thailand NAAQS (37.5 µg m⁻³)']
    ax1.legend(lines, labels, fontsize=8, ncol=2, framealpha=0.90,
               loc='upper center', bbox_to_anchor=(0.5, -0.22))

    savefig(fig, 'fig_bangkok_pm25_vc.png')


if __name__ == '__main__':
    plot(load_all())
