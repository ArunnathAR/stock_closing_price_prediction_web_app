from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import json
from datetime import datetime, timedelta
import pandas as pd

# Import existing modules
from stock_data import get_stock_data, NIFTY50_STOCKS, calculate_technical_indicators, get_current_price, get_stock_overview
from prediction import StockPredictor
from trading import calculate_tax, calculate_profit_potential, get_broker_recommendations, execute_trade
from auth import hash_password, verify_password
from database import (
    initialize_database, add_user, check_user_exists, verify_user, 
    save_stock_analysis, get_user_stock_history,
    save_trading_transaction, get_user_trading_history,
    add_to_portfolio, get_user_portfolio,
    add_to_watchlist, remove_from_watchlist, get_user_watchlist
)

# Initialize FastAPI app
app = FastAPI(title="Stock Market Analysis API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, you should restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
initialize_database()

# ---- Data Models ----

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserSession(BaseModel):
    user_id: int
    username: str
    token: str

class StockData(BaseModel):
    symbol: str
    period: str

class TradingData(BaseModel):
    symbol: str
    transaction_type: str
    quantity: int
    price: float
    is_short_term: bool = True

class WatchlistItem(BaseModel):
    symbol: str

class AnalysisResult(BaseModel):
    symbol: str
    period: str
    user_id: int
    recommendation: str
    prediction_result: Dict[str, float]

# ---- Authentication Helper ----
# Simple token-based authentication (in a real app, use JWT or OAuth)
active_sessions = {}

def get_current_user(token: str = Query(...)):
    if token not in active_sessions:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return active_sessions[token]

# ---- API Routes ----

@app.get("/")
def read_root():
    return {"message": "Stock Market Analysis API is running"}

# ---- Authentication Routes ----

@app.post("/api/auth/register", response_model=dict)
def register_user(user: UserCreate):
    if check_user_exists(user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = hash_password(user.password)
    user_id = add_user(user.username, user.email, hashed_password)
    
    if user_id:
        return {"success": True, "message": "User registered successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to register user")

@app.post("/api/auth/login", response_model=UserSession)
def login_user(user: UserLogin):
    user_data = verify_user(user.username)
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    stored_password = user_data[2]
    if not verify_password(stored_password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Generate a simple token (in a real app, use JWT)
    token = f"{user.username}_{datetime.now().timestamp()}"
    user_id = user_data[0]
    
    # Store in active sessions
    active_sessions[token] = {"user_id": user_id, "username": user.username}
    
    return UserSession(user_id=user_id, username=user.username, token=token)

@app.post("/api/auth/logout")
def logout_user(current_user: dict = Depends(get_current_user)):
    # Remove from active sessions
    tokens_to_remove = []
    for token, user in active_sessions.items():
        if user.get("user_id") == current_user.get("user_id"):
            tokens_to_remove.append(token)
    
    for token in tokens_to_remove:
        active_sessions.pop(token, None)
    
    return {"success": True, "message": "Logged out successfully"}

# ---- Stock Data Routes ----

@app.get("/api/stocks/list")
def get_stock_list():
    # Return list of stocks with clean names
    clean_stocks = [{"symbol": stock, "name": stock.split('.')[0]} for stock in NIFTY50_STOCKS]
    return {"stocks": clean_stocks}

@app.get("/api/stocks/data")
def get_stock_price_data(symbol: str, period: str = "1month"):
    # Validate period
    if period not in ["1month", "3month", "5month"]:
        raise HTTPException(status_code=400, detail="Invalid period. Choose from: 1month, 3month, 5month")
    
    # Get stock data
    stock_data = get_stock_data(symbol, period)
    
    if stock_data is None or stock_data.empty:
        raise HTTPException(status_code=404, detail="Stock data not found")
    
    # Calculate technical indicators
    with_indicators = calculate_technical_indicators(stock_data)
    
    # Convert to dictionary format suitable for JSON
    result = {
        "dates": with_indicators.index.strftime('%Y-%m-%d').tolist(),
        "prices": {
            "open": with_indicators['open'].tolist(),
            "high": with_indicators['high'].tolist(),
            "low": with_indicators['low'].tolist(),
            "close": with_indicators['close'].tolist(),
            "volume": with_indicators['volume'].tolist()
        },
        "indicators": {}
    }
    
    # Add indicators
    indicator_columns = [
        'SMA_20', 'SMA_50', 'EMA_20', 'RSI', 'MACD', 'MACD_Signal',
        'BB_Middle', 'BB_Upper', 'BB_Lower'
    ]
    
    for col in indicator_columns:
        if col in with_indicators.columns:
            result["indicators"][col] = with_indicators[col].tolist()
    
    return result

@app.get("/api/stocks/price")
def get_current_stock_price(symbol: str):
    price = get_current_price(symbol)
    
    if price is None:
        raise HTTPException(status_code=404, detail="Current price not found")
    
    return {"symbol": symbol, "price": price}

@app.get("/api/stocks/overview")
def get_stock_details(symbol: str):
    overview = get_stock_overview(symbol)
    
    if overview is None:
        raise HTTPException(status_code=404, detail="Stock overview not found")
    
    return overview

# ---- Prediction Routes ----

@app.get("/api/prediction")
def predict_stock_price(symbol: str, period: str = "1month"):
    # Validate period
    if period not in ["1month", "3month", "5month"]:
        raise HTTPException(status_code=400, detail="Invalid period. Choose from: 1month, 3month, 5month")
    
    # Get stock data
    stock_data = get_stock_data(symbol, period)
    
    if stock_data is None or stock_data.empty:
        raise HTTPException(status_code=404, detail="Stock data not found")
    
    # Get current price
    current_price = get_current_price(symbol)
    
    if current_price is None:
        raise HTTPException(status_code=404, detail="Current price not found")
    
    # Initialize predictor with 30-day forecast
    predictor = StockPredictor(stock_data, forecast_days=30)
    
    # Generate ensemble prediction
    ensemble_predictions = predictor.ensemble_prediction()
    
    if ensemble_predictions is None:
        raise HTTPException(status_code=500, detail="Failed to generate predictions")
    
    # Generate recommendation
    recommendation, explanation = predictor.generate_recommendation(ensemble_predictions, current_price)
    
    # Prepare response data
    result = {
        "symbol": symbol,
        "current_price": current_price,
        "recommendation": recommendation,
        "explanation": explanation,
        "historical_dates": stock_data.index.strftime('%Y-%m-%d').tolist(),
        "historical_prices": stock_data['close'].tolist(),
        "prediction_dates": ensemble_predictions.index.strftime('%Y-%m-%d').tolist(),
        "predictions": {}
    }
    
    # Add predictions for each model
    for column in ensemble_predictions.columns:
        result["predictions"][column] = ensemble_predictions[column].tolist()
    
    return result

@app.post("/api/prediction/save")
def save_analysis(analysis: AnalysisResult, current_user: dict = Depends(get_current_user)):
    success = save_stock_analysis(
        current_user["user_id"],
        analysis.symbol,
        analysis.period,
        analysis.prediction_result,
        analysis.recommendation
    )
    
    if success:
        return {"success": True, "message": "Analysis saved successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save analysis")

# ---- Trading Routes ----

@app.post("/api/trading/calculate-tax")
def calculate_transaction_tax(data: TradingData):
    tax_info = calculate_tax(
        data.transaction_type,
        data.price,
        data.quantity,
        data.is_short_term
    )
    
    if tax_info is None:
        raise HTTPException(status_code=500, detail="Failed to calculate tax")
    
    return tax_info

@app.post("/api/trading/profit-potential")
def calculate_profit(data: TradingData):
    # For buy transactions only
    if data.transaction_type.lower() != "buy":
        raise HTTPException(status_code=400, detail="Profit potential only available for buy transactions")
    
    # Default to 15% short-term tax rate (could add long-term logic)
    tax_rate = 0.15
    
    # Get stock data for prediction (simulate some price changes for different periods)
    prediction_periods = {
        "1 Week": 7,
        "1 Month": 30,
        "3 Months": 90,
        "6 Months": 180,
        "1 Year": 365
    }
    
    # In real app, use actual prediction models for these values
    # Here, we'll use simple random changes as placeholders
    import numpy as np
    np.random.seed(int(datetime.now().timestamp()))
    
    expected_growth = {
        "1 Week": np.random.uniform(-3, 3),
        "1 Month": np.random.uniform(-8, 8),
        "3 Months": np.random.uniform(-15, 15),
        "6 Months": np.random.uniform(-25, 25),
        "1 Year": np.random.uniform(-40, 40)
    }
    
    # Calculate predicted prices and profit potential
    results = {}
    for period, growth in expected_growth.items():
        predicted_price = data.price * (1 + growth / 100)
        
        # Use long-term tax rate for 1 Year
        period_tax_rate = 0.10 if period == "1 Year" else 0.15
        profit = calculate_profit_potential(data.price, predicted_price, data.quantity, period_tax_rate)
        
        # Add to results
        results[period] = {
            "predicted_price": predicted_price,
            "price_change_percentage": (predicted_price - data.price) / data.price * 100,
            "profit_details": profit
        }
    
    return results

@app.get("/api/trading/brokers")
def get_brokers():
    brokers = get_broker_recommendations()
    return {"brokers": brokers}

@app.post("/api/trading/execute")
def execute_transaction(data: TradingData, current_user: dict = Depends(get_current_user)):
    success = execute_trade(
        current_user["user_id"],
        data.symbol,
        data.transaction_type.lower(),
        data.quantity,
        data.price
    )
    
    if success:
        return {"success": True, "message": f"{data.transaction_type} transaction executed successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to execute trade")

# ---- Portfolio Routes ----

@app.get("/api/portfolio")
def get_portfolio(current_user: dict = Depends(get_current_user)):
    portfolio = get_user_portfolio(current_user["user_id"])
    
    if portfolio is None:
        return {"holdings": []}
    
    # Convert DataFrame to list of dictionaries for JSON response
    holdings = []
    for index, row in portfolio.iterrows():
        # Get current price for each stock
        current_price = get_current_price(row['symbol'])
        
        if current_price:
            # Calculate current value and profit/loss
            current_value = current_price * row['quantity']
            pl_value = current_value - (row['avg_price'] * row['quantity'])
            pl_percentage = (current_price - row['avg_price']) / row['avg_price'] * 100
            
            holdings.append({
                "symbol": row['symbol'],
                "name": row['symbol'].split('.')[0],
                "quantity": row['quantity'],
                "avg_price": row['avg_price'],
                "current_price": current_price,
                "current_value": current_value,
                "pl_value": pl_value,
                "pl_percentage": pl_percentage
            })
    
    return {"holdings": holdings}

# ---- Watchlist Routes ----

@app.get("/api/watchlist")
def get_watchlist(current_user: dict = Depends(get_current_user)):
    watchlist = get_user_watchlist(current_user["user_id"])
    
    if watchlist is None:
        return {"items": []}
    
    # Convert DataFrame to list of dictionaries for JSON response
    items = []
    for index, row in watchlist.iterrows():
        # Get current price for each stock
        current_price = get_current_price(row['symbol'])
        
        items.append({
            "symbol": row['symbol'],
            "name": row['symbol'].split('.')[0],
            "current_price": current_price if current_price else None
        })
    
    return {"items": items}

@app.post("/api/watchlist/add")
def add_to_watchlist_api(item: WatchlistItem, current_user: dict = Depends(get_current_user)):
    success = add_to_watchlist(current_user["user_id"], item.symbol)
    
    if success:
        return {"success": True, "message": "Added to watchlist"}
    else:
        raise HTTPException(status_code=500, detail="Failed to add to watchlist or already in watchlist")

@app.post("/api/watchlist/remove")
def remove_from_watchlist_api(item: WatchlistItem, current_user: dict = Depends(get_current_user)):
    success = remove_from_watchlist(current_user["user_id"], item.symbol)
    
    if success:
        return {"success": True, "message": "Removed from watchlist"}
    else:
        raise HTTPException(status_code=500, detail="Failed to remove from watchlist or not in watchlist")

# ---- History Routes ----

@app.get("/api/history/analysis")
def get_analysis_history(current_user: dict = Depends(get_current_user), limit: int = 20):
    history = get_user_stock_history(current_user["user_id"], limit)
    
    if history is None:
        return {"history": []}
    
    # Convert DataFrame to list of dictionaries for JSON response
    items = []
    for index, row in history.iterrows():
        try:
            prediction_result = json.loads(row['prediction_result'])
        except:
            prediction_result = {}
        
        items.append({
            "id": row['id'],
            "symbol": row['stock_symbol'],
            "name": row['stock_symbol'].split('.')[0],
            "period": row['analysis_period'],
            "date": row['date'].strftime('%Y-%m-%d'),
            "recommendation": row['recommendation'],
            "prediction_result": prediction_result
        })
    
    return {"history": items}

@app.get("/api/history/trading")
def get_trading_history(current_user: dict = Depends(get_current_user), limit: int = 50):
    history = get_user_trading_history(current_user["user_id"], limit)
    
    if history is None:
        return {"history": []}
    
    # Convert DataFrame to list of dictionaries for JSON response
    items = []
    for index, row in history.iterrows():
        items.append({
            "id": row['id'],
            "symbol": row['stock_symbol'],
            "name": row['stock_symbol'].split('.')[0],
            "transaction_type": row['transaction_type'],
            "quantity": row['quantity'],
            "price": row['price'],
            "total_amount": row['total_amount'],
            "tax_amount": row['tax_amount'],
            "date": row['date'].strftime('%Y-%m-%d')
        })
    
    return {"history": items}

# Start the server with: uvicorn api:app --host 0.0.0.0 --port 5000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)