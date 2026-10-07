import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

"""
Performing a preprocessing on the data by selecting only the cols we're working with and the granularity of the indices 
we want to use ( just to be clear, you can look at the variation of the price of the food, of the cheese or of 
a particular cheese)
"""

file_path = "data/raw/istat_data.csv"

df = pd.read_csv(
    file_path,
    sep=",",
    quotechar="'",
    escapechar='"',
    doublequote=False,
    encoding="utf-8-sig",
    low_memory=False
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

divisions = annual_indices[
    annual_indices["ECOICOP_2"].str.fullmatch(r"\d{2}")
    & (annual_indices["ECOICOP_2"] != "00")
].copy()

categories = (
    divisions[["ECOICOP_2", "ECOICOP 2"]]
    .drop_duplicates()
    .sort_values("ECOICOP_2")
)

print(categories.to_string(index=False))

# =================================================================================================================

# Read personal expenses specified by the user, perform some safety checks
expenses = pd.read_csv(
    "data/input/personal_expense.csv",
    dtype={"ECOICOP_2": str}
)

# Check if negative expenses
if (expenses["annual_expense"] < 0).any():
    raise ValueError("Expenses cannot be negative")

total_expense = expenses["annual_expense"].sum()

# Check if we have expenses
if total_expense == 0:
    raise ValueError("Total expenditure must be greater than zero")

# Create a new column "personal weight" that stores the weight of each category
expenses["personal_weight"] = (
    expenses["annual_expense"] / total_expense
)

# Merges ISTAT data with personal weights
personal_data = divisions.merge(
    expenses,
    on="ECOICOP_2", # match rows using the category code
    how="inner", # keep only categories present in both tables
    validate="many_to_one" # divisions can contain many rows for each code—one per year—but expenses
                           # must contain each code only once
)

# Personal contribution of each category
personal_data["contribution"] = (
    personal_data["personal_weight"]
    * personal_data["Osservazione"]
)


# sum the contribution of all the categories by year and rename the col
personal_indices = (
    personal_data
    .groupby("TIME_PERIOD", as_index=False)["contribution"]
    .sum()
    .rename(columns={"contribution": "personal_index"})
    .sort_values("TIME_PERIOD")
)

personal_indices["personal_inflation"] = (
    personal_indices["personal_index"]
    .pct_change(fill_method=None)
    .mul(100)
)

official_indices = annual_indices[
    annual_indices["ECOICOP_2"] == "00"
][["TIME_PERIOD", "Osservazione"]].copy()

official_indices = (
    official_indices
    .rename(columns={"Osservazione": "istat_index"})
    .sort_values("TIME_PERIOD")
)

official_indices["istat_inflation"] = (
    official_indices["istat_index"]
    .pct_change()
    .mul(100)
)

comparison = personal_indices.merge(
    official_indices,
    on="TIME_PERIOD",
    how="inner"
)

print(
    comparison[
        [
            "TIME_PERIOD",
            "personal_inflation",
            "istat_inflation"
        ]
    ].to_string(index=False)
)

# ============================================== Plotting ============================================================
plot_data = comparison.dropna(
    subset=["personal_inflation", "istat_inflation"]
)

plt.figure(figsize=(10, 6))

plt.plot(
    plot_data["TIME_PERIOD"],
    plot_data["personal_inflation"],
    marker="o",
    linewidth=2,
    label="Personal inflation"
)

plt.plot(
    plot_data["TIME_PERIOD"],
    plot_data["istat_inflation"],
    marker="o",
    linewidth=2,
    label="ISTAT inflation"
)

plt.axhline(
    y=0,
    color="black",
    linewidth=0.8
)

plt.title("Personal inflation compared with ISTAT inflation")
plt.xlabel("Year")
plt.ylabel("Annual inflation (%)")

plt.grid(
    True,
    linestyle="--",
    alpha=0.4
)

plt.legend()
plt.tight_layout()
plt.show()

# ====================================================================================================================

# Saving on GitHub the processed dataset
processed_indices = annual_indices[
    annual_indices["ECOICOP_2"].str.fullmatch(r"\d{2}")
][
    [
        "ECOICOP_2",
        "ECOICOP 2",
        "TIME_PERIOD",
        "Osservazione"
    ]
].copy()

processed_indices = (
    processed_indices
    .dropna(subset=["TIME_PERIOD", "Osservazione"])
    .drop_duplicates()
    .sort_values(["TIME_PERIOD", "ECOICOP_2"])
)

output_path = Path("data/processed/annual_indices.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

processed_indices.to_csv(output_path, index=False)

print(f"Saved processed data to {output_path}")
print(processed_indices.shape)