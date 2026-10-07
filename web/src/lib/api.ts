import axios from 'axios';
import { useAuthStore } from '../store/authStore';

// Same-origin base URL: the Vite dev server proxies /api to the FastAPI
// backend (see vite.config.ts), so this works regardless of host/port.
const api = axios.create({
  baseURL: '/',
});

// Add a request interceptor to inject the JWT token
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add a response interceptor to handle 401s (token expired)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
    }
    return Promise.reject(error);
  }
);

export default api;
