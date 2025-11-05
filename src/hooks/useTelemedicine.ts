import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../lib/apiClient';
import { useTelemedicineStore } from '../stores/telemedicineStore';
import { useUIStore } from '../stores/uiStore';
import { queryKeys } from '../lib/queryClient';

export const useTelemedicine = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useUIStore();

  // Get user sessions
  const { data: sessions, isLoading: sessionsLoading } = useQuery({
    queryKey: queryKeys.telemedicine.sessions(),
    queryFn: async () => {
      const response = await apiClient.get('/telemedicine/sessions');
      return response.data;
    },
    staleTime: 1000 * 60 * 2, // 2 minutes
  });

  // Get upcoming sessions
  const { data: upcomingSessions, isLoading: upcomingLoading } = useQuery({
    queryKey: ['telemedicine', 'upcoming'],
    queryFn: async () => {
      const response = await apiClient.get('/telemedicine/sessions/upcoming');
      return response.data;
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  // Get active sessions
  const { data: activeSessions, isLoading: activeLoading } = useQuery({
    queryKey: ['telemedicine', 'active'],
    queryFn: async () => {
      const response = await apiClient.get('/telemedicine/sessions/active');
      return response.data;
    },
    staleTime: 1000 * 30, // 30 seconds
    refetchInterval: 1000 * 30, // Refetch every 30 seconds
  });

  // Create session mutation
  const createSessionMutation = useMutation({
    mutationFn: async (sessionData: any) => {
      const response = await apiClient.createTelemedicineSession(sessionData);
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.telemedicine.sessions() });
      addNotification({
        type: 'success',
        title: 'Session Created',
        message: 'Telemedicine session has been scheduled successfully.',
      });
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to create session.';
      addNotification({
        type: 'error',
        title: 'Session Creation Failed',
        message,
      });
    },
  });

  // Start session mutation
  const startSessionMutation = useMutation({
    mutationFn: async (sessionId: string) => {
      const response = await apiClient.startTelemedicineSession(sessionId);
      return response.data;
    },
    onSuccess: (data, sessionId) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.telemedicine.session(sessionId) });
      queryClient.invalidateQueries({ queryKey: ['telemedicine', 'active'] });
      useTelemedicineStore.getState().setConnected(true);
      addNotification({
        type: 'success',
        title: 'Session Started',
        message: 'Telemedicine session is now active.',
      });
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to start session.';
      addNotification({
        type: 'error',
        title: 'Session Start Failed',
        message,
      });
    },
  });

  // End session mutation
  const endSessionMutation = useMutation({
    mutationFn: async ({ sessionId, medicalData }: { sessionId: string; medicalData: any }) => {
      const response = await apiClient.put(`/telemedicine/sessions/${sessionId}`, {
        status: 'completed',
        ...medicalData,
      });
      return response.data;
    },
    onSuccess: (data, { sessionId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.telemedicine.session(sessionId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.telemedicine.sessions() });
      queryClient.invalidateQueries({ queryKey: ['telemedicine', 'active'] });
      useTelemedicineStore.getState().setConnected(false);
      useTelemedicineStore.getState().setActiveSession(null);
      addNotification({
        type: 'success',
        title: 'Session Completed',
        message: 'Telemedicine session has been completed successfully.',
      });
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to complete session.';
      addNotification({
        type: 'error',
        title: 'Session Completion Failed',
        message,
      });
    },
  });

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: async ({ sessionId, content, messageType = 'text' }: {
      sessionId: string;
      content: string;
      messageType?: string;
    }) => {
      const response = await apiClient.post(`/telemedicine/sessions/${sessionId}/messages`, {
        content,
        message_type: messageType,
      });
      return response.data;
    },
    onSuccess: (data, { sessionId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.telemedicine.messages(sessionId) });
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to send message.';
      addNotification({
        type: 'error',
        title: 'Message Failed',
        message,
      });
    },
  });

  // Join waiting room mutation
  const joinWaitingRoomMutation = useMutation({
    mutationFn: async (sessionId: string) => {
      const response = await apiClient.post(`/telemedicine/sessions/${sessionId}/waiting-room/join`);
      return response.data;
    },
    onSuccess: (data, sessionId) => {
      useTelemedicineStore.getState().setInWaitingRoom(true);
      queryClient.invalidateQueries({ queryKey: queryKeys.telemedicine.waitingRoom(sessionId) });
      addNotification({
        type: 'info',
        title: 'Joined Waiting Room',
        message: 'You have been added to the waiting room.',
      });
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to join waiting room.';
      addNotification({
        type: 'error',
        title: 'Waiting Room Error',
        message,
      });
    },
  });

  // Submit feedback mutation
  const submitFeedbackMutation = useMutation({
    mutationFn: async ({ sessionId, feedback }: { sessionId: string; feedback: any }) => {
      const response = await apiClient.post(`/telemedicine/sessions/${sessionId}/feedback`, feedback);
      return response.data;
    },
    onSuccess: () => {
      addNotification({
        type: 'success',
        title: 'Feedback Submitted',
        message: 'Thank you for your feedback!',
      });
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to submit feedback.';
      addNotification({
        type: 'error',
        title: 'Feedback Error',
        message,
      });
    },
  });

  return {
    // Data
    sessions,
    upcomingSessions,
    activeSessions,

    // Loading states
    sessionsLoading,
    upcomingLoading,
    activeLoading,

    // Mutations
    createSession: createSessionMutation.mutate,
    startSession: startSessionMutation.mutate,
    endSession: endSessionMutation.mutate,
    sendMessage: sendMessageMutation.mutate,
    joinWaitingRoom: joinWaitingRoomMutation.mutate,
    submitFeedback: submitFeedbackMutation.mutate,

    // Mutation states
    isCreatingSession: createSessionMutation.isPending,
    isStartingSession: startSessionMutation.isPending,
    isEndingSession: endSessionMutation.isPending,
    isSendingMessage: sendMessageMutation.isPending,
    isJoiningWaitingRoom: joinWaitingRoomMutation.isPending,
    isSubmittingFeedback: submitFeedbackMutation.isPending,

    // Errors
    createSessionError: createSessionMutation.error,
    startSessionError: startSessionMutation.error,
    endSessionError: endSessionMutation.error,
    sendMessageError: sendMessageMutation.error,
    joinWaitingRoomError: joinWaitingRoomMutation.error,
    submitFeedbackError: submitFeedbackMutation.error,
  };
};