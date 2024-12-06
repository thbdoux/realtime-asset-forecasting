import os
import time
import streamlit as st
from data_retrieval import BinanceDataRetriever

def data_retrieval_daemon():
    """
    Daemon process to continuously retrieve and save BTC data
    Designed to run in background during Streamlit app execution
    """
    retriever = BinanceDataRetriever()
    
    while True:
        # Retrieve and save data
        new_data = retriever.get_btcusdt_data()
        retriever.save_to_csv(new_data)
        
        # Notify Streamlit of new data
        st.experimental_memo.clear_all()
        
        # Wait before next retrieval
        time.sleep(30)  # Adjust interval as needed

def main():
    data_retrieval_daemon()

if __name__ == "__main__":
    main()