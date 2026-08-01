import { useEffect, useState, useRef, useCallback } from 'react';
import Chart from 'chart.js/auto';
import { Activity, Shield, AlertTriangle } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useLiveData } from '../../hooks/useLiveData';
import { api } from '../../api/client';

const Monitoring = () => {
  const { user } = useAuth();
  const [metrics, setMetrics] = useState([]);
  const chartRef = useRef(null);
  const chartInstance = useRef(null);

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

  // Render chart when metrics update
  useEffect(() => {
    if (metrics.length && chartRef.current) {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
      const ctx = chartRef.current.getContext('2d');
      const data = {
        labels: metrics.map(m => m.title),
        datasets: [{
          label: 'Current Metrics',
          data: metrics.map(m => Number(m.val.replace(/[^0-9\.]/g, ''))),
          backgroundColor: metrics.map(m => {
            // simple color mapping based on Tailwind bg class
            const colorMap = {
              'bg-blue-100': 'rgba(59,130,246,0.6)',
              'bg-purple-100': 'rgba(139,92,246,0.6)',
              'bg-green-100': 'rgba(34,197,94,0.6)',
              'bg-yellow-100': 'rgba(234,179,8,0.6)',
              'bg-red-100': 'rgba(239,68,68,0.6)'
            };
            return colorMap[m.color] || 'rgba(100,100,100,0.6)';
          })
        }]
      };
      chartInstance.current = new Chart(ctx, {
        type: 'bar',
        data,
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: true } }
        }
      });
    }
  }, [metrics]);
  
  if (user?.role !== 'Admin') {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <Shield className="w-16 h-16 text-red-500 mb-4" />
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">Access Denied</h2>
        <p className="text-gray-500 mt-2">You don't have permission to perform this action.</p>
      </div>
    );
  }

  // metrics state is populated from API; fallback to empty array

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <Activity className="w-6 h-6 text-teal-600" />
          System Monitoring
        </h1>
        <p className="text-sm text-gray-500 mt-1">Real-time health and performance metrics for the backend engine.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {metrics.map((m, idx) => (
          <div key={idx} className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 flex items-center gap-4">
            <div className={`w-12 h-12 rounded-full ${m.color} dark:bg-opacity-20 flex items-center justify-center`}>
              <Activity className="w-5 h-5 text-gray-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{m.title}</p>
              <h4 className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{m.val}</h4>
            </div>
          </div>
        ))}
      <canvas ref={chartRef} className="w-full h-64 mt-4"></canvas>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Live Service Status</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-100 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <div className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse"></div>
              <span className="font-medium text-gray-900 dark:text-white">FastAPI Backend API</span>
            </div>
            <span className="text-sm text-green-600 dark:text-green-400 font-medium">Operational</span>
          </div>
          <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-100 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <div className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse"></div>
              <span className="font-medium text-gray-900 dark:text-white">Supabase Database</span>
            </div>
            <span className="text-sm text-green-600 dark:text-green-400 font-medium">Operational</span>
          </div>
          <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-100 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <div className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse"></div>
              <span className="font-medium text-gray-900 dark:text-white">Sync Orchestrator</span>
            </div>
            <span className="text-sm text-green-600 dark:text-green-400 font-medium">Operational</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Queue Activity</h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span className="text-gray-500">Queued jobs</span><span className="font-medium text-gray-900 dark:text-white">{queue?.queued ?? '—'}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">In progress</span><span className="font-medium text-gray-900 dark:text-white">{queue?.in_progress ?? '—'}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Completed (1h)</span><span className="font-medium text-gray-900 dark:text-white">{queue?.completed_1h ?? '—'}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Failed (1h)</span><span className="font-medium text-red-600">{queue?.failed_1h ?? '—'}</span></div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">System Health</h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span className="text-gray-500">Health score</span><span className="font-medium text-gray-900 dark:text-white">{status?.health_score != null ? `${status.health_score}%` : '—'}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Scheduler</span><span className="font-medium text-gray-900 dark:text-white">{status?.scheduler?.is_running ? 'Running' : 'Stopped'}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Sync interval</span><span className="font-medium text-gray-900 dark:text-white">{status?.scheduler?.interval_minutes != null ? `${status.scheduler.interval_minutes} min` : '—'}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Total emails</span><span className="font-medium text-gray-900 dark:text-white">{status?.database?.total_emails ?? '—'}</span></div>
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Processing Logs</h3>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b border-gray-200 dark:border-gray-700">
              <th className="py-2 pr-4 font-medium">Time</th>
              <th className="py-2 pr-4 font-medium">Event</th>
              <th className="py-2 pr-4 font-medium">Detail</th>
              <th className="py-2 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {(logs || []).map((log, idx) => (
              <tr key={idx} className="border-b border-gray-100 dark:border-gray-700 last:border-0">
                <td className="py-2 pr-4 text-gray-500">{log.time ? new Date(log.time).toLocaleTimeString() : '—'}</td>
                <td className="py-2 pr-4 text-gray-900 dark:text-white">{log.event}</td>
                <td className="py-2 pr-4 text-gray-500">{log.detail}</td>
                <td className="py-2">
                  <span className={`text-xs font-bold px-2 py-0.5 rounded-full uppercase ${log.status === 'success' ? 'bg-green-100 text-green-700' : log.status === 'failed' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'}`}>
                    {log.status}
                  </span>
                </td>
              </tr>
            ))}
            {(!logs || logs.length === 0) && (
              <tr><td colSpan={4} className="py-4 text-center text-gray-500">No processing logs yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-red-500" /> Recent Errors
        </h3>
        {(!errors || errors.length === 0) ? (
          <p className="text-sm text-gray-500">No recent errors.</p>
        ) : (
          <div className="space-y-3">
            {errors.map((err, idx) => (
              <div key={idx} className="flex items-start gap-3 text-sm border-b border-gray-100 dark:border-gray-700 last:border-0 pb-3 last:pb-0">
                <span className="text-gray-500 w-16 flex-shrink-0">{err.time ? new Date(err.time).toLocaleTimeString() : '—'}</span>
                <span className="font-medium text-gray-900 dark:text-white w-28 flex-shrink-0">{err.source}</span>
                <span className="text-gray-500">{err.message}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Monitoring;
