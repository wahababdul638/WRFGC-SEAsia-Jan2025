"""
fig08_soa_precursors.py — 4-panel spatial map of SOA precursors during stagnation:
  (a) Biogenic terpenes:  MTPA + MTPO + LIMO  [pptv]
  (b) Anthropogenic aromatics: AROMP4 + AROMP5  [pptv]
  (c) SOAP — lumped gas-phase SOA precursor pool  [ppb]
  (d) SOAS — non-volatile SOA aerosol in PM2.5   [µg m⁻³]

SOAP is a gas-phase tracer (Is_Gas=True in GEOS-Chem species database).
SOAS is the aerosol product (Is_Aerosol=True, MW=150 g/mol), counted in PM2_5_DRY.
"""

import numpy as np
import matplotlib.pyplot as plt

from config import PROJ, TH_LON, TH_LAT, N_AIR_SFC
from plot_helpers import make_map, thailand_box, savefig
from loaders import load_spatial_sum_ppmv
from precompute import load_all


def plot(d):
    bio_terp_stag  = load_spatial_sum_ppmv(d.stag_files, ['mtpa', 'mtpo', 'limo'])
    anth_arom_stag = load_spatial_sum_ppmv(d.stag_files, ['aromp4', 'aromp5'])
    soap_stag_map  = load_spatial_sum_ppmv(d.stag_files, ['soap'])
    soas_stag_map  = load_spatial_sum_ppmv(d.stag_files, ['soas'])

    bio_terp_vent  = load_spatial_sum_ppmv(d.vent_files, ['mtpa', 'mtpo', 'limo'])
    anth_arom_vent = load_spatial_sum_ppmv(d.vent_files, ['aromp4', 'aromp5'])
    soap_vent_map  = load_spatial_sum_ppmv(d.vent_files, ['soap'])
    soas_vent_map  = load_spatial_sum_ppmv(d.vent_files, ['soas'])

    # Unit conversions for display
    bio_terp_pptv  = bio_terp_stag  * 1e6
    anth_arom_pptv = anth_arom_stag * 1e6
    soap_ppb_map   = soap_stag_map  * 1e3
    soas_ugm3_map  = soas_stag_map  * N_AIR_SFC * 150.0

    def th_mean(arr): return float(np.mean(arr[d.th_mask]))

    ratios = {
        'bio':  th_mean(bio_terp_stag)  / max(th_mean(bio_terp_vent),  1e-30),
        'anth': th_mean(anth_arom_stag) / max(th_mean(anth_arom_vent), 1e-30),
        'soap': th_mean(soap_stag_map)  / max(th_mean(soap_vent_map),  1e-30),
        'soas': th_mean(soas_stag_map)  / max(th_mean(soas_vent_map),  1e-30),
    }

    fig, axes = plt.subplots(2, 2, figsize=(14, 11),
                             subplot_kw={'projection': PROJ})
    fig.subplots_adjust(wspace=0.06, hspace=0.14, top=0.91, bottom=0.04)
    fig.suptitle(
        'WRF-GC January 2025 — SOA Precursor Identification (Stagnation Composite)\n'
        f'n = {d.stag_mask.sum()} stagnation days  |  VC ≤ {d.vc_median:.0f} m² s⁻¹  '
        '|  SOAP = gas-phase precursor  |  SOAS = aerosol product in PM$_{2.5}$',
        fontsize=10.5, y=0.97)

    sk = 8
    panels = [
        (axes[0, 0], bio_terp_pptv,
         '(a)  Biogenic Terpene Precursors\nMTPA + MTPO + LIMO',
         'YlGn', 'pptv', 'bio'),
        (axes[0, 1], anth_arom_pptv,
         '(b)  Anthropogenic Aromatic Oxidation Products\nAROMP4 + AROMP5',
         'RdPu', 'pptv', 'anth'),
        (axes[1, 0], soap_ppb_map,
         '(c)  SOAP — Lumped Gas-Phase SOA Precursor Pool\n(biogenic + anthropogenic merged)',
         'YlOrBr', 'ppb', 'soap'),
        (axes[1, 1], soas_ugm3_map,
         '(d)  SOAS — Non-volatile SOA Aerosol in PM$_{2.5}$\n(MW = 150 g mol⁻¹)',
         'BuPu', 'µg m$^{-3}$', 'soas'),
    ]

    for ax, data, title, cmap, units, rkey in panels:
        make_map(ax)
        vmax = np.percentile(data, 97)
        im = ax.pcolormesh(d.LON, d.LAT, data, transform=PROJ,
                           cmap=cmap, vmin=0, vmax=vmax, shading='gouraud', zorder=1)
        ax.quiver(d.LON[::sk, ::sk], d.LAT[::sk, ::sk],
                  d.u10_stag[::sk, ::sk], d.v10_stag[::sk, ::sk],
                  transform=PROJ, scale=80, width=0.0022,
                  color='#2c3e50', alpha=0.65, zorder=4)
        thailand_box(ax)
        cb = plt.colorbar(im, ax=ax, orientation='horizontal', shrink=0.84, pad=0.03)
        cb.set_label(units, fontsize=8.5)
        cb.ax.tick_params(labelsize=7.5)
        ax.set_title(title, fontsize=9, pad=5)
        ax.text(TH_LON[0] + 0.3, TH_LAT[0] + 0.6,
                f'Stag/Vent\n= {ratios[rkey]:.2f}×',
                fontsize=7.5, color='white', transform=PROJ, zorder=6,
                fontweight='bold',
                bbox=dict(facecolor='#1a1a2e', alpha=0.72, pad=2, lw=0))

    fig.text(0.5, 0.005,
             'SOAP (panels a–c) is a GAS-PHASE tracer (Is_Gas=True) — NOT in PM₂.₅.  '
             'SOAS (panel d) is the AEROSOL product (Is_Aerosol=True, non-volatile) — '
             'counted in PM₂.₅_DRY.\n'
             'Biogenic (a) and anthropogenic (b) precursors merge into SOAP (c) '
             'before condensing to SOAS (d).  Source separation requires sensitivity runs.',
             ha='center', fontsize=7, color='#444', style='italic')

    savefig(fig, 'figP8_soa_precursor_spatial.png')


if __name__ == '__main__':
    plot(load_all())
