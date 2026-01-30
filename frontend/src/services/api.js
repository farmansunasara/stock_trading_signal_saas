import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  signup: (email, password) => 
    api.post('/auth/signup', { email, password }),
  
  login: (email, password) => 
    api.post('/auth/login', { email, password }),
  
  getMe: () => 
    api.get('/auth/me'),
};

// Billing API
export const billingAPI = {
  createCheckout: (successUrl, cancelUrl) => 
    api.post('/billing/create-checkout', { success_url: successUrl, cancel_url: cancelUrl }),
  
  getStatus: () => 
    api.get('/billing/status'),
};

// Signals API
export const signalsAPI = {
  getSignals: () => 
    api.get('/signals'),
};

export default api;
