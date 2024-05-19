// src/services/api.js

import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  withCredentials: true, // This is important for CSRF protection
});

apiClient.interceptors.request.use((config) => {
  const token = document.cookie.match(/csrftoken=([^;]+)/)?.[1];
  if (token) {
    config.headers['X-CSRFToken'] = token;
  }
  return config;
});

export default apiClient;
