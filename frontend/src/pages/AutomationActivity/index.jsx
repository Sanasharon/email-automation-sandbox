import { useLiveData } from '../../hooks/useLiveData';
import { api } from '../../api/client';
import { StatusBadge } from '../../components/StatusBadge';
import { ActivityTimeline } from '../../components/ActivityTimeline';
import { LoadingSkeleton } from '../../components/LoadingSkeleton';
import { Activity, Clock } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

export const AutomationActivity = () => {
  const { data: currentTask, loading: loadingTask } = useLiveData(api.getCurrentTask, 5000);
  const { data: queueData, loading: loadingQueue } = useLiveData(api.getAutomationQueue, 5000);
  const { data: historyData, loading: loadingHistory, lastUpdated, error } = useLiveData(api.getAutomationHistory, 10000);

  const [timeAgo, setTimeAgo] = useState('just now');

  useEffect(() => {
    if (!lastUpdated) return;
    const interval = setInterval(() => {
      const seconds = Math.floor((new Date() - lastUpdated) / 1000);
      if (seconds < 5) setTimeAgo('just now');
      else if (seconds < 60) setTimeAgo(`${seconds}s ago`);
      else setTimeAgo(`${Math.floor(seconds / 60)}m ago`);
    }, 1000);
    return () => clearInterval(interval);
  }, [lastUpdated]);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <h2 className="font-headline-sm text-on-surface">Live Automation Activity</h2>
        <div className="flex items-center gap-2">
          {error && <span className="text-[10px] text-error font-bold uppercase tracking-widest bg-error-container px-2 py-1 rounded">Connection Issue</span>}
          <span className="text-label-md text-on-surface-variant flex items-center gap-1">
            <Clock size={14} /> Last updated {timeAgo}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Current Task & Queue */}
        <div className="lg:col-span-1 flex flex-col gap-6">
          <div className="flat-card border-primary/20 bg-primary-fixed-dim/10">
            <div className="px-6 py-4 border-b border-primary/10 flex justify-between items-center">
              <h3 className="font-label-bold text-primary uppercase tracking-wider flex items-center gap-2">
                <Activity size={16} className="animate-pulse" /> Current Task
              </h3>
            </div>
            <div className="p-6">
              {loadingTask ? <LoadingSkeleton type="card" /> : currentTask ? (
                <div className="flex flex-col gap-4">
                  <div>
                    <h4 className="font-headline-sm text-on-surface mb-1">{currentTask.task_name}</h4>
                    <p className="text-label-md text-on-surface-variant">{currentTask.description}</p>
                  </div>
                  
                  <div className="flex flex-col gap-2">
                    <div className="flex justify-between text-label-md">
                      <span className="font-bold text-primary">{currentTask.progress}% Complete</span>
                      <span className="text-on-surface-variant">ETA: {currentTask.eta_seconds}s</span>
                    </div>
                    <div className="w-full bg-surface-container-high rounded-full h-2 overflow-hidden">
                      <div 
                        className="bg-primary h-2 rounded-full transition-all duration-1000 ease-in-out" 
                        style={{ width: `${currentTask.progress}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-4 text-on-surface-variant text-body-md">No task running</div>
              )}
            </div>
          </div>

          <div className="flat-card">
            <div className="px-6 py-4 bg-[#F6F8FA] border-b border-outline-variant">
              <h3 className="font-label-bold text-on-surface uppercase tracking-wider">Execution Queue ({queueData?.data?.length || 0})</h3>
            </div>
            <div className="divide-y divide-outline-variant max-h-[300px] overflow-y-auto">
              {loadingQueue ? <LoadingSkeleton type="table" rows={3} /> : queueData?.data?.length > 0 ? (
                queueData.data.map(q => (
                  <div key={q.task_id} className="px-6 py-3 flex justify-between items-center">
                    <div>
                      <p className="font-body-md text-on-surface font-medium">{q.task_name}</p>
                      <p className="text-label-md text-on-surface-variant">Est. {q.estimated_time}</p>
                    </div>
                    <StatusBadge status={q.status} />
                  </div>
                ))
              ) : (
                <div className="px-6 py-8 text-center text-on-surface-variant text-body-md">Queue is empty</div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: History Timeline */}
        <div className="lg:col-span-2 flat-card">
          <div className="px-6 py-4 bg-[#F6F8FA] border-b border-outline-variant flex justify-between items-center">
            <h3 className="font-label-bold text-on-surface uppercase tracking-wider">Recent History</h3>
            <Link to="/automation/logs" className="text-primary text-label-bold uppercase hover:underline">
              View Full Logs
            </Link>
          </div>
          {loadingHistory ? (
            <div className="p-6"><LoadingSkeleton type="table" rows={6} /></div>
          ) : (
            <ActivityTimeline activities={historyData?.data} />
          )}
        </div>
        
      </div>
    </div>
  );
};
