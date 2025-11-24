/**
 * Axios instance configured for API requests with credentials
 * This ensures cookies (JWT tokens) are sent with all requests
 */
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { updateActivity, clearAuth } from './auth';

// Support both NEXT_PUBLIC_BACKEND_URL and NEXT_PUBLIC_API_BASE for flexibility
const API_BASE =
  (process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_BASE)?.replace(/\/$/, '') ?? 'http://localhost:8000';

// Create axios instance with credentials enabled
export const apiClient = axios.create({
  baseURL: API_BASE,
  withCredentials: true, // Important: Send cookies with all requests
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor to handle token refresh on 401 errors
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: any) => void;
  reject: (error?: any) => void;
}> = [];

const processQueue = (error: AxiosError | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  
  failedQueue = [];
};

apiClient.interceptors.response.use(
  (response) => {
    // Update activity on successful API calls
    updateActivity();
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Helper function to clear auth and redirect to login
    const handleUnauthorized = () => {
      if (typeof window !== 'undefined') {
        // Clear all auth tokens and sessions
        clearAuth();
        // Clear user info cache if it exists
        localStorage.removeItem('user_info');
        // Set flag to show session expired message
        sessionStorage.setItem('authExpired', 'true');
        // Redirect to auth page
        window.location.href = '/auth';
      }
    };

    // If error is 401
    if (error.response?.status === 401) {
      const requestUrl = originalRequest?.url || '';
      
      // If the request is to /auth/refresh or /auth/me, don't try to refresh
      // Just clear auth and redirect (these endpoints returning 401 means session is expired)
      if (requestUrl.includes('/auth/refresh') || requestUrl.includes('/auth/me')) {
        handleUnauthorized();
        return Promise.reject(error);
      }

      // For other endpoints, try to refresh token if we haven't tried yet
      if (!originalRequest._retry) {
        if (isRefreshing) {
          // If already refreshing, queue this request
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject });
          })
            .then((token) => {
              if (originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${token}`;
              }
              return apiClient(originalRequest);
            })
            .catch((err) => {
              return Promise.reject(err);
            });
        }

        originalRequest._retry = true;
        isRefreshing = true;

        try {
          // Try to refresh the token using apiClient to ensure baseURL is used
          const response = await apiClient.post(
            '/auth/refresh',
            {}
          );

          if (response.status === 200) {
            processQueue(null, null);
            // Retry the original request
            return apiClient(originalRequest);
          }
        } catch (refreshError) {
          processQueue(refreshError as AxiosError, null);
          // If refresh fails, clear auth and redirect to login
          handleUnauthorized();
          return Promise.reject(refreshError);
        } finally {
          isRefreshing = false;
        }
      } else {
        // Already tried to refresh and still got 401, clear auth and redirect
        handleUnauthorized();
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
export { API_BASE };

