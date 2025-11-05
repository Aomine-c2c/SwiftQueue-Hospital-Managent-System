import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription } from './ui/alert';
import { ScrollArea } from './ui/scroll-area';
import { Separator } from './ui/separator';
import { apiService } from '../services/apiService';

interface Message {
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

interface MessageStats {
  total_messages: number;
  unread_messages: number;
  urgent_messages: number;
}

const StaffCommunicationHub: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [stats, setStats] = useState<MessageStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [activeTab, setActiveTab] = useState('inbox');

  // New message form state
  const [newMessage, setNewMessage] = useState({
    recipient_id: '',
    subject: '',
    message: '',
    message_type: 'direct',
    priority: 'normal',
    department_filter: '',
    role_filter: ''
  });

  useEffect(() => {
    loadMessages();
    loadStats();
  }, []);

  const loadMessages = async (unreadOnly = false) => {
    try {
      const response = await apiService.getStaffMessages(unreadOnly);
      setMessages(response.data);
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await apiService.getMessageStats();
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load message stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.subject.trim() || !newMessage.message.trim()) {
      alert('Please fill in subject and message');
      return;
    }

    setSending(true);
    try {
      await apiService.sendStaffMessage(newMessage);
      setNewMessage({
        recipient_id: '',
        subject: '',
        message: '',
        message_type: 'direct',
        priority: 'normal',
        department_filter: '',
        role_filter: ''
      });
      loadMessages();
      loadStats();
      alert('Message sent successfully!');
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Failed to send message');
    } finally {
      setSending(false);
    }
  };

  const markAsRead = async (messageId: number) => {
    try {
      await apiService.markMessageRead(messageId);
      loadMessages();
      loadStats();
    } catch (error) {
      console.error('Failed to mark message as read:', error);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'destructive';
      case 'high': return 'secondary';
      case 'normal': return 'default';
      case 'low': return 'outline';
      default: return 'default';
    }
  };

  const getMessageTypeIcon = (type: string) => {
    switch (type) {
      case 'direct': return '👤';
      case 'broadcast': return '📢';
      case 'announcement': return '📣';
      case 'alert': return '🚨';
      case 'task': return '📋';
      default: return '💬';
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading...</div>;
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Staff Communication Hub</h1>
        {stats && (
          <div className="flex gap-4">
            <Badge variant="outline">Total: {stats.total_messages}</Badge>
            <Badge variant="secondary">Unread: {stats.unread_messages}</Badge>
            <Badge variant="destructive">Urgent: {stats.urgent_messages}</Badge>
          </div>
        )}
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="inbox">Inbox</TabsTrigger>
          <TabsTrigger value="compose">Compose</TabsTrigger>
          <TabsTrigger value="broadcast">Broadcast</TabsTrigger>
        </TabsList>

        <TabsContent value="inbox" className="space-y-4">
          <div className="flex gap-2 mb-4">
            <Button
              variant="outline"
              onClick={() => loadMessages(false)}
            >
              All Messages
            </Button>
            <Button
              variant="outline"
              onClick={() => loadMessages(true)}
            >
              Unread Only
            </Button>
          </div>

          <ScrollArea className="h-96">
            <div className="space-y-2">
              {messages.length === 0 ? (
                <Alert>
                  <AlertDescription>No messages found.</AlertDescription>
                </Alert>
              ) : (
                messages.map((message) => (
                  <Card key={message.id} className={`cursor-pointer ${!message.is_read ? 'border-l-4 border-l-blue-500' : ''}`}>
                    <CardHeader className="pb-2">
                      <div className="flex justify-between items-start">
                        <div className="flex items-center gap-2">
                          <span>{getMessageTypeIcon(message.message_type)}</span>
                          <CardTitle className="text-lg">{message.subject}</CardTitle>
                          <Badge variant={getPriorityColor(message.priority)}>
                            {message.priority}
                          </Badge>
                        </div>
                        {!message.is_read && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => markAsRead(message.id)}
                          >
                            Mark Read
                          </Button>
                        )}
                      </div>
                      <div className="text-sm text-gray-600">
                        From: {message.sender_name} • {new Date(message.created_at).toLocaleString()}
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-700">{message.message}</p>
                      {message.department_filter && (
                        <div className="mt-2">
                          <Badge variant="outline">Department: {message.department_filter}</Badge>
                        </div>
                      )}
                      {message.role_filter && (
                        <div className="mt-1">
                          <Badge variant="outline">Role: {message.role_filter}</Badge>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </ScrollArea>
        </TabsContent>

        <TabsContent value="compose" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Compose New Message</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Recipient ID (optional)</label>
                  <Input
                    type="number"
                    placeholder="Leave empty for broadcast"
                    value={newMessage.recipient_id}
                    onChange={(e) => setNewMessage({...newMessage, recipient_id: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Priority</label>
                  <Select value={newMessage.priority} onValueChange={(value) => setNewMessage({...newMessage, priority: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="normal">Normal</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="urgent">Urgent</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Subject</label>
                <Input
                  placeholder="Message subject"
                  value={newMessage.subject}
                  onChange={(e) => setNewMessage({...newMessage, subject: e.target.value})}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Message</label>
                <Textarea
                  placeholder="Type your message here..."
                  rows={4}
                  value={newMessage.message}
                  onChange={(e) => setNewMessage({...newMessage, message: e.target.value})}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Message Type</label>
                  <Select value={newMessage.message_type} onValueChange={(value) => setNewMessage({...newMessage, message_type: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="direct">Direct</SelectItem>
                      <SelectItem value="broadcast">Broadcast</SelectItem>
                      <SelectItem value="announcement">Announcement</SelectItem>
                      <SelectItem value="alert">Alert</SelectItem>
                      <SelectItem value="task">Task</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Department Filter (optional)</label>
                  <Input
                    placeholder="e.g., Emergency, Cardiology"
                    value={newMessage.department_filter}
                    onChange={(e) => setNewMessage({...newMessage, department_filter: e.target.value})}
                  />
                </div>
              </div>

              <Button
                onClick={sendMessage}
                disabled={sending}
                className="w-full"
              >
                {sending ? 'Sending...' : 'Send Message'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="broadcast" className="space-y-4">
          <Alert>
            <AlertDescription>
              Broadcast messages are sent to all staff members matching the specified filters.
              Use this feature responsibly for important announcements only.
            </AlertDescription>
          </Alert>

          <Card>
            <CardHeader>
              <CardTitle>Broadcast Message</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Department Filter</label>
                  <Input
                    placeholder="e.g., Emergency (leave empty for all)"
                    value={newMessage.department_filter}
                    onChange={(e) => setNewMessage({...newMessage, department_filter: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Role Filter</label>
                  <Input
                    placeholder="e.g., staff, nurse (leave empty for all)"
                    value={newMessage.role_filter}
                    onChange={(e) => setNewMessage({...newMessage, role_filter: e.target.value})}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Subject</label>
                <Input
                  placeholder="Broadcast subject"
                  value={newMessage.subject}
                  onChange={(e) => setNewMessage({...newMessage, subject: e.target.value})}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Message</label>
                <Textarea
                  placeholder="Important announcement or broadcast message..."
                  rows={4}
                  value={newMessage.message}
                  onChange={(e) => setNewMessage({...newMessage, message: e.target.value})}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Priority</label>
                <Select value={newMessage.priority} onValueChange={(value) => setNewMessage({...newMessage, priority: value})}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="normal">Normal</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="urgent">Urgent</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button
                onClick={() => {
                  setNewMessage({...newMessage, message_type: 'broadcast'});
                  sendMessage();
                }}
                disabled={sending}
                className="w-full"
                variant="destructive"
              >
                {sending ? 'Broadcasting...' : 'Send Broadcast'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default StaffCommunicationHub;