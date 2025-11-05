/**
 * Central API service for the Queue Management System
 * Handles all HTTP requests to the backend API
 */

// Read Vite env var VITE_API_URL if provided, and normalize to have no trailing slash
const _VITE_API = (import.meta as any).env?.VITE_API_URL as string | undefined;
const _DEFAULT_API = 'http://127.0.0.1:8000';
// Ensure base does NOT include a trailing slash and does not end with '/api'
const API_BASE_URL = (_VITE_API && _VITE_API.length > 0 ? _VITE_API : _DEFAULT_API).replace(/\/+$/, '').replace(/\/api$/i, '');

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  // Staff Communication methods
  async getStaffMessages(unreadOnly = false): Promise<ApiResponse<StaffMessage[]>> {
    return this.get(`/api/staff-communication/messages${unreadOnly ? '?unread_only=true' : ''}`);
  }

  async getMessageStats(): Promise<ApiResponse<MessageStats>> {
    return this.get('/api/staff-communication/messages/stats');
  }

  async sendStaffMessage(message: any): Promise<ApiResponse<any>> {
    return this.post('/api/staff-communication/messages', message);
  }

  async markMessageRead(messageId: number): Promise<ApiResponse<any>> {
    return this.put(`/api/staff-communication/messages/${messageId}/read`);
  }

  // Patient Portal methods
  async getPatientDashboard(): Promise<ApiResponse<PatientDashboard>> {
    return this.get('/api/patient-portal/dashboard');
  }

  async getPatientMessages(): Promise<ApiResponse<{ messages: PatientMessage[] }>> {
    return this.get('/api/patient-portal/messages');
  }

  async getPatientDocuments(): Promise<ApiResponse<{ documents: PatientDocument[] }>> {
    return this.get('/api/patient-portal/documents');
  }

  async getPatientLabResults(): Promise<ApiResponse<{ results: LabResult[] }>> {
    return this.get('/api/patient-portal/lab-results');
  }

  async markPatientMessageRead(messageId: number): Promise<ApiResponse<any>> {
    return this.put(`/api/patient-portal/messages/${messageId}/read`);
  }

  async downloadPatientDocument(documentId: number): Promise<Blob> {
    const url = `/api/patient-portal/documents/${documentId}/download`;
    const response = await fetch(`${this.baseUrl}${url}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.blob();
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
  // Build URL safely: if endpoint starts with '/', append directly; otherwise prefix with '/'
  let url = endpoint.startsWith('/') ? `${this.baseUrl}${endpoint}` : `${this.baseUrl}/${endpoint}`;
  // Normalize accidental duplicate '/api/api' that can happen if both base and endpoint include '/api'
  url = url.replace(/\/api\/api\/+/g, '/api/').replace(/\/api\/api$/g, '/api');

  // Debug log to help trace final URL used for requests
  console.log(`apiService: Fetching ${url}`);
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // GET request
  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  // POST request
  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  // PUT request
  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  // DELETE request
  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  // PATCH request
  async patch<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }
}

// Export singleton instance
export const apiService = new ApiService();

// Export types for common API responses
export interface User {
  id: number;
  name: string;
  email: string;
  phone: string;
  date_of_birth: string;
}

export interface Service {
  id: number;
  name: string;
  description: string;
  department: string;
  staff_count: number;
  service_rate: number;
  estimated_time: number;
  current_wait_time: number;
  queue_length: number;
}

export interface QueueEntry {
  id: number;
  patient_id: number;
  service_id: number;
  queue_number: number;
  status: 'waiting' | 'called' | 'serving' | 'completed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  created_at: string;
  completed_at?: string;
  estimated_wait_time: number;
  ai_predicted_wait: number;
  patient?: User;
  service?: Service;
}

export interface ServiceCounter {
  id: number;
  name: string;
  service_id: number;
  is_active: boolean;
  current_queue_entry_id?: number;
  staff_member?: string;
}

export interface Analytics {
  id: number;
  timestamp: string;
  service_id: number;
  queue_length: number;
  avg_wait_time: number;
  avg_service_time: number;
  efficiency_score: number;
  peak_hour: number;
  peak_load: number;
  staff_utilization: number;
  patient_satisfaction: number;
  patients_served: number;
}

export interface AIRecommendation {
  type: 'critical' | 'warning' | 'improvement' | 'info';
  message: string;
  action: string;
}

export interface AIServiceSuggestion {
  service: string;
  confidence: number;
  urgency: 'low' | 'medium' | 'high';
  reasoning: string;
  alternative_services: string[];
  estimated_wait?: number;
}

export interface AIEfficiencyMetrics {
  efficiency_score: number;
  current_queue_length: number;
  avg_wait_time: number;
  staff_count: number;
  staff_utilization: number;
  throughput_per_hour: number;
  capacity_utilization: number;
  service_rate: number;
  recommendations: string[];
}

export interface AIStaffOptimization {
  service_id: number;
  service_name: string;
  current_staff: number;
  recommended_staff: number;
  efficiency_score: number;
  reasoning: string;
}

export interface EmergencyDispatch {
  id: number;
  patient_id: number;
  emergency_details: string;
  dispatch_address: string;
  dispatch_status: 'pending' | 'dispatched' | 'en_route' | 'arrived' | 'completed' | 'cancelled';
  dispatched_at?: string;
  response_time?: number;
  ambulance_id?: string;
  notes?: string;
  created_at: string;
  patient_name?: string;
  patient?: User;
}

export interface DispatchRequest {
  patient_id: number;
  emergency_details: string;
}

export interface DispatchStatusResponse extends EmergencyDispatch {
  patient_name?: string;
}

// Staff Communication API methods
export interface StaffMessage {
  id: number;
  sender_id: number;
  recipient_id?: number;
  subject: string;
  message: string;
  message_type: string;
  priority: string;
  is_read: boolean;
  read_at?: string;
  department_filter?: string;
  role_filter?: string;
  expires_at?: string;
  created_at: string;
  sender_name?: string;
}

export interface MessageStats {
  total_messages: number;
  unread_messages: number;
  urgent_messages: number;
}

// Patient Portal API methods
export interface PatientDashboard {
  unread_messages: number;
  recent_documents: any[];
  recent_lab_results: any[];
  abnormal_results_count: number;
  preferences: any;
  total_documents: number;
}

export interface PatientMessage {
  id: number;
  patient_id: number;
  staff_id?: number;
  subject: string;
  message: string;
  message_type: string;
  priority: string;
  status: string;
  is_patient_sender: boolean;
  created_at: string;
  staff?: any;
}

export interface PatientDocument {
  id: number;
  patient_id: number;
  document_type: string;
  title: string;
  description?: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  uploaded_by?: number;
  is_patient_visible: boolean;
  uploaded_at: string;
}

export interface LabResult {
  id: number;
  patient_id: number;
  test_name: string;
  test_category?: string;
  result_value?: string;
  normal_range?: string;
  unit?: string;
  status: string;
  abnormal_flag: boolean;
  ordered_by?: number;
  performed_by?: number;
  notes?: string;
  test_date?: string;
  result_date?: string;
  is_patient_visible: boolean;
}


export default apiService;