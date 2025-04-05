import os
import sqlite3
import streamlit as st
import pandas as pd
from datetime import datetime
import json

# Database path
DB_PATH = "stockapp.db"

# Initialize database when this module is imported
if not os.path.exists(DB_PATH) or os.path.getsize(DB_PATH) == 0:
    print("Creating new database file...")
else:
    print(f"Using existing database at {DB_PATH}")

# Create tables at module import time
initialize_database_called = False

def get_db_connection():
    """Create a connection to the SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Initialize the database with necessary tables if they don't exist."""
    global initialize_database_called
    
    # Return if already initialized to prevent multiple calls
    if initialize_database_called:
        return
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create stock_history table for storing user's analysis history
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        stock_symbol TEXT NOT NULL,
        analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        analysis_period TEXT NOT NULL,
        prediction_result TEXT,
        recommendation TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create trading_history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trading_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        stock_symbol TEXT NOT NULL,
        transaction_type TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        tax_amount REAL,
        total_amount REAL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create portfolio table for tracking user holdings
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS portfolio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        stock_symbol TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        average_buy_price REAL NOT NULL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        UNIQUE(user_id, stock_symbol)
    )
    ''')
    
    # Create watchlist table for users to track favorite stocks
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS watchlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        stock_symbol TEXT NOT NULL,
        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        UNIQUE(user_id, stock_symbol)
    )
    ''')
    
    conn.commit()
    conn.close()
    
    initialize_database_called = True
    print("Database tables initialized")

def add_user(username, email, password):
    """Add a new user to the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password)
        )
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        return None
    except Exception as e:
        st.error(f"Error adding user: {e}")
        return None

def check_user_exists(username):
    """Check if a username already exists in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    
    conn.close()
    return result is not None

def verify_user(username):
    """Verify if a user exists and return their credentials."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return result['id'], True, result['password']
    else:
        return None, False, None

def save_stock_analysis(user_id, stock_symbol, analysis_period, prediction_result, recommendation):
    """Save stock analysis results to the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Convert prediction_result to JSON string if it's a dictionary or list
        if isinstance(prediction_result, (dict, list)):
            prediction_result = json.dumps(prediction_result)
        
        cursor.execute(
            """
            INSERT INTO stock_history 
            (user_id, stock_symbol, analysis_period, prediction_result, recommendation)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, stock_symbol, analysis_period, prediction_result, recommendation)
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving stock analysis: {e}")
        return False

def get_user_stock_history(user_id, limit=20):
    """Get user's stock analysis history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT * FROM stock_history 
        WHERE user_id = ? 
        ORDER BY analysis_date DESC
        LIMIT ?
        """,
        (user_id, limit)
    )
    
    results = cursor.fetchall()
    conn.close()
    
    # Convert to DataFrame
    if results:
        # Convert rows to dictionaries
        history = [dict(row) for row in results]
        return pd.DataFrame(history)
    else:
        return pd.DataFrame(columns=[
            'id', 'user_id', 'stock_symbol', 'analysis_date', 
            'analysis_period', 'prediction_result', 'recommendation'
        ])

def save_trading_transaction(user_id, stock_symbol, transaction_type, quantity, price, tax_amount, total_amount):
    """Save trading transaction to the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO trading_history 
            (user_id, stock_symbol, transaction_type, quantity, price, tax_amount, total_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, stock_symbol, transaction_type, quantity, price, tax_amount, total_amount)
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving trading transaction: {e}")
        return False

def get_user_trading_history(user_id, limit=50):
    """Get user's trading history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT * FROM trading_history 
        WHERE user_id = ? 
        ORDER BY transaction_date DESC
        LIMIT ?
        """,
        (user_id, limit)
    )
    
    results = cursor.fetchall()
    conn.close()
    
    # Convert to DataFrame
    if results:
        # Convert rows to dictionaries
        history = [dict(row) for row in results]
        return pd.DataFrame(history)
    else:
        return pd.DataFrame(columns=[
            'id', 'user_id', 'stock_symbol', 'transaction_type', 'quantity',
            'price', 'transaction_date', 'tax_amount', 'total_amount'
        ])

def add_to_portfolio(user_id, stock_symbol, quantity, buy_price):
    """
    Add or update stocks in user portfolio
    
    Parameters:
    - user_id: User ID
    - stock_symbol: Stock symbol
    - quantity: Quantity to add (positive) or remove (negative)
    - buy_price: Purchase price (used for average calculation)
    
    Returns:
    - Boolean indicating success
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if stock already exists in portfolio
        cursor.execute(
            "SELECT quantity, average_buy_price FROM portfolio WHERE user_id = ? AND stock_symbol = ?",
            (user_id, stock_symbol)
        )
        
        result = cursor.fetchone()
        
        if result:
            # Stock exists, update quantity and average price
            current_quantity = result['quantity']
            current_avg_price = result['average_buy_price']
            
            if quantity > 0:
                # Buying more shares - update average price
                new_quantity = current_quantity + quantity
                new_avg_price = ((current_quantity * current_avg_price) + (quantity * buy_price)) / new_quantity
                
                cursor.execute(
                    """
                    UPDATE portfolio 
                    SET quantity = ?, average_buy_price = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND stock_symbol = ?
                    """,
                    (new_quantity, new_avg_price, user_id, stock_symbol)
                )
            else:
                # Selling shares - keep same average price but reduce quantity
                new_quantity = current_quantity + quantity  # quantity is negative for selling
                
                if new_quantity <= 0:
                    # Remove from portfolio if all shares sold
                    cursor.execute(
                        "DELETE FROM portfolio WHERE user_id = ? AND stock_symbol = ?",
                        (user_id, stock_symbol)
                    )
                else:
                    # Update with reduced quantity
                    cursor.execute(
                        """
                        UPDATE portfolio 
                        SET quantity = ?, last_updated = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND stock_symbol = ?
                        """,
                        (new_quantity, user_id, stock_symbol)
                    )
        else:
            # New stock, only insert if buying (positive quantity)
            if quantity > 0:
                cursor.execute(
                    """
                    INSERT INTO portfolio (user_id, stock_symbol, quantity, average_buy_price)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_id, stock_symbol, quantity, buy_price)
                )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error updating portfolio: {e}")
        return False

def get_user_portfolio(user_id):
    """
    Get user's portfolio
    
    Parameters:
    - user_id: User ID
    
    Returns:
    - DataFrame with portfolio data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT * FROM portfolio 
        WHERE user_id = ? 
        ORDER BY stock_symbol
        """,
        (user_id,)
    )
    
    results = cursor.fetchall()
    conn.close()
    
    # Convert to DataFrame
    if results:
        # Convert rows to dictionaries
        portfolio = [dict(row) for row in results]
        return pd.DataFrame(portfolio)
    else:
        return pd.DataFrame(columns=[
            'id', 'user_id', 'stock_symbol', 'quantity',
            'average_buy_price', 'last_updated'
        ])

def add_to_watchlist(user_id, stock_symbol):
    """
    Add stock to user's watchlist
    
    Parameters:
    - user_id: User ID
    - stock_symbol: Stock symbol
    
    Returns:
    - Boolean indicating success
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Use INSERT OR IGNORE to handle duplicates
        cursor.execute(
            """
            INSERT OR IGNORE INTO watchlist (user_id, stock_symbol)
            VALUES (?, ?)
            """,
            (user_id, stock_symbol)
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error adding to watchlist: {e}")
        return False

def remove_from_watchlist(user_id, stock_symbol):
    """
    Remove stock from user's watchlist
    
    Parameters:
    - user_id: User ID
    - stock_symbol: Stock symbol
    
    Returns:
    - Boolean indicating success
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            DELETE FROM watchlist
            WHERE user_id = ? AND stock_symbol = ?
            """,
            (user_id, stock_symbol)
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error removing from watchlist: {e}")
        return False

def get_user_watchlist(user_id):
    """
    Get user's watchlist
    
    Parameters:
    - user_id: User ID
    
    Returns:
    - DataFrame with watchlist data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT * FROM watchlist 
        WHERE user_id = ? 
        ORDER BY added_date DESC
        """,
        (user_id,)
    )
    
    results = cursor.fetchall()
    conn.close()
    
    # Convert to DataFrame
    if results:
        # Convert rows to dictionaries
        watchlist = [dict(row) for row in results]
        return pd.DataFrame(watchlist)
    else:
        return pd.DataFrame(columns=[
            'id', 'user_id', 'stock_symbol', 'added_date'
        ])

# Initialize database tables when this module is imported
initialize_database()
