"""
fig06_spatial_maps.py — 2×2 spatial maps comparing PM2.5 and SOAP+SOAS
between stagnation and ventilated composites, with wind vector overlays.
"""

import numpy as np
import matplotlib.pyplot as plt

from config import PROJ
from plot_helpers import make_map, thailand_box, savefig
from loaders import load_spatial_sum_ppmv
from precompute import load_all


def plot(d):
    soap_stag = load_spatial_sum_ppmv(d.stag_files, ['soap', 'soas'])
    soap_vent = load_spatial_sum_ppmv(d.vent_files, ['soap', 'soas'])

    vmax_pm  = max(d.pm25_stag_map.max(), d.pm25_vent_map.max()) * 0.97
    vmax_soa = max(soap_stag.max(), soap_vent.max()) * 0.97

    fig, axes = plt.subplots(2, 2, figsize=(14, 11),
                             subplot_kw={'projection': PROJ})
    fig.subplots_adjust(wspace=0.06, hspace=0.12, top=0.91, bottom=0.04)
    fig.suptitle(
        'WRF-GC January 2025 — Spatial Distribution under Different Regimes\n'
        f'Stagnation (n={d.stag_mask.sum()} days, VC ≤ {d.vc_median:.0f} m² s⁻¹)  vs  '
        f'Ventilated (n={d.vent_mask.sum()} days)',
        fontsize=11, y=0.97)

    sk = 8
    panels = [
        (axes[0, 0], d.pm25_stag_map, 'PM$_{2.5}$ — Stagnation', 'YlOrBr',
         0, vmax_pm, d.u10_stag, d.v10_stag, '(a)'),
        (axes[0, 1], d.pm25_vent_map, 'PM$_{2.5}$ — Ventilated', 'YlOrBr',
         0, vmax_pm, d.u10_vent, d.v10_vent, '(b)'),
        (axes[1, 0], soap_stag, 'SOAP+SOAS — Stagnation', 'BuPu',
         0, vmax_soa, d.u10_stag, d.v10_stag, '(c)'),
        (axes[1, 1], soap_vent, 'SOAP+SOAS — Ventilated', 'BuPu',
         0, vmax_soa, d.u10_vent, d.v10_vent, '(d)'),
    ]

    for ax, data, title, cmap, vmin, vmax, u, v, letter in panels:
        make_map(ax)
        im = ax.pcolormesh(d.LON, d.LAT, data, transform=PROJ,
                           cmap=cmap, vmin=vmin, vmax=vmax, shading='gouraud', zorder=1)
        ax.quiver(d.LON[::sk, ::sk], d.LAT[::sk, ::sk],
                  u[::sk, ::sk], v[::sk, ::sk],
                  transform=PROJ, scale=90, width=0.002,
                  color='#1a1a2e', alpha=0.7, zorder=4)
        thailand_box(ax)
        cb = plt.colorbar(im, ax=ax, orientation='horizontal', shrink=0.82, pad=0.03)
        cb_lbl = 'PM$_{2.5}$ (µg m$^{-3}$)' if 'PM' in title else 'SOAP+SOAS (ppmv)'
        cb.set_label(cb_lbl, fontsize=8)
        cb.ax.tick_params(labelsize=7)
        ax.set_title(f'{letter}  {title}', fontsize=9.5, pad=6)

    savefig(fig, 'fig06_spatial_pm25_soa.png')


if __name__ == '__main__':
    plot(load_all())
