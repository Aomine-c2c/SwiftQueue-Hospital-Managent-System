import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Video, VideoOff, Mic, MicOff, MessageSquare, Phone, PhoneOff, Send, Clock, User, Stethoscope } from 'lucide-react';
import { apiService } from '../services/apiService';

interface TelemedicineSessionProps {
  sessionId: string;
  onClose?: () => void;
}

interface SessionData {
  session_id: string;
  patient_id: number;
  doctor_id: number;
  status: string;
  session_type: string;
  room_id: string;
  chief_complaint?: string;
  diagnosis?: string;
  treatment_plan?: string;
  follow_up_instructions?: string;
  patient?: {
    id: number;
    name: string;
    email: string;
  };
  doctor?: {
    id: number;
    name: string;
    email: string;
  };
}

interface Message {
  id: number;
  sender_id: number;
  content: string;
  message_type: string;
  sent_at: string;
  sender?: {
    name: string;
  };
}

export const TelemedicineSession: React.FC<TelemedicineSessionProps> = ({ sessionId, onClose }) => {
  const [session, setSession] = useState<SessionData | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isVideoEnabled, setIsVideoEnabled] = useState(false);
  const [isAudioEnabled, setIsAudioEnabled] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'chat' | 'medical'>('chat');

  const videoRef = useRef<HTMLVideoElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadSession();
    loadMessages();
  }, [sessionId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadSession = async () => {
    try {
      const response = await apiService.get(`/telemedicine/sessions/${sessionId}`);
      setSession(response as SessionData);
    } catch (error) {
      console.error('Failed to load session:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMessages = async () => {
    try {
      const response = await apiService.get(`/telemedicine/sessions/${sessionId}/messages`);
      setMessages(response as Message[]);
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim()) return;

    try {
      await apiService.post(`/telemedicine/sessions/${sessionId}/messages`, {
        content: newMessage,
        message_type: 'text'
      });
      setNewMessage('');
      loadMessages(); // Refresh messages
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const startSession = async () => {
    try {
      await apiService.post(`/telemedicine/sessions/${sessionId}/start`);
      setIsConnected(true);
      loadSession(); // Refresh session status
    } catch (error) {
      console.error('Failed to start session:', error);
    }
  };

  const endSession = async () => {
    try {
      await apiService.put(`/telemedicine/sessions/${sessionId}`, {
        status: 'completed',
        diagnosis: session?.diagnosis || '',
        treatment_plan: session?.treatment_plan || '',
        follow_up_instructions: session?.follow_up_instructions || ''
      });
      setIsConnected(false);
      loadSession();
      if (onClose) onClose();
    } catch (error) {
      console.error('Failed to end session:', error);
    }
  };

  const toggleVideo = () => {
    setIsVideoEnabled(!isVideoEnabled);
    // WebRTC video toggle logic would go here
  };

  const toggleAudio = () => {
    setIsAudioEnabled(!isAudioEnabled);
    // WebRTC audio toggle logic would go here
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled': return 'bg-blue-100 text-blue-800';
      case 'waiting': return 'bg-yellow-100 text-yellow-800';
      case 'in_progress': return 'bg-green-100 text-green-800';
      case 'completed': return 'bg-gray-100 text-gray-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">Session not found</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Session Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div>
                <CardTitle className="text-xl">Telemedicine Session</CardTitle>
                <p className="text-sm text-gray-600">ID: {session.session_id}</p>
              </div>
              <Badge className={getStatusColor(session.status)}>
                {session.status.replace('_', ' ').toUpperCase()}
              </Badge>
            </div>
            <div className="flex items-center space-x-2">
              {session.status === 'scheduled' && (
                <Button onClick={startSession} className="bg-green-600 hover:bg-green-700">
                  <Video className="w-4 h-4 mr-2" />
                  Start Session
                </Button>
              )}
              {session.status === 'in_progress' && (
                <Button onClick={endSession} variant="destructive">
                  <PhoneOff className="w-4 h-4 mr-2" />
                  End Session
                </Button>
              )}
              <Button variant="outline" onClick={onClose}>
                Close
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center space-x-3">
              <Avatar>
                <AvatarFallback>
                  <User className="w-4 h-4" />
                </AvatarFallback>
              </Avatar>
              <div>
                <p className="font-medium">{session.patient?.name || 'Patient'}</p>
                <p className="text-sm text-gray-600">Patient</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Avatar>
                <AvatarFallback>
                  <Stethoscope className="w-4 h-4" />
                </AvatarFallback>
              </Avatar>
              <div>
                <p className="font-medium">{session.doctor?.name || 'Doctor'}</p>
                <p className="text-sm text-gray-600">Healthcare Provider</p>
              </div>
            </div>
          </div>
          {session.chief_complaint && (
            <div className="mt-4">
              <h4 className="font-medium mb-2">Chief Complaint</h4>
              <p className="text-gray-700 bg-gray-50 p-3 rounded">{session.chief_complaint}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Video/Chat Interface */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Video Section */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center">
                  <Video className="w-5 h-5 mr-2" />
                  Video Consultation
                </CardTitle>
                {isConnected && (
                  <div className="flex items-center space-x-2">
                    <Button
                      size="sm"
                      variant={isVideoEnabled ? "default" : "outline"}
                      onClick={toggleVideo}
                    >
                      {isVideoEnabled ? <Video className="w-4 h-4" /> : <VideoOff className="w-4 h-4" />}
                    </Button>
                    <Button
                      size="sm"
                      variant={isAudioEnabled ? "default" : "outline"}
                      onClick={toggleAudio}
                    >
                      {isAudioEnabled ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
                    </Button>
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center">
                {isConnected ? (
                  <video
                    ref={videoRef}
                    className="w-full h-full rounded-lg"
                    autoPlay
                    muted={!isAudioEnabled}
                  />
                ) : (
                  <div className="text-center">
                    <Video className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                    <p className="text-gray-600">
                      {session.status === 'scheduled' ? 'Click "Start Session" to begin' : 'Video will appear here'}
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Chat/Medical Notes Section */}
        <div>
          <Card className="h-full">
            <CardHeader>
              <div className="flex items-center space-x-2">
                <Button
                  size="sm"
                  variant={activeTab === 'chat' ? 'default' : 'outline'}
                  onClick={() => setActiveTab('chat')}
                >
                  <MessageSquare className="w-4 h-4 mr-1" />
                  Chat
                </Button>
                <Button
                  size="sm"
                  variant={activeTab === 'medical' ? 'default' : 'outline'}
                  onClick={() => setActiveTab('medical')}
                >
                  <Stethoscope className="w-4 h-4 mr-1" />
                  Medical
                </Button>
              </div>
            </CardHeader>
            <CardContent className="flex-1">
              {activeTab === 'chat' ? (
                <div className="space-y-4">
                  {/* Messages */}
                  <div className="h-64 overflow-y-auto space-y-2">
                    {messages.map((message) => (
                      <div key={message.id} className="flex space-x-2">
                        <Avatar className="w-6 h-6">
                          <AvatarFallback className="text-xs">
                            {message.sender?.name?.charAt(0) || 'U'}
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex-1">
                          <div className="bg-gray-100 rounded-lg p-2">
                            <p className="text-sm">{message.content}</p>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            {new Date(message.sent_at).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    ))}
                    <div ref={messagesEndRef} />
                  </div>

                  {/* Message Input */}
                  <div className="flex space-x-2">
                    <Input
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      placeholder="Type your message..."
                      onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    />
                    <Button onClick={sendMessage} size="sm">
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Diagnosis</label>
                    <Textarea
                      value={session.diagnosis || ''}
                      onChange={(e) => setSession({...session, diagnosis: e.target.value})}
                      placeholder="Enter diagnosis..."
                      rows={3}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Treatment Plan</label>
                    <Textarea
                      value={session.treatment_plan || ''}
                      onChange={(e) => setSession({...session, treatment_plan: e.target.value})}
                      placeholder="Enter treatment plan..."
                      rows={3}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Follow-up Instructions</label>
                    <Textarea
                      value={session.follow_up_instructions || ''}
                      onChange={(e) => setSession({...session, follow_up_instructions: e.target.value})}
                      placeholder="Enter follow-up instructions..."
                      rows={3}
                    />
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};