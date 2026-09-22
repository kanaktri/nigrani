import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api/v1",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("dosje_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// A 401 anywhere means the token is gone/expired - bounce to login rather
// than let the UI sit in a half-authenticated state showing stale data.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("dosje_token");
      localStorage.removeItem("dosje_user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);
