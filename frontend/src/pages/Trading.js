import React, { useState, useEffect } from 'react';
import { stockAPI, tradingAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const Trading = () => {
  const [stockList, setStockList] = useState([]);
  const [selectedStock, setSelectedStock] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [transactionType, setTransactionType] = useState('buy');
  const [isShortTerm, setIsShortTerm] = useState(true);
  const [currentPrice, setCurrentPrice] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [taxDetails, setTaxDetails] = useState(null);
  const [profitDetails, setProfitDetails] = useState(null);
  const [brokers, setBrokers] = useState([]);
  const [success, setSuccess] = useState('');
  
  const { isAuthenticated } = useAuth();

  // Fetch stock list and brokers on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        const stocksResponse = await stockAPI.getStockList();
        setStockList(stocksResponse.data.stocks);
        
        const brokersResponse = await tradingAPI.getBrokers();
        setBrokers(brokersResponse.data.brokers);
      } catch (err) {
        console.error('Failed to fetch initial data', err);
        setError('Failed to load data. Please try again later.');
      }
    };

    fetchData();
  }, []);

  // Fetch current price when stock changes
  useEffect(() => {
    const fetchCurrentPrice = async () => {
      if (!selectedStock) return;
      
      try {
        const response = await stockAPI.getCurrentPrice(selectedStock);
        setCurrentPrice(response.data.price);
      } catch (err) {
        console.error('Failed to fetch current price', err);
        setError('Failed to load current price. Please try again later.');
      }
    };

    fetchCurrentPrice();
  }, [selectedStock]);

  // Calculate tax
  const handleCalculateTax = async () => {
    if (!selectedStock || !currentPrice) {
      setError('Please select a stock and ensure price is available');
      return;
    }

    setLoading(true);
    setError('');
    setTaxDetails(null);
    
    try {
      const tradingData = {
        symbol: selectedStock,
        transaction_type: transactionType,
        quantity: parseInt(quantity),
        price: currentPrice,
        is_short_term: isShortTerm
      };
      
      const response = await tradingAPI.calculateTax(tradingData);
      setTaxDetails(response.data);
    } catch (err) {
      console.error('Tax calculation failed', err);
      setError('Failed to calculate tax. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Calculate profit potential
  const handleCalculateProfit = async () => {
    if (!selectedStock || !currentPrice) {
      setError('Please select a stock and ensure price is available');
      return;
    }

    setLoading(true);
    setError('');
    setProfitDetails(null);
    
    try {
      const tradingData = {
        symbol: selectedStock,
        transaction_type: transactionType,
        quantity: parseInt(quantity),
        price: currentPrice
      };
      
      const response = await tradingAPI.calculateProfit(tradingData);
      setProfitDetails(response.data);
    } catch (err) {
      console.error('Profit calculation failed', err);
      setError('Failed to calculate potential profit. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Execute trade
  const handleExecuteTrade = async () => {
    if (!isAuthenticated()) {
      setError('Please log in to execute trades');
      return;
    }
    
    if (!selectedStock || !currentPrice) {
      setError('Please select a stock and ensure price is available');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      const tradingData = {
        symbol: selectedStock,
        transaction_type: transactionType,
        quantity: parseInt(quantity),
        price: currentPrice,
        is_short_term: isShortTerm
      };
      
      await tradingAPI.executeTrade(tradingData);
      setSuccess(`${transactionType === 'buy' ? 'Bought' : 'Sold'} ${quantity} shares of ${selectedStock} successfully!`);
      
      // Reset after successful trade
      setQuantity(1);
    } catch (err) {
      console.error('Trade execution failed', err);
      setError('Failed to execute trade. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Trading Simulation</h1>
      
      {/* Trading Form */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
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
            <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-1">
              Quantity
            </label>
            <input
              id="quantity"
              type="number"
              min="1"
              className="input-field"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
            />
          </div>
          
          <div>
            <label htmlFor="price" className="block text-sm font-medium text-gray-700 mb-1">
              Current Price
            </label>
            <div className="input-field bg-gray-100">
              {currentPrice ? `₹${currentPrice.toFixed(2)}` : 'Select a stock'}
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Transaction Type
            </label>
            <div className="flex">
              <button
                className={`px-4 py-2 border rounded-l-md ${
                  transactionType === 'buy'
                    ? 'bg-green-600 text-white border-green-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
                onClick={() => setTransactionType('buy')}
              >
                Buy
              </button>
              <button
                className={`px-4 py-2 border rounded-r-md ${
                  transactionType === 'sell'
                    ? 'bg-red-600 text-white border-red-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
                onClick={() => setTransactionType('sell')}
              >
                Sell
              </button>
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Holding Period
            </label>
            <div className="flex">
              <button
                className={`px-4 py-2 border rounded-l-md ${
                  isShortTerm
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
                onClick={() => setIsShortTerm(true)}
              >
                Short-term (&lt; 1 year)
              </button>
              <button
                className={`px-4 py-2 border rounded-r-md ${
                  !isShortTerm
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
                onClick={() => setIsShortTerm(false)}
              >
                Long-term (&gt; 1 year)
              </button>
            </div>
          </div>
        </div>
        
        <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4">
          <button
            onClick={handleCalculateTax}
            disabled={loading || !selectedStock}
            className={`btn-primary ${loading ? 'opacity-70 cursor-not-allowed' : ''}`}
          >
            Calculate Taxes
          </button>
          <button
            onClick={handleCalculateProfit}
            disabled={loading || !selectedStock}
            className={`btn-success ${loading ? 'opacity-70 cursor-not-allowed' : ''}`}
          >
            Calculate Profit Potential
          </button>
          {isAuthenticated() && (
            <button
              onClick={handleExecuteTrade}
              disabled={loading || !selectedStock}
              className={`btn-danger ${loading ? 'opacity-70 cursor-not-allowed' : ''}`}
            >
              Execute {transactionType === 'buy' ? 'Purchase' : 'Sale'}
            </button>
          )}
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
        
        {success && (
          <div className="mt-4 bg-green-50 border-l-4 border-green-500 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-green-500" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-green-700">{success}</p>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Tax Details */}
      {taxDetails && (
        <div className="bg-white p-6 rounded-lg shadow-md mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Tax Calculation</h2>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Item</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">Transaction Value</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">₹{taxDetails.transaction_value.toFixed(2)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">Securities Transaction Tax (STT)</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">₹{taxDetails.stt.toFixed(2)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">Exchange Transaction Charges</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">₹{taxDetails.exchange_charges.toFixed(2)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">GST</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">₹{taxDetails.gst.toFixed(2)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">SEBI Charges</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">₹{taxDetails.sebi_charges.toFixed(2)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">Stamp Duty</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">₹{taxDetails.stamp_duty.toFixed(2)}</td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Total Taxes & Charges</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">₹{taxDetails.total_tax.toFixed(2)}</td>
                </tr>
                <tr className="bg-blue-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-900">Net Amount</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-900">₹{taxDetails.net_amount.toFixed(2)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}
      
      {/* Profit Potential */}
      {profitDetails && (
        <div className="bg-white p-6 rounded-lg shadow-md mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Profit Potential</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-500">Current Price</p>
              <p className="text-2xl font-bold text-blue-600">₹{profitDetails.current_price.toFixed(2)}</p>
            </div>
            
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-500">Predicted Price</p>
              <p className="text-2xl font-bold text-green-600">₹{profitDetails.predicted_price.toFixed(2)}</p>
            </div>
            
            <div className={`p-4 rounded-lg ${
              profitDetails.profit_potential.estimated_profit > 0 ? 'bg-green-50' : 'bg-red-50'
            }`}>
              <p className="text-sm text-gray-500">Estimated Profit/Loss</p>
              <p className={`text-2xl font-bold ${
                profitDetails.profit_potential.estimated_profit > 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                ₹{profitDetails.profit_potential.estimated_profit.toFixed(2)}
              </p>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Item</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Value</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">Investment Amount</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">₹{profitDetails.profit_potential.investment_amount.toFixed(2)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">Expected Return</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">₹{profitDetails.profit_potential.expected_return.toFixed(2)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">Estimated Taxes</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">₹{profitDetails.profit_potential.estimated_tax.toFixed(2)}</td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Percentage Return</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {profitDetails.profit_potential.percentage_return.toFixed(2)}%
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}
      
      {/* Brokers */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Recommended Brokers</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {brokers.map((broker, index) => (
            <div key={index} className="border rounded-lg overflow-hidden">
              <div className="bg-gray-50 px-4 py-2 border-b">
                <h3 className="font-medium text-gray-900">{broker.name}</h3>
              </div>
              <div className="p-4">
                <p className="text-sm text-gray-600 mb-4">{broker.description}</p>
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Equity Delivery</span>
                    <span className="text-sm font-medium text-gray-900">{broker.charges.equity_delivery}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Equity Intraday</span>
                    <span className="text-sm font-medium text-gray-900">{broker.charges.equity_intraday}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Account Opening</span>
                    <span className="text-sm font-medium text-gray-900">{broker.charges.account_opening}</span>
                  </div>
                </div>
                <a 
                  href={broker.website} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  Visit Website →
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Login Prompt */}
      {!isAuthenticated() && (
        <div className="bg-blue-50 p-6 rounded-lg shadow-md mt-6">
          <h2 className="text-xl font-semibold text-blue-800 mb-2">Execute real trades</h2>
          <p className="text-blue-700 mb-4">
            Create an account or log in to execute simulated trades and track your portfolio.
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

export default Trading;