"""
fig07_summary_bars.py — 2×3 summary bar chart comparing key atmospheric
variables between stagnation and ventilated periods, with t-test significance.
"""

import matplotlib.pyplot as plt

from plot_helpers import bar2, savefig
from precompute import load_all


def plot(d):
    n_s = d.stag_mask.sum()
    n_v = d.vent_mask.sum()

    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    fig.subplots_adjust(hspace=0.40, wspace=0.35, top=0.88, bottom=0.10)
    fig.suptitle('Summary: Bangkok Stagnation vs Ventilation — WRF-GC January 2025\n'
                 'All variables at surface (07:00 LST); error bars = ±1σ', fontsize=11)

    bar2(axes[0, 0], d.pm25_bkk[d.stag_mask], d.pm25_bkk[d.vent_mask],
         'µg m$^{-3}$', 'Surface PM$_{2.5}$', n_s, n_v)

    bar2(axes[0, 1], d.oa_ugm3[d.stag_mask], d.oa_ugm3[d.vent_mask],
         'µg m$^{-3}$', 'Organic Aerosol (residual)', n_s, n_v)

    bar2(axes[0, 2], d.bc_ugm3[d.stag_mask], d.bc_ugm3[d.vent_mask],
         'µg m$^{-3}$', 'Black Carbon', n_s, n_v)

    bar2(axes[1, 0], d.oh_pptv[d.stag_mask], d.oh_pptv[d.vent_mask],
         'pptv', 'OH radical', n_s, n_v)

    bar2(axes[1, 1], d.no3_pptv[d.stag_mask], d.no3_pptv[d.vent_mask],
         'pptv', 'NO$_3$ radical (07:00 LST)', n_s, n_v)

    bar2(axes[1, 2], d.nox_ppb[d.stag_mask], d.nox_ppb[d.vent_mask],
         'ppb', 'NOx (NO + NO$_2$)', n_s, n_v)

    savefig(fig, 'figP7_summary_bars.png')


if __name__ == '__main__':
    plot(load_all())
