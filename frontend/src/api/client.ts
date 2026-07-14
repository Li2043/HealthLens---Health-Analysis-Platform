import axios from "axios";
import { notifyUnauthorized } from "../auth/sessionEvents";
import {
  clearAuthStorage,
  getToken,
} from "../auth/tokenStorage";
import { getApiBaseUrl } from "../utils/env";

export const apiClient = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30_000,
});

apiClient.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      const requestUrl = error.config?.url ?? "";
      const isAuthRequest =
        requestUrl.includes("/auth/login") || requestUrl.includes("/auth/register");

      if (!isAuthRequest) {
        clearAuthStorage();
        notifyUnauthorized();
      }
    }
    return Promise.reject(error);
  },
);