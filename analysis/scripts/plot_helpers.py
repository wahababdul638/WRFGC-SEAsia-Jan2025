"""
plot_helpers.py — Reusable cartopy map setup and figure utilities.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from scipy import stats

from config import FIG_DIR, DOM_EXT, TH_LAT, TH_LON, PROJ, C_STAG, C_VENT


def make_map(ax, extent=DOM_EXT):
    """Add coastlines, borders, gridlines to a cartopy GeoAxes."""
    ax.set_extent(extent, crs=PROJ)
    ax.add_feature(cfeature.LAND,      facecolor='#f2efe9', zorder=0)
    ax.add_feature(cfeature.OCEAN,     facecolor='#d6eaf8', zorder=0)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.55, edgecolor='#333333', zorder=3)
    ax.add_feature(cfeature.BORDERS,   linewidth=0.40, edgecolor='#666666',
                   linestyle='--', zorder=3)
    gl = ax.gridlines(draw_labels=True, linewidth=0.3, color='gray',
                      alpha=0.5, linestyle=':', crs=PROJ)
    gl.top_labels = False; gl.right_labels = False
    gl.xlocator  = mticker.FixedLocator(range(85, 120, 5))
    gl.ylocator  = mticker.FixedLocator(range(-5, 30, 5))
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': 7}
    gl.ylabel_style = {'size': 7}
    return ax


def thailand_box(ax):
    """Draw a cyan rectangle marking the Thailand analysis domain."""
    ax.add_patch(mpatches.Rectangle(
        (TH_LON[0], TH_LAT[0]),
        TH_LON[1] - TH_LON[0], TH_LAT[1] - TH_LAT[0],
        lw=2, edgecolor='#00c8ff', facecolor='none',
        transform=PROJ, zorder=5))
    ax.text(TH_LON[0] + 0.2, TH_LAT[1] + 0.3, 'Thailand',
            fontsize=7, color='#00c8ff', transform=PROJ, fontweight='bold',
            zorder=6, bbox=dict(facecolor='#1a1a1a', alpha=0.4, pad=1, lw=0))


def shade_stagnation(ax, dates, stag_mask):
    """Shade stagnant days in orange on a time-series axis."""
    for k, (d, s) in enumerate(zip(dates, stag_mask)):
        if s:
            next_d = dates[k + 1] if k + 1 < len(dates) else d
            ax.axvspan(d, next_d, color='#f5cba7', alpha=0.55, zorder=0)


def savefig(fig, name, dpi=200):
    """Save figure to FIG_DIR and close it."""
    p = os.path.join(FIG_DIR, name)
    fig.savefig(p, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  saved → {p}")


def bar2(ax, s_arr, v_arr, ylabel, title, n_stag, n_vent, unit_factor=1.0, fmt='.1f'):
    """Paired bar chart (stagnation vs ventilated) with error bars and t-test annotation."""
    xs    = np.array([1, 2])
    means = np.array([s_arr.mean(), v_arr.mean()]) * unit_factor
    stds  = np.array([s_arr.std(),  v_arr.std()])  * unit_factor
    bars  = ax.bar(xs, means, width=0.5, color=[C_STAG, C_VENT],
                   alpha=0.80, edgecolor='white', lw=0.5)
    ax.errorbar(xs, means, yerr=stds, fmt='none', color='#333', capsize=5, lw=1.5, zorder=4)
    ax.set_xticks(xs)
    ax.set_xticklabels([f'Stagnation\n(n={n_stag})', f'Ventilated\n(n={n_vent})'], fontsize=8.5)
    ax.set_ylabel(ylabel, fontsize=8.5)
    ax.set_title(title, fontsize=9.5, pad=4)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, axis='y', alpha=0.25)
    for bar, m in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + stds[0] * 0.05,
                f'{m:{fmt}}', ha='center', va='bottom', fontsize=8.5, fontweight='bold')
    t, p = stats.ttest_ind(s_arr, v_arr)
    sig  = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else 'ns'))
    ax.text(0.98, 0.94, f'p={p:.3f} {sig}', transform=ax.transAxes,
            ha='right', va='top', fontsize=8,
            bbox=dict(facecolor='#fffde7', alpha=0.85, pad=2, lw=0.5, edgecolor='#bbb'))
