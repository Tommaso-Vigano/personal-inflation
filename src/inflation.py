import pandas as pd


def calculate_comparison(
    indices: pd.DataFrame,
    user_values: dict[str, float]
) -> pd.DataFrame:

    total = sum(user_values.values())

    if total <= 0:
        raise ValueError("Total expenditure must be greater than zero.")

    expenses = pd.DataFrame({
        "ECOICOP_2": list(user_values.keys()),
        "personal_weight": [
            value / total
            for value in user_values.values()
        ]
    })

    # Select the price indices chosen by the user.
    # These can be either main categories (01, 02, ...)
    # or subcategories (011, 012, ...).
    selected_category_indices = indices[
        indices["ECOICOP_2"].isin(expenses["ECOICOP_2"])
        & (indices["ECOICOP_2"] != "00")
        ].copy()

    selected_category_indices["Osservazione"] = pd.to_numeric(
        selected_category_indices["Osservazione"],
        errors="coerce"
    )

    personal_data = selected_category_indices.merge(
        expenses,
        on="ECOICOP_2",
        how="inner",
        validate="many_to_one"
    )

    personal_data["weighted_index"] = (
        personal_data["personal_weight"]
        * personal_data["Osservazione"]
    )

    personal_indices = (
        personal_data
        .groupby("TIME_PERIOD", as_index=False)["weighted_index"]
        .sum()
        .rename(columns={"weighted_index": "personal_index"})
        .sort_values("TIME_PERIOD")
    )

    personal_indices["Personal inflation"] = (
        personal_indices["personal_index"]
        .pct_change(fill_method=None)
        .mul(100)
    )

    # Official ISTAT indices
    istat_indices = indices[
        indices["ECOICOP_2"] == "00"
    ][["TIME_PERIOD", "Osservazione"]].copy()

    istat_indices["Osservazione"] = pd.to_numeric(
        istat_indices["Osservazione"],
        errors="coerce"
    )

    istat_indices = (
        istat_indices
        .rename(columns={"Osservazione": "istat_index"})
        .sort_values("TIME_PERIOD")
    )

    istat_indices["ISTAT inflation"] = (
        istat_indices["istat_index"]
        .pct_change(fill_method=None)
        .mul(100)
    )

    return personal_indices.merge(
        istat_indices,
        on="TIME_PERIOD",
        how="inner"
    )

def calculate_weight_comparison(
    user_values: dict[str, float],
    official_weights: pd.DataFrame
) -> pd.DataFrame:

    total = sum(user_values.values())

    if total <= 0:
        raise ValueError(
            "Total expenditure must be greater than zero."
        )

    user_weights = pd.DataFrame({
        "selected_code": list(user_values.keys()),
        "user_value": list(user_values.values())
    })

    # Both main categories and subcategories are compared
    # at the main-category level.
    #
    # Examples:
    # 01  -> 01
    # 011 -> 01
    # 012 -> 01
    user_weights["ECOICOP_2"] = (
        user_weights["selected_code"].str[:2]
    )

    user_weights = (
        user_weights
        .groupby("ECOICOP_2", as_index=False)["user_value"]
        .sum()
    )

    user_weights["user_weight"] = (
        user_weights["user_value"] / total
    )

    comparison = official_weights[
        [
            "ECOICOP_2",
            "category_it",
            "istat_weight"
        ]
    ].merge(
        user_weights[
            [
                "ECOICOP_2",
                "user_weight"
            ]
        ],
        on="ECOICOP_2",
        how="left",
        validate="one_to_one"
    )

    # Categories not selected by the user have weight zero.
    comparison["user_weight"] = (
        comparison["user_weight"].fillna(0.0)
    )

    # Positive: user assigns more importance than ISTAT.
    # Negative: ISTAT assigns more importance than the user.
    comparison["weight_gap"] = (
        comparison["user_weight"]
        - comparison["istat_weight"]
    )

    comparison["user_percentage"] = (
        comparison["user_weight"] * 100
    )

    comparison["istat_percentage"] = (
        comparison["istat_weight"] * 100
    )

    comparison["gap_percentage_points"] = (
        comparison["weight_gap"] * 100
    )

    comparison["absolute_gap"] = (
        comparison["weight_gap"].abs()
    )

    return (
        comparison
        .sort_values(
            "absolute_gap",
            ascending=False
        )
        .reset_index(drop=True)
    )