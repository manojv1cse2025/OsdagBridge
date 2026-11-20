# =============================================================================
# OsdagBridge — Centralized Report Formatting & Style System (Single Source of Truth)
# =============================================================================
# All page geometry, color palettes, typography, table spacing, header/footer
# themes, and matplotlib chart styling live here so global visual updates
# require editing only one file.
# =============================================================================

COLORS = {
    "osdag_green":     "91B014",
    "osdag_dark":      "2C3E50",
    "table_header_bg": "EEF4D7",
    "table_alt_row":   "F9FBF2",
    "pass_green":      "2E7D32",
    "fail_red":        "C62828",
    "warn_amber":      "EF6C00",
    "muted_gray":      "666666",
}

PAGE_GEOMETRY = {
    "paper":      "a4paper",
    "top":        "1.0in",
    "bottom":     "1.18in",   # Extra bottom clearance prevents table rows bleeding into footer
    "left":       "0.9in",
    "right":      "0.9in",
    "headheight": "16pt",
    "headsep":    "18pt",
    "footskip":   "32pt",     # Keeps footrule and "* Software default value" clear of body text
}

TYPOGRAPHY = {
    "doc_class_opts": "12pt,a4paper",
    "line_stretch":   "1.15",
}

TABLE_STYLE = {
    "tabcolsep":        "6pt",
    "arraystretch":     "1.15",
    "lt_pre":           "4pt",
    "lt_post":          "8pt",
    "arrayrulewidth":   "0.5pt",
    "extrarowheight":   "1.0pt",
    "needspace_lines":  6,
    "header_bg_macro":  "tableHeaderBg",
}

HEADER_FOOTER = {
    "footer_left":    r"Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay",
    "footer_right":   r"Page \thepage\ of \pageref{LastPage}",
    "rule_thickness": "1pt",
    "sd_note":        r"* Software default value",
}

CHART_STYLE = {
    "dpi":            300,
    "figsize_ur":     (7.4, 4.2),
    "figsize_mat":    (7.4, 4.0),
    "font_family":    "DejaVu Sans",
    "title_size":     11,
    "label_size":     9.5,
    "tick_size":      8.5,
    "value_size":     8.5,
    "bar_width":      0.50,
    "grid_alpha":     0.35,
    "pass_color":     "#6B8E23",
    "fail_color":     "#C62828",
    "steel_color":    "#2E6B9E",
    "concrete_color": "#5C768D",
    "rebar_color":    "#C97A2B",
    "threshold_red":  "#D32F2F",
}


def get_geometry_latex() -> str:
    g = PAGE_GEOMETRY
    return (
        rf"\usepackage[{g['paper']}, "
        rf"top={g['top']}, bottom={g['bottom']}, "
        rf"left={g['left']}, right={g['right']}, "
        rf"headheight={g['headheight']}, headsep={g['headsep']}, "
        rf"footskip={g['footskip']}]{{geometry}}"
    )


def get_colors_latex() -> str:
    return "\n".join([
        rf"\definecolor{{osdagGreen}}{{HTML}}{{{COLORS['osdag_green']}}}",
        rf"\definecolor{{osdagDark}}{{HTML}}{{{COLORS['osdag_dark']}}}",
        rf"\definecolor{{tableHeaderBg}}{{HTML}}{{{COLORS['table_header_bg']}}}",
        rf"\definecolor{{tableAltRow}}{{HTML}}{{{COLORS['table_alt_row']}}}",
        rf"\definecolor{{passGreen}}{{HTML}}{{{COLORS['pass_green']}}}",
        rf"\definecolor{{failRed}}{{HTML}}{{{COLORS['fail_red']}}}",
    ])


def get_table_spacing_latex() -> str:
    t = TABLE_STYLE
    return (
        rf"\setlength{{\tabcolsep}}{{{t['tabcolsep']}}}" + "\n"
        rf"\renewcommand{{\arraystretch}}{{{t['arraystretch']}}}" + "\n"
        rf"\setlength{{\LTpre}}{{{t['lt_pre']}}}" + "\n"
        rf"\setlength{{\LTpost}}{{{t['lt_post']}}}" + "\n"
        rf"\setlength{{\arrayrulewidth}}{{{t['arrayrulewidth']}}}" + "\n"
        rf"\setlength{{\extrarowheight}}{{{t['extrarowheight']}}}" + "\n"
        rf"\raggedbottom" + "\n"
        rf"\widowpenalty=10000" + "\n"
        rf"\clubpenalty=10000" + "\n"
        rf"\BeforeBeginEnvironment{{table}}{{\needspace{{{t['needspace_lines']}\baselineskip}}}}" + "\n"
        rf"\BeforeBeginEnvironment{{longtable}}{{\needspace{{{t['needspace_lines']}\baselineskip}}}}"
    )


def get_header_footer_latex(pn: str, jn: str, rd: str, rv: str) -> str:
    hf = HEADER_FOOTER
    footrule_def = (
        r"\renewcommand{\footrule}{%" + "\n"
        r"    \ifbool{hasSDonPage}{%" + "\n"
        r"      \vspace{-14pt}%" + "\n"
        r"      \hbox to \headwidth{\textcolor{black}{\footnotesize\textit{" + hf["sd_note"] + r"}}\hfil}%" + "\n"
        r"      \vspace{3pt}%" + "\n"
        r"    }{%" + "\n"
        r"      \vspace{-4pt}%" + "\n"
        r"    }%" + "\n"
        r"    \color{osdagGreen}\hrule width\headwidth height " + hf["rule_thickness"] + r" \vspace{4pt}%" + "\n"
        r"  }"
    )
    headrule_def = (
        r"\renewcommand{\headrule}{\color{osdagGreen}\hrule width\headwidth height "
        + hf["rule_thickness"] + r" \vspace{2pt}}"
    )

    body_style = (
        r"  \fancyhf{}" + "\n"
        r"  \fancyhead[L]{" + pn + r" $|$ " + jn + r"}" + "\n"
        r"  \fancyhead[R]{" + rd + r" $|$ " + rv + r"}" + "\n"
        r"  \fancyfoot[L]{" + hf["footer_left"] + r"}" + "\n"
        r"  \fancyfoot[R]{" + hf["footer_right"] + r"}" + "\n"
        r"  " + headrule_def + "\n"
        r"  " + footrule_def
    )

    return (
        r"\fancypagestyle{main}{" + "\n" + body_style + "\n}\n"
        r"\fancypagestyle{plain}{" + "\n" + body_style + "\n}\n"
        r"\fancypagestyle{firstpage}{" + "\n"
        r"  \fancyhf{}" + "\n"
        r"  \renewcommand{\headrulewidth}{0pt}" + "\n"
        r"  \fancyfoot[L]{" + hf["footer_left"] + r"}" + "\n"
        r"  \fancyfoot[R]{" + hf["footer_right"] + r"}" + "\n"
        r"  \renewcommand{\footrule}{\vspace{-4pt}\color{osdagGreen}\hrule width\headwidth height "
        + hf["rule_thickness"] + r" \vspace{4pt}}" + "\n"
        r"}" + "\n"
        r"\pagestyle{main}" + "\n"
        rf"\setstretch{{{TYPOGRAPHY['line_stretch']}}}"
    )


def get_toc_styling_latex() -> str:
    return r"""
% Chapter / TOC Formatting (centralized in styles.py)
\titleformat{\chapter}[block]
  {\normalfont\Large\bfseries\centering\color{osdagDark}}{\thechapter}{1em}{}
\titlespacing*{\chapter}{0pt}{0pt}{10pt}
\setcounter{tocdepth}{2}

\titlecontents{chapter}[1.5em]
  {\normalfont\vspace{2pt}}
  {\contentslabel{1.5em}}
  {\hspace*{-1.5em}}
  {\hfill\contentspage}

\titlecontents{section}[3.8em]
  {\normalfont}
  {\contentslabel{2.3em}}
  {\hspace*{-2.3em}}
  {\hfill\contentspage}

\titlecontents{subsection}[7.0em]
  {\normalfont}
  {\contentslabel{3.2em}}
  {\hspace*{-3.2em}}
  {\hfill\contentspage}

\newpage
\renewcommand{\contentsname}{\centering\Large\bfseries Table of Contents}
\tableofcontents
"""