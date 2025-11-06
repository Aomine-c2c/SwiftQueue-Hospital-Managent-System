import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 10, // 10 minutes (formerly cacheTime)
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors
        if (error?.status >= 400 && error?.status < 500) {
          return false;
        }
        // Retry up to 3 times for other errors
        return failureCount < 3;
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
    mutations: {
      retry: 1,
      onError: (error: any) => {
        console.error('Mutation error:', error);
      },
    },
  },
});

// Query keys for consistent caching
export const queryKeys = {
  // Auth
  auth: {
    user: ['auth', 'user'] as const,
    profile: ['auth', 'profile'] as const,
  },

  // Appointments
  appointments: {
    all: ['appointments'] as const,
    lists: () => [...queryKeys.appointments.all, 'list'] as const,
    list: (filters: Record<string, any>) => [...queryKeys.appointments.lists(), filters] as const,
    details: () => [...queryKeys.appointments.all, 'detail'] as const,
    detail: (id: number) => [...queryKeys.appointments.details(), id] as const,
  },

  // Queue
  queue: {
    all: ['queue'] as const,
    status: ['queue', 'status'] as const,
    entries: ['queue', 'entries'] as const,
    analytics: ['queue', 'analytics'] as const,
  },

  // Telemedicine
  telemedicine: {
    all: ['telemedicine'] as const,
    sessions: () => [...queryKeys.telemedicine.all, 'sessions'] as const,
    session: (id: string) => [...queryKeys.telemedicine.sessions(), id] as const,
    messages: (sessionId: string) => [...queryKeys.telemedicine.all, 'messages', sessionId] as const,
    waitingRoom: (sessionId: string) => [...queryKeys.telemedicine.all, 'waiting-room', sessionId] as const,
    history: ['telemedicine', 'history'] as const,
  },

  // Patients
  patients: {
    all: ['patients'] as const,
    lists: () => [...queryKeys.patients.all, 'list'] as const,
    list: (filters: Record<string, any>) => [...queryKeys.patients.lists(), filters] as const,
    details: () => [...queryKeys.patients.all, 'detail'] as const,
    detail: (id: number) => [...queryKeys.patients.details(), id] as const,
    history: (id: number) => [...queryKeys.patients.detail(id), 'history'] as const,
  },

  // Staff
  staff: {
    all: ['staff'] as const,
    lists: () => [...queryKeys.staff.all, 'list'] as const,
    list: (filters: Record<string, any>) => [...queryKeys.staff.lists(), filters] as const,
    details: () => [...queryKeys.staff.all, 'detail'] as const,
    detail: (id: number) => [...queryKeys.staff.details(), id] as const,
  },

  // Analytics
  analytics: {
    all: ['analytics'] as const,
    dashboard: ['analytics', 'dashboard'] as const,
    reports: ['analytics', 'reports'] as const,
    queue: ['analytics', 'queue'] as const,
    telemedicine: ['analytics', 'telemedicine'] as const,
  },

  // Prescriptions
  prescriptions: {
    all: ['prescriptions'] as const,
    lists: () => [...queryKeys.prescriptions.all, 'list'] as const,
    list: (filters: Record<string, any>) => [...queryKeys.prescriptions.lists(), filters] as const,
    details: () => [...queryKeys.prescriptions.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.prescriptions.details(), id] as const,
  },

  // Inventory
  inventory: {
    all: ['inventory'] as const,
    items: ['inventory', 'items'] as const,
    suppliers: ['inventory', 'suppliers'] as const,
    movements: ['inventory', 'movements'] as const,
    orders: ['inventory', 'orders'] as const,
  },
};