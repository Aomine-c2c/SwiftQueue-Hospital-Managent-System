import { QueryClient, DefaultOptions } from '@tanstack/react-query';

const queryConfig: DefaultOptions = {
  queries: {
    refetchOnWindowFocus: false,
    retry: 1,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
    refetchOnReconnect: true,
  },
  mutations: {
    retry: 0,
  },
};

export const queryClient = new QueryClient({
  defaultOptions: queryConfig,
});

// Query keys factory for type safety
export const queryKeys = {
  // Auth
  auth: {
    me: ['auth', 'me'] as const,
    session: ['auth', 'session'] as const,
  },
  // Queue
  queue: {
    all: ['queue'] as const,
    list: (filters?: Record<string, unknown>) => ['queue', 'list', filters] as const,
    detail: (id: string) => ['queue', 'detail', id] as const,
    stats: ['queue', 'stats'] as const,
  },
  // Patients
  patients: {
    all: ['patients'] as const,
    list: (filters?: Record<string, unknown>) => ['patients', 'list', filters] as const,
    detail: (id: string) => ['patients', 'detail', id] as const,
    history: (id: string) => ['patients', 'history', id] as const,
  },
  // Appointments
  appointments: {
    all: ['appointments'] as const,
    list: (filters?: Record<string, unknown>) => ['appointments', 'list', filters] as const,
    detail: (id: string) => ['appointments', 'detail', id] as const,
    upcoming: ['appointments', 'upcoming'] as const,
  },
  // Staff
  staff: {
    all: ['staff'] as const,
    list: (filters?: Record<string, unknown>) => ['staff', 'list', filters] as const,
    detail: (id: string) => ['staff', 'detail', id] as const,
    schedule: (id: string) => ['staff', 'schedule', id] as const,
  },
  // Analytics
  analytics: {
    dashboard: ['analytics', 'dashboard'] as const,
    waitTimes: (period?: string) => ['analytics', 'wait-times', period] as const,
    utilization: ['analytics', 'utilization'] as const,
  },
  // Notifications
  notifications: {
    all: ['notifications'] as const,
    unread: ['notifications', 'unread'] as const,
  },
} as const;
