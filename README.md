# Personal Inflation Calculator

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Data](https://img.shields.io/badge/Data-ISTAT-0066CC)

A Streamlit application that estimates how inflation affects an individual consumer based on their actual spending habits.

Official inflation describes the price evolution of a representative national basket. Real households, however, do not all distribute their expenditure in the same way. Someone who spends a large share on transport may experience price changes differently from someone whose budget is concentrated on housing, food, or services.

This project lets users build a personal consumer basket, calculates a reweighted historical inflation series, and compares it with the official Italian ISTAT inflation index.

<!-- After deploying the app, add the public link here:
[Open the live application](https://YOUR-APP-NAME.streamlit.app)
-->

## Screenshots

The following image paths are already prepared. Create the folder `assets/screenshots`, add your screenshots with the filenames below, and remove the surrounding HTML comments.

<!--
### Build your basket

![Personal inflation basket input](assets/screenshots/basket-input.png)

### Explore your results

![Personal inflation results dashboard](assets/screenshots/results-dashboard.png)

### Understand the difference

![Comparison between personal and ISTAT spending weights](assets/screenshots/spending-insights.png)
-->

## Main features

- Build a basket using either **annual amounts in euros** or **percentage shares**.
- Choose between broad ECOICOP divisions and more detailed subcategories.
- Calculate a personal historical inflation series from ISTAT price indices.
- Compare personal inflation with the official Italian NIC index.
- View the latest personal rate, official rate, and difference in percentage points.
- Inspect the categories in which personal spending differs most from the official ISTAT basket.
- Explore an interactive historical chart and a detailed annual results table.
- Edit the basket without losing the previously entered values.
- Use the application on desktop or mobile through a responsive Streamlit interface.

## How to use the application

### 1. Select an input method

Choose one of the two available modes:

- **Amounts (€):** enter estimated annual expenditure for each category. The application converts the amounts into weights automatically.
- **Percentages (%):** enter the share of the budget assigned to each category. The values must sum to exactly 100%.

Only the relative distribution matters. For example, an annual basket of `€4,000`, `€3,000`, and `€3,000` produces the same weights as `40%`, `30%`, and `30%`.

### 2. Build the personal basket

Enter a value for each relevant main category, such as:

- food and non-alcoholic beverages;
- housing and utilities;
- transport;
- health;
- recreation and culture;
- restaurants and accommodation.

Enable **Use detailed categories** when a more precise breakdown is useful. Transport, for example, can be divided into vehicle purchases, use of personal transport, passenger transport, and transport of goods.

The application avoids counting a main category and its subcategories at the same time: each division is represented either by its total or by the detailed values selected by the user.

### 3. Calculate the result

Click **Calculate inflation**. The application validates the input, constructs the personal weights, applies them to the historical category indices, and opens a separate results view.

### 4. Interpret the dashboard

The results page contains:

- **Personal inflation:** the estimated annual rate for the selected basket;
- **ISTAT inflation:** the official annual rate for the general NIC index;
- **Difference:** personal inflation minus official inflation, expressed in percentage points;
- **Historical comparison:** an interactive chart showing both series over time;
- **Spending insight:** a pop-up identifying where the personal basket assigns substantially more or less weight than ISTAT;
- **Detailed results:** the annual values used in the chart.

A positive difference does not mean that every item became more expensive. It means that the categories receiving greater weight in the personal basket experienced, in combination, a larger price increase than the official basket.

## Methodology

Let $e_i$ be the expenditure entered for category $i$. The personal weight is:

$$
w_i = \frac{e_i}{\sum_j e_j}
$$

The weights therefore sum to one. When percentages are entered directly, the same normalization is obtained after validation.

For every year $t$, the personal price index is calculated as a weighted combination of the category-level price indices:

$$
P_t^{\text{personal}} = \sum_i w_i P_{i,t}
$$

The personal annual inflation rate is then:

$$
\pi_t^{\text{personal}}
=
\left(
\frac{P_t^{\text{personal}}}{P_{t-1}^{\text{personal}}} - 1
\right) \times 100
$$

The official comparison series is calculated from the general ISTAT index identified by ECOICOP code `00`:

$$
\pi_t^{\text{ISTAT}}
=
\left(
\frac{P_t^{\text{ISTAT}}}{P_{t-1}^{\text{ISTAT}}} - 1
\right) \times 100
$$

The application applies the same personal spending distribution to every historical year. The output should therefore be interpreted as a counterfactual estimate: **how historical price changes would have affected the currently selected consumer profile**.

## Data

The project uses data published by the Italian National Institute of Statistics (**ISTAT**):

- annual national consumer price indices;
- the general NIC index for the entire population;
- ECOICOP product categories and subcategories;
- the official 2026 NIC weighting structure.

In 2026, ISTAT adopted ECOICOP version 2, organized into 13 expenditure divisions. The preprocessing scripts clean the downloaded files, repair malformed rows where necessary, select the relevant hierarchy levels, and generate the compact CSV files used by the application.

Official sources:

- [ISTAT consumer-price data](https://www.istat.it/tavole-di-dati/prezzi-al-consumo-dati/)
- [ISTAT 2026 basket and weighting structure](https://www.istat.it/comunicato-stampa/gli-indici-dei-prezzi-al-consumo-anno-2026/)

### Processed files

| File | Purpose |
| --- | --- |
| `data/processed/annual_indices.csv` | Annual general, division-level, and subcategory price indices |
| `data/processed/istat_weights_2026.csv` | Official 2026 NIC basket weights by main division |

Raw ISTAT files can be kept locally and excluded from Git when they are large. The processed files required by the deployed application must remain in the repository.

## Project structure

```text
personal-inflation/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── processed/
│       ├── annual_indices.csv
│       └── istat_weights_2026.csv
├── src/
│   ├── __init__.py
│   └── inflation.py
├── data_preprocessing_annual.py
└── weights_preprocessing.py
```

### Main components

- `app.py` contains the Streamlit interface, navigation, visual styling, input validation, charts, and explanatory insights.
- `src/inflation.py` contains the personal inflation and basket-weight comparison logic.
- `data_preprocessing_annual.py` prepares the annual ISTAT price-index dataset.
- `weights_preprocessing.py` converts the official ISTAT weighting spreadsheet into the format used by the app.

## Run the project locally

### Prerequisites

- Python 3.10 or newer;
- Git;
- the processed CSV files included in the repository.

### 1. Clone the repository

```bash
git clone https://github.com/Tommaso-Vigano/personal-inflation.git
cd personal-inflation
```

### 2. Create a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install the dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The minimum runtime dependencies are:

```txt
streamlit
pandas
plotly
```

`openpyxl` is additionally required only when running `weights_preprocessing.py` on the original Excel workbook.

### 4. Start the application

```bash
streamlit run app.py
```

Streamlit will display a local address, normally `http://localhost:8501`.

## Rebuild the processed datasets

The application itself reads only the processed CSV files. Rebuilding them is optional and requires the original ISTAT downloads in the expected local paths.

Install the preprocessing dependency:

```bash
pip install openpyxl
```

Then run:

```bash
python data_preprocessing_annual.py
python weights_preprocessing.py
```

Review the generated files before committing them, particularly after ISTAT changes its classification, base year, or published schema.

## Deploy on Streamlit Community Cloud

### 1. Push the project to GitHub

Make sure the following deployment files are committed:

- `app.py`;
- `src/inflation.py`;
- `requirements.txt`;
- `data/processed/annual_indices.csv`;
- `data/processed/istat_weights_2026.csv`.

Then push the current version:

```bash
git add .
git commit -m "Prepare Streamlit deployment"
git push
```

### 2. Create the Streamlit application

1. Open [Streamlit Community Cloud](https://share.streamlit.io/).
2. Sign in with the GitHub account that owns the repository.
3. Select **Create app** and choose **Deploy a public app from GitHub**.
4. Use these values:
   - repository: `Tommaso-Vigano/personal-inflation`;
   - branch: `main`;
   - main file path: `app.py`.
5. Choose an available application URL.
6. Click **Deploy**.

Streamlit installs the packages listed in `requirements.txt`, starts `app.py`, and provides a public `.streamlit.app` URL.

### 3. Publish future updates

The deployment remains connected to the GitHub repository. To update the live application:

```bash
git add .
git commit -m "Describe the update"
git push
```

Streamlit normally detects the new commit and rebuilds the app automatically. If it does not, open **Manage app** from the deployed application and select **Reboot app**.

### Common deployment problems

| Error | Likely cause | Solution |
| --- | --- | --- |
| `This branch does not exist` | The branch has not been pushed or has another name | Run `git branch -M main` followed by `git push -u origin main` |
| `ModuleNotFoundError: plotly` | `plotly` is missing from `requirements.txt` | Add it, commit, and push again |
| `ModuleNotFoundError: src` | The `src` directory was not committed | Commit `src/__init__.py` and `src/inflation.py` |
| `FileNotFoundError` for a CSV | A processed data file is absent or ignored | Commit both files under `data/processed/` |
| App does not reflect a new commit | The deployment has not rebuilt yet | Wait briefly or reboot it from **Manage app** |

## Adding screenshots to this README

Create the screenshot directory:

```bash
mkdir -p assets/screenshots
```

On Windows, you can also create `assets` and `screenshots` directly from PyCharm.

Recommended filenames:

```text
assets/screenshots/basket-input.png
assets/screenshots/results-dashboard.png
assets/screenshots/spending-insights.png
```

Then remove the HTML comment markers around the prepared image section near the beginning of this README and push the images:

```bash
git add README.md assets/screenshots
git commit -m "Add application screenshots"
git push
```

## Limitations

- The result is an estimate, not an official personalized statistic produced by ISTAT.
- Spending weights are assumed to remain constant throughout the historical period.
- The calculation does not model substitutions between products when relative prices change.
- Accuracy depends on the detail and quality of the expenditure entered by the user.
- Annual indices cannot describe short-term differences within a year.
- Categories that are broad or unavailable at the chosen level may hide substantial variation among individual products.

## Possible improvements

- support monthly inflation estimates;
- allow users to save or export baskets and results;
- add shareable result summaries;
- visualize the complete difference between personal and official basket weights;
- update ISTAT weights automatically when a new annual structure is published;
- add tests for preprocessing, category selection, and inflation calculations;
- provide Italian and English interface options.

## Disclaimer

This project is intended for educational and informational purposes. It is not financial advice, and its output should not be interpreted as an official ISTAT measure.

## Author

**Tommaso Viganò**

- GitHub: [@Tommaso-Vigano](https://github.com/Tommaso-Vigano)

