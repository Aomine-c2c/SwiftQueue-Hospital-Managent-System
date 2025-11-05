import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '../lib/react-query';
import { useAuthStore } from '../stores/authStore';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api';

// Axios instance with interceptors
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = useAuthStore.getState().refreshToken;
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });
        
        const { access_token, refresh_token } = response.data;
        useAuthStore.getState().setTokens(access_token, refresh_token);
        
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        useAuthStore.getState().logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export { api };

// Queue Hooks
export const useQueues = (filters?: Record<string, unknown>) => {
  return useQuery({
    queryKey: queryKeys.queue.list(filters),
    queryFn: async () => {
      const { data } = await api.get('/queue', { params: filters });
      return data;
    },
  });
};

export const useQueue = (id: string) => {
  return useQuery({
    queryKey: queryKeys.queue.detail(id),
    queryFn: async () => {
      const { data } = await api.get(`/queue/${id}`);
      return data;
    },
    enabled: !!id,
  });
};

export const useCreateQueue = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (queueData: unknown) => {
      const { data } = await api.post('/queue', queueData);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.queue.all });
    },
  });
};

export const useUpdateQueue = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, updates }: { id: string; updates: unknown }) => {
      const { data } = await api.patch(`/queue/${id}`, updates);
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.queue.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.queue.all });
    },
  });
};

export const useDeleteQueue = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/queue/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.queue.all });
    },
  });
};

// Patient Hooks
export const usePatients = (filters?: Record<string, unknown>) => {
  return useQuery({
    queryKey: queryKeys.patients.list(filters),
    queryFn: async () => {
      const { data } = await api.get('/patients', { params: filters });
      return data;
    },
  });
};

export const usePatient = (id: string) => {
  return useQuery({
    queryKey: queryKeys.patients.detail(id),
    queryFn: async () => {
      const { data } = await api.get(`/patients/${id}`);
      return data;
    },
    enabled: !!id,
  });
};

// Appointment Hooks
export const useAppointments = (filters?: Record<string, unknown>) => {
  return useQuery({
    queryKey: queryKeys.appointments.list(filters),
    queryFn: async () => {
      const { data } = await api.get('/appointments', { params: filters });
      return data;
    },
  });
};

export const useCreateAppointment = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (appointmentData: unknown) => {
      const { data } = await api.post('/appointments', appointmentData);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.appointments.all });
    },
  });
};

// Analytics Hooks
export const useDashboardAnalytics = () => {
  return useQuery({
    queryKey: queryKeys.analytics.dashboard,
    queryFn: async () => {
      const { data } = await api.get('/analytics/dashboard');
      return data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

export const useWaitTimeAnalytics = (period?: string) => {
  return useQuery({
    queryKey: queryKeys.analytics.waitTimes(period),
    queryFn: async () => {
      const { data } = await api.get('/analytics/wait-times', { params: { period } });
      return data;
    },
  });
};
