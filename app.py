# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objs as go
# from datetime import datetime, timedelta

# from data_retrieval import BinanceDataRetriever
# from forecasting import BTCForecaster
# from streamlit_autorefresh import st_autorefresh


# def load_recent_data(hours=24):
#     """
#     Load recent data from the last specified hours
    
#     :param hours: Number of hours of data to load
#     :return: Filtered DataFrame
#     """
#     try:
#         # Read CSV
#         df = pd.read_csv('data/btcusdt_trades.csv')
#         df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
#         # Filter to recent data
#         cutoff = datetime.now() - timedelta(hours=hours)
#         recent_df = df[df['Timestamp'] > cutoff]
        
#         # Additional data preparation can be done here
#         return recent_df
#     except Exception as e:
#         st.error(f"Error loading data: {e}")
#         return pd.DataFrame()


# def perform_forecast():
#     """
#     Perform price forecasting with memoization
    
#     :return: Forecast data
#     """
#     try:
#         forecaster = BTCForecaster()
#         forecast = forecaster.forecast_price()
        
#         if forecast is not None:
#             # Prepare forecast data
#             last_timestamp = load_recent_data()['Timestamp'].iloc[-1]
#             forecast_timestamps = pd.date_range(
#                 start=last_timestamp, 
#                 periods=len(forecast)+1,
#                 freq='H'  # Hourly intervals
#             )[1:]
            
#             forecast_df = pd.DataFrame({
#                 'Timestamp': forecast_timestamps,
#                 'Forecast Price': forecast
#             })
            
#             return forecast_df
#         return None
#     except Exception as e:
#         st.error(f"Forecasting error: {e}")
#         return None

# def main():
#     # Page configuration
#     st.set_page_config(layout="wide")
#     st_autorefresh(interval=2 * 1000, key="dataframerefresh") # refreshes every two seconds
    
#     st.title('BTC/USDT in Real-Time')
#     st.markdown(f"Last update: __{datetime.now()}__")
#     # Load recent data
#     recent_data = load_recent_data()
    
#     if not recent_data.empty:
#         # Create two columns
#         col1, col2 = st.columns(2)
        
#         with col1.expander("Streaming BTCUSDT Spot", expanded=True):
            
#             # Price Chart
#             fig_price = px.line(
#                 recent_data, 
#                 x='Timestamp', 
#                 y='Price (USDT)', 
#                 title='BTC Price Over Time',
#                 labels={'Price (USDT)': 'Price in USDT'}
#             )
#             st.plotly_chart(fig_price, use_container_width=True)
            
#             # Key Metrics
#             first_price = recent_data['Price (USDT)'].iloc[0]
#             last_price = recent_data['Price (USDT)'].iloc[-1]
#             price_change = last_price - first_price
#             price_change_percent = (price_change / first_price) * 100
            
#             # Time of first and last record
#             first_time = recent_data['Timestamp'].iloc[0]
#             last_time = recent_data['Timestamp'].iloc[-1]
#             time_span = last_time - first_time
            
#             # Metrics display
#             col_current, col_change = st.columns(2)
#             with col_current:
#                 st.metric(
#                     label="Current Price", 
#                     value=f"${last_price:.2f}"
#                 )
#             with col_change:
#                 st.metric(
#                     label="Price Change", 
#                     value=f"${price_change:.2f} ({price_change_percent:.2f}%)",
#                     delta=f"Over {time_span}"
#                 )
        
#         with col2.expander("Price Forecasting", expanded=True):
#             # Forecasting
#             forecast_df = perform_forecast()
            
#             if forecast_df is not None:
#                 # Forecast Chart
#                 fig_forecast = go.Figure()
                
#                 # Historical prices
#                 fig_forecast.add_trace(go.Scatter(
#                     x=recent_data['Timestamp'], 
#                     y=recent_data['Price (USDT)'], 
#                     mode='lines', 
#                     name='Historical Price'
#                 ))
                
#                 # Forecast prices
#                 fig_forecast.add_trace(go.Scatter(
#                     x=forecast_df['Timestamp'], 
#                     y=forecast_df['Forecast Price'], 
#                     mode='lines', 
#                     name='Price Forecast',
#                     line=dict(color='red', dash='dot')
#                 ))
                
#                 fig_forecast.update_layout(
#                     title='BTC Price Forecast',
#                     xaxis_title='Timestamp',
#                     yaxis_title='Price (USDT)'
#                 )
                
#                 st.plotly_chart(fig_forecast, use_container_width=True)
                
#                 # Forecast Table
#                 st.subheader('Forecast Details')
#                 st.dataframe(forecast_df, use_container_width=True)
#     else:
#         st.warning("No recent data available")
    
# if __name__ == "__main__":
#     main()

import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta

from src.pathway_data_tranformer import BinanceDataTransformer
from src.forecasting import BTCForecaster
from streamlit_autorefresh import st_autorefresh


def load_recent_data(hours=24):
    """
    Load recent data from the last specified hours
    
    :param hours: Number of hours of data to load
    :return: Filtered DataFrame
    """
    try:
        # Read CSV with OHLCV data
        df = pd.read_csv('data/btcusdt_ohlcv.csv')
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        # Filter to recent data
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_df = df[df['Timestamp'] > cutoff]
        
        return recent_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()


def perform_forecast():
    """
    Perform multi-metric forecasting
    
    :return: Forecast data
    """
    try:
        forecaster = BTCForecaster()
        forecast = forecaster.forecast_multiple_metrics()
        
        if forecast is not None:
            # Prepare forecast data
            recent_data = load_recent_data()
            last_timestamp = recent_data['Timestamp'].iloc[-1]
            
            forecast_timestamps = pd.date_range(
                start=last_timestamp, 
                periods=len(forecast['Close (USDT)'])+1,
                freq='T'  # Minute intervals to match OHLCV data
            )[1:]
            
            forecast_df = pd.DataFrame({
                'Timestamp': forecast_timestamps,
                **{metric: values for metric, values in forecast.items()}
            })
            
            return forecast_df
        return None
    except Exception as e:
        st.error(f"Forecasting error: {e}")
        return None


def main():
    # Page configuration
    st.set_page_config(layout="wide")
    st_autorefresh(interval=2 * 1000, key="dataframerefresh")  # refreshes every two seconds
    
    st.title('BTC/USDT Real-Time OHLCV Analysis')
    st.markdown(f"Last update: __{datetime.now()}__")
    
    # Load recent data
    recent_data = load_recent_data()
    
    if not recent_data.empty:
        # Create two columns
        col1, col2 = st.columns(2)
        
        with col1.expander("BTCUSDT Candlestick Chart", expanded=True):
            # Candlestick Chart
            fig_candlestick = go.Figure(data=[go.Candlestick(
                x=recent_data['Timestamp'],
                open=recent_data['Open (USDT)'],
                high=recent_data['High (USDT)'],
                low=recent_data['Low (USDT)'],
                close=recent_data['Close (USDT)']
            )])
            
            fig_candlestick.update_layout(
                title='BTC Price Candlestick Chart',
                xaxis_title='Timestamp',
                yaxis_title='Price (USDT)',
                xaxis_rangeslider_visible=False
            )
            
            st.plotly_chart(fig_candlestick, use_container_width=True)
            
            # Volume Subplot
            fig_volume = go.Figure()
            fig_volume.add_trace(go.Bar(
                x=recent_data['Timestamp'],
                y=recent_data['Volume (BTC)'],
                name='Trading Volume'
            ))
            
            fig_volume.update_layout(
                title='Trading Volume',
                xaxis_title='Timestamp',
                yaxis_title='Volume (BTC)'
            )
            
            st.plotly_chart(fig_volume, use_container_width=True)
        
        with col2.expander("Price Forecasting", expanded=True):
            # Forecasting
            forecast_df = perform_forecast()
            
            if forecast_df is not None:
                # Forecast Candlestick Chart
                fig_forecast = go.Figure()
                
                # Historical prices
                fig_forecast.add_trace(go.Candlestick(
                    x=recent_data['Timestamp'],
                    open=recent_data['Open (USDT)'],
                    high=recent_data['High (USDT)'],
                    low=recent_data['Low (USDT)'],
                    close=recent_data['Close (USDT)'],
                    name='Historical'
                ))
                
                # Forecast prices
                fig_forecast.add_trace(go.Scatter(
                    x=forecast_df['Timestamp'], 
                    y=forecast_df['Close (USDT)'], 
                    mode='lines', 
                    name='Price Forecast',
                    line=dict(color='red', dash='dot')
                ))
                
                fig_forecast.update_layout(
                    title='BTC Price Forecast',
                    xaxis_title='Timestamp',
                    yaxis_title='Price (USDT)'
                )
                
                st.plotly_chart(fig_forecast, use_container_width=True)
                
                # Forecast Table
                st.subheader('Forecast Details')
                st.dataframe(forecast_df, use_container_width=True)
    else:
        st.warning("No recent data available")
    
if __name__ == "__main__":
    # pathway transform data ? 
    main()