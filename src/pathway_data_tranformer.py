import pathway as pw
import pandas as pd
import os
import datetime

class RawBinanceData(pw.Schema):
    id: int
    price: float
    qty: float
    time: pw.DateTimeUtc
    isBuyerMaker: str
    # Trade ID,price,Quantity (BTC),Timestamp,Initiator

class BinanceDataTransformer:
    def __init__(self, 
                 input_path='data/btcusdt_trades.csv', 
                 output_path='data/btcusdt_ohlcv.csv',
                 time_window_minutes=1,
                 max_rows=10000):
        """
        Initialize Binance data transformer using Pathway
        
        :param input_path: Path to input raw trades CSV
        :param output_path: Path to output OHLCV CSV
        :param time_window_minutes: Aggregation window in minutes
        :param max_rows: Maximum number of rows to keep in output CSV
        """
        self.input_path = input_path
        self.output_path = output_path
        self.time_window_minutes = time_window_minutes
        self.max_rows = max_rows
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    def transform_data(self):
        """
        Transform raw trades data into OHLCV (Open, High, Low, Close, Volume) format
        Uses Pathway for real-time data processing
        """
        # Define input data connector
        input_data = pw.io.csv.read(
            self.input_path,
            schema=RawBinanceData,
            mode='static'
        )

        # Group data by time windows
        def time_window_key(row):
            """Create time window key by truncating timestamp to specified interval"""
            return row['time'].replace(
                minute=row['time'].minute // self.time_window_minutes * self.time_window_minutes, 
                second=0, 
                microsecond=0
            )

        # Perform OHLCV aggregation
        ohlcv_data = input_data.groupby(time_window_key).reduce(
            pw.this.timestamp << pw.global_reduce(pw.agg.first(pw.this.time)),
            open_price=pw.global_reduce(pw.agg.first(pw.this['price'])),
            close_price=pw.global_reduce(pw.agg.last(pw.this['price'])),
            high_price=pw.global_reduce(pw.agg.max(pw.this['price'])),
            low_price=pw.global_reduce(pw.agg.min(pw.this['price'])),
            volume=pw.global_reduce(pw.agg.sum(pw.this['qty']))
        )

        # Convert Pathway table to pandas DataFrame
        df = ohlcv_data.to_pandas()

        # Sort by timestamp
        df.sort_values('timestamp', inplace=True)

        # Implement CSV rotation
        if os.path.exists(self.output_path):
            existing_df = pd.read_csv(self.output_path)
            if len(existing_df) + len(df) > self.max_rows:
                # Keep only the most recent rows
                existing_df = existing_df.tail(self.max_rows - len(df))

        # Save to CSV
        df.to_csv(self.output_path, index=False)
        
        return df

def main():
    transformer = BinanceDataTransformer()
    transformed_data = transformer.transform_data()
    print(transformed_data)

if __name__ == "__main__":
    main()