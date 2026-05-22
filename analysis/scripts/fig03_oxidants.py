"""
fig03_oxidants.py — Box plots comparing OH, NO3, and N2O5 between
stagnation and ventilated regimes.

Note: all snapshots are at 07:00 LST (00:00 UTC). NO3 appears lower during
stagnation because accumulated NO rapidly titrates it (NO + NO3 → 2NO2).
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from config import C_STAG, C_VENT
from plot_helpers import savefig
from precompute import load_all


def plot(d):
    fig, axes = plt.subplots(1, 3, figsize=(13, 5))
    fig.subplots_adjust(wspace=0.35, top=0.85, bottom=0.18)
    fig.suptitle('Atmospheric Oxidant Concentrations — Bangkok (13.75°N, 100.50°E)\n'
                 'WRF-GC January 2025  |  Stagnation vs Ventilated  |  07:00 LST snapshots',
                 fontsize=11)

    oxidants = [
        ('OH',          d.oh_pptv,   'OH (pptv)',          '#f39c12'),
        ('NO$_3$',      d.no3_pptv,  'NO$_3$ (pptv)',      '#16a085'),
        ('N$_2$O$_5$',  d.n2o5_pptv, 'N$_2$O$_5$ (pptv)', '#2980b9'),
    ]

    for ax, (name, ts, ylabel, color) in zip(axes, oxidants):
        stag_data = ts[d.stag_mask]
        vent_data = ts[d.vent_mask]

        bplot = ax.boxplot(
            [stag_data, vent_data], positions=[1, 2], widths=0.55, patch_artist=True,
            medianprops=dict(color='white', lw=2),
            whiskerprops=dict(lw=1.2), capprops=dict(lw=1.2),
            flierprops=dict(marker='o', ms=4, alpha=0.7))

        for patch, c in zip(bplot['boxes'], [C_STAG, C_VENT]):
            patch.set_facecolor(c); patch.set_alpha(0.75)

        for x_pos, data, c in [(1, stag_data, C_STAG), (2, vent_data, C_VENT)]:
            ax.scatter(np.random.normal(x_pos, 0.07, len(data)), data,
                       color=c, alpha=0.7, s=25, zorder=3)

        t_stat, p_val = stats.ttest_ind(stag_data, vent_data)
        sig   = '***' if p_val < 0.001 else ('**' if p_val < 0.01 else ('*' if p_val < 0.05 else 'ns'))
        y_top = max(np.concatenate([stag_data, vent_data])) * 1.12
        ax.plot([1, 2], [y_top, y_top], 'k-', lw=0.8)
        ax.text(1.5, y_top * 1.02, f'p={p_val:.3f} {sig}', ha='center', fontsize=8)

        ratio = stag_data.mean() / max(vent_data.mean(), 1e-30)
        ax.text(0.98, 0.05, f'Stag/Vent = {ratio:.2f}×',
                transform=ax.transAxes, ha='right', fontsize=8.5, color='#333333',
                bbox=dict(facecolor='#fffde7', alpha=0.8, pad=2, lw=0.5, edgecolor='#bbb'))

        ax.set_xticks([1, 2])
        ax.set_xticklabels([f'Stagnation\n(n={d.stag_mask.sum()})',
                            f'Ventilated\n(n={d.vent_mask.sum()})'], fontsize=9)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.set_title(name, fontsize=11, pad=6)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, axis='y', alpha=0.3)

    fig.text(0.5, 0.03,
             'Note: snapshots at 07:00 LST capture end-of-night chemistry. '
             'High NO during stagnation titrates NO₃ (NO + NO₃ → 2NO₂), '
             'suppressing NO₃ at this hour.\n'
             'Peak NO₃ accumulation occurs 20:00–02:00 LST and cannot be observed '
             'from daily 00:00 UTC output alone.',
             ha='center', fontsize=7.5, style='italic', color='#555')

    savefig(fig, 'fig03_oxidants.png')


if __name__ == '__main__':
    plot(load_all())
