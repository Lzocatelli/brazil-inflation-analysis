# 📊 Brazilian Inflation Analysis & Forecasting (IPCA) | Exploratory Data Analysis (EDA)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge.svg)](https://brazil-inflation-analysis.streamlit.app)

## 📌 Project Overview
This project provides a comprehensive analysis of the **IPCA (Extended National Consumer Price Index)**, Brazil's official inflation measure. It transitions from raw data extraction to an interactive business dashboard featuring predictive analytics.

### Why this matters:
Managing historical economic data in Brazil requires handling extreme volatility (hyperinflation) from the 80s/90s. This project demonstrates the ability to filter noise and deliver actionable insights for the modern economic landscape.

---

## 🛠️ Tech Stack
- **Language:** Python 3.10+
- **Libraries:** Pandas (Data Wrangling), Plotly (Interactive Viz), Requests (API Integration).
- **Econometrics:** Statsmodels (ARIMA Model).
- **Deployment:** Streamlit Cloud.
- **Data Source:** Central Bank of Brazil (BCB) API.

---

## 📈 Key Features

### 1. Automated ETL Pipeline
- Direct integration with the BCB API to fetch real-time monthly variation data.
- Automated data cleaning and datetime transformation.

### 2. Business Intelligence Dashboard
- **Cumulative Inflation Calculation:** Implemented financial math to calculate compounded inflation over selected periods.
- **Dynamic Filtering:** Default view set to post-2000 to focus on the Real Plan's stability, avoiding the 911 trillion % hyperinflation skew.

### 3. Predictive Modeling (ARIMA)
- Applied an **ARIMA (5,1,0)** model to forecast the next 6 months of inflation.
- Visualized confidence intervals (Lower/Upper bounds) to represent statistical uncertainty.

---

## 🧠 Business Insights
- **The "Real" Scale:** By filtering the start date to 2000, we observed a cumulative inflation of **~366.04%**, providing a much more relevant metric for current pricing and investment strategies than the raw historical series.
- **Seasonality:** The dashboard helps identify seasonal peaks in Brazilian consumer prices.

---

## 🚀 How to Run Locally
1. Clone the repo: `git clone https://github.com/Lzocatelli/brazil-inflation-analysis.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `streamlit run app.py`
