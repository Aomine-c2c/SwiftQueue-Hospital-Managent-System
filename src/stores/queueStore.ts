import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface QueueItem {
  id: string;
  patient_id: string;
  patient_name: string;
  service_id: string;
  service_name: string;
  priority: 'emergency' | 'urgent' | 'normal' | 'low';
  status: 'waiting' | 'in-progress' | 'completed' | 'cancelled';
  estimated_wait_time: number;
  check_in_time: string;
  notes?: string;
}

interface QueueState {
  queues: QueueItem[];
  selectedQueue: QueueItem | null;
  filterStatus: string;
  sortBy: 'priority' | 'wait_time' | 'check_in_time';
  isLoading: boolean;
  
  // Actions
  setQueues: (queues: QueueItem[]) => void;
  addQueue: (queue: QueueItem) => void;
  updateQueue: (id: string, updates: Partial<QueueItem>) => void;
  removeQueue: (id: string) => void;
  selectQueue: (queue: QueueItem | null) => void;
  setFilterStatus: (status: string) => void;
  setSortBy: (sortBy: 'priority' | 'wait_time' | 'check_in_time') => void;
  setLoading: (loading: boolean) => void;
  
  // Computed
  getFilteredQueues: () => QueueItem[];
  getQueuesByPriority: (priority: string) => QueueItem[];
}

export const useQueueStore = create<QueueState>()(
  devtools(
    (set, get) => ({
      queues: [],
      selectedQueue: null,
      filterStatus: 'all',
      sortBy: 'priority',
      isLoading: false,

      setQueues: (queues) => set({ queues }, false, 'setQueues'),
      
      addQueue: (queue) => 
        set((state) => ({ 
          queues: [...state.queues, queue] 
        }), false, 'addQueue'),
      
      updateQueue: (id, updates) =>
        set((state) => ({
          queues: state.queues.map((q) => 
            q.id === id ? { ...q, ...updates } : q
          ),
          selectedQueue: state.selectedQueue?.id === id 
            ? { ...state.selectedQueue, ...updates } 
            : state.selectedQueue
        }), false, 'updateQueue'),
      
      removeQueue: (id) =>
        set((state) => ({
          queues: state.queues.filter((q) => q.id !== id),
          selectedQueue: state.selectedQueue?.id === id ? null : state.selectedQueue
        }), false, 'removeQueue'),
      
      selectQueue: (queue) => set({ selectedQueue: queue }, false, 'selectQueue'),
      
      setFilterStatus: (status) => set({ filterStatus: status }, false, 'setFilterStatus'),
      
      setSortBy: (sortBy) => set({ sortBy }, false, 'setSortBy'),
      
      setLoading: (loading) => set({ isLoading: loading }, false, 'setLoading'),
      
      getFilteredQueues: () => {
        const { queues, filterStatus, sortBy } = get();
        let filtered = queues;
        
        if (filterStatus !== 'all') {
          filtered = queues.filter((q) => q.status === filterStatus);
        }
        
        return filtered.sort((a, b) => {
          if (sortBy === 'priority') {
            const priorityOrder = { emergency: 0, urgent: 1, normal: 2, low: 3 };
            return priorityOrder[a.priority] - priorityOrder[b.priority];
          } else if (sortBy === 'wait_time') {
            return a.estimated_wait_time - b.estimated_wait_time;
          } else {
            return new Date(a.check_in_time).getTime() - new Date(b.check_in_time).getTime();
          }
        });
      },
      
      getQueuesByPriority: (priority) => {
        const { queues } = get();
        return queues.filter((q) => q.priority === priority);
      }
    }),
    { name: 'QueueStore' }
  )
);
