import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from stock_data import get_stock_data, NIFTY50_STOCKS, calculate_technical_indicators, get_current_price, get_stock_overview
from prediction import StockPredictor
from utils import format_currency, format_percentage, create_recommendation_box, loading_spinner, display_error_message
from database import save_stock_analysis
from auth import is_authenticated

# Set page config
st.set_page_config(
    page_title="Stock Analysis | Stock Market Platform",
    page_icon="📊",
    layout="wide"
)

# Check authentication
if not is_authenticated():
    st.warning("Please log in to access this page.")
    st.stop()

# Page title
st.markdown('<h1 class="title-text">Stock Analysis</h1>', unsafe_allow_html=True)
st.markdown('<p class="body-text">Analyze stocks and get price predictions</p>', unsafe_allow_html=True)

# Stock selection and period
col1, col2 = st.columns([2, 1])

with col1:
    # Clean up stock symbols for display
    display_stocks = [stock.split('.')[0] for stock in NIFTY50_STOCKS]
    selected_stock_display = st.selectbox("Select a stock", display_stocks)
    # Get the full symbol for API call
    selected_stock = NIFTY50_STOCKS[display_stocks.index(selected_stock_display)]

with col2:
    analysis_period = st.selectbox(
        "Analysis period",
        options=["1month", "3month", "5month"],
        index=0
    )

# Fetch stock data
with loading_spinner("Fetching stock data..."):
    stock_data = get_stock_data(selected_stock, analysis_period)
    
    if stock_data is None or stock_data.empty:
        display_error_message("Unable to fetch stock data. Please try again later.")
        st.stop()
    
    # Calculate technical indicators
    stock_data_with_indicators = calculate_technical_indicators(stock_data)
    
    # Get current price
    current_price = get_current_price(selected_stock)
    
    # Get stock overview
    stock_overview = get_stock_overview(selected_stock)

# Display stock overview
if stock_overview:
    st.markdown(f'<h2 class="title-text">{selected_stock_display} Overview</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Current Price", f"₹{current_price:.2f}")
    
    with col2:
        if 'PERatio' in stock_overview:
            st.metric("P/E Ratio", f"{float(stock_overview.get('PERatio', 'N/A')):.2f}")
        else:
            st.metric("P/E Ratio", "N/A")
    
    with col3:
        if 'DividendYield' in stock_overview:
            st.metric("Dividend Yield", f"{float(stock_overview.get('DividendYield', '0')):.2f}%")
        else:
            st.metric("Dividend Yield", "N/A")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Description' in stock_overview:
            st.markdown(f'<p class="body-text"><strong>About:</strong> {stock_overview.get("Description", "No description available.")}</p>', unsafe_allow_html=True)
    
    with col2:
        if 'Sector' in stock_overview:
            st.markdown(f'<p class="body-text"><strong>Sector:</strong> {stock_overview.get("Sector", "N/A")}</p>', unsafe_allow_html=True)
        if 'Industry' in stock_overview:
            st.markdown(f'<p class="body-text"><strong>Industry:</strong> {stock_overview.get("Industry", "N/A")}</p>', unsafe_allow_html=True)

# Stock price chart
st.markdown(f'<h2 class="title-text">Price Chart</h2>', unsafe_allow_html=True)

# Create figure
fig = go.Figure()

# Add candlestick chart
fig.add_trace(
    go.Candlestick(
        x=stock_data.index,
        open=stock_data['open'],
        high=stock_data['high'],
        low=stock_data['low'],
        close=stock_data['close'],
        name='Price'
    )
)

# Add volume as bar chart on secondary y-axis
fig.add_trace(
    go.Bar(
        x=stock_data.index,
        y=stock_data['volume'],
        name='Volume',
        marker_color='rgba(45, 69, 98, 0.3)',
        yaxis='y2'
    )
)

# Add moving averages if available
if 'SMA_20' in stock_data_with_indicators.columns:
    fig.add_trace(
        go.Scatter(
            x=stock_data_with_indicators.index,
            y=stock_data_with_indicators['SMA_20'],
            name='SMA 20',
            line=dict(color='#2962FF', width=1)
        )
    )

if 'SMA_50' in stock_data_with_indicators.columns:
    fig.add_trace(
        go.Scatter(
            x=stock_data_with_indicators.index,
            y=stock_data_with_indicators['SMA_50'],
            name='SMA 50',
            line=dict(color='#00C853', width=1)
        )
    )

# Update layout
fig.update_layout(
    title=f'{selected_stock_display} Stock Price',
    xaxis_title='Date',
    yaxis_title='Price',
    xaxis_rangeslider_visible=True,
    yaxis2=dict(
        title='Volume',
        overlaying='y',
        side='right',
        showgrid=False
    ),
    height=600,
    template='plotly_white',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

# Display chart
st.plotly_chart(fig, use_container_width=True)

# Technical indicators
st.markdown(f'<h2 class="title-text">Technical Indicators</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    # RSI
    if 'RSI' in stock_data_with_indicators.columns:
        last_rsi = stock_data_with_indicators['RSI'].iloc[-1]
        rsi_status = "Overbought" if last_rsi > 70 else ("Oversold" if last_rsi < 30 else "Neutral")
        st.metric("RSI (14)", f"{last_rsi:.2f}", rsi_status)
    else:
        st.metric("RSI (14)", "N/A")

with col2:
    # MACD
    if 'MACD' in stock_data_with_indicators.columns and 'MACD_Signal' in stock_data_with_indicators.columns:
        last_macd = stock_data_with_indicators['MACD'].iloc[-1]
        last_signal = stock_data_with_indicators['MACD_Signal'].iloc[-1]
        macd_diff = last_macd - last_signal
        macd_status = f"{'+' if macd_diff > 0 else ''}{macd_diff:.4f}"
        st.metric("MACD", f"{last_macd:.4f}", macd_status)
    else:
        st.metric("MACD", "N/A")

with col3:
    # Bollinger Bands
    if 'BB_Middle' in stock_data_with_indicators.columns and 'BB_Upper' in stock_data_with_indicators.columns and 'BB_Lower' in stock_data_with_indicators.columns:
        last_price = stock_data['close'].iloc[-1]
        last_upper = stock_data_with_indicators['BB_Upper'].iloc[-1]
        last_lower = stock_data_with_indicators['BB_Lower'].iloc[-1]
        
        bb_position = (last_price - last_lower) / (last_upper - last_lower) * 100
        bb_status = "Upper Band" if bb_position > 80 else ("Lower Band" if bb_position < 20 else "Middle Band")
        
        st.metric("Bollinger Band Position", f"{bb_position:.2f}%", bb_status)
    else:
        st.metric("Bollinger Band Position", "N/A")

# Stock price prediction
st.markdown(f'<h2 class="title-text">Price Prediction</h2>', unsafe_allow_html=True)

# Run prediction
with loading_spinner("Generating price predictions..."):
    # Initialize predictor
    predictor = StockPredictor(stock_data, forecast_days=30)
    
    # Generate ensemble prediction
    ensemble_predictions = predictor.ensemble_prediction()
    
    if ensemble_predictions is None:
        display_error_message("Unable to generate predictions. Please try again later.")
    else:
        # Generate recommendation
        recommendation, explanation = predictor.generate_recommendation(ensemble_predictions, current_price)
        
        # Create prediction plot
        prediction_plot = predictor.plot_prediction(ensemble_predictions)
        
        if prediction_plot:
            st.plotly_chart(prediction_plot, use_container_width=True)
        
        # Display recommendation
        create_recommendation_box(recommendation, explanation)
        
        # Add trading buttons based on recommendation
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("Buy", type="primary" if recommendation == "buy" else "secondary"):
                # Store details in session state for trading page
                st.session_state.trade_stock = selected_stock
                st.session_state.trade_price = current_price
                st.session_state.trade_type = "buy"
                st.session_state.from_analysis = True
                # Redirect to trading page
                st.switch_page("pages/2_Trading.py")
        
        with col2:
            if st.button("Sell", type="primary" if recommendation == "sell" else "secondary"):
                # Store details in session state for trading page
                st.session_state.trade_stock = selected_stock
                st.session_state.trade_price = current_price
                st.session_state.trade_type = "sell"
                st.session_state.from_analysis = True
                # Redirect to trading page
                st.switch_page("pages/2_Trading.py")
        
        with col3:
            if st.button("Add to Watchlist"):
                # Logic to add to watchlist will be implemented
                from database import add_to_watchlist
                if add_to_watchlist(st.session_state.user_id, selected_stock):
                    st.success(f"{selected_stock_display} added to watchlist!")
                else:
                    st.error("Failed to add to watchlist or already in watchlist")
        
        # Save analysis to database if user is authenticated
        if st.session_state.user_id:
            # Convert ensemble predictions to string for storage
            prediction_result = {
                'last_price': float(current_price),
                'prediction_7d': float(ensemble_predictions['ensemble'].iloc[6]),
                'prediction_14d': float(ensemble_predictions['ensemble'].iloc[13]),
                'prediction_30d': float(ensemble_predictions['ensemble'].iloc[-1])
            }
            
            save_stock_analysis(
                st.session_state.user_id,
                selected_stock,
                analysis_period,
                prediction_result,
                recommendation
            )

# Indicator visualization
st.markdown(f'<h2 class="title-text">Technical Analysis</h2>', unsafe_allow_html=True)

# Technical indicator selection
selected_indicator = st.selectbox(
    "Select Technical Indicator",
    options=["RSI", "MACD", "Bollinger Bands"],
    index=0
)

# Create indicator plot
fig_indicator = go.Figure()

if selected_indicator == "RSI":
    if 'RSI' in stock_data_with_indicators.columns:
        # Add RSI line
        fig_indicator.add_trace(
            go.Scatter(
                x=stock_data_with_indicators.index,
                y=stock_data_with_indicators['RSI'],
                name='RSI',
                line=dict(color='#2962FF', width=2)
            )
        )
        
        # Add overbought/oversold lines
        fig_indicator.add_shape(
            type="line",
            x0=stock_data_with_indicators.index[0],
            y0=70,
            x1=stock_data_with_indicators.index[-1],
            y1=70,
            line=dict(color="red", width=1, dash="dash")
        )
        
        fig_indicator.add_shape(
            type="line",
            x0=stock_data_with_indicators.index[0],
            y0=30,
            x1=stock_data_with_indicators.index[-1],
            y1=30,
            line=dict(color="green", width=1, dash="dash")
        )
        
        fig_indicator.update_layout(
            title='Relative Strength Index (RSI)',
            yaxis_title='RSI Value',
            yaxis=dict(range=[0, 100]),
            height=400
        )
    else:
        st.info("RSI data not available.")

elif selected_indicator == "MACD":
    if 'MACD' in stock_data_with_indicators.columns and 'MACD_Signal' in stock_data_with_indicators.columns:
        # Add MACD line
        fig_indicator.add_trace(
            go.Scatter(
                x=stock_data_with_indicators.index,
                y=stock_data_with_indicators['MACD'],
                name='MACD',
                line=dict(color='#2962FF', width=2)
            )
        )
        
        # Add signal line
        fig_indicator.add_trace(
            go.Scatter(
                x=stock_data_with_indicators.index,
                y=stock_data_with_indicators['MACD_Signal'],
                name='Signal Line',
                line=dict(color='#FF6B6B', width=2)
            )
        )
        
        # Add MACD histogram
        fig_indicator.add_trace(
            go.Bar(
                x=stock_data_with_indicators.index,
                y=stock_data_with_indicators['MACD'] - stock_data_with_indicators['MACD_Signal'],
                name='MACD Histogram',
                marker_color=np.where(
                    stock_data_with_indicators['MACD'] - stock_data_with_indicators['MACD_Signal'] > 0,
                    '#00C853',
                    '#FF6B6B'
                )
            )
        )
        
        fig_indicator.update_layout(
            title='Moving Average Convergence Divergence (MACD)',
            yaxis_title='MACD Value',
            height=400
        )
    else:
        st.info("MACD data not available.")

elif selected_indicator == "Bollinger Bands":
    if 'BB_Middle' in stock_data_with_indicators.columns and 'BB_Upper' in stock_data_with_indicators.columns and 'BB_Lower' in stock_data_with_indicators.columns:
        # Add price line
        fig_indicator.add_trace(
            go.Scatter(
                x=stock_data_with_indicators.index,
                y=stock_data['close'],
                name='Close Price',
                line=dict(color='#5D6D7E', width=2)
            )
        )
        
        # Add middle band
        fig_indicator.add_trace(
            go.Scatter(
                x=stock_data_with_indicators.index,
                y=stock_data_with_indicators['BB_Middle'],
                name='Middle Band (SMA 20)',
                line=dict(color='#2962FF', width=1.5)
            )
        )
        
        # Add upper band
        fig_indicator.add_trace(
            go.Scatter(
                x=stock_data_with_indicators.index,
                y=stock_data_with_indicators['BB_Upper'],
                name='Upper Band (+2σ)',
                line=dict(color='#00C853', width=1, dash='dash')
            )
        )
        
        # Add lower band
        fig_indicator.add_trace(
            go.Scatter(
                x=stock_data_with_indicators.index,
                y=stock_data_with_indicators['BB_Lower'],
                name='Lower Band (-2σ)',
                line=dict(color='#FF6B6B', width=1, dash='dash')
            )
        )
        
        fig_indicator.update_layout(
            title='Bollinger Bands',
            yaxis_title='Price',
            height=400
        )
    else:
        st.info("Bollinger Bands data not available.")

# Display indicator plot
st.plotly_chart(fig_indicator, use_container_width=True)
