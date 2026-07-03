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
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    fig.subplots_adjust(hspace=0.12, top=0.90, bottom=0.10)
    fig.suptitle(
        'WRF-GC January 2025 — Bangkok Grid Point (13.75°N, 100.50°E)\n'
        'Daily surface PM$_{2.5}$ and Ventilation Coefficient',
        fontsize=12)

    for ax in (ax1, ax2):
        ax.grid(True, alpha=0.25, lw=0.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    # ── (a) PM2.5 ──────────────────────────────────────────────────────────────
    ax1.plot(d.dates_late, d.pm25_bkk, 'o-', color='#c0392b', lw=2.0, ms=5,
             label='Bangkok PM$_{2.5}$', zorder=3)
    ax1.axhline(15,   color='#7f8c8d', lw=1.0, ls='--', label='WHO 24-hr guideline (15 µg m⁻³)')
    ax1.axhline(37.5, color='#7f8c8d', lw=1.0, ls=':',  label='Thailand NAAQS (37.5 µg m⁻³)')
    ax1.set_ylabel('PM$_{2.5}$ (µg m$^{-3}$)', fontsize=10)
    ax1.legend(fontsize=8, loc='upper left', framealpha=0.8)
    ax1.text(0.01, 0.93, '(a)', transform=ax1.transAxes, fontsize=10, fontweight='bold')

    # ── (b) VC at Bangkok ─────────────────────────────────────────────────────
    vc_bkk_median = np.median(d.vc_bkk_ts)
    ax2.plot(d.dates_late, d.vc_bkk_ts, 'o-', color='#27ae60', lw=2.0, ms=5,
             label='Bangkok VC = PBLH × |Wind$_{10m}$|', zorder=3)
    ax2.axhline(vc_bkk_median, color='#27ae60', lw=1.0, ls='--', alpha=0.7,
                label=f'Bangkok VC median = {vc_bkk_median:.0f} m² s⁻¹')
    ax2.set_ylabel('Ventilation Coefficient (m² s$^{-1}$)', fontsize=10)
    ax2.legend(fontsize=8, loc='upper right', framealpha=0.8)
    ax2.text(0.01, 0.93, '(b)', transform=ax2.transAxes, fontsize=10, fontweight='bold')

    # x-axis formatting
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    ax2.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=30, ha='right', fontsize=9)

    savefig(fig, 'fig_bangkok_pm25_vc.png')


if __name__ == '__main__':
    plot(load_all())
