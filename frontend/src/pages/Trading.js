import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell
} from 'recharts';
import apiService from '../services/api';

const Trading = () => {
  const location = useLocation();
  const [stocksList, setStocksList] = useState([]);
  const [selectedStock, setSelectedStock] = useState('');
  const [currentPrice, setCurrentPrice] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [transactionType, setTransactionType] = useState('buy');
  const [taxInfo, setTaxInfo] = useState(null);
  const [profitInfo, setProfitInfo] = useState(null);
  const [brokers, setBrokers] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [tradingHistory, setTradingHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [isShortTerm, setIsShortTerm] = useState(true);

  // Initialize from navigation state if available
  useEffect(() => {
    if (location.state?.symbol) {
      setSelectedStock(location.state.symbol);
      if (location.state.currentPrice) {
        setCurrentPrice(location.state.currentPrice);
      }
    }
  }, [location]);

  // Fetch stock list and broker info on component mount
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        setLoading(true);
        
        // Fetch stocks list
        const stocksResponse = await apiService.stocks.getList();
        setStocksList(stocksResponse.data.stocks);
        
        // Fetch brokers
        const brokersResponse = await apiService.trading.getBrokers();
        setBrokers(brokersResponse.data.brokers);
        
        // Fetch trading history
        const historyResponse = await apiService.history.getTrading();
        setTradingHistory(historyResponse.data.history);
        
        if (selectedStock && !currentPrice) {
          // Fetch current price if not already set
          fetchStockPrice(selectedStock);
        }
      } catch (error) {
        setError('Failed to load initial data');
        console.error('Error fetching initial data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchInitialData();
  }, []);

  // Update price when stock changes
  useEffect(() => {
    if (selectedStock) {
      fetchStockPrice(selectedStock);
    } else {
      setCurrentPrice(null);
      setTaxInfo(null);
      setProfitInfo(null);
    }
  }, [selectedStock]);

  // Calculate tax when price, quantity, or transaction type changes
  useEffect(() => {
    if (selectedStock && currentPrice && quantity > 0) {
      calculateTax();
      if (transactionType === 'buy') {
        calculateProfitPotential();
      } else {
        setProfitInfo(null);
      }
    }
  }, [selectedStock, currentPrice, quantity, transactionType, isShortTerm]);

  // Fetch current price of a stock
  const fetchStockPrice = async (symbol) => {
    try {
      setLoading(true);
      const response = await apiService.stocks.getCurrentPrice(symbol);
      setCurrentPrice(response.data.price);
    } catch (error) {
      setError(`Failed to fetch current price for ${symbol}`);
      console.error('Error fetching price:', error);
    } finally {
      setLoading(false);
    }
  };

  // Handle stock selection
  const handleStockChange = (e) => {
    setSelectedStock(e.target.value);
    setSuccessMessage('');
  };

  // Handle quantity change
  const handleQuantityChange = (e) => {
    const value = parseInt(e.target.value);
    setQuantity(value > 0 ? value : 1);
    setSuccessMessage('');
  };

  // Handle transaction type change
  const handleTransactionTypeChange = (e) => {
    setTransactionType(e.target.value);
    setSuccessMessage('');
  };

  // Handle investment type change
  const handleInvestmentTypeChange = (e) => {
    setIsShortTerm(e.target.value === 'short');
    setSuccessMessage('');
  };

  // Calculate taxes for the transaction
  const calculateTax = async () => {
    try {
      const response = await apiService.trading.calculateTax({
        symbol: selectedStock,
        transaction_type: transactionType,
        quantity: quantity,
        price: currentPrice,
        is_short_term: isShortTerm
      });
      
      setTaxInfo(response.data);
    } catch (error) {
      console.error('Error calculating tax:', error);
    }
  };

  // Calculate potential profit
  const calculateProfitPotential = async () => {
    try {
      const response = await apiService.trading.calculateProfit({
        symbol: selectedStock,
        transaction_type: 'buy',
        quantity: quantity,
        price: currentPrice,
        is_short_term: isShortTerm
      });
      
      setProfitInfo(response.data);
    } catch (error) {
      console.error('Error calculating profit potential:', error);
    }
  };

  // Execute a trade
  const executeTrade = async () => {
    if (!selectedStock || !currentPrice || quantity <= 0) {
      setError('Please select a stock and enter a valid quantity');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      const response = await apiService.trading.executeTrade({
        symbol: selectedStock,
        transaction_type: transactionType,
        quantity: quantity,
        price: currentPrice,
        is_short_term: isShortTerm
      });
      
      if (response.data.success) {
        setSuccessMessage(`${transactionType.toUpperCase()} transaction executed successfully!`);
        
        // Refresh trading history
        const historyResponse = await apiService.history.getTrading();
        setTradingHistory(historyResponse.data.history);
      }
    } catch (error) {
      setError('Failed to execute trade');
      console.error('Error executing trade:', error);
    } finally {
      setLoading(false);
    }
  };

  // Format currency display
  const formatCurrency = (value) => {
    return `₹${value.toFixed(2)}`;
  };

  // Format percentage display
  const formatPercentage = (value) => {
    return `${value.toFixed(2)}%`;
  };

  // Get tax breakdown for pie chart
  const getTaxBreakdownData = () => {
    if (!taxInfo) return [];
    
    const breakdown = [];
    
    if (taxInfo.stt_amount > 0) {
      breakdown.push({ name: 'STT', value: taxInfo.stt_amount });
    }
    
    if (taxInfo.transaction_charges > 0) {
      breakdown.push({ name: 'Transaction Charges', value: taxInfo.transaction_charges });
    }
    
    if (taxInfo.gst_amount > 0) {
      breakdown.push({ name: 'GST', value: taxInfo.gst_amount });
    }
    
    if (taxInfo.sebi_charges > 0) {
      breakdown.push({ name: 'SEBI Charges', value: taxInfo.sebi_charges });
    }
    
    if (taxInfo.stamp_duty > 0) {
      breakdown.push({ name: 'Stamp Duty', value: taxInfo.stamp_duty });
    }
    
    return breakdown;
  };

  // Colors for pie chart
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  return (
    <div className="flex flex-col space-y-6">
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">
          Trading Interface
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
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
            
            {currentPrice && (
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">
                  Current Price
                </h3>
                <div className="p-4 bg-gray-100 rounded-md">
                  <span className="text-2xl font-bold data-text">
                    {formatCurrency(currentPrice)}
                  </span>
                </div>
              </div>
            )}
            
            <div>
              <label htmlFor="quantity" className="label">
                Quantity
              </label>
              <input
                id="quantity"
                type="number"
                min="1"
                className="input"
                value={quantity}
                onChange={handleQuantityChange}
                disabled={loading}
              />
            </div>
            
            <div>
              <label className="label">Transaction Type</label>
              <div className="flex space-x-4">
                <label className="inline-flex items-center">
                  <input
                    type="radio"
                    className="form-radio"
                    name="transactionType"
                    value="buy"
                    checked={transactionType === 'buy'}
                    onChange={handleTransactionTypeChange}
                    disabled={loading}
                  />
                  <span className="ml-2">Buy</span>
                </label>
                <label className="inline-flex items-center">
                  <input
                    type="radio"
                    className="form-radio"
                    name="transactionType"
                    value="sell"
                    checked={transactionType === 'sell'}
                    onChange={handleTransactionTypeChange}
                    disabled={loading}
                  />
                  <span className="ml-2">Sell</span>
                </label>
              </div>
            </div>
            
            <div>
              <label className="label">Investment Type</label>
              <div className="flex space-x-4">
                <label className="inline-flex items-center">
                  <input
                    type="radio"
                    className="form-radio"
                    name="investmentType"
                    value="short"
                    checked={isShortTerm}
                    onChange={handleInvestmentTypeChange}
                    disabled={loading}
                  />
                  <span className="ml-2">Short-term (&lt; 1 year)</span>
                </label>
                <label className="inline-flex items-center">
                  <input
                    type="radio"
                    className="form-radio"
                    name="investmentType"
                    value="long"
                    checked={!isShortTerm}
                    onChange={handleInvestmentTypeChange}
                    disabled={loading}
                  />
                  <span className="ml-2">Long-term (&gt; 1 year)</span>
                </label>
              </div>
            </div>
            
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
            
            <button
              onClick={executeTrade}
              className={`btn w-full py-2 ${
                transactionType === 'buy' ? 'btn-primary' : 'btn-danger'
              }`}
              disabled={loading || !selectedStock || !currentPrice}
            >
              {loading ? 'Processing...' : `${transactionType === 'buy' ? 'Buy' : 'Sell'} ${selectedStock ? selectedStock.split('.')[0] : 'Stock'}`}
            </button>
          </div>
          
          <div className="space-y-4">
            {taxInfo && (
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">
                  Transaction Summary
                </h3>
                <div className="bg-gray-100 rounded-md p-4 space-y-2">
                  <div className="flex justify-between">
                    <span>Stock Value:</span>
                    <span className="font-semibold">{formatCurrency(taxInfo.stock_value)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Total Taxes & Charges:</span>
                    <span className="font-semibold">{formatCurrency(taxInfo.total_tax)}</span>
                  </div>
                  <div className="border-t border-gray-300 my-2 pt-2 flex justify-between">
                    <span className="font-bold">Total Amount:</span>
                    <span className="font-bold">{formatCurrency(taxInfo.total_amount)}</span>
                  </div>
                </div>
                
                <div className="mt-4">
                  <h4 className="font-semibold text-gray-800 mb-2">
                    Tax Breakdown
                  </h4>
                  <div className="h-40">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={getTaxBreakdownData()}
                          cx="50%"
                          cy="50%"
                          outerRadius={60}
                          fill="#8884d8"
                          dataKey="value"
                          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                        >
                          {getTaxBreakdownData().map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value) => formatCurrency(value)} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            )}
            
            {profitInfo && transactionType === 'buy' && (
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">
                  Profit Potential
                </h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full bg-white">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="py-2 px-2 text-left text-xs font-medium text-gray-700">Period</th>
                        <th className="py-2 px-2 text-right text-xs font-medium text-gray-700">Predicted Price</th>
                        <th className="py-2 px-2 text-right text-xs font-medium text-gray-700">Change</th>
                        <th className="py-2 px-2 text-right text-xs font-medium text-gray-700">Potential Profit</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(profitInfo).map(([period, data]) => (
                        <tr key={period} className="border-b">
                          <td className="py-2 px-2 text-sm">{period}</td>
                          <td className="py-2 px-2 text-right text-sm">
                            {formatCurrency(data.predicted_price)}
                          </td>
                          <td className={`py-2 px-2 text-right text-sm ${
                            data.price_change_percentage >= 0 ? 'text-green-600' : 'text-red-500'
                          }`}>
                            {formatPercentage(data.price_change_percentage)}
                          </td>
                          <td className={`py-2 px-2 text-right text-sm ${
                            data.profit_details.net_profit >= 0 ? 'text-green-600' : 'text-red-500'
                          }`}>
                            {formatCurrency(data.profit_details.net_profit)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold text-gray-800">
            Trading History
          </h3>
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="btn btn-neutral text-sm"
          >
            {showHistory ? 'Hide History' : 'Show History'}
          </button>
        </div>
        
        {showHistory && (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white">
              <thead className="bg-gray-100">
                <tr>
                  <th className="py-2 px-4 text-left text-sm font-medium text-gray-700">Date</th>
                  <th className="py-2 px-4 text-left text-sm font-medium text-gray-700">Stock</th>
                  <th className="py-2 px-4 text-left text-sm font-medium text-gray-700">Type</th>
                  <th className="py-2 px-4 text-right text-sm font-medium text-gray-700">Quantity</th>
                  <th className="py-2 px-4 text-right text-sm font-medium text-gray-700">Price</th>
                  <th className="py-2 px-4 text-right text-sm font-medium text-gray-700">Total</th>
                </tr>
              </thead>
              <tbody>
                {tradingHistory.length > 0 ? (
                  tradingHistory.map((item) => (
                    <tr key={item.id} className="border-b">
                      <td className="py-2 px-4 text-sm text-gray-700">{item.date}</td>
                      <td className="py-2 px-4 text-sm text-gray-700">{item.name}</td>
                      <td className="py-2 px-4">
                        <span className={`badge ${
                          item.transaction_type === 'buy' ? 'badge-blue' : 'badge-red'
                        }`}>
                          {item.transaction_type.toUpperCase()}
                        </span>
                      </td>
                      <td className="py-2 px-4 text-right text-sm text-gray-700">{item.quantity}</td>
                      <td className="py-2 px-4 text-right text-sm data-text">{formatCurrency(item.price)}</td>
                      <td className="py-2 px-4 text-right text-sm font-semibold data-text">{formatCurrency(item.total_amount)}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="6" className="py-4 px-4 text-center text-gray-500">
                      No trading history found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
      
      <div className="card">
        <h3 className="text-xl font-bold text-gray-800 mb-4">
          Recommended Brokers
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {brokers.map((broker, index) => (
            <div key={index} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
              <h4 className="text-lg font-semibold text-gray-800 mb-2">{broker.name}</h4>
              <p className="text-sm text-gray-600 mb-2">{broker.description}</p>
              <div className="mb-2">
                <span className="text-xs font-semibold text-gray-700">Brokerage:</span>
                <span className="text-xs text-gray-700 ml-1">{broker.brokerage}</span>
              </div>
              <a
                href={broker.website}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 text-sm"
              >
                Visit Website →
              </a>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Trading;