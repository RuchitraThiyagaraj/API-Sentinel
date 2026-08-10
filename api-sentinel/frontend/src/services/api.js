/**
 * services/api.js
 * ----------------
 * Single Axios instance shared by the whole app.
 *
 * - baseURL points at the FastAPI backend.
 * - An interceptor automatically attaches the JWT (from localStorage)
 *   to every outgoing request, so individual pages don't have to.
 */

import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
