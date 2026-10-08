from pathlib import Path

import pandas as pd


weights_path = "data/raw/istat_weights_2026.xlsx"

# Row 3 of the spreadsheet contains the real column names.
# Using positional columns avoids problems with spaces in their names.
weights = pd.read_excel(
    weights_path,
    sheet_name="2026",
    header=3,
    usecols=[0, 1, 2],
    dtype={0: str}
)

weights.columns = [
    "ECOICOP_2",
    "category_it",
    "weight_raw"
]

weights["ECOICOP_2"] = (
    weights["ECOICOP_2"]
    .astype("string")
    .str.strip()
)

weights["weight_raw"] = pd.to_numeric(
    weights["weight_raw"],
    errors="coerce"
)

# Keep only the 13 main categories:
# 01, 02, ..., 13
division_weights = weights[
    weights["ECOICOP_2"].str.fullmatch(
        r"\d{2}",
        na=False
    )
].copy()

division_weights = division_weights.dropna(
    subset=["weight_raw"]
)

# Normalise the official weights so they sum to 1
official_total = division_weights["weight_raw"].sum()

division_weights["istat_weight"] = (
    division_weights["weight_raw"]
    / official_total
)

division_weights["istat_percentage"] = (
    division_weights["istat_weight"] * 100
)

division_weights = (
    division_weights
    .sort_values("ECOICOP_2")
    .reset_index(drop=True)
)

output_path = Path(
    "data/processed/istat_weights_2026.csv"
)

output_path.parent.mkdir(
    parents=True,
    exist_ok=True
)

division_weights.to_csv(
    output_path,
    index=False
)

print(division_weights.to_string(index=False))

print(
    "\nTotal official weight:",
    division_weights["istat_weight"].sum()
)

print(f"\nSaved processed weights to {output_path}")