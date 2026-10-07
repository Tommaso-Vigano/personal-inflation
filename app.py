from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.inflation import calculate_comparison

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

# -------------------------------------------------------------------
# Page configuration
# -------------------------------------------------------------------

st.set_page_config(
    page_title="Personal Inflation",
    page_icon="📈",
    layout="wide"
)


# -------------------------------------------------------------------
# Styling
# -------------------------------------------------------------------

st.markdown(
    """
    <style>
        .block-container {
            max-width: 1250px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .hero {
            padding: 2rem;
            border-radius: 20px;
            color: white;
            background:
                linear-gradient(120deg, #111827 0%, #1e3a8a 60%, #2563eb 100%);
            margin-bottom: 2rem;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.18);
        }

        .hero h1 {
            margin: 0;
            font-size: 2.6rem;
        }

        .hero p {
            margin-top: 0.75rem;
            margin-bottom: 0;
            color: #dbeafe;
            font-size: 1.05rem;
        }

        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 1rem;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.10);
        }

        div[data-testid="stMetric"] [data-testid="stMetricLabel"],
        div[data-testid="stMetric"] [data-testid="stMetricLabel"] p {
            color: #64748b !important;
        }
        
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: #0f172a !important;
        }

        div[data-testid="stNumberInput"] {
            margin-bottom: 0.4rem;
        }

        .section-label {
            color: #64748b;
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.08rem;
            text-transform: uppercase;
            margin-bottom: 0.3rem;
        }

        .method-note {
            background: #f8fafc;
            border-left: 4px solid #2563eb;
            border-radius: 8px;
            padding: 1rem;
            color: #475569;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# -------------------------------------------------------------------
# Data loading
# -------------------------------------------------------------------

@st.cache_data
def load_indices() -> pd.DataFrame:
    data_path = (
        Path(__file__).parent
        / "data"
        / "processed"
        / "annual_indices.csv"
    )

    return pd.read_csv(
        data_path,
        dtype={
            "ECOICOP_2": str,
            "parent_code": str
        }
    )


indices = load_indices()

# Main two-digit categories
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
)

# Three-digit subcategories
subcategories = (
    indices[
        indices["category_level"] == 3
    ][
        [
            "ECOICOP_2",
            "ECOICOP 2",
            "parent_code"
        ]
    ]
    .drop_duplicates()
    .sort_values(["parent_code", "ECOICOP_2"])
    .reset_index(drop=True)
)

# -------------------------------------------------------------------
# Header
# -------------------------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>Personal Inflation Dashboard</h1>
        <p>
            Discover how inflation affects your personal spending basket
            and compare it with the official Italian ISTAT index.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# -------------------------------------------------------------------
# Input section
# -------------------------------------------------------------------

st.markdown(
    '<div class="section-label">Your spending profile</div>',
    unsafe_allow_html=True
)

st.subheader("Build your personal consumer basket")

input_mode = st.radio(
    "Input method",
    ["Amounts (€)", "Percentages (%)"],
    horizontal=True
)

icons = {
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
    "13": "🧴"
}

user_values = {}

input_step = (
    100.0
    if input_mode == "Amounts (€)"
    else 1.0
)

with st.expander("Configure spending categories", expanded=True):

    columns = st.columns(3)

    for position, (_, category) in enumerate(
        main_categories.iterrows()
    ):
        code = category["ECOICOP_2"]
        name = category["category_en"]
        icon = icons.get(code, "•")

        category_subcategories = subcategories[
            subcategories["parent_code"] == code
        ]

        with columns[position % 3]:

            st.markdown(f"#### {icon} {name}")

            use_detailed_categories = st.toggle(
                "Use detailed categories",
                key=f"detailed-{code}",
                disabled=category_subcategories.empty
            )

            if use_detailed_categories:

                for _, subcategory in (
                    category_subcategories.iterrows()
                ):
                    subcategory_code = subcategory["ECOICOP_2"]
                    subcategory_name = subcategory["ECOICOP 2"]

                    user_values[subcategory_code] = st.number_input(
                        subcategory_name,
                        min_value=0.0,
                        value=0.0,
                        step=input_step,
                        format="%.2f",
                        key=(
                            f"{input_mode}-"
                            f"{subcategory_code}"
                        )
                    )

            else:

                user_values[code] = st.number_input(
                    "Total category value",
                    min_value=0.0,
                    value=0.0,
                    step=input_step,
                    format="%.2f",
                    key=f"{input_mode}-{code}"
                )

            st.divider()


# -------------------------------------------------------------------
# Input summary
# -------------------------------------------------------------------

total = sum(user_values.values())

summary_col, button_col = st.columns([3, 1])

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
        use_container_width=True
    )


# -------------------------------------------------------------------
# Calculation
# -------------------------------------------------------------------

if calculate:

    if total <= 0:
        st.error("Enter at least one positive value.")

    elif input_mode == "Percentages (%)" and abs(total - 100) > 0.01:
        st.error("The percentages must sum to exactly 100%.")

    else:
        comparison = calculate_comparison(
            indices=indices,
            user_values=user_values
        )

        st.session_state["comparison"] = comparison


# -------------------------------------------------------------------
# Results dashboard
# -------------------------------------------------------------------

if "comparison" in st.session_state:

    comparison = st.session_state["comparison"]

    valid_results = comparison.dropna(
        subset=["Personal inflation", "ISTAT inflation"]
    )

    latest = valid_results.iloc[-1]

    latest_year = int(latest["TIME_PERIOD"])
    personal_value = latest["Personal inflation"]
    istat_value = latest["ISTAT inflation"]
    difference = personal_value - istat_value

    st.divider()

    st.markdown(
        '<div class="section-label">Results</div>',
        unsafe_allow_html=True
    )

    st.subheader(f"Inflation summary for {latest_year}")

    metric_1, metric_2, metric_3 = st.columns(3)

    metric_1.metric(
        "Personal inflation",
        f"{personal_value:.2f}%"
    )

    metric_2.metric(
        "ISTAT inflation",
        f"{istat_value:.2f}%"
    )

    metric_3.metric(
        "Difference",
        f"{difference:+.2f} pp",
        delta=f"{difference:+.2f} percentage points",
        delta_color="inverse"
    )


    st.subheader("Historical comparison")

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=valid_results["TIME_PERIOD"],
            y=valid_results["Personal inflation"],
            mode="lines+markers",
            name="Personal inflation",
            line={
                "color": "#f97316",
                "width": 3
            },
            marker={
                "size": 8
            },
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Personal inflation: %{y:.2f}%"
                "<extra></extra>"
            )
        )
    )

    figure.add_trace(
        go.Scatter(
            x=valid_results["TIME_PERIOD"],
            y=valid_results["ISTAT inflation"],
            mode="lines+markers",
            name="ISTAT inflation",
            line={
                "color": "#2563eb",
                "width": 3
            },
            marker={
                "size": 8
            },
            hovertemplate=(
                "<b>%{x}</b><br>"
                "ISTAT inflation: %{y:.2f}%"
                "<extra></extra>"
            )
        )
    )

    figure.add_hline(
        y=0,
        line_width=1,
        line_dash="dash",
        line_color="#94a3b8"
    )

    figure.update_layout(
        template="plotly_white",
        height=500,
        hovermode="x unified",
        margin={
            "l": 20,
            "r": 20,
            "t": 30,
            "b": 20
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1
        },
        xaxis_title="Year",
        yaxis_title="Annual inflation (%)"
    )

    st.plotly_chart(
        figure,
        use_container_width=True
    )

    with st.expander("View detailed results"):

        results_table = comparison[
            [
                "TIME_PERIOD",
                "Personal inflation",
                "ISTAT inflation"
            ]
        ].rename(
            columns={"TIME_PERIOD": "Year"}
        )

        st.dataframe(
            results_table.style.format({
                "Personal inflation": "{:.2f}%",
                "ISTAT inflation": "{:.2f}%"
            }),
            hide_index=True,
            use_container_width=True
        )

    st.markdown(
        """
        <div class="method-note">
            <strong>Methodology:</strong>
            the same personal spending distribution is applied to every
            historical year. The result therefore estimates how historical
            inflation would have affected the selected consumer profile.
        </div>
        """,
        unsafe_allow_html=True
    )