import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLiveData } from '../../hooks/useLiveData';
import { api } from '../../api/client';
import { KpiCard } from '../../components/KpiCard';
import { ActivityTimeline } from '../../components/ActivityTimeline';
import { LoadingSkeleton } from '../../components/LoadingSkeleton';
import { Mail, ArrowRight, CheckCircle2 } from 'lucide-react';
import { useMailbox } from '../../context/MailboxContext';

// Charts
import { Bar, Pie, Line } from 'react-chartjs-2';
import 'chart.js/auto';

export const DashboardOverview = () => {
  const navigate = useNavigate();
  const { isConnected, loading: mailboxLoading } = useMailbox();

  const { data: summary, loading: summaryLoading } = useLiveData(
    api.getDashboardSummary,
    5000,
    [isConnected],
    isConnected
  );
  const { data: recentActivity, loading: activityLoading } = useLiveData(
    api.getRecentActivity,
    5000,
    [isConnected],
    isConnected
  );

  // Analytics state (Business Insights)
  const [analyticsSummary, setAnalyticsSummary] = useState(null);
  const [dailyTrends, setDailyTrends] = useState(null);
  const [processingTimes, setProcessingTimes] = useState(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const analyticsIntervalRef = useRef(null);

  const fetchAnalytics = async () => {
    setAnalyticsLoading(true);
    try {
      const [sRes, dRes, pRes] = await Promise.all([
        fetch('/api/v1/analytics/summary', { credentials: 'include' }),
        fetch('/api/v1/analytics/daily_trends?days=30', { credentials: 'include' }),
        fetch('/api/v1/analytics/processing_times?days=30', { credentials: 'include' }),
      ]);

      if (sRes.ok) {
        const sJson = await sRes.json();
        setAnalyticsSummary(sJson);
      } else {
        console.warn('analytics/summary returned', sRes.status);
      }

      if (dRes.ok) {
        const dJson = await dRes.json();
        setDailyTrends(dJson);
      } else {
        console.warn('analytics/daily_trends returned', dRes.status);
      }

      if (pRes.ok) {
        const pJson = await pRes.json();
        setProcessingTimes(pJson);
      } else {
        console.warn('analytics/processing_times returned', pRes.status);
      }
    } catch (err) {
      console.error('Failed to fetch analytics', err);
    } finally {
      setAnalyticsLoading(false);
    }
  };

  useEffect(() => {
    // Start polling analytics only when connected
    if (isConnected) {
      // initial fetch
      fetchAnalytics();
      // poll every 60s
      analyticsIntervalRef.current = setInterval(fetchAnalytics, 60_000);
    }

    return () => {
      if (analyticsIntervalRef.current) {
        clearInterval(analyticsIntervalRef.current);
        analyticsIntervalRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isConnected]);

  // Prepare chart data safely
  const categoryLabels = (analyticsSummary?.category_counts || []).map(c => c.category_name);
  const categoryData = (analyticsSummary?.category_counts || []).map(c => c.count);

  const priorityLabels = (analyticsSummary?.priority_counts || []).map(p => p.priority);
  const priorityData = (analyticsSummary?.priority_counts || []).map(p => p.count);

  const trendLabels = (dailyTrends?.data || []).map(d => d.day);
  const trendValues = (dailyTrends?.data || []).map(d => d.count);

  const avgProcessingSec = processingTimes?.avg_seconds;
  const avgProcessingDisplay = avgProcessingSec ? `${Math.round(avgProcessingSec)}s` : 'N/A';

  return (
    <div className="flex flex-col gap-8">
      {/* Connection State Onboarding Banner */}
      {!mailboxLoading && !isConnected && (
        <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-2xl p-6 md:p-8 shadow-md flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-white/20 text-white backdrop-blur-sm">
              <Mail className="w-3.5 h-3.5 mr-1.5" /> Setup Required
            </div>
            <h2 className="text-xl md:text-2xl font-bold">Connect your Gmail Account to start automation</h2>
            <p className="text-sm text-blue-100 leading-relaxed">
              Workflows, automated categorization, and email monitoring are currently paused. Connect your Google OAuth account to begin parsing emails in real time.
            </p>
          </div>
          <button
            onClick={() => navigate('/settings')}
            className="bg-white text-blue-700 hover:bg-blue-50 font-bold px-6 py-3 rounded-xl text-sm transition-all shadow-sm flex items-center gap-2 whitespace-nowrap"
          >
            Connect Gmail Account <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* KPI Grid - Only show when connected */}
      {isConnected && (
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          {summaryLoading ? (
            Array(6).fill(0).map((_, i) => <LoadingSkeleton key={i} type="card" />)
          ) : summary ? (
            <>
              <KpiCard label="Total Workflows" value={(summary.total_workflows ?? 0).toLocaleString()} />
              <KpiCard label="Active Workflows" value={(summary.active_workflows ?? 0).toLocaleString()} trend={{ value: '4%', direction: 'up' }} status="success" />
              <KpiCard label="Emails Processed" value={(summary.emails_processed ?? 0) >= 1000 ? ((summary.emails_processed / 1000).toFixed(1) + 'k') : (summary.emails_processed ?? 0).toLocaleString()} />
              <KpiCard label="Failed Executions" value={(summary.failed_executions ?? 0).toLocaleString()} trend={{ value: '8%', direction: 'down' }} status="error" />
              <KpiCard label="Pending Jobs" value={(summary.pending_jobs ?? 0).toLocaleString()} />
              <KpiCard label="System Health" value={`${summary.system_health_percent ?? 0}%`} status="success" />
            </>
          ) : (
            Array(6).fill(0).map((_, i) => <KpiCard key={i} label="—" value="—" />)
          )}
        </section>
      )}

      {/* Business Insights Section (analytics) */}
      {isConnected && (
        <section className="flat-card p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="font-headline-sm text-headline-sm text-on-surface">Business Insights</h2>
            <div className="text-sm text-on-surface-variant">Updated every 60s</div>
          </div>

          {analyticsLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {Array(4).fill(0).map((_, i) => <LoadingSkeleton key={i} type="card" />)}
            </div>
          ) : analyticsSummary ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <KpiCard label="Total Emails" value={(analyticsSummary.totals?.total_emails ?? 0).toLocaleString()} />
                <KpiCard label="Processed" value={(analyticsSummary.totals?.processed_count ?? 0).toLocaleString()} />
                <KpiCard label="Backlog" value={(analyticsSummary.totals?.processing_backlog ?? 0).toLocaleString()} />
                <KpiCard label="Avg Processing" value={avgProcessingDisplay} />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                <div className="bg-white p-4 rounded-md shadow-sm">
                  <h4 className="mb-2">Category counts</h4>
                  <Bar
                    data={{
                      labels: categoryLabels,
                      datasets: [{ label: 'Emails', data: categoryData, backgroundColor: 'rgba(54,162,235,0.8)' }]
                    }}
                    options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }}
                    height={220}
                  />
                </div>

                <div className="bg-white p-4 rounded-md shadow-sm">
                  <h4 className="mb-2">Priority distribution</h4>
                  <Pie
                    data={{
                      labels: priorityLabels,
                      datasets: [{ data: priorityData, backgroundColor: ['#ef4444', '#f59e0b', '#10b981', '#6b7280'] }]
                    }}
                    options={{ responsive: true, maintainAspectRatio: false }}
                    height={220}
                  />
                </div>

                <div className="bg-white p-4 rounded-md shadow-sm">
                  <h4 className="mb-2">Daily email trends (30 days)</h4>
                  <Line
                    data={{
                      labels: trendLabels,
                      datasets: [{ label: 'Received', data: trendValues, borderColor: 'rgba(75,192,192,1)', backgroundColor: 'rgba(75,192,192,0.08)', fill: true }]
                    }}
                    options={{ responsive: true, maintainAspectRatio: false }}
                    height={220}
                  />
                </div>
              </div>

              <div className="mt-6">
                <h4 className="mb-2">Tasks & Monitoring</h4>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <KpiCard label="Pending tasks" value={(analyticsSummary.task_summary?.pending_tasks ?? 0).toLocaleString()} />
                  <KpiCard label="Failed (24h)" value={(analyticsSummary.task_summary?.failed_tasks_last_24h ?? 0).toLocaleString()} />
                  <KpiCard label="Processing rate" value={`${((analyticsSummary.totals?.processed_count ?? 0) / Math.max(1, analyticsSummary.totals?.total_emails ?? 1) * 100).toFixed(1)}%`} />
                </div>
              </div>
            </>
          ) : (
            <div className="text-sm text-on-surface-variant">Analytics data not available.</div>
          )}
        </section>
      )}

      {/* Line Chart Area - Only show when connected */}
      {isConnected && (
        <section className="flat-card p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="font-headline-sm text-headline-sm text-on-surface">Email Processing Volume</h2>
            <div className="flex gap-4">
              <span className="text-label-md text-on-surface-variant flex items-center gap-1">
                <span className="w-3 h-3 bg-primary block rounded-full"></span> Incoming
              </span>
              <span className="text-label-md text-on-surface-variant flex items-center gap-1">
                <span className="w-3 h-3 bg-secondary block rounded-full"></span> Automated
              </span>
            </div>
          </div>

          <div className="h-64 w-full flex items-end justify-between gap-1 border-b border-l border-outline-variant pb-1 pl-1">
            <div className="relative w-full h-full flex flex-col justify-end pb-[10px]">
               <div className="absolute inset-0 flex flex-col justify-between pointer-events-none mb-[10px]">
                 <div className="border-t border-outline-variant/30 w-full h-px"></div>
                 <div className="border-t border-outline-variant/30 w-full h-px"></div>
                 <div className="border-t border-outline-variant/30 w-full h-px"></div>
                 <div className="border-t border-outline-variant/30 w-full h-px"></div>
               </div>

               {summaryLoading ? (
                  <div className="w-full h-full bg-surface-container-low animate-pulse"></div>
                ) : (
                  (() => {
                    const series = summary?.email_volume_series || [];
                    if (series.length < 2) return null;

                    const maxVal = Math.max(...series.map(d => Math.max(d.incoming, 1)));
                    const points = series.map((d, i) => {
                      const x = (i / (series.length - 1)) * 1000;
                      const y = 100 - ((d.incoming / maxVal) * 80);
                      return `${x},${y}`;
                    }).join(' ');

                    return (
                      <svg className="w-full h-[calc(100%-10px)] absolute bottom-[10px]" preserveAspectRatio="none" viewBox="0 0 1000 100">
                         <polyline fill="none" points={points} stroke="#0051ae" strokeWidth="2"></polyline>
                         <path d={`M0,100 L${points} L1000,100 Z`} fill="rgba(0, 81, 174, 0.05)"></path>
                      </svg>
                    );
                  })()
                )}
            </div>
          </div>

          <div className="flex justify-between mt-2 text-[10px] text-on-surface-variant font-bold uppercase tracking-tighter">
            {summary?.email_volume_series ? summary.email_volume_series.map((pt, i) => (
               <span key={i}>{pt.time} {parseInt(pt.time) < 12 ? 'AM' : 'PM'}</span>
            )) : (
               <>
                  <span>08:00 AM</span>
                  <span>10:00 AM</span>
                  <span>12:00 PM</span>
                  <span>02:00 PM</span>
                  <span>04:00 PM</span>
                  <span>06:00 PM</span>
                  <span>08:00 PM</span>
               </>
            )}
          </div>
        </section>
      )}

      {/* Recent Activity - Only show when connected */}
      {isConnected && (
        <section className="flat-card overflow-hidden">
          <div className="px-6 py-4 bg-[#F6F8FA] border-b border-outline-variant">
            <h3 className="font-label-bold text-on-surface uppercase tracking-wider">Recent System Activity</h3>
          </div>
          {activityLoading ? (
            <div className="p-6"><LoadingSkeleton type="table" rows={4} /></div>
          ) : (
            <ActivityTimeline activities={recentActivity?.data} />
          )}
          <div className="px-6 py-3 bg-[#F6F8FA] flex justify-center border-t border-outline-variant">
            <button className="text-label-bold text-primary hover:underline transition-all">View All Activity History</button>
          </div>
        </section>
      )}

      {/* Activity Paused State when disconnected */}
      {!mailboxLoading && !isConnected && (
        <section className="flat-card overflow-hidden">
          <div className="px-6 py-4 bg-[#F6F8FA] border-b border-outline-variant">
            <h3 className="font-label-bold text-on-surface uppercase tracking-wider">Recent System Activity</h3>
          </div>
          <div className="p-12 text-center">
            <CheckCircle2 className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-base font-bold text-gray-900 dark:text-white mb-2">Activity tracking paused</h3>
            <p className="text-sm text-gray-500">Connect your Gmail account to see real-time activity.</p>
          </div>
        </section>
      )}
    </div>
  );
};