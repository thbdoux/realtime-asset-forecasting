import pandas as pd
from binance.client import Client
import pathway as pw
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt
from datetime import datetime
import time
import os
from dotenv import load_dotenv
load_dotenv()

# Configuration Binance API (utilise tes clés API)
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_SECRET")
client = Client(API_KEY, API_SECRET)


# Fonction pour récupérer les données de la paire BTCUSDT
def get_btcusdt_data():
    # Récupération des données de trades récents (dernières transactions)
    trades = client.get_recent_trades(symbol='BTCUSDT', limit=10)
    
    # Transformation des données en DataFrame pandas
    df = pd.DataFrame(trades)
    df = df[['id', 'price', 'qty', 'time', 'isBuyerMaker']]
    
    # Convertir les colonnes en types appropriés
    df['price'] = pd.to_numeric(df['price'])
    df['qty'] = pd.to_numeric(df['qty'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')  # Conversion de timestamp
    df['isBuyerMaker'] = df['isBuyerMaker'].map({True: 'Seller', False: 'Buyer'})
    
    # Renommer les colonnes pour plus de clarté
    df.rename(columns={
        'id': 'Trade ID',
        'price': 'Price (USDT)',
        'qty': 'Quantity (BTC)',
        'time': 'Timestamp',
        'isBuyerMaker': 'Initiator'
    }, inplace=True)
    
    return df

# Appel de la fonction et affichage
if __name__ == "__main__":
    btcusdt_df = get_btcusdt_data()
    print(btcusdt_df)
