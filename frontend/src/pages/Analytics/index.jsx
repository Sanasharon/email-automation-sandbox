// frontend/src/pages/Analytics/index.jsx
import React, { useEffect, useState } from 'react';
import { api } from '../../api/client';
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  LineElement,
  PointElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { BarChart3, Clock, AlertCircle, Tag, RefreshCw } from 'lucide-react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  LineElement,
  PointElement,
  Tooltip,
  Legend
);

const PRIORITY_COLORS = {
  High: '#ef4444',
  Medium: '#f59e0b',
  Low: '#22c55e',
  unset: '#9ca3af',
};

const CATEGORY_PALETTE = [
  '#2563eb', '#7c3aed', '#0891b2', '#d97706', '#dc2626', '#16a34a', '#db2777',
];

function KpiCard({ icon: Icon, label, value, hint }) {
  return (
    <div className="p-4 border rounded-xl bg-white dark:bg-gray-800 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <div className="text-xs font-medium text-gray-500 dark:text-gray-400">{label}</div>
        <Icon className="h-4 w-4 text-blue-600 dark:text-blue-400" />
      </div>
      <div className="mt-2 text-2xl font-bold text-gray-900 dark:text-white">{value}</div>
      {hint ? <div className="mt-1 text-xs text-gray-400">{hint}</div> : null}
    </div>
  );
}

function formatSeconds(seconds) {
  if (seconds === null || seconds === undefined) return '—';
  if (seconds < 60) return `${Math.round(seconds)}s`;
  if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
  return `${(seconds / 3600).toFixed(1)}h`;
}

export function Analytics() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [days, setDays] = useState(7);

  useEffect(() => {
    let mounted = true;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const s = await api.getAnalyticsSummary(days);
        if (!mounted) return;
        setSummary(s || {});
      } catch (e) {
        if (!mounted) return;
        console.error('Failed to load analytics', e);
        setError(e?.response?.data?.detail || e?.message || 'Failed to load analytics');
      } finally {
        if (!mounted) return;
        setLoading(false);
      }
    }
    load();
    return () => { mounted = false; };
  }, [days]);

  const categoryEntries = Object.entries(summary?.category_counts || {});
  const priorityEntries = Object.entries(summary?.priority_counts || {});
  const dailyTrend = summary?.daily_trend || [];

  const categoryChart = {
    labels: categoryEntries.map(([name]) => name),
    datasets: [{
      label: 'Emails',
      data: categoryEntries.map(([, count]) => count),
      backgroundColor: categoryEntries.map((_, i) => CATEGORY_PALETTE[i % CATEGORY_PALETTE.length]),
      borderRadius: 6,
    }],
  };

  const priorityChart = {
    labels: priorityEntries.map(([name]) => name),
    datasets: [{
      data: priorityEntries.map(([, count]) => count),
      backgroundColor: priorityEntries.map(([name]) => PRIORITY_COLORS[name] || '#9ca3af'),
      borderWidth: 0,
    }],
  };

  const trendChart = {
    labels: dailyTrend.map((d) => d.date),
    datasets: [{
      label: 'Emails received',
      data: dailyTrend.map((d) => d.count),
      borderColor: '#2563eb',
      backgroundColor: 'rgba(37,99,235,0.1)',
      tension: 0.3,
      fill: true,
      pointRadius: 3,
    }],
  };

  const chartOptions = {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { display: false } },
      y: { beginAtZero: true, ticks: { precision: 0 } },
    },
  };

  return (
    <div className="p-4 space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <BarChart3 className="w-6 h-6 text-gray-700 dark:text-gray-300" />
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Business Insights</h1>
        </div>
        <div className="flex items-center gap-2">
          {[7, 14, 30, 90].map((d) => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors ${
                days === d
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-700'
              }`}
            >
              {d}d
            </button>
          ))}
        </div>
      </div>

      {error ? (
        <div className="rounded-lg bg-red-50 p-4 border border-red-200 dark:bg-red-900/30 dark:border-red-800 text-sm text-red-700 dark:text-red-400">
          {error}
        </div>
      ) : null}

      {loading ? (
        <div className="text-sm text-gray-500">Loading analytics...</div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <KpiCard
              icon={BarChart3}
              label="Emails Processed"
              value={summary?.emails_processed ?? 0}
              hint={`last ${days} days`}
            />
            <KpiCard
              icon={Clock}
              label="Avg Processing Time"
              value={formatSeconds(summary?.avg_processing_time_seconds)}
              hint="classification + priority"
            />
            <KpiCard
              icon={AlertCircle}
              label="High Priority"
              value={`${summary?.high_priority_pct ?? 0}%`}
              hint="of processed emails"
            />
            <KpiCard
              icon={Tag}
              label="Categories Tracked"
              value={summary?.categories_tracked ?? 0}
              hint="distinct categories seen"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="bg-white dark:bg-gray-800 p-4 rounded-xl border dark:border-gray-700">
              <h3 className="font-semibold mb-3 text-gray-900 dark:text-white">Emails by Category</h3>
              {categoryEntries.length === 0 ? (
                <div className="text-sm text-gray-500 py-8 text-center">
                  No categorized emails yet — this fills in as the AI classification queue processes new emails.
                </div>
              ) : (
                <Bar data={categoryChart} options={chartOptions} />
              )}
            </div>

            <div className="bg-white dark:bg-gray-800 p-4 rounded-xl border dark:border-gray-700">
              <h3 className="font-semibold mb-3 text-gray-900 dark:text-white">Priority Breakdown</h3>
              {priorityEntries.length === 0 ? (
                <div className="text-sm text-gray-500 py-8 text-center">No priority data yet.</div>
              ) : (
                <div className="max-w-xs mx-auto">
                  <Doughnut data={priorityChart} options={{ plugins: { legend: { position: 'bottom' } } }} />
                </div>
              )}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 p-4 rounded-xl border dark:border-gray-700">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-900 dark:text-white">Daily Email Volume</h3>
              <RefreshCw className="h-4 w-4 text-gray-400" />
            </div>
            {dailyTrend.length === 0 ? (
              <div className="text-sm text-gray-500 py-8 text-center">No emails received in this window.</div>
            ) : (
              <Line data={trendChart} options={chartOptions} />
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default Analytics;
