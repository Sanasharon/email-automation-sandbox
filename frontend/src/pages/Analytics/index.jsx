// frontend/src/pages/Analytics/index.jsx
import React, { useEffect, useState } from 'react';
import { api } from '../../api/client';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js';
import { Activity } from 'lucide-react';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

export function Analytics() {
  const [summary, setSummary] = useState(null);
  const [recent, setRecent] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    async function load() {
      setLoading(true);
      try {
        const s = await api.getDashboardSummary();
        const r = await api.getRecentActivity();
        if (!mounted) return;
        setSummary(s || {});
        setRecent(Array.isArray(r) ? r : []);
      } catch (e) {
        console.error('Failed to load analytics', e);
      } finally {
        if (!mounted) return;
        setLoading(false);
      }
    }
    load();
    return () => { mounted = false; };
  }, []);

  const chartData = {
    labels: recent.map((a, i) => a.label ?? `Item ${i+1}`),
    datasets: [{
      label: 'Recent activity',
      data: recent.map(a => a.value ?? 0),
      backgroundColor: 'rgba(59,130,246,0.6)'
    }]
  };

  return (
    <div className="p-4">
      <div className="flex items-center gap-3 mb-4">
        <Activity className="w-6 h-6 text-gray-700" />
        <h1 className="text-2xl font-semibold">Analytics</h1>
      </div>

      {loading ? (
        <div className="text-sm text-gray-500">Loading analytics...</div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="p-4 border rounded-lg bg-white dark:bg-gray-800">
              <div className="text-xs text-gray-500">Total Workflows</div>
              <div className="text-2xl font-bold">{summary?.total_workflows ?? '—'}</div>
            </div>
            <div className="p-4 border rounded-lg bg-white dark:bg-gray-800">
              <div className="text-xs text-gray-500">Active Workflows</div>
              <div className="text-2xl font-bold">{summary?.active_workflows ?? '—'}</div>
            </div>
            <div className="p-4 border rounded-lg bg-white dark:bg-gray-800">
              <div className="text-xs text-gray-500">Errors</div>
              <div className="text-2xl font-bold">{summary?.errors ?? '—'}</div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
            <h3 className="font-semibold mb-3">Recent Activity</h3>
            {recent.length === 0 ? (
              <div className="text-sm text-gray-500">No recent activity.</div>
            ) : (
              <div className="max-w-2xl">
                <Bar data={chartData} />
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default Analytics;