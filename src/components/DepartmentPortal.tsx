import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Activity, Users, Clock, CheckCircle, XCircle, Phone } from 'lucide-react';
import { wsService } from '@/services/wsService';
import { useToast } from "@/components/ui/use-toast";
import apiClient from '@/services/apiClient';

export default function DepartmentPortal() {
  const { id } = useParams();
  const { toast } = useToast();
  const [dept, setDept] = useState<any>({ id, name: `Department ${id}`, is_active: true, avg_wait_time: 12 });
  const [queue, setQueue] = useState<any[]>([
    { id: 1, ticket: 'A201', patient_name: 'Anna', service: 'Consult', wait_seconds: 90, status: 'waiting' },
    { id: 2, ticket: 'A202', patient_name: 'Ben', service: 'X-ray', wait_seconds: 300, status: 'waiting' }
  ]);
  const [staff, setStaff] = useState<any[]>([
    { id: 1, name: 'Dr. Smith', role: 'Lead' },
    { id: 2, name: 'Nurse Joy', role: 'Nurse' }
  ]);
  const [loading, setLoading] = useState(false);
  const [serviceId, setServiceId] = useState<number | null>(null);

  useEffect(() => {
    // Fetch services for this department
    const fetchServices = async () => {
      try {
        const response = await apiClient.get('/services');
        const departmentServices = response.data.filter((s: any) => 
          s.department?.toLowerCase() === id?.toLowerCase()
        );
        if (departmentServices.length > 0) {
          setServiceId(departmentServices[0].id);
        }
      } catch (error) {
        console.error('Failed to fetch services:', error);
      }
    };
    
    fetchServices();

    let unsubscribe: (() => void) | undefined;
    // subscribe to department WS channel if enabled
    wsService.connect().then(() => {
      unsubscribe = wsService.subscribe((data) => {
        if (data.type === 'queue_update' && data.department_id === Number(id)) {
          setQueue(data.queue || []);
        }
      });
    }).catch(() => {
      // ignore if ws disabled
    });

    return () => {
      unsubscribe?.();
    };
  }, [id]);

  const callNext = async () => {
    if (!serviceId) {
      toast({
        title: "Service not found",
        description: "Unable to determine service for this department.",
        variant: "destructive"
      });
      return;
    }

    if (queue.length === 0) {
      toast({
        title: "No patients in queue",
        description: "There are no waiting patients to call.",
        variant: "destructive"
      });
      return;
    }

    const nextPatient = queue.find(q => q.status === 'waiting');
    if (!nextPatient) {
      toast({
        title: "No waiting patients",
        description: "All patients have been called.",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      // Try to call the backend API with correct parameters
      const response = await apiClient.post('/queue/call-next', {
        service_id: serviceId,
        counter_name: `${id} Counter 1`
      });

      const calledPatient = response.data.called_patient;
      toast({
        title: "Patient Called",
        description: `Ticket #${calledPatient.queue_number} called to ${response.data.counter_name}`,
      });

      // Update local queue state
      setQueue(prev => prev.map((q) => q.id === nextPatient.id ? { ...q, status: 'called' } : q));
    } catch (error: any) {
      console.error('Failed to call next patient:', error);
      
      // Fallback to local update if API fails
      setQueue(prev => prev.map((q) => q.id === nextPatient.id ? { ...q, status: 'called' } : q));
      
      const errorMessage = error?.response?.data?.detail || 'Using offline mode';
      toast({
        title: "Patient Called (Offline)",
        description: `Called ${nextPatient.patient_name} - Ticket: ${nextPatient.ticket}. ${errorMessage}`,
      });
    } finally {
      setLoading(false);
    }
  };

  const markServed = async (ticketId: number) => {
    setQueue(prev => prev.map(q => q.id === ticketId ? { ...q, status: 'served' } : q));
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">{dept.name}</h1>
            <div className="text-sm text-gray-600">Avg wait: {dept.avg_wait_time}m</div>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${wsService.isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <Button size="sm" variant="ghost" onClick={async () => { try { await wsService.connect(); } catch {} }}>Reconnect</Button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2"><Activity className="h-5 w-5" /> Live Queue</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-end mb-2">
                    <Button 
                      onClick={callNext} 
                      disabled={loading || queue.length === 0}
                      className="flex items-center gap-2"
                    >
                      <Phone className="h-4 w-4" />
                      {loading ? 'Calling...' : 'Call Next'}
                    </Button>
                  </div>
                  {queue.map(q => (
                    <div key={q.id} className="flex justify-between items-center border rounded p-2">
                      <div>
                        <div className="font-medium">{q.ticket} — {q.patient_name}</div>
                        <div className="text-sm text-gray-500">{q.service}</div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="text-sm text-gray-700">{Math.round(q.wait_seconds/60)}m</div>
                        {q.status === 'served' ? <CheckCircle className="h-5 w-5 text-green-600" /> : <XCircle className="h-5 w-5 text-gray-400" />}
                        <Button size="sm" onClick={() => markServed(q.id)}>Mark Served</Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          <div>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2"><Users className="h-5 w-5" /> On Duty</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {staff.map(s => (
                    <div key={s.id} className="flex justify-between items-center p-2 border rounded">
                      <div>{s.name}</div>
                      <div className="text-sm text-gray-500">{s.role}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card className="mt-4">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2"><Clock className="h-5 w-5" /> Today</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-gray-600">No scheduled items (mock)</div>
              </CardContent>
            </Card>
          </div>
        </div>

      </div>
    </div>
  );
}
