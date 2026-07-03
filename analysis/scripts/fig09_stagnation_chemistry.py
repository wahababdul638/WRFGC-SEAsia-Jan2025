"""
fig09_stagnation_chemistry.py — Objective 2: SOA Formation State Analysis

Proxy diagnostics to characterise whether stagnation enhances SOA through
boundary-layer compression or genuine new chemical production.

Panels:
  (a) SOAP (gas precursor) and SOAS (aerosol) time series at Bangkok
  (b) SOAP/SOAS molar ratio: formation state proxy
      High ratio → precursor-rich, active formation; similar between regimes
      → formation state unchanged; compression effect dominates
  (c) SOAS column burden proxy (SOAS_surface × PBLH): compression vs production test
      Constant burden → PBLH compression explains surface increase
      Higher burden during stagnation → net new aerosol production
  (d) Ventilation coefficient vs SOAS: quantifies stagnation–SOA relationship (H2)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import stats

from config import C_STAG, C_VENT
from plot_helpers import savefig, shade_stagnation
from precompute import load_all


def plot(d):
    # SOAS in µg/m³: ppb × 1e-9 × n_air (mol/m³) × MW (g/mol) × 1e6 µg/g = ppb × n_air × MW × 1e-3
    soas_ugm3 = d.soas_ppb * d.n_air_bkk * 150.0 * 1e-3
    soap_soas_ratio = d.soap_ppb / np.maximum(d.soas_ppb, 1e-10)
    col_burden = d.soas_ppb * d.pblh_bkk   # ppb·m — rough column integral proxy

    n_s, n_v = int(d.stag_mask.sum()), int(d.vent_mask.sum())

    fig = plt.figure(figsize=(14, 10))
    fig.suptitle(
        'Objective 2: SOA Formation State During Stagnation — Bangkok (13.75°N, 100.50°E)\n'
        'WRF-GC January 2025  |  Proxy diagnostics for local production vs boundary-layer compression',
        fontsize=12, fontweight='bold')

    gs = fig.add_gridspec(2, 2, wspace=0.40, hspace=0.48, top=0.88, bottom=0.10)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    for ax in [ax_a, ax_b, ax_c, ax_d]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    # ── (a) SOAP and SOAS time series ─────────────────────────────────────────
    shade_stagnation(ax_a, d.dates_late, d.stag_mask)
    ax_a_r = ax_a.twinx()
    ax_a_r.spines['top'].set_visible(False)
    l1, = ax_a.plot(d.dates_late, d.soap_ppb, 'o-', color='#e67e22',
                    lw=1.8, ms=4, label='SOAP (ppb, gas)', zorder=3)
    l2, = ax_a_r.plot(d.dates_late, soas_ugm3, 's-', color='#27ae60',
                      lw=1.8, ms=4, label='SOAS (µg m⁻³, aerosol)', zorder=3)
    ax_a.set_ylabel('SOAP (ppb)', color='#e67e22', fontsize=9)
    ax_a_r.set_ylabel('SOAS (µg m⁻³)', color='#27ae60', fontsize=9)
    ax_a.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    ax_a.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    plt.setp(ax_a.xaxis.get_majorticklabels(), rotation=25, ha='right', fontsize=7.5)
    ax_a.legend(handles=[l1, l2], fontsize=7.5, loc='upper left', framealpha=0.8)
    ax_a.set_title('(a)  SOAP gas precursor and SOAS aerosol\n(orange shading = stagnation days)',
                   fontsize=9, pad=6)
    ax_a.grid(True, alpha=0.20, zorder=1)

    # ── (b) SOAP/SOAS ratio boxplot ───────────────────────────────────────────
    ratio_s = soap_soas_ratio[d.stag_mask]
    ratio_v = soap_soas_ratio[d.vent_mask]
    ratio_s = ratio_s[np.isfinite(ratio_s)]
    ratio_v = ratio_v[np.isfinite(ratio_v)]

    bplot = ax_b.boxplot([ratio_s, ratio_v], positions=[1, 2], widths=0.55,
                         patch_artist=True, medianprops=dict(color='white', lw=2.5),
                         flierprops=dict(marker='o', markersize=4, alpha=0.5))
    for patch, c in zip(bplot['boxes'], [C_STAG, C_VENT]):
        patch.set_facecolor(c)
        patch.set_alpha(0.78)

    t, p = stats.ttest_ind(ratio_s, ratio_v)
    sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else 'ns'))
    ax_b.set_xticks([1, 2])
    ax_b.set_xticklabels([f'Stagnation\n(n={n_s})', f'Ventilated\n(n={n_v})'], fontsize=9)
    ax_b.set_ylabel('SOAP / SOAS (molar ratio)', fontsize=9)
    ax_b.set_title('(b)  Formation state proxy: SOAP/SOAS ratio\n'
                   'Higher = more precursor-rich / actively forming', fontsize=9, pad=6)
    ax_b.grid(True, axis='y', alpha=0.20)
    ax_b.text(0.5, 0.96, f'p = {p:.3f}  {sig}',
              transform=ax_b.transAxes, ha='center', fontsize=8.5,
              bbox=dict(facecolor='#fffde7', alpha=0.85, pad=2, lw=0.5, edgecolor='#bbb'))
    ax_b.text(0.5, 0.02,
              f'Stag mean: {ratio_s.mean():.2f}  |  Vent mean: {ratio_v.mean():.2f}\n'
              'Similar ratio → formation state similar between regimes',
              transform=ax_b.transAxes, ha='center', fontsize=7.5, style='italic', color='#555')

    # ── (c) Column burden time series ─────────────────────────────────────────
    shade_stagnation(ax_c, d.dates_late, d.stag_mask)
    ax_c.plot(d.dates_late, col_burden, 'D-', color='#d35400', lw=1.8, ms=4, zorder=3)

    s_burden = col_burden[d.stag_mask].mean()
    v_burden = col_burden[d.vent_mask].mean()
    pct = (s_burden - v_burden) / max(v_burden, 1e-10) * 100

    ax_c.axhline(s_burden, color=C_STAG, ls='--', lw=1.3,
                 label=f'Stag mean: {s_burden:.1f} ppb·m', zorder=4)
    ax_c.axhline(v_burden, color=C_VENT, ls='--', lw=1.3,
                 label=f'Vent mean: {v_burden:.1f} ppb·m', zorder=4)
    ax_c.set_ylabel('SOAS_surface × PBLH (ppb·m)', fontsize=9)
    ax_c.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    ax_c.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    plt.setp(ax_c.xaxis.get_majorticklabels(), rotation=25, ha='right', fontsize=7.5)
    ax_c.legend(fontsize=7.5, loc='upper left', framealpha=0.8)
    ax_c.set_title(f'(c)  Column burden proxy (SOAS × PBLH)\n'
                   f'Stag vs vent change: {pct:+.1f}%', fontsize=9, pad=6)
    ax_c.grid(True, alpha=0.20, zorder=1)
    ax_c.text(0.98, 0.04,
              '≈ constant burden → BL compression explains surface increase\n'
              'Higher during stagnation → net new SOA production',
              transform=ax_c.transAxes, ha='right', fontsize=7.5,
              style='italic', color='#555')

    # ── (d) VC vs SOAS scatter ────────────────────────────────────────────────
    ax_d.scatter(d.vc_th_ts[d.vent_mask], soas_ugm3[d.vent_mask],
                 c=C_VENT, s=70, edgecolors='white', lw=0.5, label='Ventilated', zorder=3)
    ax_d.scatter(d.vc_th_ts[d.stag_mask], soas_ugm3[d.stag_mask],
                 c=C_STAG, s=70, marker='D', edgecolors='white', lw=0.5,
                 label='Stagnation', zorder=3)

    slope, intercept, r, p_r, _ = stats.linregress(d.vc_th_ts, soas_ugm3)
    vc_fit = np.linspace(0, d.vc_th_ts.max() * 1.05, 100)
    ax_d.plot(vc_fit, slope * vc_fit + intercept, 'k--', lw=1.2, alpha=0.65)

    ax_d.axvline(np.median(d.vc_th_ts), color='gray', ls=':', lw=1.2,
                 alpha=0.7, label=f'VC median ({np.median(d.vc_th_ts):.0f} m²/s)')
    ax_d.set_xlabel('Ventilation Coefficient, Thailand mean (m²/s)', fontsize=9)
    ax_d.set_ylabel('SOAS (µg m⁻³)', fontsize=9)
    ax_d.set_title('(d)  Stagnation driving SOA magnitude\n'
                   '(VC inverse relationship — Hypothesis 2)', fontsize=9, pad=6)
    ax_d.legend(fontsize=7.5, framealpha=0.8)
    ax_d.grid(True, alpha=0.20)
    ax_d.text(0.05, 0.94, f'r = {r:.3f}  (p = {p_r:.3f})',
              transform=ax_d.transAxes, fontsize=9, fontweight='bold')

    fig.text(0.5, 0.01,
             'H2: Stagnation increases SOA by suppressing dispersion and increasing precursor residence time.  '
             'SOAP/SOAS ratio is the formation-state proxy (local vs transported signal).',
             ha='center', fontsize=8, style='italic', color='#333',
             bbox=dict(facecolor='#f8f9fa', alpha=0.85, pad=4, edgecolor='#ccc'))

    savefig(fig, 'fig09_soa_formation_state.png')


if __name__ == '__main__':
    plot(load_all())
