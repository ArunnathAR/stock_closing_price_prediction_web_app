import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from dashboard import load_user_data, format_history_data, format_trading_data, format_portfolio_data, format_watchlist_data, create_analysis_trend_chart, create_trading_analysis_chart
from utils import format_currency, format_percentage, display_error_message, display_info_message, display_success_message
from auth import is_authenticated
from database import add_to_watchlist, remove_from_watchlist

# Set page config
st.set_page_config(
    page_title="Dashboard | Stock Market Platform",
    page_icon="📋",
    layout="wide"
)

# Check authentication
if not is_authenticated():
    st.warning("Please log in to access this page.")
    st.stop()

# Page title
st.markdown('<h1 class="title-text">Personal Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p class="body-text">Track your stock analysis history and trading activity</p>', unsafe_allow_html=True)

# Load user data
with st.spinner("Loading your dashboard..."):
    user_data = load_user_data(st.session_state.user_id)
    
    # Format the data
    stock_history = format_history_data(user_data['stock_history']) if 'stock_history' in user_data else pd.DataFrame()
    trading_history = format_trading_data(user_data['trading_history']) if 'trading_history' in user_data else pd.DataFrame()
    portfolio = format_portfolio_data(user_data['portfolio']) if 'portfolio' in user_data else pd.DataFrame()
    watchlist = format_watchlist_data(user_data['watchlist']) if 'watchlist' in user_data else pd.DataFrame()

# Dashboard layout
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<h2 class="title-text">Activity Overview</h2>', unsafe_allow_html=True)
    
    # Summary metrics
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        total_analyses = len(stock_history) if not stock_history.empty else 0
        st.metric("Total Stock Analyses", total_analyses)
    
    with metric_col2:
        total_trades = len(trading_history) if not trading_history.empty else 0
        st.metric("Total Trades", total_trades)
    
    with metric_col3:
        if not trading_history.empty and 'total_value' in trading_history.columns:
            total_value = trading_history['total_value'].sum()
            st.metric("Total Trading Value", format_currency(total_value))
        else:
            st.metric("Total Trading Value", format_currency(0))

with col2:
    st.markdown('<h2 class="title-text">Analysis Distribution</h2>', unsafe_allow_html=True)
    
    if not stock_history.empty:
        # Create analysis trend chart
        analysis_chart = create_analysis_trend_chart(stock_history)
        
        if analysis_chart:
            st.plotly_chart(analysis_chart, use_container_width=True)
        else:
            display_info_message("Not enough analysis data to show distribution.")
    else:
        display_info_message("No analysis history found. Start analyzing stocks to see data here.")

# Recent stock analyses
st.markdown('<h2 class="title-text">Recent Stock Analyses</h2>', unsafe_allow_html=True)

if not stock_history.empty:
    # Display recent analyses
    st.dataframe(
        stock_history[['formatted_date', 'stock_symbol', 'analysis_period', 'recommendation_display']].head(10),
        column_config={
            "formatted_date": "Date",
            "stock_symbol": "Stock",
            "analysis_period": "Period",
            "recommendation_display": "Recommendation"
        },
        hide_index=True
    )
    
    # Most analyzed stocks
    st.markdown('<h3 class="title-text">Most Analyzed Stocks</h3>', unsafe_allow_html=True)
    
    stock_counts = stock_history['stock_symbol'].value_counts().reset_index()
    stock_counts.columns = ['Stock', 'Count']
    
    fig = px.bar(
        stock_counts.head(10),
        x='Stock',
        y='Count',
        title='Top 10 Most Analyzed Stocks',
        color='Count',
        color_continuous_scale=['#5D6D7E', '#2962FF']
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    display_info_message("No analysis history found. Start analyzing stocks to see data here.")

# Trading history
st.markdown('<h2 class="title-text">Trading History</h2>', unsafe_allow_html=True)

if not trading_history.empty:
    # Display recent trades
    st.dataframe(
        trading_history[['formatted_date', 'stock_symbol', 'transaction_type_display', 'quantity', 'price', 'total_amount']].head(10),
        column_config={
            "formatted_date": "Date",
            "stock_symbol": "Stock",
            "transaction_type_display": "Type",
            "quantity": "Quantity",
            "price": st.column_config.NumberColumn("Price", format="₹%.2f"),
            "total_amount": st.column_config.NumberColumn("Total Amount", format="₹%.2f")
        },
        hide_index=True
    )
    
    # Trading activity charts
    st.markdown('<h3 class="title-text">Trading Activity</h3>', unsafe_allow_html=True)
    
    # Create trading analysis charts
    trading_chart1, trading_chart2 = create_trading_analysis_chart(trading_history)
    
    if trading_chart1 and trading_chart2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(trading_chart1, use_container_width=True)
        
        with col2:
            st.plotly_chart(trading_chart2, use_container_width=True)
    else:
        display_info_message("Not enough trading data to show analysis charts.")
else:
    display_info_message("No trading history found. Start executing trades to see data here.")

# Portfolio section
st.markdown('<h2 class="title-text">Your Portfolio</h2>', unsafe_allow_html=True)

if not portfolio.empty:
    # Calculate portfolio total value and profit/loss
    total_invested = portfolio['invested_value'].sum()
    total_current = portfolio['current_value'].sum()
    total_profit_loss = portfolio['profit_loss'].sum()
    profit_loss_pct = (total_profit_loss / total_invested) * 100 if total_invested > 0 else 0
    
    # Display portfolio summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Invested", format_currency(total_invested))
    
    with col2:
        st.metric("Current Value", format_currency(total_current))
    
    with col3:
        st.metric("Total Profit/Loss", 
                 format_currency(total_profit_loss), 
                 format_percentage(profit_loss_pct))
    
    # Display portfolio table
    st.dataframe(
        portfolio[['stock_symbol', 'quantity', 'average_buy_price', 'current_price', 'current_value', 'profit_loss', 'profit_loss_pct']],
        column_config={
            "stock_symbol": "Stock",
            "quantity": "Quantity",
            "average_buy_price": st.column_config.NumberColumn("Avg. Buy Price", format="₹%.2f"),
            "current_price": st.column_config.NumberColumn("Current Price", format="₹%.2f"),
            "current_value": st.column_config.NumberColumn("Current Value", format="₹%.2f"),
            "profit_loss": st.column_config.NumberColumn("Profit/Loss", format="₹%.2f"),
            "profit_loss_pct": st.column_config.NumberColumn("P/L %", format="%.2f%%")
        },
        hide_index=True
    )
    
    # Portfolio composition
    st.markdown('<h3 class="title-text">Portfolio Composition</h3>', unsafe_allow_html=True)
    
    fig = px.pie(
        portfolio, 
        values='current_value', 
        names='stock_symbol',
        title='Portfolio Allocation',
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)
    
else:
    display_info_message("Your portfolio is empty. Start trading to build your portfolio.")

# Watchlist section
st.markdown('<h2 class="title-text">Your Watchlist</h2>', unsafe_allow_html=True)

# Add to watchlist form
col1, col2 = st.columns([3, 1])

with col1:
    with st.form("add_watchlist_form", clear_on_submit=True):
        stock_symbol = st.text_input("Enter stock symbol to add to watchlist:", max_chars=10)
        submitted = st.form_submit_button("Add to Watchlist")
        
        if submitted and stock_symbol:
            success = add_to_watchlist(st.session_state.user_id, stock_symbol.upper())
            if success:
                st.rerun()  # Refresh the page to show updated watchlist

if not watchlist.empty:
    # Display watchlist table
    watchlist_df = st.dataframe(
        watchlist[['stock_symbol', 'current_price', 'formatted_date']],
        column_config={
            "stock_symbol": "Stock",
            "current_price": st.column_config.NumberColumn("Current Price", format="₹%.2f"),
            "formatted_date": "Date Added"
        },
        hide_index=True
    )
    
    # Remove from watchlist
    stock_to_remove = st.selectbox("Select stock to remove from watchlist:", watchlist['stock_symbol'].tolist())
    if st.button("Remove from Watchlist"):
        success = remove_from_watchlist(st.session_state.user_id, stock_to_remove)
        if success:
            display_success_message(f"Removed {stock_to_remove} from watchlist.")
            st.rerun()  # Refresh the page to show updated watchlist
else:
    display_info_message("Your watchlist is empty. Add stocks to track them.")

# Tips and recommendations
st.markdown('<h2 class="title-text">Tips & Recommendations</h2>', unsafe_allow_html=True)

st.markdown("""
<div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
    <h3 style="margin-top: 0;" class="title-text">Improving Your Investment Strategy</h3>
    
    <p><strong>1. Diversify Your Portfolio</strong><br>
    Analyze different sectors to spread risk across various industries.</p>
    
    <p><strong>2. Regular Analysis</strong><br>
    Set a schedule to review stocks regularly, even those already in your portfolio.</p>
    
    <p><strong>3. Long-term Perspective</strong><br>
    Focus on stocks with strong fundamentals rather than short-term price movements.</p>
    
    <p><strong>4. Tax Efficiency</strong><br>
    Consider tax implications when planning buy/sell decisions, especially holding periods.</p>
    
    <p><strong>5. Market Trends</strong><br>
    Stay informed about broader market trends that may affect your investments.</p>
</div>
""", unsafe_allow_html=True)

# Feedback section
st.markdown('<h2 class="title-text">Your Feedback</h2>', unsafe_allow_html=True)

with st.form("feedback_form"):
    st.markdown('<p class="body-text">Help us improve by sharing your thoughts about the platform.</p>', unsafe_allow_html=True)
    
    feedback_rating = st.slider("Rate your experience", 1, 5, 5)
    feedback_text = st.text_area("Your comments or suggestions")
    
    submitted = st.form_submit_button("Submit Feedback")
    
    if submitted:
        st.success("Thank you for your feedback! We appreciate your input.")
