import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from database import get_user_stock_history, get_user_trading_history, get_user_portfolio, get_user_watchlist
from stock_data import get_current_price

def load_user_data(user_id):
    """
    Load user's data for dashboard
    
    Parameters:
    - user_id: User ID
    
    Returns:
    - Dictionary with user data
    """
    # Get stock analysis history
    stock_history = get_user_stock_history(user_id)
    
    # Get trading history
    trading_history = get_user_trading_history(user_id)
    
    # Get portfolio
    portfolio = get_user_portfolio(user_id)
    
    # Get watchlist
    watchlist = get_user_watchlist(user_id)
    
    # Return data
    return {
        'stock_history': stock_history,
        'trading_history': trading_history,
        'portfolio': portfolio,
        'watchlist': watchlist
    }

def format_history_data(stock_history):
    """
    Format stock history data for display
    
    Parameters:
    - stock_history: DataFrame with stock history
    
    Returns:
    - Formatted DataFrame
    """
    if stock_history is None or stock_history.empty:
        return pd.DataFrame()
    
    # Create a copy to avoid modifying the original
    df = stock_history.copy()
    
    # Format the date
    if 'analysis_date' in df.columns:
        df['analysis_date'] = pd.to_datetime(df['analysis_date'])
        df['formatted_date'] = df['analysis_date'].dt.strftime('%b %d, %Y')
    
    # Extract recommendation for display
    if 'recommendation' in df.columns:
        df['recommendation_display'] = df['recommendation'].str.capitalize()
    
    # Create color-coded recommendation
    if 'recommendation' in df.columns:
        df['recommendation_color'] = df['recommendation'].apply(
            lambda x: '#00C853' if x == 'buy' else ('#FF6B6B' if x == 'sell' else '#FFA726')
        )
    
    return df

def format_trading_data(trading_history):
    """
    Format trading history data for display
    
    Parameters:
    - trading_history: DataFrame with trading history
    
    Returns:
    - Formatted DataFrame
    """
    if trading_history is None or trading_history.empty:
        return pd.DataFrame()
    
    # Create a copy to avoid modifying the original
    df = trading_history.copy()
    
    # Format the date
    if 'transaction_date' in df.columns:
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        df['formatted_date'] = df['transaction_date'].dt.strftime('%b %d, %Y')
    
    # Format transaction type
    if 'transaction_type' in df.columns:
        df['transaction_type_display'] = df['transaction_type'].str.capitalize()
    
    # Create color-coded transaction type
    if 'transaction_type' in df.columns:
        df['transaction_color'] = df['transaction_type'].apply(
            lambda x: '#00C853' if x == 'buy' else '#FF6B6B'
        )
    
    # Calculate total value
    if 'price' in df.columns and 'quantity' in df.columns:
        df['total_value'] = df['price'] * df['quantity']
    
    return df

def create_analysis_trend_chart(stock_history):
    """
    Create a trend chart for stock analysis history
    
    Parameters:
    - stock_history: DataFrame with stock history
    
    Returns:
    - Plotly figure
    """
    if stock_history is None or stock_history.empty:
        return None
    
    # Get counts of each recommendation
    recommendation_counts = stock_history['recommendation'].value_counts().reset_index()
    recommendation_counts.columns = ['Recommendation', 'Count']
    
    # Define colors
    colors = {
        'buy': '#00C853',   # Green
        'sell': '#FF6B6B',  # Red
        'hold': '#FFA726'   # Orange
    }
    
    # Create figure
    fig = px.pie(
        recommendation_counts, 
        values='Count', 
        names='Recommendation',
        color='Recommendation',
        color_discrete_map=colors
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        title='Analysis Recommendations Distribution',
        height=400
    )
    
    return fig

def create_trading_analysis_chart(trading_history):
    """
    Create analysis charts for trading history
    
    Parameters:
    - trading_history: DataFrame with trading history
    
    Returns:
    - Tuple with multiple Plotly figures
    """
    if trading_history is None or trading_history.empty:
        return None, None
    
    # Create time series chart of transactions
    trading_history['transaction_date'] = pd.to_datetime(trading_history['transaction_date'])
    trading_by_date = trading_history.copy()
    
    # Create monthly aggregation
    trading_by_date['month'] = trading_by_date['transaction_date'].dt.strftime('%Y-%m')
    monthly_trading = trading_by_date.groupby(['month', 'transaction_type']).agg(
        total_value=('total_amount', 'sum'),
        count=('id', 'count')
    ).reset_index()
    
    # Time series chart
    fig1 = px.bar(
        monthly_trading,
        x='month',
        y='total_value',
        color='transaction_type',
        color_discrete_map={'buy': '#00C853', 'sell': '#FF6B6B'},
        barmode='group',
        labels={'total_value': 'Total Value', 'month': 'Month', 'transaction_type': 'Transaction Type'},
        title='Monthly Trading Activity'
    )
    
    # Stock distribution chart
    stock_distribution = trading_history.groupby('stock_symbol').agg(
        total_value=('total_amount', 'sum'),
        count=('id', 'count')
    ).reset_index()
    
    stock_distribution = stock_distribution.sort_values('total_value', ascending=False).head(10)
    
    fig2 = px.bar(
        stock_distribution,
        x='stock_symbol',
        y='total_value',
        labels={'total_value': 'Total Value', 'stock_symbol': 'Stock', 'count': 'Number of Transactions'},
        title='Top 10 Stocks by Trading Value',
        color='total_value',
        color_continuous_scale=['#5D6D7E', '#2962FF']
    )
    
    return fig1, fig2

def format_portfolio_data(portfolio):
    """
    Format portfolio data with current prices and profit/loss calculations
    
    Parameters:
    - portfolio: DataFrame with portfolio data
    
    Returns:
    - Formatted DataFrame with current prices and P/L
    """
    if portfolio is None or portfolio.empty:
        return pd.DataFrame()
    
    # Create a copy to avoid modifying the original
    df = portfolio.copy()
    
    # Add current prices and calculate P/L
    current_prices = {}
    for index, row in df.iterrows():
        try:
            # Get current price (with cache to avoid multiple API calls for same symbol)
            symbol = row['stock_symbol']
            if symbol not in current_prices:
                current_prices[symbol] = get_current_price(symbol)
            
            current_price = current_prices[symbol]
            
            # Calculate values
            df.at[index, 'current_price'] = current_price
            df.at[index, 'current_value'] = current_price * row['quantity']
            df.at[index, 'invested_value'] = row['average_buy_price'] * row['quantity']
            df.at[index, 'profit_loss'] = df.at[index, 'current_value'] - df.at[index, 'invested_value']
            df.at[index, 'profit_loss_pct'] = (df.at[index, 'profit_loss'] / df.at[index, 'invested_value']) * 100
        except Exception as e:
            # Handle any errors gracefully
            st.warning(f"Error getting current price for {row['stock_symbol']}: {e}")
            df.at[index, 'current_price'] = None
            df.at[index, 'current_value'] = None
            df.at[index, 'profit_loss'] = None
            df.at[index, 'profit_loss_pct'] = None
    
    # Format the date
    if 'last_updated' in df.columns:
        df['last_updated'] = pd.to_datetime(df['last_updated'])
        df['formatted_date'] = df['last_updated'].dt.strftime('%b %d, %Y')
    
    return df

def format_watchlist_data(watchlist):
    """
    Format watchlist data with current prices
    
    Parameters:
    - watchlist: DataFrame with watchlist data
    
    Returns:
    - Formatted DataFrame with current prices
    """
    if watchlist is None or watchlist.empty:
        return pd.DataFrame()
    
    # Create a copy to avoid modifying the original
    df = watchlist.copy()
    
    # Add current prices
    for index, row in df.iterrows():
        try:
            # Get current price
            symbol = row['stock_symbol']
            current_price = get_current_price(symbol)
            
            df.at[index, 'current_price'] = current_price
        except Exception as e:
            # Handle any errors gracefully
            st.warning(f"Error getting current price for {row['stock_symbol']}: {e}")
            df.at[index, 'current_price'] = None
    
    # Format the date
    if 'added_date' in df.columns:
        df['added_date'] = pd.to_datetime(df['added_date'])
        df['formatted_date'] = df['added_date'].dt.strftime('%b %d, %Y')
    
    return df
