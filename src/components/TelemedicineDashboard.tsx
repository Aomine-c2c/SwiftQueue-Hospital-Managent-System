import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Calendar, Clock, Video, MessageSquare, Plus, User, Stethoscope, Phone } from 'lucide-react';
import { apiService } from '../services/apiService';
import { TelemedicineSession } from './TelemedicineSession';

interface Session {
  session_id: string;
  patient_id: number;
  doctor_id: number;
  status: string;
  session_type: string;
  scheduled_start: string;
  actual_start?: string;
  duration_minutes?: number;
  chief_complaint?: string;
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

export const TelemedicineDashboard: React.FC = () => {
  const [upcomingSessions, setUpcomingSessions] = useState<Session[]>([]);
  const [activeSessions, setActiveSessions] = useState<Session[]>([]);
  const [pastSessions, setPastSessions] = useState<Session[]>([]);
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'upcoming' | 'active' | 'past'>('upcoming');

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const [upcomingRes, activeRes, pastRes] = await Promise.all([
        apiService.get('/telemedicine/sessions/upcoming'),
        apiService.get('/telemedicine/sessions/active'),
        apiService.get('/telemedicine/sessions?status=completed&limit=10')
      ]);

      setUpcomingSessions(upcomingRes as Session[]);
      setActiveSessions(activeRes as Session[]);
      setPastSessions(pastRes as Session[]);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setLoading(false);
    }
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

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getSessionIcon = (type: string) => {
    switch (type) {
      case 'video': return <Video className="w-4 h-4" />;
      case 'audio': return <Phone className="w-4 h-4" />;
      case 'chat': return <MessageSquare className="w-4 h-4" />;
      default: return <Video className="w-4 h-4" />;
    }
  };

  const SessionCard: React.FC<{ session: Session; showActions?: boolean }> = ({ session, showActions = true }) => (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-3">
            {getSessionIcon(session.session_type)}
            <div>
              <h3 className="font-medium">
                {session.patient?.name || 'Patient'} ↔ {session.doctor?.name || 'Doctor'}
              </h3>
              <p className="text-sm text-gray-600">ID: {session.session_id}</p>
            </div>
          </div>
          <Badge className={getStatusColor(session.status)}>
            {session.status.replace('_', ' ').toUpperCase()}
          </Badge>
        </div>

        <div className="space-y-2 mb-3">
          <div className="flex items-center text-sm text-gray-600">
            <Calendar className="w-4 h-4 mr-2" />
            {formatDateTime(session.scheduled_start)}
          </div>
          {session.chief_complaint && (
            <div className="text-sm text-gray-700">
              <strong>Complaint:</strong> {session.chief_complaint}
            </div>
          )}
          {session.duration_minutes && (
            <div className="flex items-center text-sm text-gray-600">
              <Clock className="w-4 h-4 mr-2" />
              Duration: {session.duration_minutes} minutes
            </div>
          )}
        </div>

        {showActions && (
          <div className="flex space-x-2">
            <Button
              size="sm"
              onClick={() => setSelectedSession(session.session_id)}
              className="flex-1"
            >
              {session.status === 'in_progress' ? 'Join Session' : 'View Details'}
            </Button>
            {session.status === 'scheduled' && (
              <Button size="sm" variant="outline">
                Reschedule
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );

  if (selectedSession) {
    return (
      <TelemedicineSession
        sessionId={selectedSession}
        onClose={() => {
          setSelectedSession(null);
          loadSessions(); // Refresh data when closing session
        }}
      />
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Telemedicine Dashboard</h1>
          <p className="text-gray-600">Manage your virtual consultations</p>
        </div>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Schedule New Session
        </Button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <Calendar className="w-8 h-8 text-blue-600 mr-3" />
              <div>
                <p className="text-2xl font-bold">{upcomingSessions.length}</p>
                <p className="text-sm text-gray-600">Upcoming</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <Video className="w-8 h-8 text-green-600 mr-3" />
              <div>
                <p className="text-2xl font-bold">{activeSessions.length}</p>
                <p className="text-sm text-gray-600">Active</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <Clock className="w-8 h-8 text-gray-600 mr-3" />
              <div>
                <p className="text-2xl font-bold">{pastSessions.length}</p>
                <p className="text-sm text-gray-600">Completed</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <MessageSquare className="w-8 h-8 text-purple-600 mr-3" />
              <div>
                <p className="text-2xl font-bold">24/7</p>
                <p className="text-sm text-gray-600">Available</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Sessions Tabs */}
      <Card>
        <CardHeader>
          <div className="flex space-x-4">
            <Button
              variant={activeTab === 'upcoming' ? 'default' : 'ghost'}
              onClick={() => setActiveTab('upcoming')}
            >
              Upcoming ({upcomingSessions.length})
            </Button>
            <Button
              variant={activeTab === 'active' ? 'default' : 'ghost'}
              onClick={() => setActiveTab('active')}
            >
              Active ({activeSessions.length})
            </Button>
            <Button
              variant={activeTab === 'past' ? 'default' : 'ghost'}
              onClick={() => setActiveTab('past')}
            >
              Past Sessions ({pastSessions.length})
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {activeTab === 'upcoming' && (
            <div className="space-y-4">
              {upcomingSessions.length === 0 ? (
                <div className="text-center py-8">
                  <Calendar className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-600">No upcoming sessions</p>
                  <Button className="mt-4">
                    <Plus className="w-4 h-4 mr-2" />
                    Schedule Session
                  </Button>
                </div>
              ) : (
                <div className="grid gap-4">
                  {upcomingSessions.map((session) => (
                    <SessionCard key={session.session_id} session={session} />
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'active' && (
            <div className="space-y-4">
              {activeSessions.length === 0 ? (
                <div className="text-center py-8">
                  <Video className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-600">No active sessions</p>
                </div>
              ) : (
                <div className="grid gap-4">
                  {activeSessions.map((session) => (
                    <SessionCard key={session.session_id} session={session} />
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'past' && (
            <div className="space-y-4">
              {pastSessions.length === 0 ? (
                <div className="text-center py-8">
                  <Clock className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-600">No past sessions</p>
                </div>
              ) : (
                <div className="grid gap-4">
                  {pastSessions.map((session) => (
                    <SessionCard key={session.session_id} session={session} showActions={false} />
                  ))}
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button variant="outline" className="h-20 flex-col">
              <Video className="w-6 h-6 mb-2" />
              Start Video Call
            </Button>
            <Button variant="outline" className="h-20 flex-col">
              <MessageSquare className="w-6 h-6 mb-2" />
              Send Message
            </Button>
            <Button variant="outline" className="h-20 flex-col">
              <Calendar className="w-6 h-6 mb-2" />
              Schedule Appointment
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};