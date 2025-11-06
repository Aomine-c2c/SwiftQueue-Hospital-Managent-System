import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { useAuthStore } from '../stores/authStore';
import { useUIStore } from '../stores/uiStore';

class ApiClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = '/api') {
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL,
      timeout: 30000, // 30 seconds
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = useAuthStore.getState().token;
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        // Set loading state for mutations
        if (config.method !== 'get') {
          useUIStore.getState().setGlobalLoading(true);
        }

        return config;
      },
      (error) => {
        useUIStore.getState().setGlobalLoading(false);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        useUIStore.getState().setGlobalLoading(false);
        return response;
      },
      (error) => {
        useUIStore.getState().setGlobalLoading(false);

        // Handle authentication errors
        if (error.response?.status === 401) {
          useAuthStore.getState().logout();
          useUIStore.getState().addNotification({
            type: 'error',
            title: 'Session Expired',
            message: 'Please log in again.',
          });
        }

        // Handle other errors
        if (error.response?.status >= 500) {
          useUIStore.getState().addNotification({
            type: 'error',
            title: 'Server Error',
            message: 'Something went wrong. Please try again.',
          });
        }

        // Handle network errors
        if (!error.response) {
          useUIStore.getState().addNotification({
            type: 'error',
            title: 'Network Error',
            message: 'Please check your connection and try again.',
          });
        }

        return Promise.reject(error);
      }
    );
  }

  // Generic request methods
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.get(url, config);
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.post(url, data, config);
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.put(url, data, config);
  }

  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.patch(url, data, config);
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.delete(url, config);
  }

  // Specialized methods for common operations

  // Auth methods
  async login(credentials: { email: string; password: string }) {
    const response = await this.post('/auth/login', credentials);
    const { user, access_token } = response.data;

    useAuthStore.getState().login(user, access_token);

    useUIStore.getState().addNotification({
      type: 'success',
      title: 'Login Successful',
      message: `Welcome back, ${user.name}!`,
    });

    return response;
  }

  async logout() {
    try {
      await this.post('/auth/logout');
    } catch (error) {
      // Ignore logout errors
    } finally {
      useAuthStore.getState().logout();
      useUIStore.getState().addNotification({
        type: 'info',
        title: 'Logged Out',
        message: 'You have been successfully logged out.',
      });
    }
  }

  async register(userData: any) {
    const response = await this.post('/auth/register', userData);
    useUIStore.getState().addNotification({
      type: 'success',
      title: 'Registration Successful',
      message: 'Your account has been created. Please log in.',
    });
    return response;
  }

  // Queue methods
  async joinQueue(queueData: any) {
    const response = await this.post('/queue/join', queueData);
    useUIStore.getState().addNotification({
      type: 'success',
      title: 'Joined Queue',
      message: 'You have been added to the queue.',
    });
    return response;
  }

  async getQueueStatus() {
    return this.get('/queue/status');
  }

  // Appointment methods
  async getAppointments(filters?: any) {
    const params = filters ? { params: filters } : {};
    return this.get('/appointments', params);
  }

  async createAppointment(appointmentData: any) {
    const response = await this.post('/appointments', appointmentData);
    useUIStore.getState().addNotification({
      type: 'success',
      title: 'Appointment Created',
      message: 'Your appointment has been scheduled.',
    });
    return response;
  }

  // Telemedicine methods
  async createTelemedicineSession(sessionData: any) {
    const response = await this.post('/telemedicine/sessions', sessionData);
    useUIStore.getState().addNotification({
      type: 'success',
      title: 'Session Created',
      message: 'Telemedicine session has been scheduled.',
    });
    return response;
  }

  async getTelemedicineSessions() {
    return this.get('/telemedicine/sessions');
  }

  async startTelemedicineSession(sessionId: string) {
    const response = await this.post(`/telemedicine/sessions/${sessionId}/start`);
    useUIStore.getState().addNotification({
      type: 'success',
      title: 'Session Started',
      message: 'Telemedicine session is now active.',
    });
    return response;
  }

  // File upload method
  async uploadFile(file: File, endpoint: string, onProgress?: (progress: number) => void) {
    const formData = new FormData();
    formData.append('file', file);

    const config: AxiosRequestConfig = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    };

    if (onProgress) {
      config.onUploadProgress = (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total!);
        onProgress(percentCompleted);
      };
    }

    const response = await this.post(endpoint, formData, config);
    useUIStore.getState().addNotification({
      type: 'success',
      title: 'Upload Successful',
      message: 'File has been uploaded successfully.',
    });
    return response;
  }
}

// Create and export singleton instance
export const apiClient = new ApiClient();

// Export the class for testing purposes
export { ApiClient };