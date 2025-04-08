import React, { useState, useEffect } from 'react';
import { stockAPI, predictionAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const StockAnalysis = () => {
  const [stockList, setStockList] = useState([]);
  const [selectedStock, setSelectedStock] = useState('');
  const [period, setPeriod] = useState('1month');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [stockData, setStockData] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [currentPrice, setCurrentPrice] = useState(null);
  
  const { isAuthenticated } = useAuth();

  // Fetch stock list on component mount
  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const response = await stockAPI.getStockList();
        setStockList(response.data.stocks);
      } catch (err) {
        console.error('Failed to fetch stock list', err);
        setError('Failed to load stock list. Please try again later.');
      }
    };

    fetchStocks();
  }, []);

  // Fetch stock data and prediction when stock or period changes
  const handleAnalyze = async () => {
    if (!selectedStock) {
      setError('Please select a stock to analyze');
      return;
    }

    setLoading(true);
    setError('');
    setStockData(null);
    setPrediction(null);
    
    try {
      // Fetch stock data
      const dataResponse = await stockAPI.getStockData(selectedStock, period);
      setStockData(dataResponse.data.data);
      
      // Fetch current price
      const priceResponse = await stockAPI.getCurrentPrice(selectedStock);
      setCurrentPrice(priceResponse.data.price);
      
      // Fetch prediction
      const predictionResponse = await predictionAPI.predictStockPrice(selectedStock, period);
      setPrediction(predictionResponse.data);
      
    } catch (err) {
      console.error('Analysis failed', err);
      setError('Failed to analyze stock. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Save analysis to user account
  const handleSaveAnalysis = async () => {
    if (!isAuthenticated()) {
      setError('Please log in to save analysis');
      return;
    }
    
    if (!prediction) {
      setError('No analysis to save');
      return;
    }
    
    try {
      const analysisData = {
        symbol: selectedStock,
        period: period,
        user_id: 0, // This will be overridden by the server based on the token
        recommendation: prediction.recommendation,
        prediction_result: {
          current_price: prediction.current_price,
          predicted_price: prediction.prediction[prediction.prediction.length - 1].predicted_price
        }
      };
      
      await predictionAPI.saveAnalysis(analysisData);
      alert('Analysis saved successfully!');
    } catch (err) {
      console.error('Failed to save analysis', err);
      setError('Failed to save analysis. Please try again later.');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Stock Analysis</h1>
      
      {/* Analysis Controls */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label htmlFor="stock" className="block text-sm font-medium text-gray-700 mb-1">
              Select Stock
            </label>
            <select
              id="stock"
              className="select-field"
              value={selectedStock}
              onChange={(e) => setSelectedStock(e.target.value)}
            >
              <option value="">-- Select a stock --</option>
              {stockList.map((stock) => (
                <option key={stock} value={stock}>
                  {stock}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label htmlFor="period" className="block text-sm font-medium text-gray-700 mb-1">
              Analysis Period
            </label>
            <select
              id="period"
              className="select-field"
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
            >
              <option value="1month">1 Month</option>
              <option value="3month">3 Months</option>
              <option value="5month">5 Months</option>
            </select>
          </div>
          
          <div className="flex items-end">
            <button
              onClick={handleAnalyze}
              disabled={loading || !selectedStock}
              className={`btn-primary w-full ${loading ? 'opacity-70 cursor-not-allowed' : ''}`}
            >
              {loading ? 'Analyzing...' : 'Analyze Stock'}
            </button>
          </div>
        </div>
        
        {error && (
          <div className="mt-4 bg-red-50 border-l-4 border-red-500 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Results */}
      {prediction && (
        <div className="space-y-6">
          {/* Overview */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Overview</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-500">Current Price</p>
                <p className="text-2xl font-bold text-blue-600">₹{currentPrice.toFixed(2)}</p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-500">Predicted Price</p>
                <p className="text-2xl font-bold text-green-600">
                  ₹{prediction.prediction[prediction.prediction.length - 1].predicted_price.toFixed(2)}
                </p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-500">Recommendation</p>
                <p className={`text-2xl font-bold ${
                  prediction.recommendation === 'buy' ? 'text-green-600' :
                  prediction.recommendation === 'sell' ? 'text-red-600' : 'text-yellow-600'
                }`}>
                  {prediction.recommendation.toUpperCase()}
                </p>
              </div>
            </div>
            
            {/* Recommendation Box */}
            <div className={`mt-6 p-4 border-l-4 rounded-r-md ${
              prediction.recommendation === 'buy' ? 'border-green-500 bg-green-50' :
              prediction.recommendation === 'sell' ? 'border-red-500 bg-red-50' : 'border-yellow-500 bg-yellow-50'
            }`}>
              <h3 className="text-lg font-medium mb-2 text-gray-900">Recommendation Explanation</h3>
              <p className="text-gray-700">{prediction.explanation}</p>
            </div>
            
            {/* Save Analysis Button */}
            {isAuthenticated() && (
              <div className="mt-6 flex justify-end">
                <button 
                  onClick={handleSaveAnalysis}
                  className="btn-success"
                >
                  Save Analysis
                </button>
              </div>
            )}
          </div>
          
          {/* Chart will go here - for now just display text */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Price Prediction Chart</h2>
            <div className="bg-gray-100 p-10 rounded-lg flex items-center justify-center">
              <p className="text-gray-500">Chart will be implemented here</p>
            </div>
          </div>
          
          {/* Technical Indicators */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Technical Indicators</h2>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Close</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RSI</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">MACD</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">SMA 20</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">SMA 50</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {stockData && stockData.slice(0, 5).map((data, index) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(data.Date || data.date).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ₹{data.close.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {data.RSI ? data.RSI.toFixed(2) : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {data.MACD ? data.MACD.toFixed(2) : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {data.SMA_20 ? data.SMA_20.toFixed(2) : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {data.SMA_50 ? data.SMA_50.toFixed(2) : 'N/A'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
      
      {/* Login Prompt */}
      {!isAuthenticated() && (
        <div className="bg-blue-50 p-6 rounded-lg shadow-md mt-6">
          <h2 className="text-xl font-semibold text-blue-800 mb-2">Save your analysis</h2>
          <p className="text-blue-700 mb-4">
            Create an account or log in to save your stock analysis and build your portfolio.
          </p>
          <div className="flex space-x-4">
            <a href="/login" className="btn-primary">
              Log In
            </a>
            <a href="/register" className="btn-success">
              Create Account
            </a>
          </div>
        </div>
      )}
    </div>
  );
};

export default StockAnalysis;