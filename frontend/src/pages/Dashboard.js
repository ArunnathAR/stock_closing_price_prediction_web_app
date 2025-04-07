import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell,
  ComposedChart, Area
} from 'recharts';
import apiService from '../services/api';

const Dashboard = () => {
  const [portfolio, setPortfolio] = useState([]);
  const [watchlist, setWatchlist] = useState([]);
  const [tradingHistory, setTradingHistory] = useState([]);
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [stocksList, setStocksList] = useState([]);
  const [selectedStock, setSelectedStock] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  
  const navigate = useNavigate();

  // Load dashboard data on component mount
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Fetch portfolio data
        const portfolioResponse = await apiService.portfolio.get();
        setPortfolio(portfolioResponse.data.holdings);
        
        // Fetch watchlist
        const watchlistResponse = await apiService.watchlist.get();
        setWatchlist(watchlistResponse.data.items);
        
        // Fetch trading history
        const tradingResponse = await apiService.history.getTrading(20);
        setTradingHistory(tradingResponse.data.history);
        
        // Fetch analysis history
        const analysisResponse = await apiService.history.getAnalysis(10);
        setAnalysisHistory(analysisResponse.data.history);
        
        // Fetch stocks list for watchlist
        const stocksResponse = await apiService.stocks.getList();
        setStocksList(stocksResponse.data.stocks);
      } catch (error) {
        setError('Failed to load dashboard data');
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Handle adding stock to watchlist
  const handleAddToWatchlist = async () => {
    if (!selectedStock) {
      setError('Please select a stock to add to watchlist');
      return;
    }

    try {
      setLoading(true);
      
      const response = await apiService.watchlist.add(selectedStock);
      
      if (response.data.success) {
        // Refresh watchlist
        const watchlistResponse = await apiService.watchlist.get();
        setWatchlist(watchlistResponse.data.items);
        
        setSuccessMessage('Stock added to watchlist');
        setSelectedStock('');
      }
    } catch (error) {
      setError('Failed to add stock to watchlist');
      console.error('Error adding to watchlist:', error);
    } finally {
      setLoading(false);
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage('');
      }, 3000);
    }
  };

  // Handle removing stock from watchlist
  const handleRemoveFromWatchlist = async (symbol) => {
    try {
      setLoading(true);
      
      const response = await apiService.watchlist.remove(symbol);
      
      if (response.data.success) {
        // Refresh watchlist
        const watchlistResponse = await apiService.watchlist.get();
        setWatchlist(watchlistResponse.data.items);
        
        setSuccessMessage('Stock removed from watchlist');
      }
    } catch (error) {
      setError('Failed to remove stock from watchlist');
      console.error('Error removing from watchlist:', error);
    } finally {
      setLoading(false);
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage('');
      }, 3000);
    }
  };

  // Navigate to stock analysis page
  const goToAnalysis = (symbol) => {
    navigate('/analysis', { state: { symbol } });
  };

  // Navigate to trading page
  const goToTrading = (symbol, currentPrice) => {
    navigate('/trading', { 
      state: { 
        symbol,
        currentPrice
      } 
    });
  };

  // Format currency display
  const formatCurrency = (value) => {
    if (!value && value !== 0) return 'N/A';
    return `₹${value.toFixed(2)}`;
  };

  // Format percentage display
  const formatPercentage = (value) => {
    if (!value && value !== 0) return 'N/A';
    return `${value.toFixed(2)}%`;
  };

  // Get recommendation color
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

  // Calculate total portfolio value
  const calculateTotalPortfolioValue = () => {
    return portfolio.reduce((total, item) => total + (item.current_value || 0), 0);
  };

  // Calculate total portfolio profit/loss
  const calculateTotalProfitLoss = () => {
    return portfolio.reduce((total, item) => total + (item.pl_value || 0), 0);
  };

  // Prepare data for portfolio allocation pie chart
  const getPortfolioAllocationData = () => {
    if (!portfolio.length) return [];
    
    return portfolio.map(item => ({
      name: item.name,
      value: item.current_value
    }));
  };

  // Prepare data for profit/loss bar chart
  const getProfitLossData = () => {
    if (!portfolio.length) return [];
    
    return portfolio.map(item => ({
      name: item.name,
      value: item.pl_value
    }));
  };

  // Get trading history by type for chart
  const getTradingByTypeData = () => {
    if (!tradingHistory.length) return [];
    
    const buyCount = tradingHistory.filter(item => 
      item.transaction_type === 'buy'
    ).length;
    
    const sellCount = tradingHistory.filter(item => 
      item.transaction_type === 'sell'
    ).length;
    
    return [
      { name: 'Buy', value: buyCount },
      { name: 'Sell', value: sellCount }
    ];
  };

  // Colors for pie charts
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#1890FF', '#6EBE49', '#F87171'];

  return (
    <div className="flex flex-col space-y-6">
      {loading && (
        <div className="card text-center py-8">
          <p className="text-gray-600">Loading dashboard data...</p>
        </div>
      )}
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}
      
      {successMessage && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
          {successMessage}
        </div>
      )}
      
      {!loading && (
        <>
          {/* Portfolio Summary */}
          <div className="card">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">
              Portfolio Summary
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <div className="flex flex-col space-y-4">
                  <div className="bg-gray-100 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-gray-600 mb-1">
                      Total Portfolio Value
                    </h3>
                    <p className="text-2xl font-bold data-text">
                      {formatCurrency(calculateTotalPortfolioValue())}
                    </p>
                  </div>
                  
                  <div className={`rounded-lg p-4 ${
                    calculateTotalProfitLoss() >= 0 
                      ? 'bg-green-50' 
                      : 'bg-red-50'
                  }`}>
                    <h3 className="text-sm font-semibold text-gray-600 mb-1">
                      Total Profit/Loss
                    </h3>
                    <p className={`text-2xl font-bold data-text ${
                      calculateTotalProfitLoss() >= 0 
                        ? 'text-green-600' 
                        : 'text-red-500'
                    }`}>
                      {formatCurrency(calculateTotalProfitLoss())}
                    </p>
                  </div>
                </div>
                
                <div className="mt-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">
                    Portfolio Allocation
                  </h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={getPortfolioAllocationData()}
                          cx="50%"
                          cy="50%"
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                          nameKey="name"
                          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                        >
                          {getPortfolioAllocationData().map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value) => formatCurrency(value)} />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">
                  Profit/Loss by Stock
                </h3>
                <div className="h-64 mb-6">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={getProfitLossData()}
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis tickFormatter={(value) => `₹${value}`} />
                      <Tooltip formatter={(value) => formatCurrency(value)} />
                      <Bar 
                        dataKey="value" 
                        fill="#8884d8"
                        name="Profit/Loss"
                      >
                        {getProfitLossData().map((entry, index) => (
                          <Cell 
                            key={`cell-${index}`} 
                            fill={entry.value >= 0 ? '#00C853' : '#FF6B6B'} 
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                
                <h3 className="text-lg font-semibold text-gray-800 mb-2">
                  Trading Activity
                </h3>
                <div className="h-40">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={getTradingByTypeData()}
                        cx="50%"
                        cy="50%"
                        outerRadius={60}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        <Cell fill="#2962FF" /> {/* Buy */}
                        <Cell fill="#FF6B6B" /> {/* Sell */}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                Holdings
              </h3>
              <div className="overflow-x-auto">
                <table className="min-w-full bg-white">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="py-2 px-3 text-left text-sm font-medium text-gray-700">Stock</th>
                      <th className="py-2 px-3 text-right text-sm font-medium text-gray-700">Quantity</th>
                      <th className="py-2 px-3 text-right text-sm font-medium text-gray-700">Avg. Price</th>
                      <th className="py-2 px-3 text-right text-sm font-medium text-gray-700">Current Price</th>
                      <th className="py-2 px-3 text-right text-sm font-medium text-gray-700">Value</th>
                      <th className="py-2 px-3 text-right text-sm font-medium text-gray-700">P/L</th>
                      <th className="py-2 px-3 text-center text-sm font-medium text-gray-700">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {portfolio.length > 0 ? (
                      portfolio.map((item, index) => (
                        <tr key={index} className="border-b">
                          <td className="py-2 px-3 text-sm">{item.name}</td>
                          <td className="py-2 px-3 text-right text-sm">{item.quantity}</td>
                          <td className="py-2 px-3 text-right text-sm data-text">{formatCurrency(item.avg_price)}</td>
                          <td className="py-2 px-3 text-right text-sm data-text">{formatCurrency(item.current_price)}</td>
                          <td className="py-2 px-3 text-right text-sm font-semibold data-text">{formatCurrency(item.current_value)}</td>
                          <td className={`py-2 px-3 text-right text-sm font-semibold ${
                            item.pl_value >= 0 ? 'text-green-600' : 'text-red-500'
                          }`}>
                            {formatCurrency(item.pl_value)} ({formatPercentage(item.pl_percentage)})
                          </td>
                          <td className="py-2 px-3 text-center">
                            <div className="flex justify-center space-x-2">
                              <button
                                onClick={() => goToAnalysis(item.symbol)}
                                className="text-blue-600 hover:text-blue-800 text-sm"
                                title="Analyze"
                              >
                                Analyze
                              </button>
                              <button
                                onClick={() => goToTrading(item.symbol, item.current_price)}
                                className="text-blue-600 hover:text-blue-800 text-sm"
                                title="Trade"
                              >
                                Trade
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="7" className="py-4 px-3 text-center text-gray-500">
                          No stocks in portfolio
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          
          {/* Watchlist */}
          <div className="card">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">
              Watchlist
            </h2>
            
            <div className="flex flex-col md:flex-row md:items-end md:space-x-4 space-y-4 md:space-y-0 mb-6">
              <div className="md:w-1/3">
                <label htmlFor="watchlistStock" className="label">
                  Add Stock to Watchlist
                </label>
                <select
                  id="watchlistStock"
                  className="input"
                  value={selectedStock}
                  onChange={(e) => setSelectedStock(e.target.value)}
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
              
              <button
                onClick={handleAddToWatchlist}
                className="btn btn-primary"
                disabled={loading || !selectedStock}
              >
                Add to Watchlist
              </button>
            </div>
            
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="py-2 px-4 text-left text-sm font-medium text-gray-700">Stock</th>
                    <th className="py-2 px-4 text-right text-sm font-medium text-gray-700">Current Price</th>
                    <th className="py-2 px-4 text-center text-sm font-medium text-gray-700">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {watchlist.length > 0 ? (
                    watchlist.map((item, index) => (
                      <tr key={index} className="border-b">
                        <td className="py-2 px-4 text-sm">{item.name}</td>
                        <td className="py-2 px-4 text-right text-sm font-semibold data-text">
                          {item.current_price ? formatCurrency(item.current_price) : 'N/A'}
                        </td>
                        <td className="py-2 px-4 text-center">
                          <div className="flex justify-center space-x-2">
                            <button
                              onClick={() => goToAnalysis(item.symbol)}
                              className="text-blue-600 hover:text-blue-800 text-sm"
                              title="Analyze"
                            >
                              Analyze
                            </button>
                            <button
                              onClick={() => goToTrading(item.symbol, item.current_price)}
                              className="text-blue-600 hover:text-blue-800 text-sm"
                              title="Trade"
                            >
                              Trade
                            </button>
                            <button
                              onClick={() => handleRemoveFromWatchlist(item.symbol)}
                              className="text-red-500 hover:text-red-700 text-sm"
                              title="Remove"
                            >
                              Remove
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="3" className="py-4 px-4 text-center text-gray-500">
                        No stocks in watchlist
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
          
          {/* Recent Activity */}
          <div className="card">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">
              Recent Activity
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">
                  Recent Analyses
                </h3>
                <div className="overflow-y-auto max-h-80">
                  <table className="min-w-full bg-white">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="py-2 px-3 text-left text-sm font-medium text-gray-700">Date</th>
                        <th className="py-2 px-3 text-left text-sm font-medium text-gray-700">Stock</th>
                        <th className="py-2 px-3 text-left text-sm font-medium text-gray-700">Recommendation</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analysisHistory.length > 0 ? (
                        analysisHistory.map((item) => (
                          <tr key={item.id} className="border-b">
                            <td className="py-2 px-3 text-sm text-gray-700">{item.date}</td>
                            <td className="py-2 px-3 text-sm text-gray-700">{item.name}</td>
                            <td className="py-2 px-3">
                              <span className={`badge ${getRecommendationColor(item.recommendation)}`}>
                                {item.recommendation}
                              </span>
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan="3" className="py-4 px-3 text-center text-gray-500">
                            No analysis history found
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">
                  Recent Trades
                </h3>
                <div className="overflow-y-auto max-h-80">
                  <table className="min-w-full bg-white">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="py-2 px-3 text-left text-sm font-medium text-gray-700">Date</th>
                        <th className="py-2 px-3 text-left text-sm font-medium text-gray-700">Stock</th>
                        <th className="py-2 px-3 text-left text-sm font-medium text-gray-700">Type</th>
                        <th className="py-2 px-3 text-right text-sm font-medium text-gray-700">Amount</th>
                      </tr>
                    </thead>
                    <tbody>
                      {tradingHistory.length > 0 ? (
                        tradingHistory.slice(0, 10).map((item) => (
                          <tr key={item.id} className="border-b">
                            <td className="py-2 px-3 text-sm text-gray-700">{item.date}</td>
                            <td className="py-2 px-3 text-sm text-gray-700">{item.name}</td>
                            <td className="py-2 px-3">
                              <span className={`badge ${
                                item.transaction_type === 'buy' ? 'badge-blue' : 'badge-red'
                              }`}>
                                {item.transaction_type.toUpperCase()}
                              </span>
                            </td>
                            <td className="py-2 px-3 text-right text-sm data-text">
                              {formatCurrency(item.total_amount)}
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan="4" className="py-4 px-3 text-center text-gray-500">
                            No trading history found
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Dashboard;