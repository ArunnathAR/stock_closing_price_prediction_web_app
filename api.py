from fastapi import FastAPI, Depends, Query, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import stock_data
import prediction
import trading
import database
import auth
from datetime import datetime
import jwt
import os

# Initialize FastAPI
app = FastAPI(title="Stock Analysis API")

# Secret key for JWT
SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")
ALGORITHM = "HS256"

# Initialize database
database.initialize_database()

# Define models
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

# Authentication function
def get_current_user(token: str = Query(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        username: str = payload.get("username")
        
        if user_id is None or username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        return {"user_id": user_id, "username": username}
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

# API Routes
@app.get("/")
def read_root():
    return {"message": "Welcome to the Stock Analysis API"}

# Auth routes
@app.post("/api/auth/register")
def register_user(user: UserCreate):
    if database.check_user_exists(user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Hash password and add user
    hashed_password = auth.hash_password(user.password)
    success = database.add_user(user.username, user.email, hashed_password)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    return {"message": "User created successfully"}

@app.post("/api/auth/login")
def login_user(user: UserLogin):
    # Verify user
    user_data = database.verify_user(user.username)
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Verify password
    stored_password = user_data['password']
    if not auth.verify_password(stored_password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Create JWT token
    token_data = {
        "sub": user_data['id'],
        "username": user_data['username'],
        "exp": datetime.utcnow().timestamp() + 86400  # 24 hours
    }
    
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return {
        "user_id": user_data['id'],
        "username": user_data['username'],
        "token": token
    }

@app.post("/api/auth/logout")
def logout_user(current_user: dict = Depends(get_current_user)):
    # JWT tokens are stateless, so we don't need to do anything server-side
    return {"message": "Logged out successfully"}

# Stock data routes
@app.get("/api/stocks/list")
def get_stock_list():
    return {"stocks": stock_data.NIFTY50_STOCKS}

@app.get("/api/stocks/data")
def get_stock_price_data(symbol: str, period: str = "1month"):
    df = stock_data.get_stock_data(symbol, period)
    
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="Stock data not found")
    
    # Calculate technical indicators
    df_with_indicators = stock_data.calculate_technical_indicators(df)
    
    # Convert to dict
    result = df_with_indicators.reset_index().to_dict(orient='records')
    
    return {"data": result}

@app.get("/api/stocks/price")
def get_current_stock_price(symbol: str):
    price = stock_data.get_current_price(symbol)
    
    if price is None:
        raise HTTPException(status_code=404, detail="Stock price not found")
    
    return {"symbol": symbol, "price": price}

@app.get("/api/stocks/overview")
def get_stock_details(symbol: str):
    overview = stock_data.get_stock_overview(symbol)
    
    if overview is None:
        raise HTTPException(status_code=404, detail="Stock overview not found")
    
    return overview

# Prediction routes
@app.get("/api/prediction")
def predict_stock_price(symbol: str, period: str = "1month"):
    # Get stock data
    df = stock_data.get_stock_data(symbol, period)
    
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="Stock data not found")
    
    # Get current price
    current_price = stock_data.get_current_price(symbol)
    
    if current_price is None:
        raise HTTPException(status_code=404, detail="Current stock price not found")
    
    # Create predictor
    predictor = prediction.StockPredictor(df)
    
    # Get predictions
    ensemble_pred = predictor.ensemble_prediction()
    
    # Generate recommendation
    recommendation, explanation = predictor.generate_recommendation(ensemble_pred, current_price)
    
    # Get prediction chart
    chart_data = predictor.plot_prediction(ensemble_pred)
    
    # Return results
    return {
        "symbol": symbol,
        "current_price": current_price,
        "prediction": ensemble_pred.to_dict(orient='records'),
        "recommendation": recommendation,
        "explanation": explanation,
        "chart_data": chart_data
    }

@app.post("/api/prediction/save")
def save_analysis(analysis: AnalysisResult, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    
    # Save analysis to database
    success = database.save_stock_analysis(
        user_id,
        analysis.symbol,
        analysis.period,
        analysis.prediction_result,
        analysis.recommendation
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save analysis")
    
    return {"message": "Analysis saved successfully"}

# Trading routes
@app.post("/api/trading/calculate-tax")
def calculate_transaction_tax(data: TradingData):
    tax_result = trading.calculate_tax(
        data.transaction_type,
        data.price,
        data.quantity,
        data.is_short_term
    )
    
    return tax_result

@app.post("/api/trading/profit-potential")
def calculate_profit(data: TradingData):
    # For profit calculation, we need to get the current price and predicted price
    current_price = stock_data.get_current_price(data.symbol)
    
    if current_price is None:
        raise HTTPException(status_code=404, detail="Current stock price not found")
    
    # Get prediction (using 1month as default)
    df = stock_data.get_stock_data(data.symbol, "1month")
    
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="Stock data not found")
    
    predictor = prediction.StockPredictor(df)
    predictions = predictor.ensemble_prediction()
    
    # Get the predicted price (last day of prediction)
    predicted_price = predictions.iloc[-1]['predicted_price']
    
    profit_result = trading.calculate_profit_potential(
        current_price,
        predicted_price,
        data.quantity
    )
    
    return {
        "current_price": current_price,
        "predicted_price": predicted_price,
        "profit_potential": profit_result
    }

@app.get("/api/trading/brokers")
def get_brokers():
    brokers = trading.get_broker_recommendations()
    return {"brokers": brokers}

@app.post("/api/trading/execute")
def execute_transaction(data: TradingData, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    
    # Execute trade
    success = trading.execute_trade(
        user_id,
        data.symbol,
        data.transaction_type,
        data.quantity,
        data.price
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to execute transaction")
    
    return {"message": "Transaction executed successfully"}

# Portfolio and watchlist routes
@app.get("/api/portfolio")
def get_portfolio(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    
    # Get portfolio
    portfolio = database.get_user_portfolio(user_id)
    
    if portfolio is None:
        return {"portfolio": []}
    
    return {"portfolio": portfolio.to_dict(orient='records')}

@app.get("/api/watchlist")
def get_watchlist(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    
    # Get watchlist
    watchlist = database.get_user_watchlist(user_id)
    
    if watchlist is None:
        return {"watchlist": []}
    
    return {"watchlist": watchlist.to_dict(orient='records')}

@app.post("/api/watchlist/add")
def add_to_watchlist_api(item: WatchlistItem, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    
    # Add to watchlist
    success = database.add_to_watchlist(user_id, item.symbol)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add to watchlist")
    
    return {"message": "Added to watchlist successfully"}

@app.post("/api/watchlist/remove")
def remove_from_watchlist_api(item: WatchlistItem, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    
    # Remove from watchlist
    success = database.remove_from_watchlist(user_id, item.symbol)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to remove from watchlist")
    
    return {"message": "Removed from watchlist successfully"}

# History routes
@app.get("/api/history/analysis")
def get_analysis_history(current_user: dict = Depends(get_current_user), limit: int = 20):
    user_id = current_user["user_id"]
    
    # Get analysis history
    history = database.get_user_stock_history(user_id, limit)
    
    if history is None:
        return {"history": []}
    
    return {"history": history}

@app.get("/api/history/trading")
def get_trading_history(current_user: dict = Depends(get_current_user), limit: int = 50):
    user_id = current_user["user_id"]
    
    # Get trading history
    history = database.get_user_trading_history(user_id, limit)
    
    if history is None:
        return {"history": []}
    
    return {"history": history}