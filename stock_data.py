import os
import pandas as pd
import numpy as np
import streamlit as st
import requests
from datetime import datetime, timedelta

# Alpha Vantage API key from environment
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")

# Nifty 50 stocks list
NIFTY50_STOCKS = [
    "RELIANCE.BSE", "TCS.BSE", "HDFCBANK.BSE", "ICICIBANK.BSE", "HINDUNILVR.BSE",
    "INFY.BSE", "HDFC.BSE", "KOTAKBANK.BSE", "ITC.BSE", "SBIN.BSE",
    "BHARTIARTL.BSE", "BAJFINANCE.BSE", "LT.BSE", "ASIANPAINT.BSE", "AXISBANK.BSE",
    "WIPRO.BSE", "MARUTI.BSE", "ULTRACEMCO.BSE", "TITAN.BSE", "BAJAJFINSV.BSE",
    "HCLTECH.BSE", "SUNPHARMA.BSE", "TATASTEEL.BSE", "M&M.BSE", "TECHM.BSE",
    "NTPC.BSE", "POWERGRID.BSE", "NESTLEIND.BSE", "JSWSTEEL.BSE", "DRREDDY.BSE",
    "HDFCLIFE.BSE", "IOC.BSE", "CIPLA.BSE", "ONGC.BSE", "DIVISLAB.BSE",
    "COALINDIA.BSE", "GRASIM.BSE", "BPCL.BSE", "UPL.BSE", "SHREECEM.BSE",
    "HEROMOTOCO.BSE", "TATAMOTORS.BSE", "ADANIPORTS.BSE", "INDUSINDBK.BSE", "BRITANNIA.BSE",
    "HINDALCO.BSE", "EICHERMOT.BSE", "SBILIFE.BSE", "BAJAJ-AUTO.BSE", "TATACONSUM.BSE"
]

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_stock_data(symbol, period='1month'):
    """
    Fetch stock data from Alpha Vantage API
    
    Parameters:
    - symbol: Stock symbol
    - period: Time period ('1month', '3month', '5month')
    
    Returns:
    - Pandas DataFrame with stock data
    """
    try:
        if period == '1month':
            outputsize = "compact"  # Last 100 data points
        else:
            outputsize = "full"  # Full data

        # Base URL for API request
        base_url = "https://www.alphavantage.co/query"
        
        # Parameters for API request
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": outputsize,
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        
        # Make API request
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if "Error Message" in data:
            st.error(f"API Error: {data['Error Message']}")
            return None
        
        if "Time Series (Daily)" not in data:
            st.error("No time series data found. Please check the stock symbol.")
            return None
        
        # Extract time series data
        time_series = data["Time Series (Daily)"]
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(time_series, orient='index')
        
        # Rename columns
        df.rename(columns={
            '1. open': 'open',
            '2. high': 'high',
            '3. low': 'low',
            '4. close': 'close',
            '5. volume': 'volume'
        }, inplace=True)
        
        # Convert index to datetime
        df.index = pd.to_datetime(df.index)
        
        # Sort by date (newest first)
        df.sort_index(ascending=False, inplace=True)
        
        # Convert columns to numeric
        for col in df.columns:
            df[col] = pd.to_numeric(df[col])
        
        # Filter based on period
        if period == '1month':
            start_date = datetime.now() - timedelta(days=30)
        elif period == '3month':
            start_date = datetime.now() - timedelta(days=90)
        elif period == '5month':
            start_date = datetime.now() - timedelta(days=150)
        else:
            start_date = datetime.now() - timedelta(days=30)  # Default to 1 month
        
        df = df[df.index >= start_date]
        
        return df
    
    except Exception as e:
        st.error(f"Error fetching stock data: {e}")
        return None

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_stock_overview(symbol):
    """
    Fetch stock overview information from Alpha Vantage API
    
    Parameters:
    - symbol: Stock symbol
    
    Returns:
    - Dictionary with stock overview data
    """
    try:
        # Base URL for API request
        base_url = "https://www.alphavantage.co/query"
        
        # Parameters for API request
        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        
        # Make API request
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if "Error Message" in data:
            st.error(f"API Error: {data['Error Message']}")
            return None
        
        return data
    
    except Exception as e:
        st.error(f"Error fetching stock overview: {e}")
        return None

def calculate_technical_indicators(df):
    """
    Calculate technical indicators for the stock data
    
    Parameters:
    - df: Pandas DataFrame with stock data
    
    Returns:
    - DataFrame with added technical indicators
    """
    if df is None or df.empty:
        return None
    
    # Create a copy of the dataframe
    df_indicators = df.copy()
    
    # Calculate Simple Moving Averages (SMA)
    df_indicators['SMA_20'] = df_indicators['close'].rolling(window=20).mean()
    df_indicators['SMA_50'] = df_indicators['close'].rolling(window=50).mean()
    
    # Calculate Exponential Moving Average (EMA)
    df_indicators['EMA_20'] = df_indicators['close'].ewm(span=20, adjust=False).mean()
    
    # Calculate Relative Strength Index (RSI)
    delta = df_indicators['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    
    rs = gain / loss
    df_indicators['RSI'] = 100 - (100 / (1 + rs))
    
    # Calculate Moving Average Convergence Divergence (MACD)
    ema_12 = df_indicators['close'].ewm(span=12, adjust=False).mean()
    ema_26 = df_indicators['close'].ewm(span=26, adjust=False).mean()
    df_indicators['MACD'] = ema_12 - ema_26
    df_indicators['MACD_Signal'] = df_indicators['MACD'].ewm(span=9, adjust=False).mean()
    
    # Calculate Bollinger Bands
    df_indicators['BB_Middle'] = df_indicators['close'].rolling(window=20).mean()
    df_indicators['BB_StdDev'] = df_indicators['close'].rolling(window=20).std()
    df_indicators['BB_Upper'] = df_indicators['BB_Middle'] + (df_indicators['BB_StdDev'] * 2)
    df_indicators['BB_Lower'] = df_indicators['BB_Middle'] - (df_indicators['BB_StdDev'] * 2)
    
    return df_indicators

def get_current_price(symbol):
    """
    Get the current stock price
    
    Parameters:
    - symbol: Stock symbol
    
    Returns:
    - Current stock price (float)
    """
    try:
        # Base URL for API request
        base_url = "https://www.alphavantage.co/query"
        
        # Parameters for API request
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        
        # Make API request
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if "Error Message" in data:
            st.error(f"API Error: {data['Error Message']}")
            return None
        
        if "Global Quote" not in data or not data["Global Quote"]:
            st.error("No quote data found. Please check the stock symbol.")
            return None
        
        # Extract current price
        current_price = float(data["Global Quote"]["05. price"])
        return current_price
    
    except Exception as e:
        st.error(f"Error fetching current price: {e}")
        return None
