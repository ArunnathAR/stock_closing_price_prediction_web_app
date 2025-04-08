import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import functools
import time

# Cache for data fetching (1 hour expiry)
def timed_lru_cache(seconds=3600, maxsize=128):
    def wrapper_cache(func):
        func = functools.lru_cache(maxsize=maxsize)(func)
        func.lifetime = seconds
        func.expiration = time.time() + seconds
        
        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            if time.time() > func.expiration:
                func.cache_clear()
                func.expiration = time.time() + func.lifetime
            return func(*args, **kwargs)
        
        return wrapped_func
    
    return wrapper_cache

# Nifty 50 stocks list (with Yahoo Finance symbols)
NIFTY50_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "HINDUNILVR.NS",
    "INFY.NS", "HDFC.NS", "KOTAKBANK.NS", "ITC.NS", "SBIN.NS",
    "BHARTIARTL.NS", "BAJFINANCE.NS", "LT.NS", "ASIANPAINT.NS", "AXISBANK.NS",
    "WIPRO.NS", "MARUTI.NS", "ULTRACEMCO.NS", "TITAN.NS", "BAJAJFINSV.NS",
    "HCLTECH.NS", "SUNPHARMA.NS", "TATASTEEL.NS", "M&M.NS", "TECHM.NS",
    "NTPC.NS", "POWERGRID.NS", "NESTLEIND.NS", "JSWSTEEL.NS", "DRREDDY.NS",
    "HDFCLIFE.NS", "IOC.NS", "CIPLA.NS", "ONGC.NS", "DIVISLAB.NS",
    "COALINDIA.NS", "GRASIM.NS", "BPCL.NS", "UPL.NS", "SHREECEM.NS",
    "HEROMOTOCO.NS", "TATAMOTORS.NS", "ADANIPORTS.NS", "INDUSINDBK.NS", "BRITANNIA.NS",
    "HINDALCO.NS", "EICHERMOT.NS", "SBILIFE.NS", "BAJAJ-AUTO.NS", "TATACONSUM.NS"
]

@timed_lru_cache(seconds=3600)
def get_stock_data(symbol, period='1month'):
    """
    Fetch stock data using yfinance
    
    Parameters:
    - symbol: Stock symbol (Yahoo Finance format)
    - period: Time period ('1month', '3month', '5month')
    
    Returns:
    - Pandas DataFrame with stock data
    """
    try:
        # Map period to yfinance period format
        if period == '1month':
            yf_period = '1mo'
            interval = '1d'
        elif period == '3month':
            yf_period = '3mo'
            interval = '1d'
        elif period == '5month':
            yf_period = '5mo'
            interval = '1d'
        else:
            yf_period = '1mo'  # Default
            interval = '1d'
        
        # Fetch data using yfinance
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=yf_period, interval=interval)
        
        if df.empty:
            print(f"No data found for {symbol}")
            return None
        
        # Rename columns to match expected format
        df.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }, inplace=True)
        
        # Sort by date (newest first)
        df.sort_index(ascending=False, inplace=True)
        
        return df
    
    except Exception as e:
        print(f"Error fetching stock data for {symbol}: {e}")
        return None

@timed_lru_cache(seconds=3600)
def get_stock_overview(symbol):
    """
    Fetch stock overview information
    
    Parameters:
    - symbol: Stock symbol (Yahoo Finance format)
    
    Returns:
    - Dictionary with stock overview data
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Create a standardized overview dict
        overview = {
            'Symbol': symbol,
            'Name': info.get('shortName', ''),
            'Description': info.get('longBusinessSummary', ''),
            'Sector': info.get('sector', ''),
            'Industry': info.get('industry', ''),
            'MarketCap': info.get('marketCap', 0),
            'PERatio': info.get('trailingPE', 0),
            'EPS': info.get('trailingEps', 0),
            'DividendYield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
            '52WeekHigh': info.get('fiftyTwoWeekHigh', 0),
            '52WeekLow': info.get('fiftyTwoWeekLow', 0),
            'AnalystTarget': info.get('targetMeanPrice', 0),
        }
        
        return overview
    
    except Exception as e:
        print(f"Error fetching stock overview for {symbol}: {e}")
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
    - symbol: Stock symbol (Yahoo Finance format)
    
    Returns:
    - Current stock price (float)
    """
    try:
        ticker = yf.Ticker(symbol)
        ticker_data = ticker.history(period='1d')
        
        if ticker_data.empty:
            print(f"No data found for {symbol}")
            return None
        
        # Get the latest close price
        current_price = ticker_data['Close'].iloc[-1]
        return float(current_price)
    
    except Exception as e:
        print(f"Error fetching current price for {symbol}: {e}")
        return None
