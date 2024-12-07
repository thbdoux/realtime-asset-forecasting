# import pandas as pd
# import numpy as np
# from statsmodels.tsa.arima.model import ARIMA
# import matplotlib.pyplot as plt
# import logging

# class BTCForecaster:
#     def __init__(self, 
#                  data_path='data/btcusdt_trades.csv', 
#                  chunk_size=5000):
#         """
#         Initialize forecaster with memory-efficient data loading
        
#         :param data_path: Path to CSV file
#         :param chunk_size: Number of rows to load at a time
#         """
#         self.data_path = data_path
#         self.chunk_size = chunk_size
#         self.historical_data = None
#         self.forecast = None
        
#         # Setup logging
#         logging.basicConfig(level=logging.INFO, 
#                             format='%(asctime)s - %(levelname)s: %(message)s')
#         self.logger = logging.getLogger(__name__)

#     def load_data(self, use_recent_chunks=True):
#         """
#         Load historical price data from CSV with memory efficiency
        
#         :param use_recent_chunks: If True, load only most recent chunks
#         :return: DataFrame with historical data
#         """
#         try:
#             # Read data in chunks
#             chunks = pd.read_csv(self.data_path, chunksize=self.chunk_size)
            
#             if use_recent_chunks:
#                 # Keep only last N chunks
#                 chunks_list = list(chunks)
#                 recent_chunks = chunks_list[-5:]  # Adjust number of chunks as needed
                
#                 # Concatenate recent chunks
#                 self.historical_data = pd.concat(recent_chunks)
#             else:
#                 # Load full dataset (use with caution for large files)
#                 self.historical_data = pd.read_csv(self.data_path)
            
#             # Ensure timestamp is datetime
#             self.historical_data['Timestamp'] = pd.to_datetime(self.historical_data['Timestamp'])
            
#             # Group by timestamp and get mean price
#             grouped_data = self.historical_data.groupby('Timestamp')['Price (USDT)'].mean().reset_index()
#             grouped_data.set_index('Timestamp', inplace=True)
            
#             self.logger.info(f"Loaded {len(self.historical_data)} rows of data")
#             return grouped_data
        
#         except Exception as e:
#             self.logger.error(f"Error loading data: {e}")
#             return None

#     def forecast_price(self, periods=5, use_recent_data=True):
#         """
#         Forecast BTC price with memory-efficient approach
        
#         :param periods: Number of future periods to forecast
#         :param use_recent_data: Use only recent data for forecasting
#         :return: Forecasted prices
#         """
#         try:
#             # Load data
#             prices = self.load_data(use_recent_data)
            
#             if prices is None:
#                 self.logger.error("Could not load price data")
#                 return None
            
#             # Fit ARIMA model
#             model = ARIMA(prices['Price (USDT)'], order=(1,1,1))
#             model_fit = model.fit()
            
#             # Generate forecast
#             self.forecast = model_fit.forecast(steps=periods)
            
#             self.logger.info(f"Generated forecast for {periods} periods")
#             return self.forecast
        
#         except Exception as e:
#             self.logger.error(f"Forecasting error: {e}")
#             return None

# def main():
#     forecaster = BTCForecaster()
#     historical_data = forecaster.load_data()
#     forecast = forecaster.forecast_price()
    
#     print("Forecast:", forecast)

# if __name__ == "__main__":
#     main()


import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import logging

class BTCForecaster:
    def __init__(self, 
                 data_path='data/btcusdt_ohlcv.csv', 
                 chunk_size=5000):
        """
        Initialize forecaster with memory-efficient data loading
        
        :param data_path: Path to OHLCV CSV file
        :param chunk_size: Number of rows to load at a time
        """
        self.data_path = data_path
        self.chunk_size = chunk_size
        self.historical_data = None
        self.forecast = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s: %(message)s')
        self.logger = logging.getLogger(__name__)

    def load_data(self, use_recent_chunks=True):
        """
        Load historical OHLCV data from CSV with memory efficiency
        
        :param use_recent_chunks: If True, load only most recent chunks
        :return: DataFrame with historical data
        """
        try:
            # Read data in chunks
            chunks = pd.read_csv(self.data_path, chunksize=self.chunk_size)
            
            if use_recent_chunks:
                # Keep only last N chunks
                chunks_list = list(chunks)
                recent_chunks = chunks_list[-5:]  # Adjust number of chunks as needed
                
                # Concatenate recent chunks
                self.historical_data = pd.concat(recent_chunks)
            else:
                # Load full dataset (use with caution for large files)
                self.historical_data = pd.read_csv(self.data_path)
            
            # Ensure timestamp is datetime
            self.historical_data['Timestamp'] = pd.to_datetime(self.historical_data['Timestamp'])
            
            # Set timestamp as index for time series analysis
            self.historical_data.set_index('Timestamp', inplace=True)
            
            self.logger.info(f"Loaded {len(self.historical_data)} rows of data")
            return self.historical_data
        
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            return None

    def forecast_price(self, periods=5, forecast_column='Close (USDT)', use_recent_data=True):
        """
        Forecast OHLCV metrics with memory-efficient approach
        
        :param periods: Number of future periods to forecast
        :param forecast_column: Column to forecast (default: Close Price)
        :param use_recent_data: Use only recent data for forecasting
        :return: Forecasted values
        """
        try:
            # Load data
            prices = self.load_data(use_recent_data)
            
            if prices is None:
                self.logger.error("Could not load price data")
                return None
            
            # Fit ARIMA model
            model = ARIMA(prices[forecast_column], order=(1,1,1))
            model_fit = model.fit()
            
            # Generate forecast
            self.forecast = model_fit.forecast(steps=periods)
            
            self.logger.info(f"Generated forecast for {periods} periods")
            return self.forecast
        
        except Exception as e:
            self.logger.error(f"Forecasting error: {e}")
            return None

    def forecast_multiple_metrics(self, periods=5):
        """
        Forecast multiple OHLCV metrics
        
        :param periods: Number of future periods to forecast
        :return: Dictionary of forecasts for different metrics
        """
        forecasts = {}
        metrics = ['Open (USDT)', 'Close (USDT)', 'High (USDT)', 'Low (USDT)', 'Volume (BTC)']
        
        for metric in metrics:
            forecast = self.forecast_price(periods=periods, forecast_column=metric)
            forecasts[metric] = forecast
        
        return forecasts

def main():
    forecaster = BTCForecaster()
    
    # Forecast multiple metrics
    multi_forecast = forecaster.forecast_multiple_metrics()
    
    # Print forecasts
    for metric, forecast in multi_forecast.items():
        print(f"{metric} Forecast:", forecast)

if __name__ == "__main__":
    main()