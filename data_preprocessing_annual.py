import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

"""
Performing a preprocessing on the data by selecting only the cols we're working with and the granularity of the indices 
we want to use ( just to be clear, you can look at the variation of the price of the food, of the cheese or of 
a particular cheese)
"""

file_path = "../data/raw/istat_data.csv"

df = pd.read_csv(
    file_path,
    sep=",",
    quotechar="'",
    escapechar='"',
    doublequote=False,
    encoding="utf-8-sig",
    low_memory=False
)

measure_columns = [
    column
    for column in df.columns
    if "MEASURE" in column.upper()
    or "MISUR" in column.upper()
]

print(
    df[measure_columns]
    .drop_duplicates()
    .sort_values(measure_columns)
    .to_string(index=False)
)

df = df[df["REF_AREA"] == "IT"].copy()
# MEASURE = 4 contains the price indices
annual_indices = df[df["MEASURE"] == 4].copy()

# Keep only the cols we actually need
annual_indices = annual_indices[['ECOICOP_2', 'ECOICOP 2',
'TIME_PERIOD', 'Osservazione']]

# The file seems formatted wrongly. In fact in some rows the columns "ECOICOP 2" and "TIME_PERIOD" are merged.
# In order to fix this problem we have to detect the wrongly specified rows and then perform the fix
annual_indices["TIME_PERIOD"] = (
    annual_indices["TIME_PERIOD"].astype("string")
)

year_pattern = r"\d{4}"
# Boolean mask to detect broken rows
broken = ~annual_indices["TIME_PERIOD"].astype(str).str.fullmatch(
    year_pattern
)

"""
To see some wrong formatted lines look at this print

print(
    annual_indices.loc[broken]
    .head(30)
    .to_string(index=False)
)
"""

# Select only the broken rows and the column "ECOICOP 2", then using a RegEx find the pattern miss-used and extract
# extracted[0]   Category name
# extracted[1]   Year
# because the wrong line is like: Viaggi "tutto compreso",2016
extracted = annual_indices.loc[
    broken, "ECOICOP 2"
].str.extract(r"^(.*),(\d{4})$")

repairable = extracted[1].notna()
year_to_fix_indices = extracted.index[repairable]

# Take the TIME_PERIOD in the line to correct since they're currently storing the Observations index
old_observations = pd.to_numeric(
    annual_indices.loc[year_to_fix_indices, "TIME_PERIOD"],
    errors="coerce"
)

# Repair the three columns
annual_indices.loc[year_to_fix_indices, "ECOICOP 2"] = (
    extracted.loc[year_to_fix_indices, 0].str.strip()
)

annual_indices.loc[year_to_fix_indices, "TIME_PERIOD"] = (
    extracted.loc[year_to_fix_indices, 1]
)

annual_indices.loc[year_to_fix_indices, "Osservazione"] = old_observations

# Convert to numeric values the Observations
annual_indices["Osservazione"] = pd.to_numeric(
    annual_indices["Osservazione"],
    errors="coerce"
)

# ================= CURRENT CATEGORICAL SEPARATION, MAYBE LATER A MORE DEEP ONE ===================================
# For the moment I select only the 12 top-level categories
annual_indices["ECOICOP_2"] = annual_indices["ECOICOP_2"].astype(str)

# Keep:
# 00  = official general index
# XX  = main categories
# XXX = subcategories
selected_indices = annual_indices[
    annual_indices["ECOICOP_2"].eq("00")
    | annual_indices["ECOICOP_2"].str.fullmatch(r"\d{2,3}", na=False)
].copy()

selected_indices["category_level"] = (
    selected_indices["ECOICOP_2"].str.len()
)

selected_indices["parent_code"] = (
    selected_indices["ECOICOP_2"].str[:2]
)

categories = (
    selected_indices[
        (selected_indices["category_level"] == 2)
        & (selected_indices["ECOICOP_2"] != "00")
    ][["ECOICOP_2", "ECOICOP 2"]]
    .drop_duplicates()
    .sort_values("ECOICOP_2")
)

print(categories.to_string(index=False))

# =================================================================================================================


# Saving on GitHub the processed dataset
# Save the general index, main categories and subcategories
processed_indices = selected_indices[
    [
        "ECOICOP_2",
        "ECOICOP 2",
        "TIME_PERIOD",
        "Osservazione",
        "category_level",
        "parent_code"
    ]
].copy()

processed_indices = (
    processed_indices
    .dropna(subset=["TIME_PERIOD", "Osservazione"])
    .drop_duplicates()
    .sort_values(
        ["TIME_PERIOD", "category_level", "ECOICOP_2"]
    )
)

output_path = Path("../data/processed/annual_indices.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

processed_indices.to_csv(output_path, index=False)

print(f"Saved processed data to {output_path}")
print(processed_indices.shape)

print("\nNumber of categories by level:")
print(
    processed_indices
    .groupby("category_level")["ECOICOP_2"]
    .nunique()
)

categories = (
    selected_indices[
        (selected_indices["category_level"] == 2)
        & (selected_indices["ECOICOP_2"] != "00")
    ][["ECOICOP_2", "ECOICOP 2"]]
    .drop_duplicates()
    .sort_values("ECOICOP_2")
)

# Extract three-digit subcategories
subcategories = (
    selected_indices[
        selected_indices["category_level"] == 3
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

print("\nMain categories:")
print(categories.to_string(index=False))

print("\nSubcategories:")
print(subcategories.to_string(index=False))