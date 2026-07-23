import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Shield, Server, Bell, Key, Mail, RefreshCw, CheckCircle2, AlertTriangle, Power, Link2, UserCheck, Activity, Clock } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../api/client';

const SystemConfig = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('gmail');
  const [mailboxes, setMailboxes] = useState([]);
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 15000); // 15s auto-refresh
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [mbData, sysData] = await Promise.all([
        api.getMailboxes(),
        api.getSystemStatus().catch(() => null)
      ]);
      setMailboxes(Array.isArray(mbData) ? mbData : []);
      if (sysData) setSystemStatus(sysData);
    } catch (e) {
      console.error('Failed to load system config data:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async () => {
    try {
      setActionLoading(true);
      setFeedback(null);
      const res = await api.connectMailbox();
      setFeedback({ type: 'success', message: res.message || 'Gmail Account Connected Successfully!' });
      await fetchData();
    } catch (e) {
      setFeedback({ type: 'error', message: e.response?.data?.detail || e.message || 'Failed to connect Gmail account' });
    } finally {
      setActionLoading(false);
    }
  };

  const handleSwitchAccount = async () => {
    try {
      setActionLoading(true);
      setFeedback({ type: 'info', message: 'Launching Google Account Chooser... Please select your account.' });
      const res = await api.switchMailboxAccount();
      setFeedback({ type: 'success', message: res.message || 'Successfully switched Gmail account!' });
      await fetchData();
    } catch (e) {
      setFeedback({ type: 'error', message: e.response?.data?.detail || e.message || 'Account switch failed' });
    } finally {
      setActionLoading(false);
    }
  };

  const handleManualSync = async (mailboxId) => {
    try {
      setActionLoading(true);
      setFeedback(null);
      const res = await api.syncMailbox(mailboxId);
      setFeedback({ type: 'success', message: res.message || 'Sync completed successfully!' });
      await fetchData();
    } catch (e) {
      setFeedback({ type: 'error', message: e.response?.data?.detail || e.message || 'Sync failed' });
    } finally {
      setActionLoading(false);
    }
  };

  const handleDisconnect = async (mailboxId) => {
    try {
      setActionLoading(true);
      setFeedback(null);
      await api.disconnectMailbox(mailboxId);
      setFeedback({ type: 'success', message: 'Mailbox disconnected successfully' });
      await fetchData();
    } catch (e) {
      setFeedback({ type: 'error', message: 'Failed to disconnect mailbox' });
    } finally {
      setActionLoading(false);
    }
  };

  const handleReconnect = async (mailboxId) => {
    try {
      setActionLoading(true);
      setFeedback(null);
      await api.reconnectMailbox(mailboxId);
      setFeedback({ type: 'success', message: 'Mailbox re-connected successfully' });
      await fetchData();
    } catch (e) {
      setFeedback({ type: 'error', message: 'Failed to reconnect mailbox' });
    } finally {
      setActionLoading(false);
    }
  };

  if (user?.role !== 'Admin' && user?.role !== 'Editor') {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <Shield className="w-16 h-16 text-red-500 mb-4" />
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">Access Denied</h2>
        <p className="text-gray-500 mt-2">You don't have permission to view System Settings.</p>
      </div>
    );
  }

  const activeMailbox = mailboxes.length > 0 ? mailboxes[0] : null;
  const isConnected = activeMailbox && activeMailbox.sync_status === 'connected';

  const sections = [
    { id: 'gmail', title: 'Gmail Connection & Scheduler', icon: <Mail className="w-5 h-5" />, desc: 'Connect, switch account & manage background sync.' },
    { id: 'general', title: 'General Settings', icon: <Server className="w-5 h-5" />, desc: 'Configure global application parameters.' },
    { id: 'keys', title: 'API Keys & Secrets', icon: <Key className="w-5 h-5" />, desc: 'Manage Supabase and API credentials.' },
    { id: 'notifications', title: 'Notifications', icon: <Bell className="w-5 h-5" />, desc: 'System alert & digest preferences.' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <SettingsIcon className="w-6 h-6 text-gray-600 dark:text-gray-400" />
          Settings & Integrations
        </h1>
        <p className="text-sm text-gray-500 mt-1">Central control panel for Gmail integration, workspace settings, and security.</p>
      </div>

      {feedback && (
        <div className={`p-4 rounded-xl flex items-center gap-3 text-sm ${feedback.type === 'success' ? 'bg-green-50 text-green-800 border border-green-200' : feedback.type === 'info' ? 'bg-blue-50 text-blue-800 border border-blue-200' : 'bg-red-50 text-red-800 border border-red-200'}`}>
          {feedback.type === 'success' ? <CheckCircle2 className="w-5 h-5 text-green-600" /> : feedback.type === 'info' ? <RefreshCw className="w-5 h-5 text-blue-600 animate-spin" /> : <AlertTriangle className="w-5 h-5 text-red-600" />}
          <span>{feedback.message}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Navigation Sidebar */}
        <div className="lg:col-span-1 space-y-2">
          {sections.map((sec) => (
            <div
              key={sec.id}
              onClick={() => setActiveTab(sec.id)}
              className={`p-4 rounded-xl cursor-pointer flex items-start gap-3 transition-colors ${
                activeTab === sec.id
                  ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-400'
                  : 'hover:bg-gray-50 dark:hover:bg-gray-800 border border-transparent text-gray-700 dark:text-gray-300'
              }`}
            >
              <div className="mt-0.5">{sec.icon}</div>
              <div>
                <h3 className="text-sm font-bold">{sec.title}</h3>
                <p className="text-xs text-gray-500 mt-1">{sec.desc}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Content Area */}
        <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          {activeTab === 'gmail' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center border-b border-gray-200 dark:border-gray-700 pb-4">
                <div>
                  <h2 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
                    <Mail className="w-5 h-5 text-blue-600" />
                    Gmail Connection Lifecycle
                  </h2>
                  <p className="text-xs text-gray-500 mt-1">Manage connected account, switch accounts, and monitor APScheduler state.</p>
                </div>
                {isConnected && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800">
                    <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Connected
                  </span>
                )}
              </div>

              {loading && mailboxes.length === 0 ? (
                <div className="p-8 text-center text-gray-500">Loading connection state...</div>
              ) : activeMailbox ? (
                <div className="space-y-6">
                  {/* Account Card */}
                  <div className="bg-gray-50 dark:bg-gray-900/50 rounded-xl p-5 border border-gray-200 dark:border-gray-700 space-y-4">
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                      <div>
                        <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Current Gmail Address</div>
                        <div className="text-lg font-bold text-gray-900 dark:text-white mt-0.5">{activeMailbox.account_identifier}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Synced Emails</div>
                        <div className="text-lg font-bold text-blue-600 dark:text-blue-400 mt-0.5">{activeMailbox.email_count || 0} Emails</div>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-3 border-t border-gray-200 dark:border-gray-700 text-xs">
                      <div>
                        <span className="text-gray-500">Sync Status: </span>
                        <span className={`font-semibold capitalize ${activeMailbox.sync_status === 'connected' ? 'text-green-600' : 'text-amber-600'}`}>
                          {activeMailbox.sync_status}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">Last Synced: </span>
                        <span className="font-medium text-gray-900 dark:text-white">
                          {activeMailbox.last_sync_at ? new Date(activeMailbox.last_sync_at).toLocaleString() : 'Just now'}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Scheduler Status Card */}
                  {systemStatus && systemStatus.scheduler && (
                    <div className="bg-blue-50/60 dark:bg-blue-950/20 rounded-xl p-5 border border-blue-200 dark:border-blue-800 space-y-3">
                      <div className="flex justify-between items-center">
                        <div className="flex items-center gap-2 font-bold text-sm text-gray-900 dark:text-white">
                          <Activity className="w-4 h-4 text-blue-600" />
                          APScheduler Background Polling Status
                        </div>
                        <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${systemStatus.scheduler.is_running ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                          {systemStatus.scheduler.is_running ? 'RUNNING (Auto Startup Active)' : 'STOPPED'}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 text-xs">
                        <div className="bg-white dark:bg-gray-800 p-2.5 rounded-lg border border-gray-200 dark:border-gray-700">
                          <div className="text-gray-400 text-[10px] uppercase font-semibold">Health Score</div>
                          <div className="font-bold text-green-600 text-sm mt-0.5">{systemStatus.health_score}%</div>
                        </div>

                        <div className="bg-white dark:bg-gray-800 p-2.5 rounded-lg border border-gray-200 dark:border-gray-700">
                          <div className="text-gray-400 text-[10px] uppercase font-semibold">Poll Interval</div>
                          <div className="font-bold text-gray-800 dark:text-white text-sm mt-0.5">{systemStatus.scheduler.interval_minutes} Minute</div>
                        </div>

                        <div className="bg-white dark:bg-gray-800 p-2.5 rounded-lg border border-gray-200 dark:border-gray-700">
                          <div className="text-gray-400 text-[10px] uppercase font-semibold">Next Sync</div>
                          <div className="font-bold text-blue-600 text-xs mt-0.5 truncate">
                            {systemStatus.scheduler.next_run_at ? new Date(systemStatus.scheduler.next_run_at).toLocaleTimeString() : 'Pending'}
                          </div>
                        </div>

                        <div className="bg-white dark:bg-gray-800 p-2.5 rounded-lg border border-gray-200 dark:border-gray-700">
                          <div className="text-gray-400 text-[10px] uppercase font-semibold">Total Runs</div>
                          <div className="font-bold text-gray-800 dark:text-white text-sm mt-0.5">{systemStatus.scheduler.execution_count}</div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Actions Bar */}
                  <div className="flex flex-wrap items-center gap-3 pt-2">
                    <button
                      onClick={() => handleManualSync(activeMailbox.id)}
                      disabled={actionLoading || !isConnected}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 disabled:opacity-50"
                    >
                      <RefreshCw className={`w-4 h-4 ${actionLoading ? 'animate-spin' : ''}`} />
                      Manual Sync Now
                    </button>

                    <button
                      onClick={handleSwitchAccount}
                      disabled={actionLoading}
                      className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 disabled:opacity-50"
                    >
                      <UserCheck className="w-4 h-4" />
                      Switch / Change Gmail Account
                    </button>

                    <button
                      onClick={() => handleReconnect(activeMailbox.id)}
                      disabled={actionLoading}
                      className="bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 disabled:opacity-50"
                    >
                      <Link2 className="w-4 h-4 text-blue-500" />
                      Reconnect OAuth
                    </button>

                    {isConnected && (
                      <button
                        onClick={() => handleDisconnect(activeMailbox.id)}
                        disabled={actionLoading}
                        className="bg-red-50 hover:bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400 px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 ml-auto disabled:opacity-50"
                      >
                        <Power className="w-4 h-4" />
                        Disconnect
                      </button>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center py-12 space-y-4">
                  <div className="w-16 h-16 bg-blue-50 dark:bg-blue-900/20 text-blue-600 rounded-full flex items-center gap-2 justify-center mx-auto">
                    <Mail className="w-8 h-8" />
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white">No Gmail Account Connected</h3>
                  <p className="text-sm text-gray-500 max-w-md mx-auto">Connect your Gmail account using Google OAuth to enable automated synchronization, attachment storage, and AI workflows.</p>
                  <button
                    onClick={handleConnect}
                    disabled={actionLoading}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl font-medium shadow-sm transition-colors disabled:opacity-50"
                  >
                    {actionLoading ? 'Connecting...' : 'Connect Gmail Account'}
                  </button>
                </div>
              )}
            </div>
          )}

          {activeTab !== 'gmail' && (
            <div className="py-12 text-center text-gray-500">
              <Server className="w-12 h-12 mx-auto mb-3 text-gray-400" />
              <p className="font-medium text-gray-700 dark:text-gray-300">Setting section is read-only in this demo environment.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SystemConfig;
