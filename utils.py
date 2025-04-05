import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta

def format_currency(value):
    """
    Format a value as currency (INR)
    
    Parameters:
    - value: Numeric value to format
    
    Returns:
    - Formatted string with currency symbol
    """
    try:
        return f"₹{value:,.2f}"
    except:
        return "₹0.00"

def format_percentage(value):
    """
    Format a value as percentage
    
    Parameters:
    - value: Numeric value to format
    
    Returns:
    - Formatted string with percentage symbol
    """
    try:
        return f"{value:.2f}%"
    except:
        return "0.00%"

def color_coded_text(value, text, threshold=0):
    """
    Create HTML for color-coded text based on value
    
    Parameters:
    - value: Numeric value to check
    - text: Text to display
    - threshold: Threshold for color change (default: 0)
    
    Returns:
    - HTML string with color-coded text
    """
    try:
        if value > threshold:
            return f'<span style="color:#00C853">{text}</span>'
        elif value < threshold:
            return f'<span style="color:#FF6B6B">{text}</span>'
        else:
            return f'<span style="color:#5D6D7E">{text}</span>'
    except:
        return text

def create_recommendation_box(recommendation, explanation):
    """
    Create a styled recommendation box
    
    Parameters:
    - recommendation: 'buy', 'sell', or 'hold'
    - explanation: Explanation text
    
    Returns:
    - None (displays directly in Streamlit)
    """
    # Set color based on recommendation
    if recommendation.lower() == 'buy':
        color = '#00C853'  # Green
        icon = '↗️'
    elif recommendation.lower() == 'sell':
        color = '#FF6B6B'  # Red
        icon = '↘️'
    else:
        color = '#FFA726'  # Orange
        icon = '↔️'
    
    # Create the recommendation box
    st.markdown(f"""
    <div style="
        border: 2px solid {color};
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0px;
        background-color: rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1);
    ">
        <h3 style="color: {color}; margin-top: 0;">{icon} Recommendation: {recommendation.upper()}</h3>
        <p style="white-space: pre-line;">{explanation}</p>
    </div>
    """, unsafe_allow_html=True)

def loading_spinner(text="Please wait..."):
    """
    Create a loading spinner with custom text
    
    Parameters:
    - text: Text to display during loading
    
    Returns:
    - Streamlit spinner context manager
    """
    return st.spinner(text)

def create_metric_card(title, value, delta=None, delta_description="from previous"):
    """
    Create a custom metric card with title, value, and delta
    
    Parameters:
    - title: Card title
    - value: Main value to display
    - delta: Change value (can be None)
    - delta_description: Description text for delta
    
    Returns:
    - None (displays directly in Streamlit)
    """
    if delta is not None:
        delta_color = "green" if delta >= 0 else "red"
        delta_sign = "+" if delta >= 0 else ""
        delta_html = f'<span style="color: {delta_color};">{delta_sign}{delta:.2f}% {delta_description}</span>'
    else:
        delta_html = ""
    
    st.markdown(f"""
    <div style="
        border: 1px solid #e6e6e6;
        border-radius: 5px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        background-color: white;
    ">
        <p style="font-size: 1rem; color: #5D6D7E; margin-bottom: 5px;">{title}</p>
        <h3 style="font-family: 'Roboto Mono', monospace; margin: 0;">{value}</h3>
        <p style="font-size: 0.8rem; margin-top: 5px;">{delta_html}</p>
    </div>
    """, unsafe_allow_html=True)

def display_error_message(message):
    """
    Display a formatted error message
    
    Parameters:
    - message: Error message to display
    
    Returns:
    - None (displays directly in Streamlit)
    """
    st.error(message)

def display_info_message(message):
    """
    Display a formatted info message
    
    Parameters:
    - message: Info message to display
    
    Returns:
    - None (displays directly in Streamlit)
    """
    st.info(message)

def display_success_message(message):
    """
    Display a formatted success message
    
    Parameters:
    - message: Success message to display
    
    Returns:
    - None (displays directly in Streamlit)
    """
    st.success(message)
