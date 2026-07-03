"""
fig01_timeseries.py — Multi-panel time series: PM2.5, SOA precursors, oxidants, VC.
Shaded orange = stagnation days (VC ≤ median Thailand VC).
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from config import C_STAG, C_VENT
from plot_helpers import shade_stagnation, savefig
from precompute import load_all


def plot(d):
    fig, axes = plt.subplots(4, 1, figsize=(11, 12), sharex=True)
    fig.subplots_adjust(hspace=0.15, top=0.90, bottom=0.07)
    fig.suptitle('WRF-GC January 2025 — Bangkok (13.75°N, 100.50°E)\n'
                 'Daily surface chemistry and boundary-layer mixing (Jan 10–28)',
                 fontsize=12, y=0.97)

    for ax in axes:
        shade_stagnation(ax, d.dates_late, d.stag_mask)
        ax.grid(True, alpha=0.25, lw=0.5, zorder=1)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    # (a) PM2.5
    ax = axes[0]
    ax.plot(d.dates_late, d.pm25_bkk, 'o-', color='#c0392b', lw=1.8, ms=4, zorder=3)
    ax.axhline(15,   color='#7f8c8d', lw=0.9, ls='--', label='WHO 24-hr (15 µg m⁻³)')
    ax.axhline(37.5, color='#7f8c8d', lw=0.9, ls=':',  label='TH NAAQS (37.5 µg m⁻³)')
    ax.set_ylabel('PM$_{2.5}$ (µg m$^{-3}$)', fontsize=9)
    ax.legend(fontsize=7, loc='upper left', framealpha=0.7)
    ax.text(0.01, 0.88, '(a)', transform=ax.transAxes, fontsize=9, fontweight='bold')
    ax.text(0.76, 0.92, '← Stagnation period (Jan 19–28)',
            transform=ax.transAxes, fontsize=7.5, color=C_STAG, style='italic')

    # (b) SOAP and SOAS proxy
    ax = axes[1]
    ax.fill_between(d.dates_late, d.soap_ppb, 0, alpha=0.60, color='#8e44ad',
                    label='SOAP (gas-phase SOA precursor)')
    ax.fill_between(d.dates_late, d.soas_ppb, 0, alpha=0.60, color='#27ae60',
                    label='SOAS (SOA aerosol in PM$_{2.5}$)')
    ax.set_ylabel('SOA tracer (ppb)', fontsize=9)
    ax.legend(fontsize=7, loc='upper left', framealpha=0.7)
    ax.text(0.01, 0.88, '(b)', transform=ax.transAxes, fontsize=9, fontweight='bold')

    # (c) OH and NO3 / N2O5
    ax  = axes[2]
    ax2 = ax.twinx()
    ax.plot(d.dates_late,  d.oh_pptv,   's-', color='#f39c12', lw=1.6, ms=4, label='OH (pptv)', zorder=3)
    ax2.plot(d.dates_late, d.no3_pptv,  '^-', color='#16a085', lw=1.6, ms=4, ls='--',
             label='NO$_3$ (pptv)', zorder=3)
    ax2.plot(d.dates_late, d.n2o5_pptv, 'v-', color='#2980b9', lw=1.2, ms=3, ls=':',
             label='N$_2$O$_5$ (pptv)', alpha=0.8, zorder=3)
    ax.set_ylabel('OH (pptv)', fontsize=9, color='#f39c12')
    ax2.set_ylabel('NO$_3$, N$_2$O$_5$ (pptv)', fontsize=9, color='#16a085')
    lines1, lbs1 = ax.get_legend_handles_labels()
    lines2, lbs2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, lbs1 + lbs2, fontsize=7, loc='upper left', framealpha=0.7)
    ax.text(0.01, 0.88, '(c)', transform=ax.transAxes, fontsize=9, fontweight='bold')
    ax2.spines['top'].set_visible(False)

    # (d) Ventilation coefficient — domain-mean (Thailand) VC used for regime classification
    ax = axes[3]
    ax.fill_between(d.dates_late, d.vc_th_ts, d.vc_median,
                    where=(d.vc_th_ts <= d.vc_median),
                    alpha=0.4, color=C_STAG, label='Stagnation')
    ax.fill_between(d.dates_late, d.vc_th_ts, d.vc_median,
                    where=(d.vc_th_ts > d.vc_median),
                    alpha=0.4, color=C_VENT, label='Ventilated')
    ax.plot(d.dates_late, d.vc_th_ts, 'k-', lw=1.5, zorder=3, label='Thailand domain-mean VC')
    ax.plot(d.dates_late, d.vc_bkk_ts, '--', color='#95a5a6', lw=1.0, zorder=2,
            label=f'Bangkok point VC (urban, lower)')
    ax.axhline(d.vc_median, color='gray', lw=1.0, ls='--',
               label=f'Classification threshold = {d.vc_median:.0f} m² s⁻¹')
    ax.set_ylabel('Vent. Coeff. (m² s$^{-1}$)', fontsize=9)
    ax.legend(fontsize=7, loc='upper right', framealpha=0.7)
    ax.text(0.01, 0.88, '(d)', transform=ax.transAxes, fontsize=9, fontweight='bold')
    ax.text(0.01, 0.04,
            'Classification based on Thailand domain-mean VC (black line).\n'
            'Bangkok urban point VC (grey dashed) is 5–7× lower due to shallow morning BL.',
            transform=ax.transAxes, fontsize=6.5, style='italic', color='#666')

    xfmt = mdates.DateFormatter('%d %b')
    axes[-1].xaxis.set_major_formatter(xfmt)
    axes[-1].xaxis.set_major_locator(mdates.DayLocator(interval=2))
    plt.setp(axes[-1].xaxis.get_majorticklabels(), rotation=30, ha='right', fontsize=8)
    for ax in axes[:-1]:
        ax.yaxis.set_tick_params(labelsize=8)

    savefig(fig, 'fig01_timeseries.png')


if __name__ == '__main__':
    plot(load_all())
