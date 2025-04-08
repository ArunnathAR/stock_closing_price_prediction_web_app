import axios from 'axios';

// Create API base URL
const API_URL = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:5000';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to request if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// API endpoints
export const authAPI = {
  login: (username, password) => api.post('/api/auth/login', { username, password }),
  register: (username, email, password) => api.post('/api/auth/register', { username, email, password }),
  logout: () => api.post('/api/auth/logout'),
};

export const stockAPI = {
  getStockList: () => api.get('/api/stocks/list'),
  getStockData: (symbol, period) => api.get(`/api/stocks/data?symbol=${symbol}&period=${period}`),
  getCurrentPrice: (symbol) => api.get(`/api/stocks/price?symbol=${symbol}`),
  getStockOverview: (symbol) => api.get(`/api/stocks/overview?symbol=${symbol}`),
};

export const predictionAPI = {
  predictStockPrice: (symbol, period) => api.get(`/api/prediction?symbol=${symbol}&period=${period}`),
  saveAnalysis: (analysis) => api.post('/api/prediction/save', analysis),
};

export const tradingAPI = {
  calculateTax: (data) => api.post('/api/trading/calculate-tax', data),
  calculateProfit: (data) => api.post('/api/trading/profit-potential', data),
  getBrokers: () => api.get('/api/trading/brokers'),
  executeTrade: (data) => api.post('/api/trading/execute', data),
};

export const portfolioAPI = {
  getPortfolio: () => api.get('/api/portfolio'),
  getWatchlist: () => api.get('/api/watchlist'),
  addToWatchlist: (symbol) => api.post('/api/watchlist/add', { symbol }),
  removeFromWatchlist: (symbol) => api.post('/api/watchlist/remove', { symbol }),
};

export const historyAPI = {
  getAnalysisHistory: (limit = 20) => api.get(`/api/history/analysis?limit=${limit}`),
  getTradingHistory: (limit = 50) => api.get(`/api/history/trading?limit=${limit}`),
};

export default api;