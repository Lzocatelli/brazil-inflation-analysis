import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from statsmodels.tsa.arima.model import ARIMA

# Page configuration
st.set_page_config(
    page_title="IPCA Inflation Dashboard", 
    page_icon="📈", 
    layout="wide"
)

# Custom Styling
st.title("📊 Brazilian Inflation Analysis (IPCA)")
st.markdown("""
This dashboard analyzes the historical behavior of the **IPCA**, extracting real-time data from the **Central Bank of Brazil (BCB)**.
*Developed as a Data Analytics portfolio project to demonstrate ETL, Financial Math, and Predictive Modeling.*
""")

@st.cache_data
def fetch_inflation_data():
    url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        df = pd.DataFrame(response.json())
        df['data'] = pd.to_datetime(df['data'], dayfirst=True)
        df['valor'] = df['valor'].astype(float)
        return df.sort_values('data')
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

df = fetch_inflation_data()

if not df.empty:
    # Sidebar - Filtering
    st.sidebar.header("Filter Settings")
    
    min_date = df['data'].min().to_pydatetime()
    max_date = df['data'].max().to_pydatetime()
    
    # Setting default view to post-2000 to avoid hyperinflation noise
    default_start = pd.to_datetime('2000-01-01').to_pydatetime()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=[default_start, max_date],
        min_value=min_date,
        max_value=max_date
    )

    if len(date_range) == 2:
        mask = (df['data'] >= pd.Timestamp(date_range[0])) & (df['data'] <= pd.Timestamp(date_range[1]))
        df_filtered = df.loc[mask].copy()
    else:
        df_filtered = df.copy()

    # Calculations
    cumulative_inflation = (((df_filtered['valor'] / 100) + 1).prod() - 1) * 100
    avg_monthly = df_filtered['valor'].mean()
    peak_monthly = df_filtered['valor'].max()

    # KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Cumulative Inflation (Period)", f"{cumulative_inflation:.2f}%")
    col2.metric("Average Monthly Rate", f"{avg_monthly:.2f}%")
    col3.metric("Highest Monthly Peak", f"{peak_monthly:.2f}%")

    # Main Chart
    st.subheader("Monthly Variation Over Time")
    fig = px.line(df_filtered, x='data', y='valor', template="plotly_white",
                  labels={'data': 'Date', 'valor': 'Variation (%)'})
    fig.update_traces(line_color='#007BFF')
    st.plotly_chart(fig, use_container_width=True)

    # Forecasting Section (ARIMA)
    st.markdown("---")
    st.subheader("🚀 Predictive Analytics: 6-Month Forecast")
    
    try:
        # Prepare series for ARIMA
        ts_data = df.set_index('data')['valor'].asfreq('MS')
        model = ARIMA(ts_data, order=(5, 1, 0))
        model_fit = model.fit()
        
        forecast = model_fit.get_forecast(steps=6)
        forecast_df = forecast.summary_frame()
        
        # Create dates for forecast
        last_date = ts_data.index[-1]
        f_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=6, freq='MS')
        
        predict_plot = pd.DataFrame({
            'Date': f_dates,
            'Forecast': forecast_df['mean'].values,
            'Lower Bound': forecast_df['mean_ci_lower'].values,
            'Upper Bound': forecast_df['mean_ci_upper'].values
        })

        fig_f = px.line(predict_plot, x='Date', y='Forecast', title="Projected IPCA (Next 6 Months)")
        fig_f.add_scatter(x=predict_plot['Date'], y=predict_plot['Upper Bound'], line=dict(width=0), showlegend=False)
        fig_f.add_scatter(x=predict_plot['Date'], y=predict_plot['Lower Bound'], line=dict(width=0), fill='tonexty', fillcolor='rgba(0,123,255,0.2)', showlegend=False)
        st.plotly_chart(fig_f, use_container_width=True)
        
        st.info(f"The model estimates an average monthly inflation of {predict_plot['Forecast'].mean():.2f}% for the next semester.")

    except Exception as e:
        st.warning("Forecasting model unavailable for the selected range.")

    with st.expander("View Raw Data"):
        st.dataframe(df_filtered.sort_values(by='data', ascending=False), use_container_width=True)

st.caption("Data Source: BCB | Project by: Lucas Zocatelli")