import axios from 'axios';

// Dynamically resolve base URL via environment variable with local fallback
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach JWT token from localStorage to authorization headers
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('cipherpage_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor: Graceful handling of 401 Unauthorized token expirations
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      console.warn('Unauthorized access. Token expired or invalid.');
      
      // Clear sensitive data
      localStorage.removeItem('cipherpage_token');
      localStorage.removeItem('cipherpage_user_role');
      
      // Emit event for React state cleanup if needed
      window.dispatchEvent(new CustomEvent('unauthorized'));
      
      // Force redirect to login page
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);
