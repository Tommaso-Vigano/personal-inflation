# Personal Inflation Calculator

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Data](https://img.shields.io/badge/Data-ISTAT-0066CC)

A Streamlit application that estimates how inflation affects an individual consumer based on their actual spending habits.

Official inflation describes the price evolution of a representative national basket. Real households, however, do not all distribute their expenditure in the same way. Someone who spends a large share on transport may experience price changes differently from someone whose budget is concentrated on housing, food, or services.

This project lets users build a personal consumer basket, calculates a reweighted historical inflation series, and compares it with the official Italian ISTAT inflation index.

[Open the live application](https://mypersonalinflation.streamlit.app)


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


## Disclaimer

This project is intended for educational and informational purposes. It is not financial advice, and its output should not be interpreted as an official ISTAT measure.

## Author

**Tommaso Viganò**

- GitHub: [@Tommaso-Vigano](https://github.com/Tommaso-Vigano)

