import axios from 'axios';

// Base API configuration
const api = axios.create({
  baseURL: '/api', // Base URL for all requests
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service object with methods for different endpoints
const apiService = {
  // Authentication endpoints
  auth: {
    register: (userData) => api.post('/auth/register', userData),
    login: (credentials) => api.post('/auth/login', credentials),
    logout: () => api.post('/auth/logout'),
  },
  
  // Stock data endpoints
  stocks: {
    getList: () => api.get('/stocks/list'),
    getData: (symbol, period) => api.get(`/stocks/data?symbol=${symbol}&period=${period}`),
    getCurrentPrice: (symbol) => api.get(`/stocks/price?symbol=${symbol}`),
    getOverview: (symbol) => api.get(`/stocks/overview?symbol=${symbol}`),
  },
  
  // Prediction endpoints
  prediction: {
    predict: (symbol, period) => api.get(`/prediction?symbol=${symbol}&period=${period}`),
    saveAnalysis: (data) => api.post('/prediction/save', data),
  },
  
  // Trading endpoints
  trading: {
    calculateTax: (data) => api.post('/trading/calculate-tax', data),
    calculateProfit: (data) => api.post('/trading/profit-potential', data),
    getBrokers: () => api.get('/trading/brokers'),
    executeTrade: (data) => api.post('/trading/execute', data),
  },
  
  // Portfolio endpoints
  portfolio: {
    get: () => api.get('/portfolio'),
  },
  
  // Watchlist endpoints
  watchlist: {
    get: () => api.get('/watchlist'),
    add: (symbol) => api.post('/watchlist/add', { symbol }),
    remove: (symbol) => api.post('/watchlist/remove', { symbol }),
  },
  
  // History endpoints
  history: {
    getAnalysis: (limit = 20) => api.get(`/history/analysis?limit=${limit}`),
    getTrading: (limit = 50) => api.get(`/history/trading?limit=${limit}`),
  },
};

export default apiService;