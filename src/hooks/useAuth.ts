import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../lib/apiClient';
import { useAuthStore } from '../stores/authStore';
import { useUIStore } from '../stores/uiStore';
import { queryKeys } from '../lib/queryClient';

export const useAuth = () => {
  const queryClient = useQueryClient();
  const { user, token, isAuthenticated } = useAuthStore();
  const { addNotification } = useUIStore();

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: async (credentials: { email: string; password: string }) => {
      const response = await apiClient.login(credentials);
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.auth.user });
      addNotification({
        type: 'success',
        title: 'Login Successful',
        message: `Welcome back, ${data.user.name}!`,
      });
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Login failed. Please try again.';
      addNotification({
        type: 'error',
        title: 'Login Failed',
        message,
      });
    },
  });

  // Register mutation
  const registerMutation = useMutation({
    mutationFn: async (userData: any) => {
      const response = await apiClient.register(userData);
      return response.data;
    },
    onSuccess: () => {
      addNotification({
        type: 'success',
        title: 'Registration Successful',
        message: 'Your account has been created. Please log in.',
      });
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Registration failed. Please try again.';
      addNotification({
        type: 'error',
        title: 'Registration Failed',
        message,
      });
    },
  });

  // Logout mutation
  const logoutMutation = useMutation({
    mutationFn: async () => {
      await apiClient.logout();
    },
    onSuccess: () => {
      queryClient.clear();
      addNotification({
        type: 'info',
        title: 'Logged Out',
        message: 'You have been successfully logged out.',
      });
    },
  });

  // Get current user profile
  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: queryKeys.auth.profile,
    queryFn: async () => {
      const response = await apiClient.get('/auth/profile');
      return response.data;
    },
    enabled: isAuthenticated,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  // Update profile mutation
  const updateProfileMutation = useMutation({
    mutationFn: async (profileData: any) => {
      const response = await apiClient.put('/auth/profile', profileData);
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.auth.profile, data);
      useAuthStore.getState().updateUser(data);
      addNotification({
        type: 'success',
        title: 'Profile Updated',
        message: 'Your profile has been updated successfully.',
      });
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to update profile.';
      addNotification({
        type: 'error',
        title: 'Update Failed',
        message,
      });
    },
  });

  return {
    // State
    user,
    token,
    isAuthenticated,
    profile,
    profileLoading,

    // Mutations
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    logout: logoutMutation.mutate,
    updateProfile: updateProfileMutation.mutate,

    // Loading states
    isLoggingIn: loginMutation.isPending,
    isRegistering: registerMutation.isPending,
    isLoggingOut: logoutMutation.isPending,
    isUpdatingProfile: updateProfileMutation.isPending,

    // Errors
    loginError: loginMutation.error,
    registerError: registerMutation.error,
    logoutError: logoutMutation.error,
    updateProfileError: updateProfileMutation.error,
  };
};