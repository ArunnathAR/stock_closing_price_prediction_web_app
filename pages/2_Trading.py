import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from stock_data import get_stock_data, NIFTY50_STOCKS, get_current_price
from trading import calculate_tax, calculate_profit_potential, get_broker_recommendations, execute_trade
from utils import format_currency, format_percentage, color_coded_text, display_error_message, display_success_message
from auth import is_authenticated

# Set page config
st.set_page_config(
    page_title="Trading Interface | Stock Market Platform",
    page_icon="💹",
    layout="wide"
)

# Check authentication
if not is_authenticated():
    st.warning("Please log in to access this page.")
    st.stop()

# Page title
st.markdown('<h1 class="title-text">Trading Interface</h1>', unsafe_allow_html=True)
st.markdown('<p class="body-text">Simulate trades and calculate taxes</p>', unsafe_allow_html=True)

# Stock selection
col1, col2 = st.columns([2, 1])

with col1:
    # Clean up stock symbols for display
    display_stocks = [stock.split('.')[0] for stock in NIFTY50_STOCKS]
    selected_stock_display = st.selectbox("Select a stock", display_stocks)
    # Get the full symbol for API call
    selected_stock = NIFTY50_STOCKS[display_stocks.index(selected_stock_display)]

with col2:
    transaction_type = st.selectbox(
        "Transaction Type",
        options=["Buy", "Sell"],
        index=0
    )

# Fetch current price
with st.spinner("Fetching current price..."):
    current_price = get_current_price(selected_stock)
    
    if current_price is None:
        display_error_message("Unable to fetch current price. Please try again later.")
        st.stop()

# Display current price
st.markdown(f'<h2 class="title-text">{selected_stock_display} - Current Price: {format_currency(current_price)}</h2>', unsafe_allow_html=True)

# Transaction details
st.markdown('<h3 class="title-text">Transaction Details</h3>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Quantity input
    quantity = st.number_input(
        "Quantity (Number of Shares)",
        min_value=1,
        value=10,
        step=1
    )
    
    # Custom price toggle
    use_custom_price = st.checkbox("Use custom price", value=False)
    
    if use_custom_price:
        custom_price = st.number_input(
            "Custom Price per Share",
            min_value=0.01,
            value=float(current_price),
            step=0.01,
            format="%.2f"
        )
        price = custom_price
    else:
        price = current_price

with col2:
    # For sell transactions, ask about holding period
    if transaction_type.lower() == "sell":
        short_term = st.radio(
            "Holding Period",
            options=["Short-term (Less than 1 year)", "Long-term (More than 1 year)"],
            index=0
        )
        is_short_term = short_term.startswith("Short-term")
    else:
        is_short_term = True  # Default for buy transactions

    # Calculate transaction details
    total_value = price * quantity
    
    st.markdown(f'<p class="body-text"><strong>Total Value:</strong> {format_currency(total_value)}</p>', unsafe_allow_html=True)

# Calculate taxes
tax_info = calculate_tax(transaction_type, price, quantity, is_short_term)

if tax_info:
    st.markdown('<h3 class="title-text">Tax Calculation</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h4 class="title-text">Tax Breakdown</h4>', unsafe_allow_html=True)
        
        tax_df = pd.DataFrame()
        
        if transaction_type.lower() == "buy":
            tax_df['Component'] = ['Transaction Value', 'Securities Transaction Tax (STT)', 
                                'Transaction Charges', 'GST on Transaction Charges', 
                                'Stamp Duty', 'Total Tax', 'Total Cost']
            tax_df['Amount'] = [
                tax_info['transaction_value'],
                tax_info['stt'],
                tax_info['transaction_charges'],
                tax_info['gst'],
                tax_info['stamp_duty'],
                tax_info['total_tax'],
                tax_info['total_cost']
            ]
        else:  # Sell
            tax_df['Component'] = ['Transaction Value', 'Securities Transaction Tax (STT)', 
                                'Transaction Charges', 'GST on Transaction Charges', 
                                'Income Tax', 'Total Tax', 'Net Proceeds']
            tax_df['Amount'] = [
                tax_info['transaction_value'],
                tax_info['stt'],
                tax_info['transaction_charges'],
                tax_info['gst'],
                tax_info['income_tax'],
                tax_info['total_tax'],
                tax_info['net_proceed']
            ]
        
        # Format currency values
        tax_df['Formatted'] = tax_df['Amount'].apply(lambda x: format_currency(x))
        
        # Calculate percentage of transaction value
        tax_df['Percentage'] = tax_df['Amount'] / tax_df['Amount'].iloc[0] * 100
        tax_df['Percentage'] = tax_df['Percentage'].apply(lambda x: f"{x:.4f}%" if x < 100 else "100.0000%")
        
        # Display tax breakdown table
        st.table(tax_df[['Component', 'Formatted', 'Percentage']])
    
    with col2:
        st.markdown('<h4 class="title-text">Tax Visualization</h4>', unsafe_allow_html=True)
        
        # Create pie chart for tax components
        if transaction_type.lower() == "buy":
            labels = ['Securities Transaction Tax', 'Transaction Charges', 'GST', 'Stamp Duty']
            values = [tax_info['stt'], tax_info['transaction_charges'], tax_info['gst'], tax_info['stamp_duty']]
        else:  # Sell
            labels = ['Securities Transaction Tax', 'Transaction Charges', 'GST', 'Income Tax']
            values = [tax_info['stt'], tax_info['transaction_charges'], tax_info['gst'], tax_info['income_tax']]
        
        # Create figure
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.4,
            marker_colors=['#2962FF', '#00C853', '#FF6B6B', '#FFA726']
        )])
        
        fig.update_layout(
            title_text=f"Tax Component Breakdown",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary
        if transaction_type.lower() == "buy":
            effective_tax_rate = tax_info['total_tax'] / tax_info['transaction_value'] * 100
            st.markdown(f'<p class="body-text"><strong>Effective Tax Rate:</strong> {format_percentage(effective_tax_rate)}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="body-text"><strong>Transaction Value:</strong> {format_currency(tax_info["transaction_value"])}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="body-text"><strong>Total Tax:</strong> {format_currency(tax_info["total_tax"])}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="body-text"><strong>Total Cost:</strong> {format_currency(tax_info["total_cost"])}</p>', unsafe_allow_html=True)
        else:  # Sell
            effective_tax_rate = tax_info['total_tax'] / tax_info['transaction_value'] * 100
            st.markdown(f'<p class="body-text"><strong>Effective Tax Rate:</strong> {format_percentage(effective_tax_rate)}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="body-text"><strong>Transaction Value:</strong> {format_currency(tax_info["transaction_value"])}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="body-text"><strong>Total Tax:</strong> {format_currency(tax_info["total_tax"])}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="body-text"><strong>Net Proceeds:</strong> {format_currency(tax_info["net_proceed"])}</p>', unsafe_allow_html=True)

# Generate profit potential for buy transactions
if transaction_type.lower() == "buy":
    st.markdown('<h3 class="title-text">Profit Potential</h3>', unsafe_allow_html=True)
    
    # Fetch historical data for prediction range
    with st.spinner("Calculating profit potential..."):
        # Simple prediction based on average growth rates
        # This is a placeholder for demonstration - in real scenario, use actual predictions
        prediction_periods = {
            "1 Week": 7,
            "1 Month": 30,
            "3 Months": 90,
            "6 Months": 180,
            "1 Year": 365
        }
        
        # Expected growth rates (in percent) for demonstration
        # These would normally come from the prediction models
        expected_growth = {
            "1 Week": np.random.uniform(-3, 3),
            "1 Month": np.random.uniform(-8, 8),
            "3 Months": np.random.uniform(-15, 15),
            "6 Months": np.random.uniform(-25, 25),
            "1 Year": np.random.uniform(-40, 40)
        }
        
        # Calculate predicted prices
        predicted_prices = {}
        for period, growth in expected_growth.items():
            predicted_prices[period] = price * (1 + growth / 100)
        
        # Calculate profit potential for different time frames
        profit_potentials = {}
        for period, pred_price in predicted_prices.items():
            tax_rate = 0.15 if period in ["1 Week", "1 Month", "3 Months", "6 Months"] else 0.10
            profit_potentials[period] = calculate_profit_potential(price, pred_price, quantity, tax_rate)
        
        # Create profit potential table
        profit_df = pd.DataFrame()
        profit_df['Time Frame'] = list(profit_potentials.keys())
        profit_df['Predicted Price'] = [predicted_prices[period] for period in profit_potentials.keys()]
        profit_df['Price Change %'] = [(predicted_prices[period] - price) / price * 100 for period in profit_potentials.keys()]
        profit_df['Gross Profit'] = [profit_potentials[period]['gross_profit'] for period in profit_potentials.keys()]
        profit_df['Tax'] = [profit_potentials[period]['tax'] for period in profit_potentials.keys()]
        profit_df['Net Profit'] = [profit_potentials[period]['net_profit'] for period in profit_potentials.keys()]
        profit_df['ROI %'] = [profit_potentials[period]['roi_percentage'] for period in profit_potentials.keys()]
        
        # Format columns
        profit_df['Predicted Price'] = profit_df['Predicted Price'].apply(lambda x: format_currency(x))
        profit_df['Price Change %'] = profit_df['Price Change %'].apply(lambda x: format_percentage(x))
        
        # Color code gross profit
        profit_df['Gross Profit Color'] = profit_df['Gross Profit'].apply(
            lambda x: color_coded_text(x, format_currency(x))
        )
        
        # Color code net profit
        profit_df['Net Profit Color'] = profit_df['Net Profit'].apply(
            lambda x: color_coded_text(x, format_currency(x))
        )
        
        # Color code ROI
        profit_df['ROI Color'] = profit_df['ROI %'].apply(
            lambda x: color_coded_text(x, format_percentage(x))
        )
        
        # Display table with colored cells
        st.markdown("""
        <style>
        table td:nth-child(3), table td:nth-child(6), table td:nth-child(8) {
            text-align: right;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.write("Potential profit scenarios based on market predictions:")
        
        # Convert to regular DataFrame for display
        display_df = profit_df[['Time Frame', 'Predicted Price', 'Price Change %', 'Gross Profit Color', 'Tax', 'Net Profit Color', 'ROI Color']].copy()
        display_df.columns = ['Time Frame', 'Predicted Price', 'Price Change %', 'Gross Profit', 'Tax (₹)', 'Net Profit', 'ROI %']
        
        # Display as HTML to show colored text
        st.markdown(pd.DataFrame.to_html(display_df, escape=False, index=False), unsafe_allow_html=True)
        
        # Display profit potential chart
        st.markdown('<h4 class="title-text">Profit Potential Chart</h4>', unsafe_allow_html=True)
        
        # Create chart data
        chart_periods = list(profit_potentials.keys())
        chart_net_profits = [profit_potentials[period]['net_profit'] for period in chart_periods]
        chart_taxes = [profit_potentials[period]['tax'] for period in chart_periods]
        
        # Create figure
        fig = go.Figure()
        
        # Add net profit bars
        fig.add_trace(go.Bar(
            x=chart_periods,
            y=chart_net_profits,
            name='Net Profit',
            marker_color=np.where(np.array(chart_net_profits) >= 0, '#00C853', '#FF6B6B')
        ))
        
        # Add tax bars
        fig.add_trace(go.Bar(
            x=chart_periods,
            y=chart_taxes,
            name='Tax',
            marker_color='#5D6D7E'
        ))
        
        # Update layout
        fig.update_layout(
            title='Profit Potential Over Time',
            xaxis_title='Time Frame',
            yaxis_title='Amount (₹)',
            barmode='stack',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Broker recommendations
st.markdown('<h3 class="title-text">Broker Recommendations</h3>', unsafe_allow_html=True)

brokers = get_broker_recommendations()

if brokers:
    # Convert to DataFrame
    broker_df = pd.DataFrame(brokers)
    
    # Add direct link buttons
    broker_df['Visit'] = broker_df['link'].apply(
        lambda x: f'<a href="{x}" target="_blank" style="text-decoration: none;"><button style="background-color: #2962FF; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer;">Visit</button></a>'
    )
    
    # Display as HTML to enable buttons
    st.markdown(pd.DataFrame.to_html(
        broker_df[['name', 'brokerage', 'min_account', 'features', 'Visit']],
        escape=False,
        index=False
    ), unsafe_allow_html=True)

# Execute transaction
st.markdown('<h3 class="title-text">Execute Transaction</h3>', unsafe_allow_html=True)

with st.form("transaction_form"):
    st.write(f"Confirm {transaction_type} of {quantity} shares of {selected_stock_display} at {format_currency(price)} per share.")
    
    if transaction_type.lower() == "buy":
        st.write(f"Total cost: {format_currency(tax_info['total_cost'])}")
    else:
        st.write(f"Net proceeds: {format_currency(tax_info['net_proceed'])}")
    
    confirm = st.checkbox("I confirm this transaction")
    
    submitted = st.form_submit_button("Execute Transaction")
    
    if submitted:
        if confirm:
            # Execute the trade
            success = execute_trade(
                st.session_state.user_id,
                selected_stock,
                transaction_type.lower(),
                quantity,
                price
            )
            
            if success:
                display_success_message(f"Transaction executed successfully! {transaction_type} order for {quantity} shares of {selected_stock_display} at {format_currency(price)} per share.")
            else:
                display_error_message("Transaction failed. Please try again.")
        else:
            st.warning("Please confirm the transaction before executing.")

# Disclaimer
st.markdown("""
<div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px;">
    <h4 style="margin-top: 0;">Disclaimer</h4>
    <p>This is a simulated trading platform for educational purposes only. No real transactions are executed. 
    Tax calculations are approximations based on current Indian tax laws and may not reflect all applicable charges or exemptions. 
    Profit projections are hypothetical and not guaranteed. Please consult with a financial advisor before making actual investment decisions.</p>
</div>
""", unsafe_allow_html=True)
