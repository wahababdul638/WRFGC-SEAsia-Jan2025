"""
fig10_oxidant_chemistry.py — Old Objective 3 Assessment: NO₃ Radical Pathway

Original H3 proposed that stagnation enhances SOA via the NO₃ + biogenic VOC
nighttime pathway. This figure shows what the available data reveals:

FINDING: NO₃ and N₂O₅ are LOWER during stagnation, not higher.
MECHANISM: Accumulated NO under stagnation directly titrates the NO₃ radical:
    NO + NO₃ → 2NO₂  (direct titration)
This is the "urban NOx penalty" — high traffic NOx eliminates the nighttime
biogenic pathway in Bangkok.

DATA LIMITATION: Even if NO₃ were elevated, the 2-product SOA scheme
(complex_SOA: false) cannot attribute SOA to specific oxidant channels.
Further simulation with complex_SOA: true is required for NO₃-SOA attribution.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from config import C_STAG, C_VENT
from plot_helpers import savefig, shade_stagnation, bar2
from precompute import load_all
import matplotlib.dates as mdates


def plot(d):
    n_s, n_v = int(d.stag_mask.sum()), int(d.vent_mask.sum())

    fig, axes = plt.subplots(1, 3, figsize=(16, 5.5))
    fig.subplots_adjust(wspace=0.42, top=0.80, bottom=0.20)
    fig.suptitle(
        'Old Objective 3: NO₃ Radical Pathway Assessment — Bangkok (13.75°N, 100.50°E)\n'
        'WRF-GC January 2025  |  NO titration suppresses nighttime NO₃ during stagnation',
        fontsize=12, fontweight='bold')

    for ax in axes:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.20)

    # ── (a) NO vs NO₃ scatter — titration curve ───────────────────────────────
    ax = axes[0]
    ax.scatter(d.no_ppb[d.vent_mask], d.no3_pptv[d.vent_mask],
               c=C_VENT, s=70, edgecolors='white', lw=0.5, label='Ventilated', zorder=3)
    ax.scatter(d.no_ppb[d.stag_mask], d.no3_pptv[d.stag_mask],
               c=C_STAG, s=70, marker='D', edgecolors='white', lw=0.5, label='Stagnation', zorder=3)

    slope, intercept, r, p, _ = stats.linregress(d.no_ppb, d.no3_pptv)
    xfit = np.linspace(0, d.no_ppb.max() * 1.05, 100)
    ax.plot(xfit, slope * xfit + intercept, 'k--', lw=1.2, alpha=0.6)

    ax.set_xlabel('NO (ppb)', fontsize=9)
    ax.set_ylabel('NO₃ radical (pptv)', fontsize=9)
    ax.set_title('(a)  NO titration of NO₃ radical\nNO + NO₃ → 2NO₂', fontsize=9.5, pad=8)
    ax.legend(fontsize=7.5, framealpha=0.8)
    ax.text(0.05, 0.95, f'r = {r:.3f}  (p = {p:.3f})',
            transform=ax.transAxes, va='top', fontsize=8.5, fontweight='bold')
    ax.text(0.96, 0.95,
            'High NO during stagnation\nconsumes NO₃ radical\n(urban NOx penalty)',
            transform=ax.transAxes, ha='right', va='top', fontsize=7.5, style='italic',
            bbox=dict(facecolor='#fef9e7', alpha=0.85, pad=2, lw=0.5, edgecolor='#bbb'))

    # ── (b) NO₃ stag vs vent boxplot ─────────────────────────────────────────
    ax = axes[1]
    no3_s = d.no3_pptv[d.stag_mask]
    no3_v = d.no3_pptv[d.vent_mask]

    bplot = ax.boxplot([no3_s, no3_v], positions=[1, 2], widths=0.55,
                       patch_artist=True, medianprops=dict(color='white', lw=2.5),
                       flierprops=dict(marker='o', markersize=4, alpha=0.5))
    for patch, c in zip(bplot['boxes'], [C_STAG, C_VENT]):
        patch.set_facecolor(c)
        patch.set_alpha(0.78)

    t, p = stats.ttest_ind(no3_s, no3_v)
    sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else 'ns'))
    ax.set_xticks([1, 2])
    ax.set_xticklabels([f'Stagnation\n(n={n_s})', f'Ventilated\n(n={n_v})'], fontsize=9)
    ax.set_ylabel('NO₃ radical (pptv)', fontsize=9)
    ax.set_title('(b)  NO₃ radical: stagnation vs ventilated\n'
                 'NO₃ is LOWER during stagnation (NO titration)', fontsize=9.5, pad=8)
    ax.text(0.5, 0.96, f'p = {p:.3f}  {sig}',
            transform=ax.transAxes, ha='center', fontsize=8.5,
            bbox=dict(facecolor='#fffde7', alpha=0.85, pad=2, lw=0.5, edgecolor='#bbb'))
    ax.text(0.5, 0.02,
            f'Stag mean: {no3_s.mean():.3f} pptv\nVent mean: {no3_v.mean():.3f} pptv\n'
            'Stagnation suppresses, not enhances, NO₃',
            transform=ax.transAxes, ha='center', fontsize=7.5, style='italic', color='#555')

    # ── (c) N₂O₅ stag vs vent boxplot ────────────────────────────────────────
    ax = axes[2]
    n2o5_s = d.n2o5_pptv[d.stag_mask]
    n2o5_v = d.n2o5_pptv[d.vent_mask]

    bplot2 = ax.boxplot([n2o5_s, n2o5_v], positions=[1, 2], widths=0.55,
                        patch_artist=True, medianprops=dict(color='white', lw=2.5),
                        flierprops=dict(marker='o', markersize=4, alpha=0.5))
    for patch, c in zip(bplot2['boxes'], [C_STAG, C_VENT]):
        patch.set_facecolor(c)
        patch.set_alpha(0.78)

    t2, p2 = stats.ttest_ind(n2o5_s, n2o5_v)
    sig2 = '***' if p2 < 0.001 else ('**' if p2 < 0.01 else ('*' if p2 < 0.05 else 'ns'))
    ax.set_xticks([1, 2])
    ax.set_xticklabels([f'Stagnation\n(n={n_s})', f'Ventilated\n(n={n_v})'], fontsize=9)
    ax.set_ylabel('N₂O₅ (pptv)', fontsize=9)
    ax.set_title('(c)  N₂O₅ reservoir: stagnation vs ventilated\n'
                 'N₂O₅ also lower during stagnation', fontsize=9.5, pad=8)
    ax.text(0.5, 0.96, f'p = {p2:.3f}  {sig2}',
            transform=ax.transAxes, ha='center', fontsize=8.5,
            bbox=dict(facecolor='#fffde7', alpha=0.85, pad=2, lw=0.5, edgecolor='#bbb'))
    ax.text(0.5, 0.02,
            f'Stag mean: {n2o5_s.mean():.4f} pptv\nVent mean: {n2o5_v.mean():.4f} pptv',
            transform=ax.transAxes, ha='center', fontsize=7.5, style='italic', color='#555')

    fig.text(0.5, 0.01,
             'DATA INSUFFICIENCY — Old H3 (NO₃ + terpenes → SOA enhanced under stagnation) is not supported by this simulation for two independent reasons:\n'
             '(1) CHEMISTRY: NO₃ radical is suppressed during stagnation by urban NOx accumulation (NO titration). Bangkok is too NOx-rich for the nighttime biogenic pathway.\n'
             '(2) SCHEME: 2-product SOA scheme (complex_SOA: false) cannot separate NO₃-driven SOA from OH/O₃ channels.\n'
             '→ Further simulation with complex_SOA: true required for pathway-resolved SOA attribution (identified as future work in dissertation).',
             ha='center', fontsize=7.5, color='#c0392b', style='italic',
             bbox=dict(facecolor='#fdf2f8', alpha=0.9, pad=5, edgecolor='#c0392b', lw=1.0))

    savefig(fig, 'fig10_no3_pathway_assessment.png')


if __name__ == '__main__':
    plot(load_all())
