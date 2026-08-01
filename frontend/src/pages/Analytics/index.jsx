import { useEffect, useRef, useCallback } from 'react';
import Chart from 'chart.js/auto';
import { useLiveData } from '../../hooks/useLiveData';
import { api } from '../../api/client';
import { KpiCard } from '../../components/KpiCard';
import { LoadingSkeleton } from '../../components/LoadingSkeleton';

const useChart = (canvasRef, buildConfig, deps) => {
  const chartInstance = useRef(null);
  useEffect(() => {
    if (!canvasRef.current) return;
    const config = buildConfig();
    if (!config) return;
    if (chartInstance.current) chartInstance.current.destroy();
    chartInstance.current = new Chart(canvasRef.current.getContext('2d'), config);
    return () => chartInstance.current?.destroy();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
};

const ChartCard = ({ title, children }) => (
  <div className="flat-card p-5 flex flex-col gap-3">
    <span className="text-label-md text-on-surface-variant font-medium">{title}</span>
    <div className="relative h-[220px]">{children}</div>
  </div>
);

export const Analytics = () => {
  const fetchSummary = useCallback(() => api.getAnalyticsSummary(7), []);
  const { data: stats, loading, error } = useLiveData(fetchSummary, 15000, []);

  const categoryRef = useRef(null);
  const priorityRef = useRef(null);
  const trendRef = useRef(null);
  const processingRef = useRef(null);

  useChart(categoryRef, () => {
    if (!stats?.category_counts) return null;
    return {
      type: 'bar',
      data: {
        labels: Object.keys(stats.category_counts),
        datasets: [{ data: Object.values(stats.category_counts), backgroundColor: 'rgba(59,130,246,0.6)' }],
      },
      options: { plugins: { legend: { display: false } }, maintainAspectRatio: false },
    };
  }, [stats]);

  useChart(priorityRef, () => {
    if (!stats?.priority_counts) return null;
    return {
      type: 'doughnut',
      data: {
        labels: Object.keys(stats.priority_counts),
        datasets: [{
          data: Object.values(stats.priority_counts),
          backgroundColor: ['rgba(239,68,68,0.7)', 'rgba(234,179,8,0.7)', 'rgba(34,197,94,0.7)', 'rgba(148,163,184,0.7)'],
        }],
      },
      options: { maintainAspectRatio: false },
    };
  }, [stats]);

  useChart(trendRef, () => {
    if (!stats?.daily_trend) return null;
    return {
      type: 'line',
      data: {
        labels: stats.daily_trend.map((d) => d.date),
        datasets: [{ data: stats.daily_trend.map((d) => d.count), borderColor: 'rgba(59,130,246,1)', backgroundColor: 'rgba(59,130,246,0.15)', fill: true, tension: 0.3 }],
      },
      options: { plugins: { legend: { display: false } }, maintainAspectRatio: false },
    };
  }, [stats]);

  useChart(processingRef, () => {
    if (!stats?.processing_time_trend) return null;
    return {
      type: 'line',
      data: {
        labels: stats.processing_time_trend.map((d) => d.date),
        datasets: [{ data: stats.processing_time_trend.map((d) => d.avg_seconds), borderColor: 'rgba(139,92,246,1)', backgroundColor: 'rgba(139,92,246,0.15)', fill: true, tension: 0.3 }],
      },
      options: { plugins: { legend: { display: false } }, maintainAspectRatio: false },
    };
  }, [stats]);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-display-lg font-display-lg text-on-surface">Analytics &amp; Business Insights</h1>
        <p className="text-body-md text-on-surface-variant mt-1">Category counts, priority breakdown, daily trends and processing time.</p>
      </div>

      {error && <div className="text-body-md text-error">{error}</div>}

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array(4).fill(0).map((_, i) => <LoadingSkeleton key={i} type="card" />)}
        </div>
      ) : (
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiCard label="Emails processed (7d)" value={(stats?.emails_processed ?? 0).toLocaleString()} />
          <KpiCard label="Avg processing time" value={stats?.avg_processing_time_seconds != null ? `${stats.avg_processing_time_seconds}s` : '—'} />
          <KpiCard label="High priority share" value={`${stats?.high_priority_pct ?? 0}%`} status="error" />
          <KpiCard label="Categories tracked" value={stats?.categories_tracked ?? 0} />
        </section>
      )}

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ChartCard title="Category counts">
          <canvas ref={categoryRef} />
        </ChartCard>
        <ChartCard title="Priority breakdown">
          <canvas ref={priorityRef} />
        </ChartCard>
        <ChartCard title="Daily email trend">
          <canvas ref={trendRef} />
        </ChartCard>
        <ChartCard title="Processing time">
          <canvas ref={processingRef} />
        </ChartCard>
      </section>
    </div>
  );
};

export default Analytics;
