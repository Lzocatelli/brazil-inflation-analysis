import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Page configuration
st.set_page_config(
    page_title="IPCA Inflation Dashboard", 
    page_icon="📈", 
    layout="wide"
)

# Custom Styling
st.title("📊 Brazilian Inflation Analysis (IPCA)")
st.markdown("""
This dashboard analyzes the historical behavior of the **IPCA** (Extended National Consumer Price Index), 
extracting real-time data from the **Central Bank of Brazil (BCB)** API.
*Developed as a Data Analytics portfolio project to demonstrate ETL, Data Visualization, and Financial Analysis.*
""")

# Data Loading with Caching for Performance
@st.cache_data
def fetch_inflation_data():
    """
    Fetches historical IPCA data from the BCB Time Series Management System (SGS).
    Series 433: IPCA - Monthly variation (%)
    """
    url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        df = pd.DataFrame(data)
        df['data'] = pd.to_datetime(df['data'], dayfirst=True)
        df['valor'] = df['valor'].astype(float)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Load data
df = fetch_inflation_data()

if not df.empty:
    # Sidebar - Filtering
    st.sidebar.header("Filter Settings")
    
    # Date Range Selector
    min_date = df['data'].min().to_pydatetime()
    max_date = df['data'].max().to_pydatetime()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

    # Filtering logic (Handle single date selection or range)
    if len(date_range) == 2:
        mask = (df['data'] >= pd.Timestamp(date_range[0])) & (df['data'] <= pd.Timestamp(date_range[1]))
        df_filtered = df.loc[mask].copy()
    else:
        df_filtered = df.copy()

    # Calculation: Cumulative Inflation for the selected period
    # Formula: [(1 + i1) * (1 + i2) * ... * (1 + in) - 1] * 100
    cumulative_inflation = (((df_filtered['valor'] / 100) + 1).prod() - 1) * 100

    # Key Performance Indicators (KPIs)
    col1, col2, col3 = st.columns(3)
    col1.metric("Cumulative Inflation (Period)", f"{cumulative_inflation:.2f}%")
    col2.metric("Average Monthly Rate", f"{df_filtered['valor'].mean():.2f}%")
    col3.metric("Highest Monthly Peak", f"{df_filtered['valor'].max():.2f}%")

    # Interactive Chart with Plotly
    st.subheader("Monthly Variation Over Time")
    fig = px.line(
        df_filtered, 
        x='data', 
        y='valor', 
        labels={'data': 'Date', 'valor': 'Monthly Variation (%)'},
        template="plotly_white"
    )
    fig.update_traces(line_color='#007BFF')
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    # Data Insights & Raw Data Table
    with st.expander("View Detailed Dataset"):
        st.dataframe(df_filtered.sort_values(by='data', ascending=False), use_container_width=True)

else:
    st.warning("No data available to display.")

from statsmodels.tsa.arima.model import ARIMA
import numpy as np

# --- Place this after the Plotly Chart section ---

st.markdown("---")
st.subheader("🚀 Predictive Analytics: Inflation Forecast")

with st.expander("About this Forecast"):
    st.write("""
    This model uses **ARIMA (AutoRegressive Integrated Moving Average)** to predict the next 6 months of IPCA. 
    It analyzes past trends and seasonality to project future values.
    """)

# Preparation for Forecasting
# ARIMA requires a fixed frequency; we'll set it to Monthly ('MS')
df_forecast = df.copy().sort_values('data')
df_forecast = df_forecast.set_index('data')
df_forecast = df_forecast.asfreq('MS')

try:
    # Fit ARIMA Model (Order parameters p,d,q - simplified for this demo)
    # In a real scenario, you'd tune these, but (5,1,0) is a solid baseline for monthly data
    model = ARIMA(df_forecast['valor'], order=(5, 1, 0))
    model_fit = model.fit()

    # Forecast the next 6 months
    forecast_steps = 6
    forecast_result = model_fit.get_forecast(steps=forecast_steps)
    forecast_df = forecast_result.summary_frame()

    # Create a DataFrame for the forecast plot
    last_date = df_forecast.index[-1]
    forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=forecast_steps, freq='MS')
    
    predict_df = pd.DataFrame({
        'Date': forecast_dates,
        'Forecast': forecast_df['mean'].values,
        'Lower Bound': forecast_df['mean_ci_lower'].values,
        'Upper Bound': forecast_df['mean_ci_upper'].values
    })

    # Plotting Forecast
    fig_forecast = px.line(predict_df, x='Date', y='Forecast', title="6-Month IPCA Projection")
    
    # Add Confidence Interval (Shaded area)
    fig_forecast.add_scatter(x=predict_df['Date'], y=predict_df['Upper Bound'], line=dict(width=0), showlegend=False, name='Upper Bound')
    fig_forecast.add_scatter(x=predict_df['Date'], y=predict_df['Lower Bound'], line=dict(width=0), fill='tonexty', fillcolor='rgba(0,123,255,0.2)', showlegend=False, name='Lower Bound')
    
    st.plotly_chart(fig_forecast, use_container_width=True)

    # Prediction Insight
    avg_pred = predict_df['Forecast'].mean()
    st.info(f"The model predicts an average monthly inflation of **{avg_pred:.2f}%** for the next semester.")

except Exception as e:
    st.warning("Could not generate forecast. This usually happens if the data series is too short or has gaps.")

# Footer
st.markdown("---")
st.caption("Data Source: Central Bank of Brazil (BCB) | Analysis: Luiz Zocatelli")