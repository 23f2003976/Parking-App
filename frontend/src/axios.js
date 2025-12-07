import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 10000,
});

api.interceptors.request.use((config) => {
  const raw = localStorage.getItem('qm_auth');
  if (raw) {
    try {
      const { token } = JSON.parse(raw);
      if (token) config.headers['Authorization'] = `Bearer ${token}`;
    } catch (e) {}
  }
  return config;
});

export default api;
