# =============================================================================
# Chapter 7: Material Take-off & Quantity Summary
# Includes automated matplotlib bar charts for Structural Steel tonnage and
# Concrete Volume (m^3) vs. Reinforcement Steel weight (MT).
# =============================================================================

import os
from osdagbridge.core.reports.report_utils import (
    parse_float_safe,
    _fig_embed,
    generate_steel_tonnage_chart,
    generate_concrete_vs_rebar_chart,
)
from osdagbridge.core.reports.styles import TABLE_STYLE


def ch7_quantities(input_dict, chart_dir=None):
    # Extract material quantities for automated visualizations
    girders_mt = parse_float_safe(input_dict.get("steel_girders_wt_total"), 0.0)
    bracing_mt = (
        parse_float_safe(input_dict.get("bracing_top_wt_total"), 0.0)
        + parse_float_safe(input_dict.get("bracing_bot_wt_total"), 0.0)
        + parse_float_safe(input_dict.get("bracing_diag_wt_total"), 0.0)
    )
    end_diaphragm_mt = parse_float_safe(
        input_dict.get("end_diaphragm_wt_total", input_dict.get("ed_wt_total")), 0.0
    )
    concrete_m3 = parse_float_safe(input_dict.get("concrete_deck_vol_total"), 0.0)
    rebar_mt = parse_float_safe(input_dict.get("rebar_deck_wt_total"), 0.0)

    charts_tex = ""
    if chart_dir:
        steel_chart_path = generate_steel_tonnage_chart(
            [
                ("Plate Girders", girders_mt),
                ("Cross Bracing", bracing_mt),
                ("End Diaphragms", end_diaphragm_mt),
            ],
            os.path.join(chart_dir, "ch7_steel_tonnage.png"),
        )
        concrete_rebar_path = generate_concrete_vs_rebar_chart(
            concrete_m3,
            rebar_mt,
            os.path.join(chart_dir, "ch7_concrete_vs_rebar.png"),
        )

        chart_blocks = []
        if steel_chart_path:
            chart_blocks.append(
                _fig_embed(
                    steel_chart_path,
                    "Structural Steel Tonnage Summary (Girders, Cross Bracing, and End Diaphragms)",
                    width=r"0.88\textwidth",
                )
            )
        if concrete_rebar_path:
            chart_blocks.append(
                _fig_embed(
                    concrete_rebar_path,
                    r"Deck Slab Concrete Volume ($\text{m}^3$) vs. Reinforcement Steel Weight (MT)",
                    width=r"0.88\textwidth",
                )
            )
        if chart_blocks:
            charts_tex = "\n\\section{Material Quantity Visualizations}\n" + "\n".join(chart_blocks)

    return r"""
\chapter{Material Take-off \& Quantity Summary}
\label{ch:material-takeoff}

This chapter summarizes the estimated quantities of structural steel, deck concrete, reinforcement, shear connectors, and crash barriers required for the superstructure.

\vspace{0.5em}
\begingroup
\setlength{\tabcolsep}{3.5pt}
\begin{longtable}{|C{1.0cm}|L{3.8cm}|C{2.6cm}|C{1.8cm}|C{1.8cm}|C{1.8cm}|C{1.8cm}|}
\caption{\textbf{Bill of Materials (Steel, Concrete, and Reinforcement Quantities)}}
\hline
\textbf{S.N.} & \textbf{Item Description} & \textbf{Volume} & \textbf{Quantity} & \textbf{Total Volume} & \textbf{Weight (MT)} & \textbf{Total Weight (MT)} \\
\hline
1 & Structural Steel (IS 2062) for Girders & """ + str(input_dict.get("steel_girders_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_qty", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_wt_total", "N.A.")) + r""" \\
\hline
2(a) & Cross Bracing - Top Chord & """ + str(input_dict.get("bracing_top_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_wt_total", "N.A.")) + r""" \\
\hline
2(b) & Cross Bracing - Bottom Chord & """ + str(input_dict.get("bracing_bot_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_wt_total", "N.A.")) + r""" \\
\hline
2(c) & Cross Bracing - Diagonal Chord & """ + str(input_dict.get("bracing_diag_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_wt_total", "N.A.")) + r""" \\
\hline
3 & Concrete (M40) for Deck Slab & """ + str(input_dict.get("concrete_deck_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_qty", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_wt_total", "N.A.")) + r""" \\
\hline
4 & Reinforcement Steel (Fe 500) & """ + str(input_dict.get("rebar_deck_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_qty", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_wt_total", "N.A.")) + r""" \\
\hline
5 & Shear Stud Connectors & """ + str(input_dict.get("shear_studs_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_qty", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_wt_total", "N.A.")) + r""" \\
\hline
6 & Crash Barrier & """ + str(input_dict.get("crash_barrier_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_qty", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_wt_total", "N.A.")) + r""" \\
\hline
\end{longtable}
\endgroup
""" + charts_tex + "\n"