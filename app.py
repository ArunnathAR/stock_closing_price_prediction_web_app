import streamlit as st
import pandas as pd
import time
from auth import login, signup, initialize_authentication, is_authenticated, logout
from database import initialize_database

# Set page configuration
st.set_page_config(
    page_title="Stock Market Analysis Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize authentication and database
initialize_authentication()
initialize_database()

# Custom styling for headers and text
st.markdown("""
    <style>
    .title-text {
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
    }
    .body-text {
        font-family: 'Inter', sans-serif;
        font-weight: 400;
    }
    .data-text {
        font-family: 'Roboto Mono', monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# Main container
def main():
    if not is_authenticated():
        st.markdown('<h1 class="title-text">Stock Market Analysis Platform</h1>', unsafe_allow_html=True)
        st.markdown('<p class="body-text">Make informed investment decisions with our comprehensive analysis tools.</p>', unsafe_allow_html=True)
        
        # Login/Signup tabs
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            login()
        
        with tab2:
            signup()
    
    else:
        # Display welcome message and logout button
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f'<h1 class="title-text">Welcome to the Stock Market Analysis Platform</h1>', unsafe_allow_html=True)
        
        with col2:
            if st.button("Logout"):
                logout()
                st.rerun()
        
        # Main page content
        st.markdown('<p class="body-text">Use the sidebar to navigate through different features.</p>', unsafe_allow_html=True)
        
        st.markdown("## Features Overview")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<h3 class="title-text">Stock Analysis</h3>', unsafe_allow_html=True)
            st.markdown('<p class="body-text">• View real-time stock data<br>• Analyze market trends<br>• Get price predictions</p>', unsafe_allow_html=True)
            st.page_link("pages/1_Stock_Analysis.py", label="Go to Stock Analysis", icon="📊")
        
        with col2:
            st.markdown('<h3 class="title-text">Trading Interface</h3>', unsafe_allow_html=True)
            st.markdown('<p class="body-text">• Simulate buy/sell transactions<br>• Calculate taxes<br>• Get profit recommendations</p>', unsafe_allow_html=True)
            st.page_link("pages/2_Trading.py", label="Go to Trading", icon="💹")
        
        with col3:
            st.markdown('<h3 class="title-text">Personal Dashboard</h3>', unsafe_allow_html=True)
            st.markdown('<p class="body-text">• View your analysis history<br>• Track performance<br>• Manage preferences</p>', unsafe_allow_html=True)
            st.page_link("pages/3_Dashboard.py", label="Go to Dashboard", icon="📋")

        # Display Nifty 50 overview
        st.markdown("## Nifty 50 Overview")
        with st.spinner("Loading market data..."):
            time.sleep(1)  # Simulate loading
            # This will be replaced with actual data in the full implementation
            st.info("Please navigate to Stock Analysis page to view detailed market data.")

if __name__ == "__main__":
    main()
