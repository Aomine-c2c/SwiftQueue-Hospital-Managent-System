import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription } from './ui/alert';
import { ScrollArea } from './ui/scroll-area';
import { Progress } from './ui/progress';
import { Calendar, FileText, MessageSquare, Activity, Bell, Download } from 'lucide-react';
import { apiService } from '../services/apiService';

interface DashboardSummary {
  unread_messages: number;
  recent_documents: any[];
  recent_lab_results: any[];
  abnormal_results_count: number;
  preferences: any;
  total_documents: number;
}

interface Message {
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

interface Document {
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

interface LabResult {
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

const PatientDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardSummary | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [labResults, setLabResults] = useState<LabResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [dashboardResponse, messagesResponse, documentsResponse, labResponse] = await Promise.all([
        apiService.getPatientDashboard(),
        apiService.getPatientMessages(),
        apiService.getPatientDocuments(),
        apiService.getPatientLabResults()
      ]);

      setDashboardData(dashboardResponse.data);
      setMessages(messagesResponse.data.messages || []);
      setDocuments(documentsResponse.data.documents || []);
      setLabResults(labResponse.data.results || []);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const markMessageRead = async (messageId: number) => {
    try {
      await apiService.markPatientMessageRead(messageId);
      loadDashboardData(); // Refresh data
    } catch (error) {
      console.error('Failed to mark message as read:', error);
    }
  };

  const downloadDocument = async (documentId: number, filename: string) => {
    try {
      const response = await apiService.downloadPatientDocument(documentId);
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to download document:', error);
      alert('Failed to download document');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Patient Dashboard</h1>
        <div className="flex gap-2">
          {dashboardData?.unread_messages > 0 && (
            <Badge variant="destructive" className="flex items-center gap-1">
              <Bell className="w-3 h-3" />
              {dashboardData.unread_messages} Unread
            </Badge>
          )}
          {dashboardData?.abnormal_results_count > 0 && (
            <Badge variant="secondary" className="flex items-center gap-1">
              <Activity className="w-3 h-3" />
              {dashboardData.abnormal_results_count} Abnormal Results
            </Badge>
          )}
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="messages">Messages</TabsTrigger>
          <TabsTrigger value="documents">Documents</TabsTrigger>
          <TabsTrigger value="lab-results">Lab Results</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <MessageSquare className="h-8 w-8 text-blue-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Unread Messages</p>
                    <p className="text-2xl font-bold">{dashboardData?.unread_messages || 0}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <FileText className="h-8 w-8 text-green-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Total Documents</p>
                    <p className="text-2xl font-bold">{dashboardData?.total_documents || 0}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <Activity className="h-8 w-8 text-red-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Abnormal Results</p>
                    <p className="text-2xl font-bold">{dashboardData?.abnormal_results_count || 0}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <Calendar className="h-8 w-8 text-purple-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Recent Labs</p>
                    <p className="text-2xl font-bold">{dashboardData?.recent_lab_results?.length || 0}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Messages */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5" />
                  Recent Messages
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-64">
                  {messages.slice(0, 5).length === 0 ? (
                    <p className="text-gray-500 text-center py-4">No messages yet</p>
                  ) : (
                    <div className="space-y-3">
                      {messages.slice(0, 5).map((message) => (
                        <div key={message.id} className="border-l-2 border-blue-200 pl-3">
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="font-medium text-sm">{message.subject}</p>
                              <p className="text-xs text-gray-600">
                                {message.is_patient_sender ? 'You' : message.staff?.name || 'Staff'} •
                                {new Date(message.created_at).toLocaleDateString()}
                              </p>
                            </div>
                            {message.status === 'unread' && (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => markMessageRead(message.id)}
                              >
                                Mark Read
                              </Button>
                            )}
                          </div>
                          <p className="text-sm text-gray-700 mt-1 line-clamp-2">{message.message}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Recent Lab Results */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Recent Lab Results
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-64">
                  {dashboardData?.recent_lab_results?.length === 0 ? (
                    <p className="text-gray-500 text-center py-4">No recent lab results</p>
                  ) : (
                    <div className="space-y-3">
                      {dashboardData?.recent_lab_results?.map((result: any) => (
                        <div key={result.id} className="border rounded p-3">
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="font-medium text-sm">{result.test_name}</p>
                              <p className="text-xs text-gray-600">
                                {result.result_date ? new Date(result.result_date).toLocaleDateString() : 'Pending'}
                              </p>
                            </div>
                            <Badge variant={result.abnormal_flag ? "destructive" : "default"}>
                              {result.abnormal_flag ? "Abnormal" : "Normal"}
                            </Badge>
                          </div>
                          {result.result_value && (
                            <p className="text-sm mt-1">
                              Result: {result.result_value} {result.unit}
                              {result.normal_range && ` (Normal: ${result.normal_range})`}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>
          </div>

          {/* Recent Documents */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Recent Documents
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {dashboardData?.recent_documents?.length === 0 ? (
                  <p className="text-gray-500 col-span-full text-center py-4">No documents yet</p>
                ) : (
                  dashboardData?.recent_documents?.map((doc: any) => (
                    <Card key={doc.id} className="cursor-pointer hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className="font-medium text-sm">{doc.title}</h4>
                            <p className="text-xs text-gray-600 mt-1">
                              {doc.document_type} • {new Date(doc.uploaded_at).toLocaleDateString()}
                            </p>
                            {doc.description && (
                              <p className="text-xs text-gray-500 mt-1 line-clamp-2">{doc.description}</p>
                            )}
                          </div>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => downloadDocument(doc.id, doc.title)}
                            className="ml-2"
                          >
                            <Download className="h-3 w-3" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="messages" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>All Messages</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                {messages.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">No messages found</p>
                ) : (
                  <div className="space-y-4">
                    {messages.map((message) => (
                      <Card key={message.id} className={message.status === 'unread' ? 'border-l-4 border-l-blue-500' : ''}>
                        <CardContent className="p-4">
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <h4 className="font-medium">{message.subject}</h4>
                              <p className="text-sm text-gray-600">
                                {message.is_patient_sender ? 'You' : message.staff?.name || 'Staff'} •
                                {new Date(message.created_at).toLocaleString()}
                              </p>
                            </div>
                            <div className="flex gap-2">
                              <Badge variant={message.priority === 'urgent' ? 'destructive' : 'default'}>
                                {message.priority}
                              </Badge>
                              {message.status === 'unread' && (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => markMessageRead(message.id)}
                                >
                                  Mark Read
                                </Button>
                              )}
                            </div>
                          </div>
                          <p className="text-gray-700">{message.message}</p>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="documents" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>All Documents</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {documents.length === 0 ? (
                  <p className="text-gray-500 col-span-full text-center py-4">No documents found</p>
                ) : (
                  documents.map((doc) => (
                    <Card key={doc.id}>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className="font-medium">{doc.title}</h4>
                            <p className="text-sm text-gray-600">
                              {doc.document_type} • {(doc.file_size / 1024).toFixed(1)} KB
                            </p>
                            <p className="text-xs text-gray-500 mt-1">
                              {new Date(doc.uploaded_at).toLocaleDateString()}
                            </p>
                            {doc.description && (
                              <p className="text-sm text-gray-700 mt-2">{doc.description}</p>
                            )}
                          </div>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => downloadDocument(doc.id, doc.title)}
                          >
                            <Download className="h-4 w-4 mr-1" />
                            Download
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="lab-results" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>All Lab Results</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                {labResults.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">No lab results found</p>
                ) : (
                  <div className="space-y-4">
                    {labResults.map((result) => (
                      <Card key={result.id} className={result.abnormal_flag ? 'border-l-4 border-l-red-500' : ''}>
                        <CardContent className="p-4">
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <h4 className="font-medium">{result.test_name}</h4>
                              <p className="text-sm text-gray-600">
                                {result.test_category} •
                                {result.result_date ? new Date(result.result_date).toLocaleDateString() : 'Pending'}
                              </p>
                            </div>
                            <div className="flex gap-2">
                              <Badge variant={result.status === 'completed' ? 'default' : 'secondary'}>
                                {result.status}
                              </Badge>
                              {result.abnormal_flag && (
                                <Badge variant="destructive">Abnormal</Badge>
                              )}
                            </div>
                          </div>

                          {result.result_value && (
                            <div className="mb-2">
                              <p className="text-sm">
                                <strong>Result:</strong> {result.result_value} {result.unit}
                              </p>
                              {result.normal_range && (
                                <p className="text-sm text-gray-600">
                                  <strong>Normal Range:</strong> {result.normal_range}
                                </p>
                              )}
                            </div>
                          )}

                          {result.notes && (
                            <div className="mt-2 p-2 bg-gray-50 rounded">
                              <p className="text-sm"><strong>Notes:</strong> {result.notes}</p>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default PatientDashboard;