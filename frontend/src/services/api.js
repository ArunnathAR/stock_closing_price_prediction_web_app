import axios from 'axios';

// Create axios instance with base URL from environment
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add interceptor to include auth token in requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.params = { ...config.params, token };
  }
  return config;
});

// Authentication API
export const authAPI = {
  register: (userData) => api.post('/api/auth/register', userData),
  login: (userData) => api.post('/api/auth/login', userData),
  logout: () => api.post('/api/auth/logout'),
};

// Stock data API
export const stockAPI = {
  getStockList: () => api.get('/api/stocks/list'),
  getStockData: (symbol, period = '1month') => 
    api.get(`/api/stocks/data?symbol=${symbol}&period=${period}`),
  getCurrentPrice: (symbol) => api.get(`/api/stocks/price?symbol=${symbol}`),
  getStockOverview: (symbol) => api.get(`/api/stocks/overview?symbol=${symbol}`),
};

// Prediction API
export const predictionAPI = {
  getPrediction: (symbol, period = '1month') => 
    api.get(`/api/prediction?symbol=${symbol}&period=${period}`),
  saveAnalysis: (analysisData) => api.post('/api/prediction/save', analysisData),
};

// Trading API
export const tradingAPI = {
  calculateTax: (tradingData) => api.post('/api/trading/calculate-tax', tradingData),
  calculateProfit: (tradingData) => api.post('/api/trading/profit-potential', tradingData),
  getBrokers: () => api.get('/api/trading/brokers'),
  executeTrade: (tradingData) => api.post('/api/trading/execute', tradingData),
};

// Portfolio API
export const portfolioAPI = {
  getPortfolio: () => api.get('/api/portfolio'),
  getWatchlist: () => api.get('/api/watchlist'),
  addToWatchlist: (symbol) => api.post('/api/watchlist/add', { symbol }),
  removeFromWatchlist: (symbol) => api.post('/api/watchlist/remove', { symbol }),
};

// History API
export const historyAPI = {
  getAnalysisHistory: (limit = 20) => api.get(`/api/history/analysis?limit=${limit}`),
  getTradingHistory: (limit = 50) => api.get(`/api/history/trading?limit=${limit}`),
};

export default api;