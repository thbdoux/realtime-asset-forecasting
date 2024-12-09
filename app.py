import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta

from src.pathway_data_tranformer import BinanceDataTransformer
from src.forecasting import BTCForecaster
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots


def load_recent_data(hours=24):
    """
    Load recent data from the last specified hours
    
    :param hours: Number of hours of data to load
    :return: Filtered DataFrame
    """
    # try:
        # Read CSV with OHLCV data
    df = pd.read_csv('data/btcusdt_ohlcv.csv')
    df['time_window'] = pd.to_datetime(df['time_window'])
    
    # Filter to recent data
    cutoff = datetime.now() - timedelta(hours=hours)
    recent_df = df[df['time_window'] > cutoff]
    
    return recent_df
    # except Exception as e:
    #     st.error(f"Error loading data: {e}")
    #     return pd.DataFrame()


def perform_forecast():
    """
    Perform multi-metric forecasting
    
    :return: Forecast data
    """
    try:
        forecaster = BTCForecaster()
        forecast = forecaster.forecast_ohlcv(periods=2)
        
        if forecast is not None:
            # Prepare forecast data
            recent_data = load_recent_data()
            last_timestamp = recent_data['time_window'].iloc[-1]
            
            forecast_timestamps = pd.date_range(
                start=last_timestamp, 
                periods=len(forecast['close_price'])+1,
                freq='T'  # Minute intervals to match OHLCV data
            )[1:]
            
            forecast_df = pd.DataFrame({
                'time_window': forecast_timestamps,
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
    st_autorefresh(interval=1 * 1000, key="dataframerefresh")  # Refreshes every two seconds
    st.title('BTC/USDT Real-Time OHLCV Analysis')
    st.markdown(f"Last update: **{datetime.now()}**")

    # Load recent data
    recent_data = load_recent_data()
    forecast_df = perform_forecast()  # Perform forecasting

    if not recent_data.empty and forecast_df is not None:
        # Combine historical and forecast data
        combined_df = pd.concat([recent_data, forecast_df], ignore_index=True)

        # Create a shared x-axis layout
        fig_combined = make_subplots(
            rows=2, cols=1, shared_xaxes=True,
            row_heights=[0.7, 0.3],
            vertical_spacing=0.02,
            subplot_titles=("BTC Price Candlestick Chart", "Trading Volume")
        )

        # Historical prices
        fig_combined.add_trace(
            go.Candlestick(
                x=recent_data['time_window'],
                open=recent_data['open_price'],
                high=recent_data['high_price'],
                low=recent_data['low_price'],
                close=recent_data['close_price'],
                name='Historical'
            ),
            row=1, col=1
        )

        # Forecast prices
        fig_combined.add_trace(
            go.Candlestick(
                x=forecast_df['time_window'],
                open=forecast_df['open_price'],
                high=forecast_df['high_price'],
                low=forecast_df['low_price'],
                close=forecast_df['close_price'],
                name='Forecasted',
                increasing_line_color='blue',  # Set a distinct color for forecast
                decreasing_line_color='red'
            ),
            row=1, col=1
        )

        # Add volume bar chart
        fig_combined.add_trace(
            go.Bar(
                x=recent_data['time_window'],
                y=recent_data['volume'],
                name='Historical Volume',
                marker_color='gray'
            ),
            row=2, col=1
        )
        fig_combined.add_trace(
            go.Bar(
                x=forecast_df['time_window'],
                y=forecast_df['volume'],
                name='Forecast Volume',
                marker_color='blue'
            ),
            row=2, col=1
        )

        # Highlight forecast zone in both subplots
        forecast_start = forecast_df['time_window'].min()
        forecast_end = forecast_df['time_window'].max()
        fig_combined.add_vrect(
            x0=forecast_start, x1=forecast_end,
            fillcolor="rgba(0, 255, 0, 0.2)",  # Light green highlight
            layer="below",
            line_width=0,
            row=1, col=1
        )
        fig_combined.add_vrect(
            x0=forecast_start, x1=forecast_end,
            fillcolor="rgba(0, 255, 0, 0.2)",  # Same highlight for volume
            layer="below",
            line_width=0,
            row=2, col=1
        )

        # Update layout
        fig_combined.update_layout(
            height=700,
            title='BTC Price Candlestick Chart with Volume and Forecast Highlight',
            xaxis_title='Time (10 sec window)',
            yaxis_title='Price (USDT)',
            xaxis2_title='Time (10 sec window)',
            yaxis2_title='Volume',
            xaxis_rangeslider_visible=False
        )

        # Plot the combined chart
        st.plotly_chart(fig_combined, use_container_width=True)

        # Forecast Table
        st.subheader('Forecast Details')
        st.dataframe(forecast_df, use_container_width=True)
    else:
        st.warning("No recent or forecast data available")

if __name__ == "__main__":
    # pathway transform data ? 
    main()