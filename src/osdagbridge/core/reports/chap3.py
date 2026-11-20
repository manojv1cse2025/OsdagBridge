# =============================================================================
# Chapter 3: Loads and Load Combinations
# Refactored to separate Vehicle Live Loads and Footpath Live Loads into
# distinct, structured tables using centralized styling from styles.py.
# =============================================================================

from osdagbridge.core.utils.common import (
    KEY_CB_LOAD,
    KEY_LL_CUSTOM_VEHICLES,
    KEY_LL_FOOTPATH_PRESSURE_MODE,
    KEY_LL_FOOTPATH_PRESSURE_VALUE,
    KEY_LL_IRC_70R_BOGIE,
    KEY_LL_IRC_70R_TRACKED,
    KEY_LL_IRC_70R_WHEELED,
    KEY_LL_IRC_AA_TRACKED,
    KEY_LL_IRC_AA_WHEELED,
    KEY_LL_IRC_CLASS_A,
    KEY_LL_IRC_CLASS_FATIGUE,
    KEY_LL_IRC_CLASS_SV,
    KEY_MATERIAL_DECK_DENSITY,
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_PL_SELF_WEIGHT_FACTOR,
    KEY_RL_LOAD_VALUE,
    KEY_SL_DAMPING,
    KEY_SL_DEAD_LOAD_MODE,
    KEY_SL_DEAD_LOAD_VALUE,
    KEY_SL_HORIZONTAL_COEFF,
    KEY_SL_IMPORTANCE_FACTOR,
    KEY_SL_LIVE_LOAD_MODE,
    KEY_SL_LIVE_LOAD_VALUE,
    KEY_SL_SEISMIC_ZONE,
    KEY_SL_SOIL_TYPE,
    KEY_SL_SPECTRAL_COEFF,
    KEY_SL_TIME_PERIOD,
    KEY_SL_VERTICAL_COEFF,
    KEY_SL_ZONE_FACTOR,
    KEY_SPAN,
    KEY_TL_BRIDGE_TEMP_MAX,
    KEY_TL_BRIDGE_TEMP_MIN,
    KEY_TL_HIGHEST_MAX_TEMP,
    KEY_TL_LOWEST_MIN_TEMP,
    KEY_TL_TEMP_FALL,
    KEY_TL_TEMP_RISE,
    KEY_WC_LD_LANE_TABLE_COUNT,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS,
    KEY_WL_AVG_EXPOSED_HEIGHT,
    KEY_WL_BASIC_WIND_SPEED,
    KEY_WL_HOURLY_MEAN_WIND,
    KEY_WL_HOURLY_WIND_PRESSURE,
    KEY_WL_LONGITUDINAL_WIND_FORCE,
    KEY_WL_TERRAIN_TYPE,
    KEY_WL_TRANSVERSE_WIND_FORCE,
    KEY_WL_VERTICAL_WIND_FORCE,
)

from osdagbridge.core.reports.report_utils import _tex, _render_value
from osdagbridge.core.reports.styles import TABLE_STYLE


def ch3_loads(input_dict):
    from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017

    span = input_dict.get(KEY_SPAN)
    span_m = None
    if span not in (None, ""):
        try:
            span_m = float(span)
        except Exception:
            span_m = None

    # Compute impact factors per IRC 6 Cl. 208
    im_class_a = "N/A"
    im_heavy = "N/A"
    if span_m is not None:
        try:
            im_class_a = f"{1.0 + IRC6_2017.cl_208_2_impact_factor(span_m):.3f}"
        except Exception:
            pass
        try:
            im_heavy = f"{1.0 + IRC6_2017.cl_208_3_impact_factor(span_m):.3f}"
        except Exception:
            pass

    # Compute braking force per IRC 6 Cl. 211.2
    lanes = input_dict.get(KEY_WC_LD_LANE_TABLE_COUNT)
    braking_kN_str = "N/A"
    if lanes not in (None, ""):
        try:
            braking_force_t = IRC6_2017.cl_211_2_braking_force(int(lanes))
            braking_kN_str = f"{braking_force_t * 9.81:.2f}"
        except Exception:
            pass

    # Standard IRC 6 vehicle specs: (key, label, total_load_kN, impact_str, braking_considered)
    vehicle_catalog = [
        (KEY_LL_IRC_CLASS_A,       "Class A",              "554.0",  im_class_a, True),
        (KEY_LL_IRC_70R_WHEELED,   "Class 70R (Wheeled)",  "1000.0", im_heavy,   True),
        (KEY_LL_IRC_70R_TRACKED,   "Class 70R (Tracked)",  "700.0",  im_heavy,   True),
        (KEY_LL_IRC_70R_BOGIE,     "Class 70R (Bogie)",    "400.0",  im_heavy,   True),
        (KEY_LL_IRC_AA_WHEELED,    "Class AA (Wheeled)",   "400.0",  im_heavy,   True),
        (KEY_LL_IRC_AA_TRACKED,    "Class AA (Tracked)",   "700.0",  im_heavy,   True),
        (KEY_LL_IRC_CLASS_SV,      "Class SV",             "3850.0", "1.000",    False),
        (KEY_LL_IRC_CLASS_FATIGUE, "Class Fatigue",        "400.0",  im_class_a, False),
    ]

    ll_rows = []
    for key, label, load_kn, imp_val, has_braking in vehicle_catalog:
        if input_dict.get(key):
            brk_cons = "Yes" if has_braking else "No"
            brk_val = braking_kN_str if has_braking else "---"
            brk_ecc = "1.20" if has_braking else "---"
            centrifugal = "N/A"
            ll_rows.append(
                f"{_tex(label)} & {load_kn} & {imp_val} & {brk_cons} & {brk_val} & {brk_ecc} & {centrifugal}"
                + r" \\[6pt]" + "\n" + r"\hline"
            )

    custom = input_dict.get(KEY_LL_CUSTOM_VEHICLES)
    if custom and isinstance(custom, list):
        for c in custom:
            cname = c.get("name", "Custom Vehicle") if isinstance(c, dict) else str(c)
            cload = str(c.get("total_load", "---")) if isinstance(c, dict) else "---"
            ll_rows.append(
                f"{_tex(cname)} & {_tex(cload)} & --- & No & --- & --- & N/A"
                + r" \\[6pt]" + "\n" + r"\hline"
            )

    if not ll_rows:
        ll_rows.append(
            r"None Selected & --- & --- & No & --- & --- & N/A \\[6pt]" + "\n" + r"\hline"
        )

    ll_rows_str = "\n".join(ll_rows)

    # Footpath live load details (separate table)
    fp_mode = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_MODE, "")
    fp_value = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_VALUE, "")
    if str(fp_mode).strip().lower() in ("as per irc 6", "as per irc6", "automatic"):
        try:
            fp_intensity_str = f"{IRC6_2017.cl_206_1_footway_load():.3f} kN/m\\textsuperscript{{2}}"
        except Exception:
            fp_intensity_str = "N/A"
        fp_mode_str = _tex(fp_mode)
    elif fp_value not in (None, ""):
        fp_intensity_str = f"{_tex(fp_value)} kN/m\\textsuperscript{{2}}"
        fp_mode_str = _tex(fp_mode) if fp_mode else "User Defined"
    else:
        fp_intensity_str = "N/A (No Footpath)"
        fp_mode_str = "Not Applicable"

    # Load combinations (dynamically generated from IRC 6)
    _LOAD_LABEL_MAP = {
        'dead_load':         'DL',
        'surfacing':         'SIDL',
        'live_load':         'LL',
        'wind_load':         'WL',
        'thermal_load':      'TL',
        'vehicle_collision': 'VC',
        'barge_impact':      'BI',
        'floating_bodies':   'FB',
        'seismic':           'EQ',
    }

    def _fmt_factors(factors):
        parts = []
        for load, val in factors.items():
            label = _LOAD_LABEL_MAP.get(load, load.upper())
            if isinstance(val, dict):
                add = val.get('adding')
                rel = val.get('relieving')
                add_s = f"{add:.2f}" if add is not None else '--'
                rel_s = f"{rel:.2f}" if rel is not None else '--'
                parts.append(f"{label}({add_s}/{rel_s})")
            else:
                if val is None:
                    continue
                parts.append(f"{label}({val:.2f})")
        return ' + '.join(parts)

    uls_combos = IRC6_2017.uls_load_combinations()
    sls_combos = IRC6_2017.sls_load_combinations()
    lc_rows = []
    for i, combo in enumerate(uls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(f"ULS-{i:02d}" + r" & " + cases + r" \\[6pt]" + "\n" + r"\hline")
    for i, combo in enumerate(sls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(f"SLS-{i:02d}" + r" & " + cases + r" \\[6pt]" + "\n" + r"\hline")

    lc_rows_str = "\n".join(lc_rows)
    hdr_bg = TABLE_STYLE["header_bg_macro"]

    return r"""
\chapter{Loads and Load Combinations}

This section summarizes all loads applied to the bridge and the load combinations considered for analysis and design.

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Dead Load -- Self Weight}}
\hline
\textbf{Parameter} & \textbf{Value} \\
\hline
\textnormal{Steel Self-Weight Applied} & """ + (_render_value(input_dict, KEY_MATERIAL_GIRDER_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\[6pt]
\hline
\textnormal{Concrete Deck Weight} & """ + (_render_value(input_dict, KEY_MATERIAL_DECK_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\[6pt]
\hline
\textnormal{Self-Weight Factor} & """ + (_render_value(input_dict, KEY_PL_SELF_WEIGHT_FACTOR)) + r""" \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Dead Load for Surfacing (DW)}}
\hline
\textbf{Parameter} & \textbf{Value} \\
\hline
\textnormal{Wearing Course Load} & """ + (_render_value(input_dict, KEY_WC_MATERIAL)) + r""" x """ + (_render_value(input_dict, KEY_WC_THICKNESS)) + r""" \\[6pt]
\hline
\textnormal{Additional SIDL (Crash Barrier)} & """ + (_render_value(input_dict, KEY_CB_LOAD)) + r""" kN/m per barrier \\[6pt]
\hline
\textnormal{Railing Load} & """ + (_render_value(input_dict, KEY_RL_LOAD_VALUE)) + r""" kN/m\sdstar{} \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begingroup
\setlength{\tabcolsep}{4pt}
\begin{longtable}{|L{2.6cm}|C{1.9cm}|C{1.7cm}|C{1.8cm}|C{1.8cm}|C{1.8cm}|C{2.0cm}|}
\caption{\textbf{Vehicle Live Loads (LL) --- per IRC 6}} \\
\hline
\rowcolor{""" + hdr_bg + r"""} \multirow{2}{*}{\textbf{Vehicle}} & \multirow{2}{*}{\makecell{\textbf{Total Load}\\\textbf{(kN)}}} & \multirow{2}{*}{\makecell{\textbf{Impact}\\\textbf{Factor}}} & \multicolumn{3}{c|}{\textbf{Braking Load}} & \multirow{2}{*}{\makecell{\textbf{Centrifugal}\\\textbf{Force (kN)}}} \\
\cline{4-6}
\rowcolor{""" + hdr_bg + r"""} & & & \textbf{Considered?} & \textbf{Value (kN)} & \textbf{Ecc. (m)} & \\
\hline
\endfirsthead
\multicolumn{7}{l}{\small\textit{(Continued from previous page)}} \\[4pt]
\hline
\rowcolor{""" + hdr_bg + r"""} \multirow{2}{*}{\textbf{Vehicle}} & \multirow{2}{*}{\makecell{\textbf{Total Load}\\\textbf{(kN)}}} & \multirow{2}{*}{\makecell{\textbf{Impact}\\\textbf{Factor}}} & \multicolumn{3}{c|}{\textbf{Braking Load}} & \multirow{2}{*}{\makecell{\textbf{Centrifugal}\\\textbf{Force (kN)}}} \\
\cline{4-6}
\rowcolor{""" + hdr_bg + r"""} & & & \textbf{Considered?} & \textbf{Value (kN)} & \textbf{Ecc. (m)} & \\
\hline
\endhead
\hline
\multicolumn{7}{r}{\small\textit{(Continued on next page)}} \\
\endfoot
\endlastfoot
""" + ll_rows_str + r"""
\end{longtable}
\endgroup
\noindent\textit{Note: Impact factors per IRC 6 Cl. 208; braking force per IRC 6 Cl. 211.2 applied at 1.20 m above carriageway level; centrifugal force applicable only for curved bridges (IRC 6 Cl. 212).}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Footpath / Footway Live Load --- per IRC 6 Cl. 206.1}}
\hline
\textbf{Parameter} & \textbf{Value} \\
\hline
\textnormal{Footpath Load Mode} & """ + fp_mode_str + r""" \\[6pt]
\hline
\textnormal{Footpath Live Load Intensity} & """ + fp_intensity_str + r""" \\[6pt]
\hline
\textnormal{Design Code Reference} & IRC 6:2017 Cl. 206.1 \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Wind Load (WL) --- per IRC 6}}
\hline
\textbf{Parameter} & \textbf{Value} \\
\hline
\textnormal{Basic Wind Speed, Vb} & """ + (_render_value(input_dict, 'wind_speed', ' m/s')) + r""" [from Project Location] \\[6pt]
\hline
\textnormal{Terrain Type} & """ + (_render_value(input_dict, KEY_WL_TERRAIN_TYPE)) + r""" \\[6pt]
\hline
\textnormal{Average Exposed Height, H (m)} & """ + (_render_value(input_dict, KEY_WL_AVG_EXPOSED_HEIGHT, ' m')) + r""" \\[6pt]
\hline
\textnormal{Hourly Mean Wind Speed, Vz} & """ + (_render_value(input_dict, KEY_WL_HOURLY_MEAN_WIND, ' m/s')) + r""" \\[6pt]
\hline
\textnormal{Hourly Wind Pressure, Pz} & """ + (_render_value(input_dict, KEY_WL_HOURLY_WIND_PRESSURE, ' N/m\\textsuperscript{2}')) + r""" \\[6pt]
\hline
\textnormal{Transverse Wind Force} & """ + (_render_value(input_dict, KEY_WL_TRANSVERSE_WIND_FORCE, ' kN')) + r""" \\[6pt]
\hline
\textnormal{Longitudinal Wind Force} & """ + (_render_value(input_dict, KEY_WL_LONGITUDINAL_WIND_FORCE, ' kN')) + r""" \\[6pt]
\hline
\textnormal{Vertical Wind Force} & """ + (_render_value(input_dict, KEY_WL_VERTICAL_WIND_FORCE, ' kN')) + r""" \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Earthquake Load (EL) --- per IRC 6}}
\hline
\textbf{Parameter} & \textbf{Value} \\
\hline
\textnormal{Seismic Zone} & """ + (_render_value(input_dict, 'seismic_zone')) + r""" [from Project Location] \\[6pt]
\hline
\textnormal{Zone Factor, Z} & """ + (_render_value(input_dict, KEY_SL_ZONE_FACTOR)) + r""" \\[6pt]
\hline
\textnormal{Importance Factor, I} & """ + (_render_value(input_dict, KEY_SL_IMPORTANCE_FACTOR)) + r""" \\[6pt]
\hline
\textnormal{Type of Soil} & """ + (_render_value(input_dict, KEY_SL_SOIL_TYPE)) + r""" \\[6pt]
\hline
\textnormal{Sa/g} & """ + (_render_value(input_dict, KEY_SL_SPECTRAL_COEFF)) + r""" \\[6pt]
\hline
\textnormal{Horizontal Seismic Coefficient, Ah} & """ + (_render_value(input_dict, KEY_SL_HORIZONTAL_COEFF)) + r""" \\[6pt]
\hline
\textnormal{Vertical Seismic Coefficient, Av} & """ + (_render_value(input_dict, KEY_SL_VERTICAL_COEFF)) + r""" \\[6pt]
\hline
\textnormal{Horizontal Seismic Force (longitudinal)} & """ + '' + r""" kN \\[6pt]
\hline
\textnormal{Horizontal Seismic Force (transverse)} & """ + '' + r""" kN \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Temperature Load (TL) --- per IRC 6}}
\hline
\textbf{Parameter} & \textbf{Value} \\
\hline
\textnormal{Maximum Shade Temperature} & """ + (_render_value(input_dict, 'shade_temp_max')) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Minimum Shade Temperature} & """ + (_render_value(input_dict, 'shade_temp_min')) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Effective Bridge Temp. Range} & """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MIN)) + r""" to """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MAX)) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Temperature Rise / Fall for Design} & +""" + (_render_value(input_dict, KEY_TL_TEMP_RISE)) + r""" $^\circ$C / \textminus{}""" + (_render_value(input_dict, KEY_TL_TEMP_FALL)) + r""" $^\circ$C \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|C{4.0cm}|p{11.5cm}|}
\caption{\textbf{Load Combinations}}
\hline
\textbf{Combination ID} & \textbf{Load Cases} \\[6pt]
\hline
""" + lc_rows_str + r"""
\end{longtable}

\noindent\textit{Note: All IRC 6 load combinations are auto-generated by OsdagBridge. User-defined custom combinations, if any, are appended.}
"""