import os
import sqlite3
import streamlit as st
import pandas as pd
from datetime import datetime
import json

# Database path
DB_PATH = "stockapp.db"

def get_db_connection():
    """Create a connection to the SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Initialize the database with necessary tables if they don't exist."""
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
    
    conn.commit()
    conn.close()

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
