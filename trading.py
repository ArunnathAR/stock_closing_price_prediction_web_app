import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from database import save_trading_transaction
from stock_data import get_current_price

def calculate_tax(transaction_type, price, quantity, short_term=True):
    """
    Calculate taxes for stock transactions based on Indian tax laws
    
    Parameters:
    - transaction_type: 'buy' or 'sell'
    - price: Stock price
    - quantity: Number of shares
    - short_term: Whether it's a short-term (< 1 year) or long-term transaction
    
    Returns:
    - Dictionary with tax breakdown
    """
    total_value = price * quantity
    
    if transaction_type.lower() == 'buy':
        # For buy transactions
        stt = total_value * 0.001  # Securities Transaction Tax (0.1%)
        transaction_charges = total_value * 0.0001  # Approximate transaction charges (0.01%)
        gst = (transaction_charges) * 0.18  # GST on transaction charges (18%)
        stamp_duty = total_value * 0.00015  # Stamp duty (0.015%)
        
        total_tax = stt + transaction_charges + gst + stamp_duty
        total_cost = total_value + total_tax
        
        return {
            'transaction_value': total_value,
            'stt': stt,
            'transaction_charges': transaction_charges,
            'gst': gst,
            'stamp_duty': stamp_duty,
            'total_tax': total_tax,
            'total_cost': total_cost
        }
    
    elif transaction_type.lower() == 'sell':
        # For sell transactions
        stt = total_value * 0.001  # Securities Transaction Tax (0.1%)
        transaction_charges = total_value * 0.0001  # Approximate transaction charges (0.01%)
        gst = (transaction_charges) * 0.18  # GST on transaction charges (18%)
        
        # Income tax depends on short-term or long-term
        if short_term:
            # Short-term capital gains tax (assumed 15%)
            income_tax = total_value * 0.15
        else:
            # Long-term capital gains tax (10% above ₹1 lakh)
            if total_value > 100000:
                income_tax = (total_value - 100000) * 0.10
            else:
                income_tax = 0
        
        total_tax = stt + transaction_charges + gst + income_tax
        net_proceed = total_value - total_tax
        
        return {
            'transaction_value': total_value,
            'stt': stt,
            'transaction_charges': transaction_charges,
            'gst': gst,
            'income_tax': income_tax,
            'total_tax': total_tax,
            'net_proceed': net_proceed
        }
    
    else:
        return None

def calculate_profit_potential(current_price, prediction_price, quantity, tax_rate=0.15):
    """
    Calculate potential profit based on prediction
    
    Parameters:
    - current_price: Current stock price
    - prediction_price: Predicted stock price
    - quantity: Number of shares
    - tax_rate: Effective tax rate (default: 15% for short-term)
    
    Returns:
    - Dictionary with profit breakdown
    """
    investment = current_price * quantity
    future_value = prediction_price * quantity
    gross_profit = future_value - investment
    tax = max(0, gross_profit * tax_rate)  # Tax only on positive profit
    net_profit = gross_profit - tax
    roi_percentage = (net_profit / investment) * 100 if investment > 0 else 0
    
    return {
        'investment': investment,
        'future_value': future_value,
        'gross_profit': gross_profit,
        'tax': tax,
        'net_profit': net_profit,
        'roi_percentage': roi_percentage
    }

def get_broker_recommendations():
    """
    Get list of brokers with their features and links
    
    Returns:
    - List of broker dictionaries
    """
    brokers = [
        {
            'name': 'Zerodha',
            'brokerage': '₹20 per trade or 0.03% (whichever is lower)',
            'min_account': '₹0',
            'features': 'User-friendly platform, low brokerage',
            'link': 'https://zerodha.com/'
        },
        {
            'name': 'Upstox',
            'brokerage': '₹20 per trade or 0.05% (whichever is lower)',
            'min_account': '₹0',
            'features': 'Good mobile app, research tools',
            'link': 'https://upstox.com/'
        },
        {
            'name': 'Groww',
            'brokerage': 'Free equity delivery, ₹20 per trade for intraday',
            'min_account': '₹0',
            'features': 'Simple interface, good for beginners',
            'link': 'https://groww.in/'
        },
        {
            'name': 'ICICI Direct',
            'brokerage': '₹20 per trade or 0.25% (whichever is lower)',
            'min_account': '₹0',
            'features': 'Integration with ICICI Bank, research reports',
            'link': 'https://www.icicidirect.com/'
        },
        {
            'name': 'Angel Broking',
            'brokerage': 'Flat ₹20 per trade',
            'min_account': '₹0',
            'features': 'AI-powered advisory, good research',
            'link': 'https://www.angelbroking.com/'
        }
    ]
    
    return brokers

def execute_trade(user_id, stock_symbol, transaction_type, quantity, price):
    """
    Execute a simulated trade and save to database
    
    Parameters:
    - user_id: User ID
    - stock_symbol: Stock symbol
    - transaction_type: 'buy' or 'sell'
    - quantity: Number of shares
    - price: Stock price
    
    Returns:
    - Boolean indicating success
    """
    try:
        tax_info = calculate_tax(transaction_type, price, quantity)
        
        if tax_info is None:
            st.error("Invalid transaction type.")
            return False
        
        if transaction_type.lower() == 'buy':
            total_amount = tax_info['total_cost']
            tax_amount = tax_info['total_tax']
        else:
            total_amount = tax_info['net_proceed']
            tax_amount = tax_info['total_tax']
        
        # Save transaction to database
        success = save_trading_transaction(
            user_id, 
            stock_symbol, 
            transaction_type.lower(), 
            quantity, 
            price, 
            tax_amount, 
            total_amount
        )
        
        return success
    
    except Exception as e:
        st.error(f"Error executing trade: {e}")
        return False
