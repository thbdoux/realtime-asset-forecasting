import os
import pandas as pd
import psutil
from binance.client import Client
from dotenv import load_dotenv
import time
import logging
import pathway as pw
import datetime

class RawBinanceData(pw.Schema): # TODO : changer les types 
    transaction_id: int
    price: float
    qty: float
    time: str
    isBuyerMaker: str

class BinanceDataRetriever:
    def __init__(self, 
                 max_rows=500,  # Maximum rows to keep in CSV
                 memory_threshold_mb=500,  # Memory usage threshold
                 time_window_minutes = 1, # size of candlesticks 
                 raw_data_path='data/raw_btcusdt.csv',
                 ohlcv_data_path = 'data/btcusdt_ohlcv.csv'):
        # Load environment variables
        load_dotenv()
        
        # Binance API Configuration
        self.API_KEY = os.getenv("BINANCE_API_KEY")
        self.API_SECRET = os.getenv("BINANCE_SECRET")
        self.client = Client(self.API_KEY, self.API_SECRET)
        
        # Memory and data management
        self.max_rows = max_rows
        self.memory_threshold_mb = memory_threshold_mb
        self.raw_data_path = raw_data_path
        self.ohlcv_data_path = ohlcv_data_path
        self.time_window_minutes = time_window_minutes
        
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

    def save_to_csv(self, df, data_path):
        """
        Save DataFrame to CSV with data rotation
        
        :param df: DataFrame to save
        """
        # try:
            # Ensure directory exists
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        
        # Check if file exists and manage row count
        if os.path.exists(data_path):
            existing_df = pd.read_csv(data_path)
            
            # If exceeding max rows, keep only recent data
            if len(existing_df) + len(df) > self.max_rows:
                existing_df = existing_df.tail(self.max_rows - len(df))
                existing_df.to_csv(data_path, index=False)
                self.logger.info(f"Rotated data, kept {len(existing_df)} rows")
        

        df.to_csv(data_path, mode='a', header=not os.path.exists(data_path), index=False) 
        self.logger.info(f"Saved {len(df)} new rows")
            
        # except Exception as e:
        #     self.logger.error(f"Error saving to CSV: {e}")

    def save_ohlcv_to_csv(self, df, data_path):
        """
        Save OHLCV DataFrame to CSV with time window overwriting and proper volume aggregation.
        
        :param df: DataFrame to save (must include 'time_window' and 'volume' column)
        :param data_path: Path to the CSV file
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        
        if os.path.exists(data_path):
            # Read existing data
            existing_df = pd.read_csv(data_path)
            
            # Ensure 'time_window' is datetime for consistency
            existing_df['time_window'] = pd.to_datetime(existing_df['time_window'])
            df['time_window'] = pd.to_datetime(df['time_window'])
            
            # Combine new and existing data
            combined_df = pd.concat([existing_df, df])
            
            # Aggregate by time window for OHLCV
            combined_df = combined_df.groupby('time_window', as_index=False).agg({
                'open_price': 'first',
                'high_price': 'max',
                'low_price': 'min',
                'close_price': 'last',
                'volume': 'sum'  # Properly aggregate volume
            })
        else:
            # No existing file, just use the new data
            combined_df = df

        # Enforce max rows if necessary
        if len(combined_df) > self.max_rows:
            combined_df = combined_df.tail(self.max_rows)
            self.logger.info(f"Rotated data, kept last {self.max_rows} rows")

        # Save updated data to CSV
        combined_df.to_csv(data_path, index=False)
        self.logger.info(f"Saved {len(df)} rows to {data_path}")


    def get_btcusdt_data(self, limit=20):
        """Retrieve recent trades data from Binance and perform OHLCV aggregation."""
        # Extraction
        # try:
        trades = self.client.get_recent_trades(symbol='BTCUSDT', limit=limit)
        df = pd.DataFrame(trades)

        # Data transformation
        df = df[['id', 'price', 'qty', 'time', 'isBuyerMaker']]
        df['price'] = pd.to_numeric(df['price'])
        df['qty'] = pd.to_numeric(df['qty'])
        # df['time'] = pd.to_datetime(df['time']).dt.strftime("%Y-%m-%dT%H:%M:%S")
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        df['isBuyerMaker'] = df['isBuyerMaker'].map({True: 'Seller', False: 'Buyer'})
        df = df.rename(columns={"id" : "transaction_id"})
        # save raw data
        self.save_to_csv(df, data_path=self.raw_data_path)

        # pandas way for OHLCV 
        df['time_window'] = df['time'].dt.floor(f'{self.time_window_minutes}T')

        # Compute OHLCV
        ohlcv = df.groupby('time_window').agg(
            open_price=('price', 'first'),
            high_price=('price', 'max'),
            low_price=('price', 'min'),
            close_price=('price', 'last'),
            volume=('qty', 'sum')
        ).reset_index()

        self.save_ohlcv_to_csv(ohlcv, data_path=self.ohlcv_data_path)
        # Ingest the DataFrame into Pathway
        """
        
        
        input_data = pw.io.csv.read(
            self.raw_data_path,
                schema=RawBinanceData
            )
        input_data = input_data.with_columns(
            dtime = input_data.time.dt.strptime(fmt="%Y-%m-%dT%H:%M:%S"),
        )
        # Perform OHLCV aggregation
        ohlcv_data = input_data.windowby(
            pw.this.dtime, 
            window=pw.temporal.sliding(
                duration=datetime.timedelta(minutes=self.time_window_minutes), 
                hop=datetime.timedelta(minutes=self.time_window_minutes)),
                ).reduce(
            open_price=pw.reducers.earliest(pw.this.price),
            close_price=pw.reducers.latest(pw.this.price),
            high_price=pw.reducers.max(pw.this.price),
            low_price=pw.reducers.min(pw.this.price),
            volume=pw.reducers.sum(pw.this.qty),
        )
        # df_ohlcv = pw.io.python.get_table_as_pandas(ohlcv_data)
        # self.save_to_csv(df_ohlcv, data_path=self.ohlcv_data_path)
        pw.io.csv.write(ohlcv_data,self.ohlcv_data_path)
        # Run Pathway
        pw.run()
        """

        # except Exception as e:
        #     self.logger.error(f"Error retrieving Binance data: {e}")
        #     return pd.DataFrame()

    def run_data_pipeline(self, interval=0.2):
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
            self.get_btcusdt_data()
            # Wait before next iteration
            time.sleep(interval)

def main():
    retriever = BinanceDataRetriever()
    retriever.run_data_pipeline()

if __name__ == "__main__":
    main()