from html import escape
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.inflation import (
    calculate_comparison,
    calculate_weight_comparison,
)


CATEGORY_NAMES_EN = {
    "01": "Food and non-alcoholic beverages",
    "02": "Alcoholic beverages, tobacco and narcotics",
    "03": "Clothing and footwear",
    "04": "Housing, water, electricity, gas and other fuels",
    "05": "Furnishings and household maintenance",
    "06": "Health",
    "07": "Transport",
    "08": "Information and communication",
    "09": "Recreation, sport and culture",
    "10": "Education services",
    "11": "Restaurants and accommodation services",
    "12": "Financial and insurance services",
    "13": "Personal care, social protection and miscellaneous services",
}

SUBCATEGORY_NAMES_EN = {
    "011": "Food",
    "012": "Non-alcoholic beverages",
    "021": "Alcoholic beverages",
    "023": "Tobacco",
    "031": "Clothing",
    "032": "Footwear",
    "041": "Actual rentals for housing",
    "043": "Maintenance, repair and security of the dwelling",
    "044": "Water supply and miscellaneous dwelling services",
    "045": "Electricity, gas and other fuels",
    "051": "Furniture, furnishings and carpets",
    "052": "Household textiles",
    "053": "Household appliances",
    "054": "Glassware, tableware and household utensils",
    "055": "Tools and equipment for house and garden",
    "056": "Goods and services for routine household maintenance",
    "061": "Medicines and health products",
    "062": "Outpatient care services",
    "063": "Hospital services",
    "064": "Other health services",
    "071": "Purchase of vehicles",
    "072": "Operation of personal transport equipment",
    "073": "Passenger transport services",
    "074": "Transport services of goods",
    "081": "Information and communication equipment",
    "083": "Information and communication services",
    "091": "Recreational durables",
    "092": "Other recreational goods",
    "093": "Garden products and pets",
    "094": "Recreational services",
    "095": "Cultural goods",
    "096": "Cultural services",
    "097": "Newspapers, books and stationery",
    "098": "Package holidays",
    "101": "Early childhood and primary education",
    "102": "Secondary education",
    "104": "Tertiary education",
    "105": "Education not definable by level",
    "111": "Food and beverage serving services",
    "112": "Accommodation services",
    "121": "Insurance services",
    "122": "Financial services",
    "131": "Personal care",
    "132": "Other personal effects",
    "133": "Social protection",
    "139": "Other services",
}

CATEGORY_ICONS = {
    "01": "🛒",
    "02": "🍷",
    "03": "👕",
    "04": "🏠",
    "05": "🛋️",
    "06": "🏥",
    "07": "🚗",
    "08": "📱",
    "09": "🎮",
    "10": "🎓",
    "11": "🍽️",
    "12": "🛡️",
    "13": "🧴",
}


st.set_page_config(
    page_title="Personal Inflation",
    page_icon="📈",
    layout="wide",
)


st.markdown(
    """
    <style>
        .block-container {
            max-width: 1180px;
            padding-top: 1.5rem;
            padding-bottom: 3.5rem;
            position: relative;
            z-index: 2;
        }

        [data-testid="stAppViewContainer"] {
            background:
                linear-gradient(
                    180deg,
                    color-mix(in srgb, var(--background-color) 94%, #2563eb 6%) 0%,
                    var(--background-color) 32%,
                    var(--background-color) 100%
                );
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        /* Hide Streamlit's automatic heading permalink icons. */
        [data-testid="stHeaderActionElements"],
        [data-testid="stHeaderLink"],
        .stHeadingWithActionElements a,
        a.header-anchor {
            display: none !important;
            visibility: hidden !important;
        }

        .ambient-background {
            position: fixed;
            inset: 0;
            z-index: 0;
            overflow: hidden;
            pointer-events: none;
        }

        .ambient-grid {
            position: absolute;
            inset: 0;
            opacity: 0.18;
            background-image:
                linear-gradient(rgba(148, 163, 184, 0.08) 1px, transparent 1px),
                linear-gradient(90deg, rgba(148, 163, 184, 0.08) 1px, transparent 1px);
            background-size: 56px 56px;
            mask-image: linear-gradient(to bottom, black, transparent 72%);
        }

        .ambient-orb {
            position: absolute;
            border-radius: 999px;
            filter: blur(85px);
            opacity: 0.16;
            will-change: transform;
        }

        .ambient-orb.one {
            width: 420px;
            height: 420px;
            top: -140px;
            right: -80px;
            background: #2563eb;
            animation: orb-drift-one 18s ease-in-out infinite alternate;
        }

        .ambient-orb.two {
            width: 340px;
            height: 340px;
            top: 42%;
            left: -170px;
            background: #7c3aed;
            animation: orb-drift-two 22s ease-in-out infinite alternate;
        }

        .hero {
            padding: 2.25rem 2.4rem;
            border-radius: 22px;
            color: white;
            background:
                radial-gradient(circle at 85% 15%, rgba(96, 165, 250, 0.35), transparent 30%),
                linear-gradient(125deg, #0f172a 0%, #172554 48%, #1d4ed8 100%);
            margin-bottom: 2rem;
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.22);
            border: 1px solid rgba(191, 219, 254, 0.16);
            position: relative;
            overflow: hidden;
            isolation: isolate;
            animation: hero-arrive 700ms cubic-bezier(0.16, 1, 0.3, 1) both;
        }

        .hero::before {
            content: "";
            position: absolute;
            width: 360px;
            height: 360px;
            top: -230px;
            right: -70px;
            border-radius: 50%;
            border: 1px solid rgba(219, 234, 254, 0.24);
            box-shadow:
                0 0 0 48px rgba(219, 234, 254, 0.035),
                0 0 0 96px rgba(219, 234, 254, 0.02);
            z-index: -1;
        }

        .hero::after {
            content: "";
            position: absolute;
            inset: -120% auto -120% -35%;
            width: 18%;
            transform: rotate(18deg);
            background: linear-gradient(
                90deg,
                transparent,
                rgba(255, 255, 255, 0.12),
                transparent
            );
            animation: hero-sheen 9s ease-in-out 1.2s infinite;
            pointer-events: none;
        }

        .hero-kicker {
            color: #bfdbfe;
            font-size: 0.75rem;
            font-weight: 750;
            letter-spacing: 0.12rem;
            text-transform: uppercase;
            margin-bottom: 0.55rem;
        }

        .hero h1 {
            margin: 0;
            font-size: clamp(2rem, 4vw, 2.75rem);
            letter-spacing: -0.04em;
        }

        .hero p {
            max-width: 760px;
            margin: 0.8rem 0 0;
            color: #dbeafe;
            font-size: 1.03rem;
            line-height: 1.6;
        }

        .section-label {
            color: #64748b;
            font-size: 0.76rem;
            font-weight: 750;
            letter-spacing: 0.1rem;
            text-transform: uppercase;
            margin-bottom: 0.25rem;
            animation: section-label-arrive 520ms ease-out both;
        }

        h2, h3 {
            letter-spacing: -0.025em;
            animation: heading-arrive 520ms cubic-bezier(0.16, 1, 0.3, 1) both;
        }

        div[data-testid="stMetric"] {
            min-height: 132px;
            background: color-mix(
                in srgb,
                var(--secondary-background-color) 88%,
                transparent
            );
            border: 1px solid rgba(148, 163, 184, 0.24);
            border-radius: 16px;
            padding: 1.05rem 1.15rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.07);
            backdrop-filter: blur(14px);
            transition:
                transform 180ms ease,
                border-color 180ms ease,
                box-shadow 180ms ease;
            animation: content-rise 600ms cubic-bezier(0.16, 1, 0.3, 1) both;
        }

        div[data-testid="stMetric"]:hover {
            transform: translateY(-3px);
            border-color: rgba(37, 99, 235, 0.36);
            box-shadow: 0 14px 34px rgba(15, 23, 42, 0.12);
        }

        div[data-testid="stMetric"] [data-testid="stMetricLabel"],
        div[data-testid="stMetric"] [data-testid="stMetricLabel"] p {
            color: #64748b !important;
            font-weight: 650;
        }

        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: var(--text-color) !important;
        }

        div[data-testid="stNumberInput"] {
            margin-bottom: 0.4rem;
        }

        div[data-testid="stNumberInput"] input {
            transition:
                border-color 180ms ease,
                box-shadow 180ms ease,
                background-color 180ms ease;
        }

        div[data-testid="stNumberInput"] input:focus {
            border-color: rgba(37, 99, 235, 0.72);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.14);
        }

        div[data-testid="stRadio"] {
            animation: control-arrive 540ms ease-out both;
        }

        div[data-testid="stToggle"] {
            transition: transform 160ms ease;
        }

        div[data-testid="stToggle"]:hover {
            transform: translateX(2px);
        }

        div[data-testid="stExpander"] {
            border: 1px solid rgba(148, 163, 184, 0.22);
            border-radius: 16px;
            overflow: hidden;
            background: color-mix(
                in srgb,
                var(--secondary-background-color) 74%,
                transparent
            );
            backdrop-filter: blur(12px);
            transition:
                border-color 200ms ease,
                box-shadow 200ms ease,
                transform 200ms ease;
            animation: panel-arrive 620ms cubic-bezier(0.16, 1, 0.3, 1) both;
        }

        div[data-testid="stExpander"]:hover {
            border-color: rgba(37, 99, 235, 0.30);
            box-shadow: 0 12px 36px rgba(15, 23, 42, 0.08);
        }

        .stButton > button {
            border-radius: 10px;
            transition:
                transform 160ms ease,
                box-shadow 160ms ease,
                border-color 160ms ease;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 20px rgba(37, 99, 235, 0.16);
        }

        .stButton > button:active {
            transform: translateY(0);
        }

        div[data-testid="stPopover"] button {
            border: 0;
            background: transparent;
            padding: 0.2rem 0;
            color: #64748b;
            font-size: 0.9rem;
            font-weight: 650;
            box-shadow: none;
        }

        div[data-testid="stPopover"] button:hover {
            border: 0;
            background: transparent;
            color: #2563eb;
        }

        div[data-testid="stPopover"] button:focus {
            box-shadow: none;
        }

        .insight-card {
            background: var(--secondary-background-color);
            border: 1px solid rgba(148, 163, 184, 0.25);
            border-radius: 12px;
            padding: 0.9rem 1rem;
            margin: 0.7rem 0;
        }

        .insight-card.user {
            border-left: 4px solid #2563eb;
        }

        .insight-card.istat {
            border-left: 4px solid #f97316;
        }

        .insight-label {
            color: #64748b;
            font-size: 0.7rem;
            font-weight: 750;
            letter-spacing: 0.07rem;
            text-transform: uppercase;
            margin-bottom: 0.3rem;
        }

        .insight-category {
            color: var(--text-color);
            font-size: 1rem;
            font-weight: 720;
            line-height: 1.35;
            margin-bottom: 0.4rem;
        }

        .insight-values {
            color: var(--text-color);
            font-size: 0.88rem;
            line-height: 1.55;
        }

        .positive-gap {
            color: #2563eb;
            font-weight: 750;
        }

        .negative-gap {
            color: #f97316;
            font-weight: 750;
        }

        .method-note {
            background: var(--secondary-background-color);
            border: 1px solid rgba(148, 163, 184, 0.20);
            border-left: 4px solid #2563eb;
            border-radius: 10px;
            padding: 1rem 1.1rem;
            color: #64748b;
            line-height: 1.55;
            animation: panel-arrive 620ms cubic-bezier(0.16, 1, 0.3, 1) both;
        }

        .screen-note {
            color: #64748b;
            font-size: 0.92rem;
            margin-top: -0.25rem;
            margin-bottom: 1rem;
            animation: content-fade 620ms ease-out both;
        }

        div[data-testid="stAlert"] {
            border-radius: 12px;
            animation: notice-arrive 480ms cubic-bezier(0.16, 1, 0.3, 1) both;
        }

        div[data-testid="stPlotlyChart"] {
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 18px;
            padding: 0.35rem;
            background: color-mix(
                in srgb,
                var(--secondary-background-color) 58%,
                transparent
            );
            backdrop-filter: blur(10px);
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
            animation: chart-arrive 760ms cubic-bezier(0.16, 1, 0.3, 1) both;
            transition:
                border-color 200ms ease,
                box-shadow 200ms ease;
        }

        div[data-testid="stPlotlyChart"]:hover {
            border-color: rgba(37, 99, 235, 0.28);
            box-shadow: 0 16px 42px rgba(15, 23, 42, 0.10);
        }

        div[data-testid="stDataFrame"] {
            animation: panel-arrive 620ms cubic-bezier(0.16, 1, 0.3, 1) both;
        }

        div[data-testid="stPopoverBody"] {
            animation: popover-fade 180ms ease-out both;
        }

        div[data-testid="stPopoverBody"] > div {
            animation: popover-content-arrive 220ms cubic-bezier(0.16, 1, 0.3, 1) both;
        }

        @keyframes hero-arrive {
            from {
                opacity: 0;
                transform: translateY(14px) scale(0.992);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        @keyframes content-rise {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes content-fade {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes section-label-arrive {
            from {
                opacity: 0;
                transform: translateX(-8px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        @keyframes heading-arrive {
            from {
                opacity: 0;
                transform: translateY(8px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes control-arrive {
            from {
                opacity: 0;
                transform: translateY(6px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes panel-arrive {
            from {
                opacity: 0;
                transform: translateY(12px) scale(0.995);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        @keyframes chart-arrive {
            from {
                opacity: 0;
                transform: translateY(18px) scale(0.985);
                filter: blur(3px);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
                filter: blur(0);
            }
        }

        @keyframes notice-arrive {
            from {
                opacity: 0;
                transform: translateX(-10px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        @keyframes popover-fade {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes popover-content-arrive {
            from {
                opacity: 0;
                transform: translateY(-4px) scale(0.985);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        @keyframes hero-sheen {
            0%, 68% {
                left: -35%;
                opacity: 0;
            }
            74% {
                opacity: 1;
            }
            88%, 100% {
                left: 125%;
                opacity: 0;
            }
        }

        @keyframes orb-drift-one {
            from { transform: translate3d(0, 0, 0) scale(1); }
            to { transform: translate3d(-70px, 85px, 0) scale(1.14); }
        }

        @keyframes orb-drift-two {
            from { transform: translate3d(0, 0, 0) scale(1); }
            to { transform: translate3d(95px, -55px, 0) scale(1.12); }
        }

        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                scroll-behavior: auto !important;
                transition-duration: 0.01ms !important;
            }
        }

        @media (max-width: 700px) {
            .block-container {
                padding-top: 0.8rem;
            }

            .hero {
                padding: 1.6rem;
                border-radius: 18px;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_indices() -> pd.DataFrame:
    data_path = Path(__file__).parent / "data" / "processed" / "annual_indices.csv"

    return pd.read_csv(
        data_path,
        dtype={
            "ECOICOP_2": str,
            "parent_code": str,
        },
    )


@st.cache_data
def load_official_weights() -> pd.DataFrame:
    weights_path = (
        Path(__file__).parent
        / "data"
        / "processed"
        / "istat_weights_2026.csv"
    )

    return pd.read_csv(
        weights_path,
        dtype={"ECOICOP_2": str},
    )


def prepare_categories(
    indices: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    main_categories = (
        indices[
            (indices["category_level"] == 2)
            & (indices["ECOICOP_2"] != "00")
        ][["ECOICOP_2", "ECOICOP 2"]]
        .drop_duplicates()
        .sort_values("ECOICOP_2")
        .reset_index(drop=True)
    )

    main_categories["category_en"] = (
        main_categories["ECOICOP_2"]
        .map(CATEGORY_NAMES_EN)
        .fillna(main_categories["ECOICOP 2"])
    )

    subcategories = (
        indices[indices["category_level"] == 3][
            ["ECOICOP_2", "ECOICOP 2", "parent_code"]
        ]
        .drop_duplicates()
        .sort_values(["parent_code", "ECOICOP_2"])
        .reset_index(drop=True)
    )

    subcategories["subcategory_en"] = (
        subcategories["ECOICOP_2"]
        .map(SUBCATEGORY_NAMES_EN)
        .fillna(subcategories["ECOICOP 2"])
    )

    return main_categories, subcategories


def render_hero() -> None:
    st.markdown(
        """
        <div class="ambient-background" aria-hidden="true">
            <div class="ambient-grid"></div>
            <div class="ambient-orb one"></div>
            <div class="ambient-orb two"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">Personal economics</div>
            <h1>Personal Inflation Dashboard</h1>
            <p>
                Build a basket around your real spending habits, estimate how
                inflation affects you, and compare the result with the official
                Italian ISTAT index.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_insight_card(
    card_type: str,
    label: str,
    category: str,
    user_percentage: float,
    istat_percentage: float,
    gap: float,
) -> None:
    gap_class = "positive-gap" if gap >= 0 else "negative-gap"
    safe_label = escape(label)
    safe_category = escape(category)

    html = (
        f'<div class="insight-card {card_type}">'
        f'<div class="insight-label">{safe_label}</div>'
        f'<div class="insight-category">{safe_category}</div>'
        '<div class="insight-values">'
        f'Your basket: <strong>{user_percentage:.1f}%</strong>'
        f' · ISTAT: <strong>{istat_percentage:.1f}%</strong><br>'
        f'<span class="{gap_class}">{gap:+.1f} percentage points</span>'
        "</div>"
        "</div>"
    )

    st.markdown(html, unsafe_allow_html=True)


def build_history_figure(valid_results: pd.DataFrame) -> go.Figure:
    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=valid_results["TIME_PERIOD"],
            y=valid_results["Personal inflation"],
            mode="lines+markers",
            name="Personal inflation",
            line={"color": "#f97316", "width": 3},
            marker={"size": 7},
            hovertemplate=(
                "<b>%{x}</b><br>Personal inflation: %{y:.2f}%<extra></extra>"
            ),
        )
    )

    figure.add_trace(
        go.Scatter(
            x=valid_results["TIME_PERIOD"],
            y=valid_results["ISTAT inflation"],
            mode="lines+markers",
            name="ISTAT inflation",
            line={"color": "#2563eb", "width": 3},
            marker={"size": 7},
            hovertemplate=(
                "<b>%{x}</b><br>ISTAT inflation: %{y:.2f}%<extra></extra>"
            ),
        )
    )

    figure.add_hline(
        y=0,
        line_width=1,
        line_dash="dash",
        line_color="#94a3b8",
    )

    figure.update_layout(
        height=480,
        hovermode="x unified",
        margin={"l": 15, "r": 15, "t": 25, "b": 15},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
        },
        xaxis_title="Year",
        yaxis_title="Annual inflation (%)",
    )

    return figure


def render_input_screen(
    indices: pd.DataFrame,
    official_weights: pd.DataFrame,
    main_categories: pd.DataFrame,
    subcategories: pd.DataFrame,
) -> None:
    st.markdown(
        '<div class="section-label">Your spending profile</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Build your personal consumer basket")
    st.markdown(
        '<div class="screen-note">Use broad categories for a quick estimate, '
        "or open the detailed categories when you know how your spending is split.</div>",
        unsafe_allow_html=True,
    )

    saved_mode = st.session_state.get("saved_input_mode", "Amounts (€)")
    input_options = ["Amounts (€)", "Percentages (%)"]
    input_mode = st.radio(
        "Input method",
        input_options,
        index=input_options.index(saved_mode),
        horizontal=True,
        key="input-mode",
    )

    input_step = 100.0 if input_mode == "Amounts (€)" else 1.0
    saved_values = st.session_state.get("saved_basket_values", {})
    saved_details = st.session_state.get("saved_detail_choices", {})
    user_values: dict[str, float] = {}
    detail_choices: dict[str, bool] = {}

    with st.expander("Configure spending categories", expanded=True):
        columns = st.columns(3)

        for position, (_, category) in enumerate(main_categories.iterrows()):
            code = category["ECOICOP_2"]
            name = category["category_en"]
            icon = CATEGORY_ICONS.get(code, "•")
            category_subcategories = subcategories[
                subcategories["parent_code"] == code
            ]

            with columns[position % 3]:
                st.markdown(f"#### {icon} {name}")

                use_details = st.toggle(
                    "Use detailed categories",
                    value=bool(saved_details.get(code, False)),
                    key=f"detailed-{code}",
                    disabled=category_subcategories.empty,
                )
                detail_choices[code] = use_details

                if use_details:
                    for _, subcategory in category_subcategories.iterrows():
                        subcategory_code = subcategory["ECOICOP_2"]
                        subcategory_name = subcategory["subcategory_en"]

                        user_values[subcategory_code] = st.number_input(
                            subcategory_name,
                            min_value=0.0,
                            value=float(saved_values.get(subcategory_code, 0.0)),
                            step=input_step,
                            format="%.2f",
                            key=f"{input_mode}-{subcategory_code}",
                        )
                else:
                    user_values[code] = st.number_input(
                        "Total category value",
                        min_value=0.0,
                        value=float(saved_values.get(code, 0.0)),
                        step=input_step,
                        format="%.2f",
                        key=f"{input_mode}-{code}",
                    )

                st.divider()

    total = sum(user_values.values())
    summary_col, button_col = st.columns([3, 1], vertical_alignment="center")

    with summary_col:
        if input_mode == "Amounts (€)":
            st.info(f"Total annual expenditure entered: €{total:,.2f}")
        else:
            st.progress(min(total / 100, 1.0))
            st.caption(f"Allocated percentage: {total:.2f}% of 100%")

    with button_col:
        calculate = st.button(
            "Calculate inflation",
            type="primary",
            use_container_width=True,
        )

    if not calculate:
        return

    if total <= 0:
        st.error("Enter at least one positive value.")
        return

    if input_mode == "Percentages (%)" and abs(total - 100) > 0.01:
        st.error("The percentages must sum to exactly 100%.")
        return

    comparison = calculate_comparison(
        indices=indices,
        user_values=user_values,
    )
    weight_comparison = calculate_weight_comparison(
        user_values=user_values,
        official_weights=official_weights,
    )

    st.session_state["comparison"] = comparison
    st.session_state["weight_comparison"] = weight_comparison
    st.session_state["saved_basket_values"] = user_values.copy()
    st.session_state["saved_detail_choices"] = detail_choices.copy()
    st.session_state["saved_input_mode"] = input_mode
    st.session_state["screen"] = "results"
    st.rerun()


def render_results_screen() -> None:
    comparison = st.session_state["comparison"]
    weight_comparison = st.session_state["weight_comparison"].copy()

    weight_comparison["category_en"] = (
        weight_comparison["ECOICOP_2"]
        .map(CATEGORY_NAMES_EN)
        .fillna(weight_comparison["category_it"])
    )

    valid_results = comparison.dropna(
        subset=["Personal inflation", "ISTAT inflation"]
    )

    if valid_results.empty:
        st.error("No comparable inflation results are available for this basket.")
        if st.button("← Edit basket"):
            st.session_state["screen"] = "input"
            st.rerun()
        return

    latest = valid_results.iloc[-1]
    latest_year = int(latest["TIME_PERIOD"])
    personal_value = latest["Personal inflation"]
    istat_value = latest["ISTAT inflation"]
    difference = personal_value - istat_value

    header_col, action_col = st.columns([5, 1], vertical_alignment="bottom")

    with header_col:
        st.markdown(
            '<div class="section-label">Your results</div>',
            unsafe_allow_html=True,
        )
        st.subheader(f"Inflation summary for {latest_year}")

    with action_col:
        if st.button("← Edit basket", use_container_width=True):
            st.session_state["screen"] = "input"
            st.rerun()

    metric_1, metric_2, metric_3 = st.columns(3)
    metric_1.metric("Personal inflation", f"{personal_value:.2f}%")
    metric_2.metric("ISTAT inflation", f"{istat_value:.2f}%")
    metric_3.metric(
        "Difference",
        f"{difference:+.2f} pp",
        delta=f"{difference:+.2f} percentage points",
        delta_color="inverse",
    )

    user_emphasises_more = weight_comparison.loc[
        weight_comparison["weight_gap"].idxmax()
    ]
    istat_emphasises_more = weight_comparison.loc[
        weight_comparison["weight_gap"].idxmin()
    ]

    with st.popover("How do your spending habits differ?  ⓘ"):
        st.markdown("#### Your basket compared with ISTAT")
        st.caption(
            "Your entries are converted into shares of total expenditure and "
            "compared with the official 2026 ISTAT consumer basket."
        )

        render_insight_card(
            card_type="user",
            label="You assign more importance to",
            category=user_emphasises_more["category_en"],
            user_percentage=user_emphasises_more["user_percentage"],
            istat_percentage=user_emphasises_more["istat_percentage"],
            gap=user_emphasises_more["gap_percentage_points"],
        )
        render_insight_card(
            card_type="istat",
            label="ISTAT assigns more importance to",
            category=istat_emphasises_more["category_en"],
            user_percentage=istat_emphasises_more["user_percentage"],
            istat_percentage=istat_emphasises_more["istat_percentage"],
            gap=istat_emphasises_more["gap_percentage_points"],
        )

        st.caption(
            "A larger basket weight does not necessarily mean greater inflation. "
            "The final effect also depends on how prices changed in that category."
        )

    st.markdown("### Historical comparison")
    figure = build_history_figure(valid_results)
    st.plotly_chart(
        figure,
        use_container_width=True,
        theme="streamlit",
    )

    with st.expander("View detailed results"):
        results_table = comparison[
            ["TIME_PERIOD", "Personal inflation", "ISTAT inflation"]
        ].rename(columns={"TIME_PERIOD": "Year"})

        st.dataframe(
            results_table.style.format(
                {
                    "Personal inflation": "{:.2f}%",
                    "ISTAT inflation": "{:.2f}%",
                }
            ),
            hide_index=True,
            use_container_width=True,
        )

    st.markdown(
        """
        <div class="method-note">
            <strong>Methodology:</strong> the same personal spending
            distribution is applied to every historical year. The result
            estimates how historical inflation would have affected the
            selected consumer profile.
        </div>
        """,
        unsafe_allow_html=True,
    )


indices = load_indices()
official_weights = load_official_weights()
main_categories, subcategories = prepare_categories(indices)

if "screen" not in st.session_state:
    st.session_state["screen"] = "input"

render_hero()

has_results = (
    "comparison" in st.session_state
    and "weight_comparison" in st.session_state
)

if st.session_state["screen"] == "results" and has_results:
    render_results_screen()
else:
    st.session_state["screen"] = "input"
    render_input_screen(
        indices=indices,
        official_weights=official_weights,
        main_categories=main_categories,
        subcategories=subcategories,
    )
