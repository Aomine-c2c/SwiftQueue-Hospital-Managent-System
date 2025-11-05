import { create } from 'zustand';

interface NotificationItem {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
  timestamp: number;
}

interface ModalState {
  isOpen: boolean;
  type: string | null;
  data: any;
}

interface UIState {
  // Theme
  theme: 'light' | 'dark' | 'system';
  sidebarOpen: boolean;

  // Notifications
  notifications: NotificationItem[];

  // Modals
  modal: ModalState;

  // Loading states
  globalLoading: boolean;
  loadingStates: Record<string, boolean>;

  // Navigation
  currentPage: string;
  breadcrumbs: Array<{ label: string; path?: string }>;

  // Actions
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;

  // Notifications
  addNotification: (notification: Omit<NotificationItem, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;

  // Modals
  openModal: (type: string, data?: any) => void;
  closeModal: () => void;

  // Loading
  setGlobalLoading: (loading: boolean) => void;
  setLoadingState: (key: string, loading: boolean) => void;

  // Navigation
  setCurrentPage: (page: string) => void;
  setBreadcrumbs: (breadcrumbs: Array<{ label: string; path?: string }>) => void;
}

export const useUIStore = create<UIState>((set, get) => ({
  // Initial state
  theme: 'system',
  sidebarOpen: true,
  notifications: [],
  modal: {
    isOpen: false,
    type: null,
    data: null,
  },
  globalLoading: false,
  loadingStates: {},
  currentPage: '',
  breadcrumbs: [],

  // Theme actions
  setTheme: (theme) => set({ theme }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),

  // Notification actions
  addNotification: (notification) => {
    const id = Date.now().toString();
    const newNotification: NotificationItem = {
      ...notification,
      id,
      timestamp: Date.now(),
    };

    set((state) => ({
      notifications: [...state.notifications, newNotification],
    }));

    // Auto-remove notification after duration
    if (notification.duration !== 0) {
      setTimeout(() => {
        get().removeNotification(id);
      }, notification.duration || 5000);
    }
  },

  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),

  clearNotifications: () => set({ notifications: [] }),

  // Modal actions
  openModal: (type, data = null) =>
    set({
      modal: {
        isOpen: true,
        type,
        data,
      },
    }),

  closeModal: () =>
    set({
      modal: {
        isOpen: false,
        type: null,
        data: null,
      },
    }),

  // Loading actions
  setGlobalLoading: (loading) => set({ globalLoading: loading }),

  setLoadingState: (key, loading) =>
    set((state) => ({
      loadingStates: {
        ...state.loadingStates,
        [key]: loading,
      },
    })),

  // Navigation actions
  setCurrentPage: (page) => set({ currentPage: page }),

  setBreadcrumbs: (breadcrumbs) => set({ breadcrumbs }),
}));

// Selectors
export const useTheme = () => useUIStore((state) => state.theme);
export const useSidebarOpen = () => useUIStore((state) => state.sidebarOpen);
export const useNotifications = () => useUIStore((state) => state.notifications);
export const useModal = () => useUIStore((state) => state.modal);
export const useGlobalLoading = () => useUIStore((state) => state.globalLoading);
export const useLoadingState = (key: string) => useUIStore((state) => state.loadingStates[key]);
export const useCurrentPage = () => useUIStore((state) => state.currentPage);
export const useBreadcrumbs = () => useUIStore((state) => state.breadcrumbs);
