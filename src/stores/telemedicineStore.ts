import { create } from 'zustand';

interface TelemedicineSession {
  session_id: string;
  patient_id: number;
  doctor_id: number;
  status: string;
  session_type: string;
  room_id: string;
  scheduled_start: string;
  actual_start?: string;
  actual_end?: string;
  duration_minutes?: number;
  chief_complaint?: string;
  diagnosis?: string;
  treatment_plan?: string;
  follow_up_instructions?: string;
  prescription_issued: boolean;
}

interface TelemedicineMessage {
  id: number;
  session_id: string;
  sender_id: number;
  content: string;
  message_type: string;
  sent_at: string;
  is_read: boolean;
}

interface WaitingRoomEntry {
  id: number;
  session_id: string;
  patient_id: number;
  joined_at: string;
  status: string;
  estimated_wait_minutes?: number;
}

interface TelemedicineState {
  // Current session
  activeSession: TelemedicineSession | null;
  sessionMessages: TelemedicineMessage[];
  waitingRoom: WaitingRoomEntry[];

  // UI state
  isVideoEnabled: boolean;
  isAudioEnabled: boolean;
  isConnected: boolean;
  isInWaitingRoom: boolean;

  // Session history
  sessionHistory: TelemedicineSession[];

  // Actions
  setActiveSession: (session: TelemedicineSession | null) => void;
  updateSessionStatus: (status: string) => void;
  addMessage: (message: TelemedicineMessage) => void;
  setMessages: (messages: TelemedicineMessage[]) => void;
  updateWaitingRoom: (waitingRoom: WaitingRoomEntry[]) => void;
  setVideoEnabled: (enabled: boolean) => void;
  setAudioEnabled: (enabled: boolean) => void;
  setConnected: (connected: boolean) => void;
  setInWaitingRoom: (inWaitingRoom: boolean) => void;
  setSessionHistory: (sessions: TelemedicineSession[]) => void;
  addToHistory: (session: TelemedicineSession) => void;

  // Reset
  reset: () => void;
}

const initialState = {
  activeSession: null,
  sessionMessages: [],
  waitingRoom: [],
  isVideoEnabled: false,
  isAudioEnabled: false,
  isConnected: false,
  isInWaitingRoom: false,
  sessionHistory: [],
};

export const useTelemedicineStore = create<TelemedicineState>((set, get) => ({
  ...initialState,

  setActiveSession: (session) => set({ activeSession: session }),

  updateSessionStatus: (status) =>
    set((state) => ({
      activeSession: state.activeSession
        ? { ...state.activeSession, status }
        : null,
    })),

  addMessage: (message) =>
    set((state) => ({
      sessionMessages: [...state.sessionMessages, message],
    })),

  setMessages: (messages) => set({ sessionMessages: messages }),

  updateWaitingRoom: (waitingRoom) => set({ waitingRoom }),

  setVideoEnabled: (enabled) => set({ isVideoEnabled: enabled }),

  setAudioEnabled: (enabled) => set({ isAudioEnabled: enabled }),

  setConnected: (connected) => set({ isConnected: connected }),

  setInWaitingRoom: (inWaitingRoom) => set({ isInWaitingRoom: inWaitingRoom }),

  setSessionHistory: (sessions) => set({ sessionHistory: sessions }),

  addToHistory: (session) =>
    set((state) => ({
      sessionHistory: [session, ...state.sessionHistory],
    })),

  reset: () => set(initialState),
}));

// Selectors
export const useActiveSession = () => useTelemedicineStore((state) => state.activeSession);
export const useSessionMessages = () => useTelemedicineStore((state) => state.sessionMessages);
export const useWaitingRoom = () => useTelemedicineStore((state) => state.waitingRoom);
export const useVideoEnabled = () => useTelemedicineStore((state) => state.isVideoEnabled);
export const useAudioEnabled = () => useTelemedicineStore((state) => state.isAudioEnabled);
export const useTelemedicineConnected = () => useTelemedicineStore((state) => state.isConnected);
export const useInWaitingRoom = () => useTelemedicineStore((state) => state.isInWaitingRoom);
export const useSessionHistory = () => useTelemedicineStore((state) => state.sessionHistory);