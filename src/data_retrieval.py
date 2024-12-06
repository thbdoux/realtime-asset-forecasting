import os
import pandas as pd
import psutil
from binance.client import Client
from dotenv import load_dotenv
import time
import logging

class BinanceDataRetriever:
    def __init__(self, 
                 max_rows=1000,  # Maximum rows to keep in CSV
                 memory_threshold_mb=500,  # Memory usage threshold
                 data_path='data/btcusdt_trades.csv'):
        # Load environment variables
        load_dotenv()
        
        # Binance API Configuration
        self.API_KEY = os.getenv("BINANCE_API_KEY")
        self.API_SECRET = os.getenv("BINANCE_SECRET")
        self.client = Client(self.API_KEY, self.API_SECRET)
        
        # Memory and data management
        self.max_rows = max_rows
        self.memory_threshold_mb = memory_threshold_mb
        self.data_path = data_path
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s: %(message)s')
        self.logger = logging.getLogger(__name__)

    def check_memory_usage(self):
        """
        Monitor current process memory usage
        
        :return: Boolean indicating if memory is above threshold
        """
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_usage_mb = memory_info.rss / 1024 / 1024
        
        if memory_usage_mb > self.memory_threshold_mb:
            self.logger.warning(f"High memory usage: {memory_usage_mb:.2f} MB")
            return True
        return False

    def save_to_csv(self, df):
        """
        Save DataFrame to CSV with data rotation
        
        :param df: DataFrame to save
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            
            # Check if file exists and manage row count
            if os.path.exists(self.data_path):
                existing_df = pd.read_csv(self.data_path)
                
                # If exceeding max rows, keep only recent data
                if len(existing_df) + len(df) > self.max_rows:
                    existing_df = existing_df.tail(self.max_rows - len(df))
                    existing_df.to_csv(self.data_path, index=False)
                    self.logger.info(f"Rotated data, kept {len(existing_df)} rows")
            
            # Append new data
            df.to_csv(self.data_path, mode='a', header=not os.path.exists(self.data_path), index=False)
            self.logger.info(f"Saved {len(df)} new rows")
            
        except Exception as e:
            self.logger.error(f"Error saving to CSV: {e}")

    def get_btcusdt_data(self, limit=20):
        """Retrieve recent trades data from Binance"""
        try:
            trades = self.client.get_recent_trades(symbol='BTCUSDT', limit=limit)
            df = pd.DataFrame(trades)
            
            # Data transformation
            df = df[['id', 'price', 'qty', 'time', 'isBuyerMaker']]
            df['price'] = pd.to_numeric(df['price'])
            df['qty'] = pd.to_numeric(df['qty'])
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            df['isBuyerMaker'] = df['isBuyerMaker'].map({True: 'Seller', False: 'Buyer'})
            
            df.rename(columns={
                'id': 'Trade ID',
                'price': 'Price (USDT)',
                'qty': 'Quantity (BTC)',
                'time': 'Timestamp',
                'isBuyerMaker': 'Initiator'
            }, inplace=True)
            
            return df
        except Exception as e:
            self.logger.error(f"Error retrieving Binance data: {e}")
            return pd.DataFrame()

    def run_data_pipeline(self, interval=1):
        """
        Continuous data retrieval and storage with memory checks
        
        :param interval: Seconds between data retrievals
        """
        while True:
            # Check memory before processing
            if self.check_memory_usage():
                # Implement your memory management strategy
                # For example, you might want to restart the process or clear some data
                self.logger.warning("High memory usage detected. Consider restarting.")
            
            # Retrieve and save data
            new_data = self.get_btcusdt_data()
            self.save_to_csv(new_data)
            
            # Wait before next iteration
            time.sleep(interval)

def main():
    retriever = BinanceDataRetriever(max_rows=500)
    retriever.run_data_pipeline()

if __name__ == "__main__":
    main()