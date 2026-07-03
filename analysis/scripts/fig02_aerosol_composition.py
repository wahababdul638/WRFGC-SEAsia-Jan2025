"""
fig02_aerosol_composition.py — Stacked bar chart of PM2.5 chemical composition:
SO4, NIT+NH4, BC, and residual OA, for stagnation vs ventilated periods.

OA is computed as: OA = PM2.5 - SO4 - NIT - NH4 - BC  (residual approach).
This avoids overcounting from direct tracer summation.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from config import C_STAG, C_VENT
from plot_helpers import savefig
from precompute import load_all


def plot(d):
    def sv(arr): return arr[d.stag_mask].mean(), arr[d.vent_mask].mean()

    so4_s, so4_v = sv(d.so4_ugm3)
    nit_s, nit_v = sv(d.nit_ugm3)
    nh4_s, nh4_v = sv(d.nh4_ugm3)
    bc_s,  bc_v  = sv(d.bc_ugm3)
    oa_s,  oa_v  = sv(d.oa_ugm3)

    comp_labels = ['SO$_4$', 'NIT + NH$_4$', 'BC', 'OA (residual)']
    comp_colors = ['#f1c40f', '#e67e22', '#2c3e50', '#8e44ad']
    stag_vals   = np.array([so4_s, nit_s + nh4_s, bc_s, oa_s])
    vent_vals   = np.array([so4_v, nit_v + nh4_v, bc_v, oa_v])
    stag_pct    = stag_vals / stag_vals.sum() * 100
    vent_pct    = vent_vals / vent_vals.sum() * 100

    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    fig.subplots_adjust(wspace=0.45, top=0.82, bottom=0.12)
    fig.suptitle('Surface PM$_{2.5}$ Chemical Composition — Bangkok (13.75°N, 100.50°E)\n'
                 'WRF-GC January 2025  |  Stagnation vs Ventilated regimes', fontsize=11)

    for ax, vals, pcts, title, color, n_days in [
        (axes[0], stag_vals, stag_pct,
         f'Stagnation (VC ≤ {d.vc_median:.0f} m² s⁻¹)', C_STAG, d.stag_mask.sum()),
        (axes[1], vent_vals, vent_pct,
         f'Ventilated (VC > {d.vc_median:.0f} m² s⁻¹)', C_VENT, d.vent_mask.sum()),
    ]:
        bottoms = 0.0
        for lbl, clr, v, pct in zip(comp_labels, comp_colors, vals, pcts):
            ax.bar([0], [v], bottom=bottoms, color=clr, alpha=0.88,
                   edgecolor='white', linewidth=0.8)
            if v > 4.0:
                txt_color = 'white' if clr == '#2c3e50' else '#111111'
                ax.text(0, bottoms + v / 2,
                        f'{lbl}\n{v:.1f} µg/m³  ({pct:.0f}%)',
                        ha='center', va='center', fontsize=8.5,
                        color=txt_color, fontweight='bold')
            elif v > 1.0:
                ax.text(0.55, bottoms + v / 2,
                        f'{lbl}  {v:.1f}  ({pct:.0f}%)',
                        ha='left', va='center', fontsize=7.5, color='#333',
                        transform=ax.get_yaxis_transform())
            bottoms += v

        ymax = max(stag_vals.sum(), vent_vals.sum()) * 1.15
        ax.set_ylim(0, ymax)
        ax.set_title(f'{title}\nn = {n_days} days', fontsize=10, color=color, pad=8)
        ax.set_ylabel('PM$_{2.5}$ (µg m$^{-3}$)', fontsize=9)
        ax.text(0, bottoms + ymax * 0.01, f'Total: {vals.sum():.1f} µg/m³',
                ha='center', va='bottom', fontsize=10, fontweight='bold', color=color)
        ax.set_xticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, axis='y', alpha=0.3)

    handles = [mpatches.Patch(color=c, label=l)
               for l, c in zip(comp_labels, comp_colors)]
    fig.legend(handles=handles, loc='lower center', ncol=4, fontsize=9,
               bbox_to_anchor=(0.5, 0.01), framealpha=0.8)

    savefig(fig, 'fig02_aerosol_composition.png')


if __name__ == '__main__':
    plot(load_all())
