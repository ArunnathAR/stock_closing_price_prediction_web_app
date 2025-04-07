import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  AreaChart, Area
} from 'recharts';
import apiService from '../services/api';

const StockAnalysis = () => {
  const [stocksList, setStocksList] = useState([]);
  const [selectedStock, setSelectedStock] = useState('');
  const [selectedPeriod, setSelectedPeriod] = useState('1month');
  const [stockData, setStockData] = useState(null);
  const [predictionResult, setPredictionResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  
  const navigate = useNavigate();

  // Fetch stock list on component mount
  useEffect(() => {
    const fetchStocksList = async () => {
      try {
        setLoading(true);
        const response = await apiService.stocks.getList();
        setStocksList(response.data.stocks);
      } catch (error) {
        setError('Failed to load stocks list');
        console.error('Error fetching stocks list:', error);
      } finally {
        setLoading(false);
      }
    };

    const fetchAnalysisHistory = async () => {
      try {
        const response = await apiService.history.getAnalysis();
        setAnalysisHistory(response.data.history);
      } catch (error) {
        console.error('Error fetching analysis history:', error);
      }
    };

    fetchStocksList();
    fetchAnalysisHistory();
  }, []);

  // Handle stock selection
  const handleStockChange = (e) => {
    setSelectedStock(e.target.value);
    setPredictionResult(null);
  };

  // Handle period selection
  const handlePeriodChange = (e) => {
    setSelectedPeriod(e.target.value);
    setPredictionResult(null);
  };

  // Generate prediction
  const handleAnalyze = async () => {
    if (!selectedStock) {
      setError('Please select a stock');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      // Get prediction results
      const response = await apiService.prediction.predict(selectedStock, selectedPeriod);
      setPredictionResult(response.data);
      
      // Save analysis for user
      await apiService.prediction.saveAnalysis({
        symbol: selectedStock,
        period: selectedPeriod,
        user_id: 0, // This will be overridden by server using token
        recommendation: response.data.recommendation,
        prediction_result: {
          current_price: response.data.current_price,
          predicted_price: response.data.predictions.ensemble[response.data.predictions.ensemble.length - 1]
        }
      });
      
      // Refresh history
      const historyResponse = await apiService.history.getAnalysis();
      setAnalysisHistory(historyResponse.data.history);
      
    } catch (error) {
      setError('Failed to generate prediction');
      console.error('Error generating prediction:', error);
    } finally {
      setLoading(false);
    }
  };

  // Load historical analysis
  const loadHistoricalAnalysis = async (item) => {
    try {
      setLoading(true);
      setError('');
      setSelectedStock(item.symbol);
      setSelectedPeriod(item.period);
      
      // Get prediction results
      const response = await apiService.prediction.predict(item.symbol, item.period);
      setPredictionResult(response.data);
      
    } catch (error) {
      setError('Failed to load historical analysis');
      console.error('Error loading historical analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  // Navigate to trading page with selected stock
  const goToTrading = () => {
    if (selectedStock && predictionResult) {
      navigate('/trading', { 
        state: { 
          symbol: selectedStock,
          currentPrice: predictionResult.current_price
        } 
      });
    }
  };

  // Format data for charts
  const formatChartData = () => {
    if (!predictionResult) return [];

    const historicalData = predictionResult.historical_dates.map((date, index) => ({
      date,
      actual: predictionResult.historical_prices[index],
    }));

    const predictionData = predictionResult.prediction_dates.map((date, index) => ({
      date,
      predicted: predictionResult.predictions.ensemble[index],
      arima: predictionResult.predictions.arima ? predictionResult.predictions.arima[index] : null,
      lstm: predictionResult.predictions.lstm ? predictionResult.predictions.lstm[index] : null,
      prophet: predictionResult.predictions.prophet ? predictionResult.predictions.prophet[index] : null,
    }));

    // Combine the data (last historical point might be first prediction point)
    const lastHistoricalDate = historicalData[historicalData.length - 1].date;
    const lastHistoricalPrice = historicalData[historicalData.length - 1].actual;
    
    // Add last historical point to prediction data if it's not already there
    if (predictionData[0].date !== lastHistoricalDate) {
      predictionData.unshift({
        date: lastHistoricalDate,
        predicted: lastHistoricalPrice,
        arima: lastHistoricalPrice,
        lstm: lastHistoricalPrice,
        prophet: lastHistoricalPrice,
      });
    }

    return [...historicalData, ...predictionData.slice(1)];
  };

  // Determine recommendation color
  const getRecommendationColor = (recommendation) => {
    if (!recommendation) return 'bg-gray-100 text-gray-800';
    
    switch(recommendation.toLowerCase()) {
      case 'buy':
        return 'bg-green-100 text-green-800';
      case 'sell':
        return 'bg-red-100 text-red-800';
      case 'hold':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="flex flex-col space-y-6">
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">
          Stock Analysis
        </h2>
        
        <div className="flex flex-col md:flex-row md:space-x-6 space-y-4 md:space-y-0 mb-6">
          <div className="md:w-1/3">
            <label htmlFor="stock" className="label">
              Select Stock
            </label>
            <select
              id="stock"
              className="input"
              value={selectedStock}
              onChange={handleStockChange}
              disabled={loading}
            >
              <option value="">Select a stock...</option>
              {stocksList.map((stock) => (
                <option key={stock.symbol} value={stock.symbol}>
                  {stock.name}
                </option>
              ))}
            </select>
          </div>
          
          <div className="md:w-1/3">
            <label htmlFor="period" className="label">
              Analysis Period
            </label>
            <select
              id="period"
              className="input"
              value={selectedPeriod}
              onChange={handlePeriodChange}
              disabled={loading}
            >
              <option value="1month">1 Month</option>
              <option value="3month">3 Months</option>
              <option value="5month">5 Months</option>
            </select>
          </div>
          
          <div className="md:w-1/3 flex items-end">
            <button
              onClick={handleAnalyze}
              className="btn btn-primary w-full py-2"
              disabled={loading || !selectedStock}
            >
              {loading ? 'Analyzing...' : 'Analyze Stock'}
            </button>
          </div>
        </div>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        
        <div className="mb-4">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="btn btn-neutral"
          >
            {showHistory ? 'Hide History' : 'Show Analysis History'}
          </button>
        </div>
        
        {showHistory && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              Your Recent Analyses
            </h3>
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="py-2 px-4 text-left text-sm font-medium text-gray-700">Date</th>
                    <th className="py-2 px-4 text-left text-sm font-medium text-gray-700">Stock</th>
                    <th className="py-2 px-4 text-left text-sm font-medium text-gray-700">Period</th>
                    <th className="py-2 px-4 text-left text-sm font-medium text-gray-700">Recommendation</th>
                    <th className="py-2 px-4 text-left text-sm font-medium text-gray-700">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {analysisHistory.length > 0 ? (
                    analysisHistory.map((item) => (
                      <tr key={item.id} className="border-b">
                        <td className="py-2 px-4 text-sm text-gray-700">{item.date}</td>
                        <td className="py-2 px-4 text-sm text-gray-700">{item.name}</td>
                        <td className="py-2 px-4 text-sm text-gray-700">{item.period}</td>
                        <td className="py-2 px-4">
                          <span className={`badge ${getRecommendationColor(item.recommendation)}`}>
                            {item.recommendation}
                          </span>
                        </td>
                        <td className="py-2 px-4">
                          <button
                            onClick={() => loadHistoricalAnalysis(item)}
                            className="text-blue-600 hover:text-blue-800 text-sm"
                          >
                            Load
                          </button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="5" className="py-4 px-4 text-center text-gray-500">
                        No analysis history found
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
      
      {predictionResult && (
        <div className="card">
          <div className="flex flex-col md:flex-row justify-between items-start mb-6">
            <div>
              <h3 className="text-2xl font-bold text-gray-800">
                Analysis Results for {selectedStock.split('.')[0]}
              </h3>
              <div className="flex items-center space-x-2 mt-2">
                <span className="text-gray-600">Current Price:</span>
                <span className="font-semibold data-text text-lg">
                  ₹{predictionResult.current_price.toFixed(2)}
                </span>
              </div>
            </div>
            
            <div className="mt-4 md:mt-0">
              <span className={`badge text-base px-3 py-1 ${getRecommendationColor(predictionResult.recommendation)}`}>
                {predictionResult.recommendation.toUpperCase()}
              </span>
            </div>
          </div>
          
          <div className="mb-8">
            <h4 className="text-lg font-semibold text-gray-800 mb-2">
              Recommendation Details
            </h4>
            <div className={`p-4 rounded-lg border ${
              predictionResult.recommendation === 'Buy' 
                ? 'border-green-200 bg-green-50' 
                : predictionResult.recommendation === 'Sell'
                  ? 'border-red-200 bg-red-50'
                  : 'border-blue-200 bg-blue-50'
            }`}>
              <p className="text-gray-700">
                {predictionResult.explanation}
              </p>
            </div>
          </div>
          
          <div className="mb-8">
            <h4 className="text-lg font-semibold text-gray-800 mb-2">
              Price Prediction Chart
            </h4>
            <div className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={formatChartData()} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis 
                    domain={['auto', 'auto']} 
                    tickFormatter={(value) => `₹${value.toFixed(0)}`}
                  />
                  <Tooltip 
                    formatter={(value) => [`₹${value.toFixed(2)}`, '']}
                    labelFormatter={(label) => `Date: ${label}`}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="actual" 
                    stroke="#3366CC" 
                    name="Actual Price" 
                    strokeWidth={2}
                    dot={{ r: 1 }}
                    activeDot={{ r: 5 }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="predicted" 
                    stroke="#DC3912" 
                    name="Ensemble Prediction" 
                    strokeWidth={2}
                    dot={{ r: 1 }}
                    activeDot={{ r: 5 }}
                    strokeDasharray="5 5"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="lstm" 
                    stroke="#FF9900" 
                    name="LSTM Model" 
                    strokeWidth={1}
                    dot={false}
                    activeDot={{ r: 4 }}
                    strokeDasharray="3 3"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="arima" 
                    stroke="#109618" 
                    name="ARIMA Model" 
                    strokeWidth={1}
                    dot={false}
                    activeDot={{ r: 4 }}
                    strokeDasharray="3 3"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="prophet" 
                    stroke="#990099" 
                    name="Prophet Model" 
                    strokeWidth={1}
                    dot={false}
                    activeDot={{ r: 4 }}
                    strokeDasharray="3 3"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          <div className="flex justify-end">
            <button 
              onClick={goToTrading}
              className="btn btn-secondary"
            >
              Go to Trading
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default StockAnalysis;