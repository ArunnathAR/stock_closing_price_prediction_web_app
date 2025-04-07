import streamlit as st
import os
import sys
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# Add the current directory to the path to import the modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modules
from stock_data import get_stock_data, get_current_price, calculate_technical_indicators, NIFTY50_STOCKS
from prediction import StockPredictor
from trading import calculate_tax, calculate_profit_potential, get_broker_recommendations, execute_trade
from auth import initialize_authentication, is_authenticated, login, logout, signup
from utils import format_currency, format_percentage, color_coded_text, create_recommendation_box, loading_spinner
from database import initialize_database

# Initialize database
initialize_database()

# Initialize authentication
initialize_authentication()

def main():
    # Set page configuration
    st.set_page_config(
        page_title="StockSage | AI Stock Analysis",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
        .main-header {font-family: 'Poppins', sans-serif; font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem;}
        .section-header {font-family: 'Poppins', sans-serif; font-size: 1.5rem; font-weight: 600; margin: 1rem 0;}
        .metric-value {font-family: 'Roboto Mono', monospace; font-weight: 500;}
        .positive {color: #00C853;}
        .negative {color: #FF6B6B;}
        .neutral {color: #2962FF;}
        .data-container {background-color: #f8f9fa; border-radius: 8px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);}
        .footer {text-align: center; margin-top: 3rem; color: #666;}
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar for navigation
    with st.sidebar:
        st.markdown("<h2 class='neutral'>StockSage</h2>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Authentication
        if not is_authenticated():
            auth_option = st.radio("", ["Login", "Register"])
            
            if auth_option == "Login":
                login()
            else:
                signup()
        else:
            st.success("You are logged in!")
            
            st.markdown("### Quick Links")
            option = st.radio("Navigate to:", [
                "Stock Analysis", "Trading Simulation", "Portfolio & Dashboard", 
            ])
            
            if st.button("Logout"):
                logout()
                st.rerun()
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        StockSage is an AI-powered stock analysis platform for Nifty 50 stocks.
        
        Features:
        - Price prediction using ensemble models
        - Technical indicators visualization
        - Trading simulation with tax calculations
        - Portfolio tracking
        """)
    
    # Main content
    if is_authenticated():
        if 'Stock Analysis' in st.session_state.get("page", ""):
            show_stock_analysis()
        elif 'Trading Simulation' in st.session_state.get("page", ""):
            show_trading_simulation()
        elif 'Portfolio & Dashboard' in st.session_state.get("page", ""):
            show_dashboard()
        else:
            st.session_state["page"] = option
            if option == "Stock Analysis":
                show_stock_analysis()
            elif option == "Trading Simulation":
                show_trading_simulation()
            elif option == "Portfolio & Dashboard":
                show_dashboard()
    else:
        # Show welcome page for non-logged in users
        st.markdown("<h1 class='main-header'>Welcome to StockSage</h1>", unsafe_allow_html=True)
        
        st.markdown("""
        StockSage is an AI-powered stock market analysis platform focused on Nifty 50 stocks.
        
        ### Key Features
        
        - **Advanced Price Predictions**: Using ensemble of models (ARIMA, LSTM, Prophet)
        - **Technical Analysis**: Visual indicators like SMA, EMA, RSI, MACD
        - **Trading Simulation**: Includes Indian tax calculations
        - **Portfolio Tracking**: Keep track of your investments
        
        Please login or register to use the platform.
        """)
        
        # Display sample visualization
        st.markdown("<h2 class='section-header'>Sample Stock Analysis</h2>", unsafe_allow_html=True)
        
        # Create a sample chart
        dates = pd.date_range(start='2023-01-01', periods=30)
        prices = [100 + (i * 0.5) + (np.random.random() * 10 - 5) for i in range(30)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=prices, mode='lines', name='Sample Stock', line=dict(color='#2962FF')))
        fig.update_layout(
            title='Sample Stock Price Trend',
            xaxis_title='Date',
            yaxis_title='Price (₹)',
            template='plotly_white',
            height=400,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.markdown("""
    <div class='footer'>
        StockSage - AI Stock Market Analysis Platform | © 2025
    </div>
    """, unsafe_allow_html=True)

def show_stock_analysis():
    st.markdown("<h1 class='main-header'>Stock Analysis</h1>", unsafe_allow_html=True)
    
    # Form for stock selection
    with st.form("stock_analysis_form"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Create a clean list of stock options
            stock_options = [f"{stock.split('.')[0]} ({stock})" for stock in NIFTY50_STOCKS]
            selected_stock_option = st.selectbox("Select Stock", stock_options)
            selected_stock = selected_stock_option.split("(")[1].split(")")[0]
        
        with col2:
            time_period = st.selectbox("Time Period", ["1month", "3month", "5month"])
        
        submitted = st.form_submit_button("Analyze Stock")
    
    if submitted:
        with loading_spinner(f"Analyzing {selected_stock}..."):
            # Get stock data
            stock_data = get_stock_data(selected_stock, time_period)
            
            if stock_data is None or stock_data.empty:
                st.error(f"Failed to fetch data for {selected_stock}. Please try a different stock or check API key.")
                return
            
            # Get current price
            current_price = get_current_price(selected_stock)
            
            if current_price is None:
                st.error(f"Failed to fetch current price for {selected_stock}.")
                return
            
            # Calculate technical indicators
            stock_data_with_indicators = calculate_technical_indicators(stock_data)
            
            # Prepare data for ML prediction
            predictor = StockPredictor(stock_data, forecast_days=30)
            ensemble_predictions = predictor.ensemble_prediction()
            
            if ensemble_predictions is None:
                st.error("Failed to generate predictions. Please try a different stock or time period.")
                return
            
            recommendation, explanation = predictor.generate_recommendation(ensemble_predictions, current_price)
            
            # Display results
            display_stock_analysis_results(
                selected_stock,
                current_price,
                stock_data_with_indicators,
                ensemble_predictions,
                recommendation,
                explanation
            )

def display_stock_analysis_results(symbol, current_price, stock_data, predictions, recommendation, explanation):
    col1, col2 = st.columns([7, 3])
    
    with col1:
        # Create main graph with historical and predicted prices
        st.markdown("<h2 class='section-header'>Price Prediction</h2>", unsafe_allow_html=True)
        
        fig = go.Figure()
        
        # Historical prices
        fig.add_trace(go.Scatter(
            x=stock_data.index,
            y=stock_data['close'],
            mode='lines',
            name='Historical',
            line=dict(color='#2962FF')
        ))
        
        # Add predictions for each model
        colors = ['#FF6B6B', '#00C853', '#FFC107']
        for i, model in enumerate(predictions.columns):
            fig.add_trace(go.Scatter(
                x=predictions.index,
                y=predictions[model],
                mode='lines',
                name=model,
                line=dict(color=colors[i % len(colors)], dash='dash')
            ))
        
        # Customize the layout
        fig.update_layout(
            title=f'{symbol.split(".")[0]} Price Prediction',
            xaxis_title='Date',
            yaxis_title='Price (₹)',
            legend=dict(x=0, y=1, orientation='h'),
            template='plotly_white',
            height=500,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add technical indicators
        st.markdown("<h2 class='section-header'>Technical Indicators</h2>", unsafe_allow_html=True)
        
        # Create tabs for different indicators
        tabs = st.tabs(["Moving Averages", "RSI & MACD", "Bollinger Bands"])
        
        with tabs[0]:
            # Moving Averages
            fig = go.Figure()
            
            # Price
            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['close'],
                mode='lines',
                name='Price',
                line=dict(color='#2962FF')
            ))
            
            # SMA 20
            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['SMA_20'],
                mode='lines',
                name='SMA 20',
                line=dict(color='#FF6B6B')
            ))
            
            # SMA 50
            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['SMA_50'],
                mode='lines',
                name='SMA 50',
                line=dict(color='#00C853')
            ))
            
            # EMA 20
            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['EMA_20'],
                mode='lines',
                name='EMA 20',
                line=dict(color='#FFC107', dash='dash')
            ))
            
            fig.update_layout(
                title='Moving Averages',
                xaxis_title='Date',
                yaxis_title='Price (₹)',
                legend=dict(x=0, y=1, orientation='h'),
                template='plotly_white',
                height=400,
                margin=dict(l=0, r=0, t=40, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tabs[1]:
            # RSI & MACD
            fig = go.Figure()
            
            # RSI
            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['RSI'],
                mode='lines',
                name='RSI',
                line=dict(color='#2962FF')
            ))
            
            # Add overbought/oversold lines
            fig.add_shape(
                type="line",
                x0=stock_data.index[0],
                y0=70,
                x1=stock_data.index[-1],
                y1=70,
                line=dict(color="#FF6B6B", width=2, dash="dash"),
            )
            
            fig.add_shape(
                type="line",
                x0=stock_data.index[0],
                y0=30,
                x1=stock_data.index[-1],
                y1=30,
                line=dict(color="#00C853", width=2, dash="dash"),
            )
            
            fig.update_layout(
                title='Relative Strength Index (RSI)',
                xaxis_title='Date',
                yaxis_title='RSI',
                legend=dict(x=0, y=1, orientation='h'),
                template='plotly_white',
                height=250,
                margin=dict(l=0, r=0, t=40, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # MACD
            fig = go.Figure()
            
            # MACD Line
            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['MACD'],
                mode='lines',
                name='MACD',
                line=dict(color='#2962FF')
            ))
            
            # Signal Line
            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['MACD_Signal'],
                mode='lines',
                name='Signal',
                line=dict(color='#FF6B6B')
            ))
            
            # Add MACD Histogram
            fig.add_trace(go.Bar(
                x=stock_data.index,
                y=stock_data['MACD'] - stock_data['MACD_Signal'],
                name='Histogram',
                marker_color=np.where(
                    stock_data['MACD'] - stock_data['MACD_Signal'] >= 0, 
                    '#00C853', '#FF6B6B'
                )
            ))
            
            fig.update_layout(
                title='Moving Average Convergence Divergence (MACD)',
                xaxis_title='Date',
                yaxis_title='MACD',
                legend=dict(x=0, y=1, orientation='h'),
                template='plotly_white',
                height=250,
                margin=dict(l=0, r=0, t=40, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tabs[2]:
            # Bollinger Bands
            fig = go.Figure()
            
            # Price
            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['close'],
                mode='lines',
                name='Price',
                line=dict(color='#2962FF')
            ))
            
            # Middle Band (SMA 20)
            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['BB_Middle'],
                mode='lines',
                name='Middle Band',
                line=dict(color='#FFC107')
            ))
            
            # Upper Band
            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['BB_Upper'],
                mode='lines',
                name='Upper Band',
                line=dict(color='#00C853', dash='dash')
            ))
            
            # Lower Band
            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['BB_Lower'],
                mode='lines',
                name='Lower Band',
                line=dict(color='#FF6B6B', dash='dash')
            ))
            
            # Create filled area between upper and lower bands
            fig.add_trace(go.Scatter(
                x=stock_data.index.tolist() + stock_data.index.tolist()[::-1],
                y=stock_data['BB_Upper'].tolist() + stock_data['BB_Lower'].tolist()[::-1],
                fill='toself',
                fillcolor='rgba(41, 98, 255, 0.1)',
                line=dict(color='rgba(255, 255, 255, 0)'),
                hoverinfo="skip",
                showlegend=False
            ))
            
            fig.update_layout(
                title='Bollinger Bands',
                xaxis_title='Date',
                yaxis_title='Price (₹)',
                legend=dict(x=0, y=1, orientation='h'),
                template='plotly_white',
                height=400,
                margin=dict(l=0, r=0, t=40, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Display current information and prediction summary
        st.markdown("<div class='data-container'>", unsafe_allow_html=True)
        
        st.markdown("<h2 class='section-header'>Current Status</h2>", unsafe_allow_html=True)
        
        # Display current price
        st.metric(
            "Current Price", 
            format_currency(current_price),
            delta=format_percentage(((current_price / stock_data['close'].iloc[1]) - 1) * 100)
        )
        
        # Display latest prices
        latest_data = stock_data.iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Open:** {format_currency(latest_data['open'])}")
            st.markdown(f"**High:** {format_currency(latest_data['high'])}")
        with col2:
            st.markdown(f"**Low:** {format_currency(latest_data['low'])}")
            st.markdown(f"**Volume:** {int(latest_data['volume']):,}")
        
        st.markdown("<h2 class='section-header'>Prediction Summary</h2>", unsafe_allow_html=True)
        
        # Calculate prediction metrics
        last_historical_price = stock_data['close'].iloc[0]
        prediction_end = predictions.iloc[-1]
        
        predicted_price = prediction_end['Ensemble']
        predicted_change = ((predicted_price / current_price) - 1) * 100
        
        # Display prediction metrics
        st.metric(
            "Predicted Price (30 days)", 
            format_currency(predicted_price),
            delta=format_percentage(predicted_change)
        )
        
        # Prediction breakdown for each model
        st.markdown("##### Model Predictions")
        for model in predictions.columns:
            if model != 'Ensemble':
                model_prediction = prediction_end[model]
                model_change = ((model_prediction / current_price) - 1) * 100
                st.markdown(
                    f"**{model}:** {format_currency(model_prediction)} "
                    f"({color_coded_text(model_change, format_percentage(model_change))})"
                , unsafe_allow_html=True)
        
        # Add recommendation
        st.markdown("<h2 class='section-header'>Recommendation</h2>", unsafe_allow_html=True)
        create_recommendation_box(recommendation, explanation)
        
        # Add action buttons
        st.markdown("<h2 class='section-header'>Actions</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Add to Watchlist"):
                # Code to add to watchlist
                st.success("Added to watchlist!")
        
        with col2:
            if st.button("Trading Simulator"):
                st.session_state["page"] = "Trading Simulation"
                st.session_state["selected_stock"] = symbol
                st.session_state["current_price"] = current_price
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

def show_trading_simulation():
    st.markdown("<h1 class='main-header'>Trading Simulation</h1>", unsafe_allow_html=True)
    
    # Get selected stock from session state or allow user to select a new one
    selected_stock = st.session_state.get("selected_stock", None)
    current_price = st.session_state.get("current_price", None)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Stock selection form
        with st.form("trading_form"):
            if selected_stock is None:
                # Create a clean list of stock options
                stock_options = [f"{stock.split('.')[0]} ({stock})" for stock in NIFTY50_STOCKS]
                selected_stock_option = st.selectbox("Select Stock", stock_options)
                selected_stock = selected_stock_option.split("(")[1].split(")")[0]
            else:
                st.markdown(f"### Trading {selected_stock.split('.')[0]}")
            
            # Transaction details
            transaction_type = st.radio("Transaction Type", ["Buy", "Sell"])
            
            # Fetch current price if not available
            if current_price is None:
                with loading_spinner("Fetching current price..."):
                    current_price = get_current_price(selected_stock)
            
            if current_price is not None:
                st.markdown(f"Current Price: **{format_currency(current_price)}**")
                
                # Allow slight price adjustment for simulation
                price = st.slider(
                    "Price (₹)",
                    min_value=float(current_price * 0.95),
                    max_value=float(current_price * 1.05),
                    value=float(current_price),
                    step=0.05
                )
                
                quantity = st.number_input("Quantity", min_value=1, max_value=10000, value=10, step=1)
                is_short_term = st.checkbox("Short-term transaction (< 1 year)", value=True)
                
                total_value = price * quantity
                st.markdown(f"Transaction Value: **{format_currency(total_value)}**")
                
                submitted = st.form_submit_button("Calculate")
            else:
                st.error("Failed to fetch current price. Please try a different stock.")
                submitted = st.form_submit_button("Calculate", disabled=True)
    
    with col2:
        # Display trading simulation results if form is submitted
        if submitted and current_price is not None:
            with loading_spinner("Calculating..."):
                # Calculate taxes
                tax_info = calculate_tax(
                    transaction_type.lower(),
                    price,
                    quantity,
                    is_short_term
                )
                
                if tax_info:
                    st.markdown("<div class='data-container'>", unsafe_allow_html=True)
                    st.markdown("<h2 class='section-header'>Transaction Summary</h2>", unsafe_allow_html=True)
                    
                    # Display transaction details
                    st.markdown(f"**Stock:** {selected_stock.split('.')[0]}")
                    st.markdown(f"**Type:** {transaction_type}")
                    st.markdown(f"**Price:** {format_currency(price)}")
                    st.markdown(f"**Quantity:** {quantity}")
                    st.markdown(f"**Value:** {format_currency(total_value)}")
                    
                    # Display tax breakdown
                    st.markdown("<h2 class='section-header'>Tax Breakdown</h2>", unsafe_allow_html=True)
                    
                    for tax_name, tax_value in tax_info["taxes"].items():
                        st.markdown(f"**{tax_name}:** {format_currency(tax_value)}")
                    
                    # Display final amounts
                    st.markdown("<h2 class='section-header'>Final Amount</h2>", unsafe_allow_html=True)
                    
                    total_taxes = tax_info["total_tax"]
                    total_amount = tax_info["total_amount"]
                    
                    st.markdown(f"**Subtotal:** {format_currency(total_value)}")
                    st.markdown(f"**Total Taxes:** {format_currency(total_taxes)}")
                    st.markdown(f"**Total Amount:** {format_currency(total_amount)}")
                    
                    # Add execute button
                    if st.button("Execute Trade"):
                        # Execute the trade
                        success = execute_trade(
                            st.session_state.get("user_id"),
                            selected_stock,
                            transaction_type.lower(),
                            quantity,
                            price
                        )
                        
                        if success:
                            st.success(f"{transaction_type} order executed successfully!")
                        else:
                            st.error("Failed to execute trade. Please try again.")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                else:
                    st.error("Failed to calculate taxes. Please check your inputs.")
        
        # If no transaction is being calculated, show broker recommendations
        if not submitted or current_price is None:
            st.markdown("<div class='data-container'>", unsafe_allow_html=True)
            st.markdown("<h2 class='section-header'>Broker Recommendations</h2>", unsafe_allow_html=True)
            
            brokers = get_broker_recommendations()
            
            for broker in brokers:
                st.markdown(f"### {broker['name']}")
                st.markdown(f"**Fees:** {broker['fees']}")
                st.markdown(f"**Features:** {broker['features']}")
                st.markdown(f"**Link:** [Visit Website]({broker['link']})")
                st.markdown("---")
            
            st.markdown("</div>", unsafe_allow_html=True)

def show_dashboard():
    st.markdown("<h1 class='main-header'>Portfolio & Dashboard</h1>", unsafe_allow_html=True)
    
    # Dashboard is usually very specific to the user, so this is just a skeleton
    # In a real app, this would fetch data from user's portfolio and display it
    
    st.markdown("#### Portfolio and dashboard features are coming soon!")
    
    # Sample data for demonstration
    sample_portfolio = {
        "holdings": [
            {"symbol": "TCS.BSE", "name": "TCS", "quantity": 10, "avg_price": 3500, "current_price": 3800, "pl_percentage": 8.57},
            {"symbol": "RELIANCE.BSE", "name": "Reliance", "quantity": 5, "avg_price": 2400, "current_price": 2350, "pl_percentage": -2.08},
            {"symbol": "INFY.BSE", "name": "Infosys", "quantity": 15, "avg_price": 1800, "current_price": 1900, "pl_percentage": 5.56}
        ],
        "total_value": 92000,
        "total_pl": 4500,
        "pl_percentage": 5.14
    }
    
    # Display portfolio summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Portfolio Value", 
            format_currency(sample_portfolio["total_value"])
        )
    
    with col2:
        st.metric(
            "Total Profit/Loss", 
            format_currency(sample_portfolio["total_pl"]),
            delta=format_percentage(sample_portfolio["pl_percentage"])
        )
    
    with col3:
        st.metric(
            "Number of Holdings", 
            len(sample_portfolio["holdings"])
        )
    
    # Display holdings
    st.markdown("<h2 class='section-header'>Your Holdings</h2>", unsafe_allow_html=True)
    
    for holding in sample_portfolio["holdings"]:
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
        
        with col1:
            st.markdown(f"**{holding['name']}**")
        
        with col2:
            st.markdown(f"{holding['quantity']} shares")
        
        with col3:
            st.markdown(f"Avg: {format_currency(holding['avg_price'])}")
        
        with col4:
            st.markdown(f"Current: {format_currency(holding['current_price'])}")
        
        with col5:
            pl_display = color_coded_text(
                holding['pl_percentage'],
                format_percentage(holding['pl_percentage'])
            )
            st.markdown(pl_display, unsafe_allow_html=True)
    
    # Sample visualization
    st.markdown("<h2 class='section-header'>Portfolio Allocation</h2>", unsafe_allow_html=True)
    
    # Create a sample pie chart
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=[holding['name'] for holding in sample_portfolio["holdings"]],
        values=[holding['current_price'] * holding['quantity'] for holding in sample_portfolio["holdings"]],
        textinfo='label+percent',
        marker=dict(colors=['#2962FF', '#00C853', '#FFC107'])
    ))
    fig.update_layout(
        title='Portfolio Allocation by Value',
        template='plotly_white',
        height=400,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

# Run the app
if __name__ == "__main__":
    main()