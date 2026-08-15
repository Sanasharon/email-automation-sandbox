import { useEffect, useState, useCallback } from 'react';
import { Activity, Shield, AlertTriangle } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useLiveData } from '../../hooks/useLiveData';
import { api } from '../../api/client';

const Monitoring = () => {
  const { user } = useAuth();
  const [metrics, setMetrics] = useState([]);

  const fetchQueue = useCallback(() => api.getQueueStatus(), []);
  const { data: queue } = useLiveData(fetchQueue, 10000, []);

  const fetchStatus = useCallback(() => api.getSystemStatus(), []);
  const { data: status } = useLiveData(fetchStatus, 15000, []);

  const fetchLogs = useCallback(() => api.getProcessingLogs(20), []);
  const { data: logs } = useLiveData(fetchLogs, 10000, []);

  const fetchErrors = useCallback(() => api.getRecentErrors(20), []);
  const { data: errors } = useLiveData(fetchErrors, 10000, []);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const data = await api.getDashboardSummary();
        const cards = data?.cards || data?.data?.cards || [];
        setMetrics(cards);
      } catch (e) {
        setMetrics([]);
      }
    };
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 10000);
    return () => clearInterval(interval);
  }, []);
  
  if (user?.role !== 'Admin') {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <Shield className="w-16 h-16 text-red-500 mb-4" />
        <h2 className="text-xl font-bold text-white">Access Denied</h2>
        <p className="text-gray-300 mt-2">You don't have permission to perform this action.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Activity className="w-6 h-6 text-teal-400" />
          System Monitoring
        </h1>
        <p className="text-sm text-gray-300 mt-1">Real-time health and performance metrics for the backend engine.</p>
      </div>

      <div className="bg-slate-900 border border-slate-700/80 shadow-lg rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold text-white">Mailbox Sync Operations</h3>
            <p className="text-xs text-gray-400 mt-0.5">Real-time cursor tracking and background scheduler countdown</p>
          </div>
          <div className="flex items-center gap-2 bg-slate-800 border border-slate-700 px-3 py-1.5 rounded-lg text-xs font-medium text-teal-400">
            <span>Next Poll: 38s</span>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-slate-800/60 border border-slate-700/80 rounded-lg p-4 flex items-center justify-between">
            <div>
              <span className="text-sm font-semibold text-white">sanasharond2005@gmail.com</span>
              <p className="text-xs text-gray-400 mt-1">History Cursor: <span className="text-teal-400 font-mono">95935</span></p>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-green-900/60 text-green-300 border border-green-700/50 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"></span> Active (0 New)
            </span>
          </div>
          <div className="bg-slate-800/60 border border-slate-700/80 rounded-lg p-4 flex items-center justify-between">
            <div>
              <span className="text-sm font-semibold text-white">yemireddivinodh@gmail.com</span>
              <p className="text-xs text-gray-400 mt-1">History Cursor: <span className="text-teal-400 font-mono">95935</span></p>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-green-900/60 text-green-300 border border-green-700/50 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"></span> Active (0 New)
            </span>
          </div>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-700/80 shadow-lg rounded-xl p-6">
        <h3 className="text-lg font-bold text-white mb-4">Live Service Status</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-slate-800/60 rounded-lg border border-slate-700">
            <div className="flex items-center gap-3">
              <div className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse"></div>
              <span className="font-medium text-white">FastAPI Backend API</span>
            </div>
            <span className="text-sm text-green-400 font-medium">Operational</span>
          </div>
          <div className="flex items-center justify-between p-4 bg-slate-800/60 rounded-lg border border-slate-700">
            <div className="flex items-center gap-3">
              <div className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse"></div>
              <span className="font-medium text-white">Supabase Database</span>
            </div>
            <span className="text-sm text-green-400 font-medium">Operational</span>
          </div>
          <div className="flex items-center justify-between p-4 bg-slate-800/60 rounded-lg border border-slate-700">
            <div className="flex items-center gap-3">
              <div className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse"></div>
              <span className="font-medium text-white">Sync Orchestrator</span>
            </div>
            <span className="text-sm text-green-400 font-medium">Operational</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900 border border-slate-700/80 shadow-lg rounded-xl p-6">
          <h3 className="text-lg font-bold text-white mb-4">Gmail Sync Queue</h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span className="text-gray-300">Queued jobs</span><span className="font-bold text-white">{queue?.queued ?? '—'}</span></div>
            <div className="flex justify-between"><span className="text-gray-300">In progress</span><span className="font-bold text-white">{queue?.in_progress ?? '—'}</span></div>
            <div className="flex justify-between"><span className="text-gray-300">Completed (1h)</span><span className="font-bold text-white">{queue?.completed_1h ?? '—'}</span></div>
            <div className="flex justify-between"><span className="text-gray-300">Failed (1h)</span><span className="font-bold text-red-400">{queue?.failed_1h ?? '—'}</span></div>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-700/80 shadow-lg rounded-xl p-6">
          <h3 className="text-lg font-bold text-white mb-1">AI Task Queue</h3>
          <p className="text-xs text-gray-400 mb-3">Classification & priority scoring</p>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span className="text-gray-300">Pending</span><span className="font-bold text-white">{queue?.ai_task_queue?.pending ?? '—'}</span></div>
            <div className="flex justify-between"><span className="text-gray-300">Processing</span><span className="font-bold text-white">{queue?.ai_task_queue?.processing ?? '—'}</span></div>
            <div className="flex justify-between"><span className="text-gray-300">Completed (1h)</span><span className="font-bold text-white">{queue?.ai_task_queue?.completed_1h ?? '—'}</span></div>
            <div className="flex justify-between"><span className="text-gray-300">Failed (1h)</span><span className="font-bold text-red-400">{queue?.ai_task_queue?.failed_1h ?? '—'}</span></div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900 border border-slate-700/80 shadow-lg rounded-xl p-6">
          <h3 className="text-lg font-bold text-white mb-4">System Health</h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span className="text-gray-300">Health score</span><span className="font-bold text-white">{status?.health_score != null ? `${status.health_score}%` : '—'}</span></div>
            <div className="flex justify-between"><span className="text-gray-300">Scheduler</span><span className="font-bold text-white">{status?.scheduler?.is_running ? 'Running' : 'Stopped'}</span></div>
            <div className="flex justify-between"><span className="text-gray-300">Sync interval</span><span className="font-bold text-white">{status?.scheduler?.interval_minutes != null ? `${status.scheduler.interval_minutes} min` : '—'}</span></div>
            <div className="flex justify-between"><span className="text-gray-300">Total emails</span><span className="font-bold text-white">{status?.database?.total_emails ?? '—'}</span></div>
          </div>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-700/80 shadow-lg rounded-xl p-6">
        <h3 className="text-lg font-bold text-white mb-4">Processing Logs</h3>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-400 border-b border-slate-700">
              <th className="py-2 pr-4 font-medium">Time</th>
              <th className="py-2 pr-4 font-medium">Event</th>
              <th className="py-2 pr-4 font-medium">Detail</th>
              <th className="py-2 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {(logs || []).map((log, idx) => (
              <tr key={idx} className="border-b border-slate-800 last:border-0">
                <td className="py-2 pr-4 text-gray-300">{log.time ? new Date(log.time).toLocaleTimeString() : '—'}</td>
                <td className="py-2 pr-4 text-white font-medium">{log.event}</td>
                <td className="py-2 pr-4 text-gray-300">{log.detail}</td>
                <td className="py-2">
                  <span className={`text-xs font-bold px-2 py-0.5 rounded-full uppercase ${log.status === 'success' ? 'bg-green-900/60 text-green-300' : log.status === 'failed' ? 'bg-red-900/60 text-red-300' : 'bg-yellow-900/60 text-yellow-300'}`}>
                    {log.status}
                  </span>
                </td>
              </tr>
            ))}
            {(!logs || logs.length === 0) && (
              <tr><td colSpan={4} className="py-4 text-center text-gray-400">No processing logs yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="bg-slate-900 border border-slate-700/80 shadow-lg rounded-xl p-6">
        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-red-500" /> Recent Errors
        </h3>
        {(!errors || errors.length === 0) ? (
          <p className="text-sm text-gray-300">No recent errors.</p>
        ) : (
          <div className="space-y-3">
            {errors.map((err, idx) => (
              <div key={idx} className="flex items-start gap-3 text-sm border-b border-slate-800 last:border-0 pb-3 last:pb-0">
                <span className="text-gray-400 w-16 flex-shrink-0">{err.time ? new Date(err.time).toLocaleTimeString() : '—'}</span>
                <span className="font-medium text-white w-28 flex-shrink-0">{err.source}</span>
                <span className="text-gray-300">{err.message}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Monitoring;