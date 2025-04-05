import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import torch
import torch.nn as nn
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
from sklearn.preprocessing import MinMaxScaler

class StockPredictor:
    def __init__(self, stock_data, forecast_days=30):
        """
        Initialize the stock predictor
        
        Parameters:
        - stock_data: Pandas DataFrame with stock price data
        - forecast_days: Number of days to forecast
        """
        self.stock_data = stock_data
        self.forecast_days = forecast_days
        self.models = {
            'ARIMA': self.predict_with_arima,
            'LSTM': self.predict_with_lstm,
            'Prophet': self.predict_with_prophet
        }
        
    def prepare_data(self):
        """Prepare data for prediction models"""
        if self.stock_data is None or self.stock_data.empty:
            st.error("No stock data available for prediction.")
            return None
        
        # Sort by date (oldest first) for time series models
        df = self.stock_data.copy().sort_index()
        
        return df
    
    def predict_with_arima(self):
        """Use ARIMA model for prediction"""
        with st.spinner("Running ARIMA prediction model..."):
            try:
                df = self.prepare_data()
                if df is None:
                    return None
                
                # Extract closing prices
                closing_prices = df['close'].values
                
                # Fit ARIMA model - using auto_arima parameters (1,1,1) as a simple default
                model = ARIMA(closing_prices, order=(1, 1, 1))
                model_fit = model.fit()
                
                # Forecast
                forecast = model_fit.forecast(steps=self.forecast_days)
                
                # Create forecast dates
                last_date = df.index[-1]
                forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=self.forecast_days)
                
                # Create forecast DataFrame
                forecast_df = pd.DataFrame({
                    'date': forecast_dates,
                    'predicted_price': forecast
                })
                forecast_df.set_index('date', inplace=True)
                
                return forecast_df
            
            except Exception as e:
                st.error(f"Error in ARIMA prediction: {e}")
                return None
    
    def predict_with_lstm(self):
        """Use LSTM model for prediction"""
        with st.spinner("Running LSTM prediction model..."):
            try:
                df = self.prepare_data()
                if df is None:
                    return None
                
                # Extract closing prices
                data = df['close'].values.reshape(-1, 1)
                
                # Scale the data
                scaler = MinMaxScaler(feature_range=(0, 1))
                scaled_data = scaler.fit_transform(data)
                
                # Create training data
                x_train = []
                y_train = []
                
                # Look back period (number of previous days to consider)
                look_back = 60
                
                for i in range(look_back, len(scaled_data)):
                    x_train.append(scaled_data[i - look_back:i, 0])
                    y_train.append(scaled_data[i, 0])
                
                # Convert to numpy arrays
                x_train, y_train = np.array(x_train), np.array(y_train)
                
                # Reshape for LSTM input [samples, time steps, features]
                x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
                
                # Define PyTorch LSTM model
                class LSTMModel(nn.Module):
                    def __init__(self, input_dim=1, hidden_dim=50, num_layers=2, output_dim=1):
                        super(LSTMModel, self).__init__()
                        self.hidden_dim = hidden_dim
                        self.num_layers = num_layers
                        
                        # LSTM layers
                        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
                        
                        # Fully connected layers
                        self.fc1 = nn.Linear(hidden_dim, 25)
                        self.fc2 = nn.Linear(25, output_dim)
                        self.relu = nn.ReLU()
                    
                    def forward(self, x):
                        # Initialize hidden state with zeros
                        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(x.device)
                        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(x.device)
                        
                        # Forward propagate LSTM
                        out, _ = self.lstm(x, (h0, c0))
                        
                        # Get the last time step output
                        out = out[:, -1, :]
                        
                        # Fully connected layers
                        out = self.relu(self.fc1(out))
                        out = self.fc2(out)
                        return out
                
                # Convert data to PyTorch tensors
                x_train_tensor = torch.FloatTensor(x_train)
                y_train_tensor = torch.FloatTensor(y_train)
                
                # Initialize model, loss function and optimizer
                model = LSTMModel()
                criterion = nn.MSELoss()
                optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
                
                # Training loop
                epochs = 25
                batch_size = 32
                n_batches = len(x_train_tensor) // batch_size
                early_stop_counter = 0
                best_loss = float('inf')
                
                model.train()
                for epoch in range(epochs):
                    epoch_loss = 0
                    
                    for i in range(n_batches):
                        start_idx = i * batch_size
                        end_idx = min(start_idx + batch_size, len(x_train_tensor))
                        batch_X = x_train_tensor[start_idx:end_idx]
                        batch_y = y_train_tensor[start_idx:end_idx]
                        
                        # Forward pass
                        outputs = model(batch_X)
                        loss = criterion(outputs.squeeze(), batch_y)
                        
                        # Backward and optimize
                        optimizer.zero_grad()
                        loss.backward()
                        optimizer.step()
                        
                        epoch_loss += loss.item()
                    
                    avg_loss = epoch_loss / n_batches
                    
                    # Early stopping
                    if avg_loss < best_loss:
                        best_loss = avg_loss
                        early_stop_counter = 0
                    else:
                        early_stop_counter += 1
                    
                    if early_stop_counter >= 5:  # Patience of 5 epochs
                        break
                
                # Set model to evaluation mode
                model.eval()
                
                # Prepare input for prediction
                inputs = scaled_data[-look_back:].copy()
                inputs_tensor = torch.FloatTensor(inputs).unsqueeze(0)  # Add batch dimension
                
                # Make predictions for forecast_days
                predicted_prices = []
                
                with torch.no_grad():  # No need to track gradients for inference
                    for _ in range(self.forecast_days):
                        # Forward pass
                        output = model(inputs_tensor)
                        next_pred = output.detach().numpy()
                        predicted_prices.append(next_pred[0][0])
                        
                        # Update inputs for next prediction
                        inputs = np.append(inputs[1:], [[next_pred[0][0]]], axis=0)
                        inputs_tensor = torch.FloatTensor(inputs).unsqueeze(0)
                
                # Inverse scaling to get actual prices
                predicted_prices = np.array(predicted_prices).reshape(-1, 1)
                predicted_prices = scaler.inverse_transform(predicted_prices)
                
                # Create forecast dates
                last_date = df.index[-1]
                forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=self.forecast_days)
                
                # Create forecast DataFrame
                forecast_df = pd.DataFrame({
                    'date': forecast_dates,
                    'predicted_price': predicted_prices.flatten()
                })
                forecast_df.set_index('date', inplace=True)
                
                return forecast_df
            
            except Exception as e:
                st.error(f"Error in LSTM prediction: {e}")
                return None
    
    def predict_with_prophet(self):
        """Use Facebook Prophet model for prediction"""
        with st.spinner("Running Prophet prediction model..."):
            try:
                df = self.prepare_data()
                if df is None:
                    return None
                
                # Prepare data for Prophet
                prophet_df = df.reset_index()
                prophet_df = prophet_df[['index', 'close']]
                prophet_df.columns = ['ds', 'y']
                
                # Initialize and fit Prophet model
                model = Prophet(daily_seasonality=True)
                model.fit(prophet_df)
                
                # Create future dataframe for prediction
                future = model.make_future_dataframe(periods=self.forecast_days)
                
                # Make prediction
                forecast = model.predict(future)
                
                # Extract prediction for forecast period
                forecast_df = forecast[['ds', 'yhat']].tail(self.forecast_days)
                forecast_df.columns = ['date', 'predicted_price']
                forecast_df.set_index('date', inplace=True)
                
                return forecast_df
            
            except Exception as e:
                st.error(f"Error in Prophet prediction: {e}")
                return None
    
    def ensemble_prediction(self):
        """Combine predictions from all models"""
        with st.spinner("Generating ensemble prediction..."):
            try:
                # Get predictions from each model
                predictions = {}
                
                for model_name, predict_func in self.models.items():
                    predictions[model_name] = predict_func()
                
                # Check if any predictions were successful
                valid_predictions = {k: v for k, v in predictions.items() if v is not None}
                
                if not valid_predictions:
                    st.error("All prediction models failed. Please check the data and try again.")
                    return None
                
                # Ensemble (average) the predictions
                dates = list(valid_predictions.values())[0].index
                ensemble_predictions = pd.DataFrame(index=dates)
                
                # Add individual model predictions
                for model_name, pred_df in valid_predictions.items():
                    ensemble_predictions[model_name] = pred_df['predicted_price']
                
                # Calculate ensemble prediction (mean of all models)
                ensemble_predictions['ensemble'] = ensemble_predictions.mean(axis=1)
                
                return ensemble_predictions
            
            except Exception as e:
                st.error(f"Error in ensemble prediction: {e}")
                return None
    
    def generate_recommendation(self, ensemble_pred, current_price):
        """
        Generate trading recommendation based on prediction
        
        Parameters:
        - ensemble_pred: DataFrame with ensemble predictions
        - current_price: Current stock price
        
        Returns:
        - Recommendation (str): 'buy', 'sell', or 'hold'
        - Explanation (str): Detailed explanation of the recommendation
        """
        try:
            if ensemble_pred is None or current_price is None:
                return "hold", "Insufficient data for recommendation."
            
            # Get the last known price and predictions
            last_price = current_price
            
            # Short-term prediction (7 days)
            short_term_pred = ensemble_pred['ensemble'].iloc[:7].mean()
            
            # Medium-term prediction (14 days)
            medium_term_pred = ensemble_pred['ensemble'].iloc[7:14].mean()
            
            # Long-term prediction (30 days)
            long_term_pred = ensemble_pred['ensemble'].iloc[-1]
            
            # Calculate expected returns
            short_term_return = (short_term_pred - last_price) / last_price * 100
            medium_term_return = (medium_term_pred - last_price) / last_price * 100
            long_term_return = (long_term_pred - last_price) / last_price * 100
            
            # Initialize recommendation variables
            recommendation = "hold"
            confidence = "moderate"
            explanation = ""
            
            # Decision logic
            if short_term_return > 5 and medium_term_return > 3 and long_term_return > 0:
                recommendation = "buy"
                confidence = "high"
                explanation = f"Strong buy signal with expected returns of {short_term_return:.2f}% (7 days), {medium_term_return:.2f}% (14 days), and {long_term_return:.2f}% (30 days). All prediction models show an upward trend."
            
            elif short_term_return > 3 and medium_term_return > 0:
                recommendation = "buy"
                confidence = "moderate"
                explanation = f"Moderate buy signal with expected returns of {short_term_return:.2f}% (7 days) and {medium_term_return:.2f}% (14 days). Short to medium-term outlook is positive."
            
            elif short_term_return < -5 and medium_term_return < -3 and long_term_return < 0:
                recommendation = "sell"
                confidence = "high"
                explanation = f"Strong sell signal with expected losses of {short_term_return:.2f}% (7 days), {medium_term_return:.2f}% (14 days), and {long_term_return:.2f}% (30 days). All prediction models show a downward trend."
            
            elif short_term_return < -3 and medium_term_return < 0:
                recommendation = "sell"
                confidence = "moderate"
                explanation = f"Moderate sell signal with expected losses of {short_term_return:.2f}% (7 days) and {medium_term_return:.2f}% (14 days). Short to medium-term outlook is negative."
            
            else:
                explanation = f"Hold recommendation based on mixed signals. Short-term: {short_term_return:.2f}%, Medium-term: {medium_term_return:.2f}%, Long-term: {long_term_return:.2f}%. Monitor the stock for clearer trends."
            
            # Add model agreement information
            last_day_predictions = ensemble_pred.iloc[-1]
            model_signals = []
            
            for model, pred in last_day_predictions.items():
                if model != 'ensemble':
                    if pred > last_price:
                        model_signals.append(f"{model}: Bullish")
                    else:
                        model_signals.append(f"{model}: Bearish")
            
            model_agreement = ", ".join(model_signals)
            explanation += f"\n\nModel signals: {model_agreement}"
            
            # Add confidence level
            explanation += f"\n\nConfidence: {confidence.capitalize()}"
            
            return recommendation, explanation
        
        except Exception as e:
            st.error(f"Error generating recommendation: {e}")
            return "hold", "Error in recommendation generation. Please check the data."
    
    def plot_prediction(self, ensemble_pred):
        """
        Create a plot of the stock price prediction
        
        Parameters:
        - ensemble_pred: DataFrame with ensemble predictions
        
        Returns:
        - Plotly figure
        """
        try:
            if ensemble_pred is None or self.stock_data is None:
                return None
            
            # Get historical data
            historical = self.stock_data.copy().sort_index()
            
            # Create figure
            fig = make_subplots(specs=[[{"secondary_y": False}]])
            
            # Add historical price line
            fig.add_trace(
                go.Scatter(
                    x=historical.index,
                    y=historical['close'],
                    mode='lines',
                    name='Historical Price',
                    line=dict(color='#212529', width=2)
                )
            )
            
            # Add prediction lines for each model
            colors = {
                'ARIMA': '#FF6B6B',  # Warning red
                'LSTM': '#2962FF',   # Primary blue
                'Prophet': '#00C853', # Secondary green
                'ensemble': '#5D6D7E' # Chart neutral
            }
            
            for model in ensemble_pred.columns:
                if model in colors:
                    line_style = 'solid' if model == 'ensemble' else 'dash'
                    width = 3 if model == 'ensemble' else 2
                    
                    fig.add_trace(
                        go.Scatter(
                            x=ensemble_pred.index,
                            y=ensemble_pred[model],
                            mode='lines',
                            name=f'{model} Prediction',
                            line=dict(color=colors[model], width=width, dash=line_style)
                        )
                    )
            
            # Update layout
            fig.update_layout(
                title='Stock Price Prediction',
                xaxis_title='Date',
                yaxis_title='Price',
                legend_title='Models',
                hovermode='x unified',
                template='plotly_white',
                height=600
            )
            
            # Add vertical line separating historical data and predictions
            last_historical_date = historical.index[-1]
            
            fig.add_vline(
                x=last_historical_date,
                line_width=1,
                line_dash="dash",
                line_color="gray",
                annotation_text="Prediction Start",
                annotation_position="top right"
            )
            
            return fig
        
        except Exception as e:
            st.error(f"Error creating prediction plot: {e}")
            return None
