import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLiveData } from '../../hooks/useLiveData';
import { api } from '../../api/client';
import { KpiCard } from '../../components/KpiCard';
import { ActivityTimeline } from '../../components/ActivityTimeline';
import { LoadingSkeleton } from '../../components/LoadingSkeleton';
import { Mail, ArrowRight, CheckCircle2 } from 'lucide-react';

export const DashboardOverview = () => {
  const navigate = useNavigate();
  const { data: summary, loading: summaryLoading, error: summaryError } = useLiveData(api.getDashboardSummary, 5000);
  const { data: recentActivity, loading: activityLoading } = useLiveData(api.getRecentActivity, 5000);
  
  const [mailboxes, setMailboxes] = useState([]);
  const [connectionLoading, setConnectionLoading] = useState(true);

  useEffect(() => {
    const fetchMailboxes = () => {
      api.getMailboxes()
        .then(res => setMailboxes(Array.isArray(res) ? res : []))
        .catch(() => setMailboxes([]))
        .finally(() => setConnectionLoading(false));
    };

    fetchMailboxes();
    const interval = setInterval(fetchMailboxes, 15000); // 15s auto-refresh
    return () => clearInterval(interval);
  }, []);

  const activeMailbox = mailboxes.length > 0 ? mailboxes[0] : null;
  const isConnected = activeMailbox && activeMailbox.sync_status === 'connected';

  return (
    <div className="flex flex-col gap-8">
      {/* Connection State Onboarding Banner */}
      {!connectionLoading && !isConnected && (
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

      {summaryError && (
        <div className="bg-error-container text-on-error-container p-4 rounded-md text-body-md">
          Failed to load summary data. Please try again.
        </div>
      )}

      {/* KPI Grid */}
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

      {/* Line Chart Area */}
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
        
        {/* Simple mock chart visualization */}
        <div className="h-64 w-full flex items-end justify-between gap-1 border-b border-l border-outline-variant pb-1 pl-1">
          <div className="relative w-full h-full flex flex-col justify-end pb-[10px]">
             {/* Note: Ideally we'd use recharts here, but we're mimicking the requested design simply */}
             <div className="absolute inset-0 flex flex-col justify-between pointer-events-none mb-[10px]">
               <div className="border-t border-outline-variant/30 w-full h-px"></div>
               <div className="border-t border-outline-variant/30 w-full h-px"></div>
               <div className="border-t border-outline-variant/30 w-full h-px"></div>
               <div className="border-t border-outline-variant/30 w-full h-px"></div>
             </div>
             
             {/* Chart Line Representation */}
             {summaryLoading ? (
               <div className="w-full h-full bg-surface-container-low animate-pulse"></div>
             ) : (
               (() => {
                 const series = summary?.email_volume_series || [];
                 if (series.length < 2) return null;
                 
                 const maxVal = Math.max(...series.map(d => Math.max(d.incoming, 1)));
                 const points = series.map((d, i) => {
                   const x = (i / (series.length - 1)) * 1000;
                   const y = 100 - ((d.incoming / maxVal) * 80); // Leave some top padding
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
        
        {/* X-Axis labels */}
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

      {/* Recent Activity */}
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
    </div>
  );
};
