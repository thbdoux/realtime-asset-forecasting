# Real-Time Finance Asset Scraper & Forecaster

A real-time pipeline to scrape and forecast financial asset prices using the Binance API. This project focuses on Bitcoin (BTC/USDT) but can be adapted to other trading pairs. The data is retrieved, visualized, and processed for forecasting using basic machine learning models.

---

## Features
- **Real-Time Data Collection**: Fetch live BTC/USDT price data using Binance API.
- **Data Visualization**: Plot real-time price data dynamically.
- **ML Forecasting**: Predict future prices using an ARIMA model (can be extended to advanced models like LSTMs).
- **Modular Architecture**: Easy-to-adapt pipeline for other assets or markets.

---

## Prerequisites
Ensure you have the following installed:
- Python ≥ 3.7
- Pip package manager

Install the required Python libraries:
```bash
pip install -r requirements.txt
```

## Installation

Clone the repository :

```bash
git clone https://github.com/your_username/finance-scraper-forecaster.git
cd finance-scraper-forecaster
```

Set Up Binance API Keys

1. Log in to your Binance account.
2. Generate an API key and secret (refer to Binance's official guide).
3. Create a .env file in the project root and add your keys.


## How to Run It Locally
In two different terminals, proceed as follow:

1. Run data retrieval
```bash
python src.data_retrieval
```

2. Run Streamlit Web App:
```bash
streamlit run src/app.py
```
