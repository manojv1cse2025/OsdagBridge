import os
import re
import logging
from osdagbridge.core.utils.common import (
    KEY_MP_GD_MEMBER_ID,
    KEY_MP_GD_SELECT_GIRDER,
    KEY_MP_GIRDER_DEPTH,
    KEY_TS_NO_OF_GIRDERS,
)
from osdagbridge.core.reports.styles import CHART_STYLE, TABLE_STYLE

logger = logging.getLogger(__name__)


def _tex(value):
    """Escape a Python value for safe LaTeX embedding."""
    s = str(value) if value is not None else ''
    if not s:
        return r''
    for uni, ascii_ in [('∠', 'L'), ('ⅹ', 'x'), ('×', 'x')]:
        s = s.replace(uni, ascii_)
    s = s.replace('\\', r'\textbackslash{}')
    for ch, esc in [('&', r'\&'), ('%', r'\%'), ('$', r'\$'), ('#', r'\#'),
                    ('{', r'\{'), ('}', r'\}'),
                    ('_', r'\_\allowbreak{}'),
                    ('~', r'\textasciitilde{}'), ('^', r'\^{}')]:
        s = s.replace(ch, esc)
    s = s.replace(':', r':\allowbreak{}')
    return s


def _render_value(source_dict, key, unit=""):
    val = source_dict.get(key)
    if val in ("", None):
        return ""
    return _tex(val) + unit


def parse_float_safe(value, default=0.0):
    """Extract a float from numeric values or strings like '12.45 MT'."""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"[-+]?\d*\.?\d+", str(value).replace(",", ""))
    if match:
        try:
            return float(match.group())
        except ValueError:
            return default
    return default


def get_girder_entries(input_dict):
    """Retrieve all girder labels and member IDs from backend keys."""
    n = int(input_dict.get(KEY_TS_NO_OF_GIRDERS, 0))
    entries = []
    for i in range(1, n + 1):
        entries.append(
            (
                input_dict.get(f"{KEY_MP_GD_SELECT_GIRDER}.G{i}", ""),
                input_dict.get(f"{KEY_MP_GD_MEMBER_ID}.G{i}.M1", ""),
            )
        )
    return entries


def _fig_or_placeholder(path, caption, width=r'0.9\textwidth'):
    """Embed figure if path is provided, else show placeholder box."""
    if path:
        p = path.replace('\\', '/')
        return (r'\begin{figure}[H]' + '\n'
                r'\centering' + '\n'
                r'\includegraphics[width=' + width + ']{' + p + '}\n'
                r'\caption{' + caption + '}\n'
                r'\end{figure}')
    return (r'\begin{figure}[H]' + '\n'
            r'\centering' + '\n'
            r'\fbox{\parbox{0.97\textwidth}{' + '\n'
            r'\textit{[ PLACEHOLDER: ' + caption + r' ]}' + '\n'
            r'}}' + '\n'
            r'\caption*{' + caption + '}\n'
            r'\end{figure}')


def _fig_embed(path, caption, width=r'\textwidth', height=None):
    """Embed a real figure when path is provided; otherwise use an fbox placeholder."""
    if path:
        p = path.replace('\\', '/')
        opts = 'width=' + width
        if height:
            opts += ',height=' + height + ',keepaspectratio'
        return (r'\begin{figure}[H]' + '\n'
                r'\vspace{-0.3em}' + '\n'
                r'\centering' + '\n'
                r'\includegraphics[' + opts + ']{' + p + '}\n'
                r'\vspace{0.3em}' + '\n'
                r'\caption{\small ' + caption + '}\n'
                r'\vspace{-0.3em}' + '\n'
                r'\end{figure}')
    return (r'\noindent\fbox{\parbox{0.97\textwidth}{' + '\n'
            r'\textit{[ PLACEHOLDER: ' + caption + r' ]}' + '\n'
            r'}}')


# =============================================================================
# GLOBAL LONGTABLE REPEATING HEADER INJECTOR
# =============================================================================

def ensure_longtable_headers(tex_content: str) -> str:
    """
    Ensure every LaTeX longtable environment repeats its column header across
    page breaks using \\endfirsthead / \\endhead and applies the centralized
    header background color from styles.py.
    Tables that already define \\endhead are left untouched.
    """
    hdr_bg = TABLE_STYLE["header_bg_macro"]
    lt_pattern = re.compile(
        r"(\\begin\{longtable\}\{[^\n]+\}\s*\n)(.*?)(\\end\{longtable\})",
        re.DOTALL,
    )

    def _transform(match):
        start_tag, body, end_tag = match.group(1), match.group(2), match.group(3)
        if r"\endhead" in body:
            return match.group(0)

        # Match optional \caption{...} + \hline + single header row + \hline
        hdr_pattern = re.compile(
            r"^(?P<cap>(?:\\caption\{.*?\}(?:\s*\\\\)?\s*\n)?)"
            r"(?P<h1>\\hline\s*\n)"
            r"(?P<hrow>(?:(?!(?:\\hline|\\multirow|\\textnormal)).)*?\\\\(?:\[[^\]]*\])?\s*\n)"
            r"(?P<h2>\\hline\s*\n)",
            re.DOTALL,
        )
        m = hdr_pattern.match(body)
        if not m:
            return match.group(0)

        hrow = m.group("hrow")
        if r"\textbf" not in hrow:
            return match.group(0)

        cap_raw = m.group("cap").strip()
        if cap_raw:
            if not cap_raw.endswith(r"\\"):
                cap_line = cap_raw + r" \\" + "\n"
            else:
                cap_line = cap_raw + "\n"
        else:
            cap_line = ""

        # Count columns from unescaped '&' separators in header row
        ncols = len(re.findall(r"(?<!\\)&", hrow)) + 1
        styled_hrow = (
            hrow if r"\rowcolor" in hrow
            else rf"\rowcolor{{{hdr_bg}}} " + hrow
        )

        new_head = (
            cap_line
            + r"\hline" + "\n"
            + styled_hrow
            + r"\hline" + "\n"
            + r"\endfirsthead" + "\n"
            + rf"\multicolumn{{{ncols}}}{{l}}{{\small\textit{{(Continued from previous page)}}}} \\[4pt]" + "\n"
            + r"\hline" + "\n"
            + styled_hrow
            + r"\hline" + "\n"
            + r"\endhead" + "\n"
            + r"\hline" + "\n"
            + rf"\multicolumn{{{ncols}}}{{r}}{{\small\textit{{(Continued on next page)}}}} \\" + "\n"
            + r"\endfoot" + "\n"
            + r"\endlastfoot" + "\n"
        )

        rest = body[m.end():]
        return start_tag + new_head + rest + end_tag

    return lt_pattern.sub(_transform, tex_content)


# =============================================================================
# THREAD-SAFE MATPLOTLIB CHART GENERATORS (Sections 5.5 & Chapter 7)
# Uses matplotlib.figure.Figure + FigureCanvasAgg so Qt GUI threads never crash.
# =============================================================================

def generate_ur_summary_chart(ur_items: list, output_path: str) -> str:
    """
    Generate Utilization Ratio (Demand / Capacity) bar chart for Section 5.5.
    ur_items: list of (label, ur_value_or_None) tuples.
    Includes a red dashed threshold line at UR = 1.0.
    """
    try:
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_agg import FigureCanvasAgg

        cs = CHART_STYLE
        fig = Figure(figsize=cs["figsize_ur"], dpi=cs["dpi"])
        FigureCanvasAgg(fig)
        ax = fig.add_subplot(111)

        labels = [item[0] for item in ur_items]
        values = [item[1] if item[1] is not None else 0.0 for item in ur_items]
        is_na = [item[1] is None for item in ur_items]
        colors = [
            "#B0BEC5" if na else (cs["fail_color"] if v > 1.0 else cs["pass_color"])
            for v, na in zip(values, is_na)
        ]

        x_pos = range(len(labels))
        bars = ax.bar(x_pos, values, width=cs["bar_width"], color=colors, edgecolor="#333333", linewidth=0.7, zorder=3)

        # Red dashed threshold line at UR = 1.0
        ax.axhline(
            1.0,
            color=cs["threshold_red"],
            linestyle="--",
            linewidth=1.5,
            label="Limit (UR = 1.0)",
            zorder=4,
        )

        ymax = max(max(values, default=0.0) * 1.25, 1.25)
        ax.set_ylim(0, ymax)
        ax.set_ylabel("Utilization Ratio (UR = Demand / Capacity)", fontsize=cs["label_size"], fontweight="bold")
        ax.set_title("Overall Design Check Summary — Governing Utilization Ratios", fontsize=cs["title_size"], fontweight="bold", pad=12)
        ax.set_xticks(list(x_pos))
        ax.set_xticklabels(labels, fontsize=cs["tick_size"])
        ax.grid(axis="y", linestyle=":", alpha=cs["grid_alpha"], zorder=0)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        for bar, val, na in zip(bars, values, is_na):
            txt = "N/A" if na else f"{val:.2f}"
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                bar.get_height() + (ymax * 0.025),
                txt,
                ha="center",
                va="bottom",
                fontsize=cs["value_size"],
                fontweight="bold",
                color="#555555" if na else ("#C62828" if val > 1.0 else "#222222"),
            )

        ax.legend(loc="upper right", frameon=True, fontsize=cs["tick_size"])
        fig.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, dpi=cs["dpi"], bbox_inches="tight")
        return output_path
    except Exception as exc:
        logger.warning("Failed to generate UR summary chart: %s", exc)
        return ""


def generate_steel_tonnage_chart(steel_items: list, output_path: str) -> str:
    """
    Generate Structural Steel Tonnage bar chart for Chapter 7.
    steel_items: list of (label, tonnage_mt) tuples.
    """
    try:
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_agg import FigureCanvasAgg

        cs = CHART_STYLE
        fig = Figure(figsize=cs["figsize_mat"], dpi=cs["dpi"])
        FigureCanvasAgg(fig)
        ax = fig.add_subplot(111)

        labels = [item[0] for item in steel_items]
        values = [max(0.0, float(item[1])) for item in steel_items]
        x_pos = range(len(labels))

        bars = ax.bar(x_pos, values, width=cs["bar_width"], color=cs["steel_color"], edgecolor="#1B3A57", linewidth=0.7, zorder=3)
        ymax = max(max(values, default=0.0) * 1.25, 1.0)
        ax.set_ylim(0, ymax)
        ax.set_ylabel("Weight (Metric Tonnes, MT)", fontsize=cs["label_size"], fontweight="bold")
        ax.set_title("Structural Steel Tonnage Breakdown", fontsize=cs["title_size"], fontweight="bold", pad=12)
        ax.set_xticks(list(x_pos))
        ax.set_xticklabels(labels, fontsize=cs["tick_size"])
        ax.grid(axis="y", linestyle=":", alpha=cs["grid_alpha"], zorder=0)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                bar.get_height() + (ymax * 0.025),
                f"{val:.2f} MT",
                ha="center",
                va="bottom",
                fontsize=cs["value_size"],
                fontweight="bold",
            )

        fig.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, dpi=cs["dpi"], bbox_inches="tight")
        return output_path
    except Exception as exc:
        logger.warning("Failed to generate steel tonnage chart: %s", exc)
        return ""


def generate_concrete_vs_rebar_chart(concrete_m3: float, rebar_mt: float, output_path: str) -> str:
    """
    Generate Concrete Volume (m^3) vs. Reinforcement Steel Weight (MT) dual-axis
    bar chart for Chapter 7.
    """
    try:
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_agg import FigureCanvasAgg

        cs = CHART_STYLE
        fig = Figure(figsize=cs["figsize_mat"], dpi=cs["dpi"])
        FigureCanvasAgg(fig)
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx()

        c_val = max(0.0, float(concrete_m3))
        r_val = max(0.0, float(rebar_mt))

        b1 = ax1.bar([0], [c_val], width=0.42, color=cs["concrete_color"], edgecolor="#2C3E50", linewidth=0.7, zorder=3)
        b2 = ax2.bar([1], [r_val], width=0.42, color=cs["rebar_color"], edgecolor="#7E4A16", linewidth=0.7, zorder=3)

        y1_max = max(c_val * 1.28, 1.0)
        y2_max = max(r_val * 1.28, 1.0)
        ax1.set_ylim(0, y1_max)
        ax2.set_ylim(0, y2_max)

        ax1.set_ylabel("Concrete Volume (m³)", fontsize=cs["label_size"], fontweight="bold", color=cs["concrete_color"])
        ax2.set_ylabel("Reinforcement Steel Weight (MT)", fontsize=cs["label_size"], fontweight="bold", color=cs["rebar_color"])
        ax1.set_title("Deck Slab Concrete Volume vs. Reinforcement Steel Weight", fontsize=cs["title_size"], fontweight="bold", pad=12)
        ax1.set_xticks([0, 1])
        ax1.set_xticklabels(["Concrete Deck Slab\n(Volume, m³)", "Reinforcement Steel\n(Weight, MT)"], fontsize=cs["tick_size"])
        ax1.grid(axis="y", linestyle=":", alpha=cs["grid_alpha"], zorder=0)
        ax1.spines["top"].set_visible(False)
        ax2.spines["top"].set_visible(False)

        ax1.text(0, c_val + y1_max * 0.025, f"{c_val:.2f} m³", ha="center", va="bottom",
                 fontsize=cs["value_size"], fontweight="bold", color=cs["concrete_color"])
        ax2.text(1, r_val + y2_max * 0.025, f"{r_val:.2f} MT", ha="center", va="bottom",
                 fontsize=cs["value_size"], fontweight="bold", color=cs["rebar_color"])

        fig.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, dpi=cs["dpi"], bbox_inches="tight")
        return output_path
    except Exception as exc:
        logger.warning("Failed to generate concrete vs rebar chart: %s", exc)
        return ""