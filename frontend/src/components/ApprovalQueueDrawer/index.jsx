import { useState, useEffect } from 'react';
import { Shield, Check, X, Edit3, Clock, Sparkles, ExternalLink } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../api/client';

export const ApprovalQueueDrawer = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const [approvals, setApprovals] = useState([]);
  const [activeTab, setActiveTab] = useState('pending');
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [editedText, setEditedText] = useState('');

  const fetchApprovals = async () => {
    try {
      setLoading(true);
      const data = await api.getPendingApprovals();
      setApprovals(data || []);
    } catch (err) {
      console.error('Failed to load pending AI approvals:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchApprovals();
    }
  }, [isOpen]);

  const handleApprove = async (id) => {
    try {
      await api.approveAIDraft(id, editingId === id ? editedText : null);
      setEditingId(null);
      fetchApprovals();
    } catch (err) {
      console.error('Failed to approve draft:', err);
    }
  };

  const handleReject = async (id) => {
    try {
      await api.rejectAIDraft(id);
      fetchApprovals();
    } catch (err) {
      console.error('Failed to reject draft:', err);
    }
  };

  if (!isOpen) return null;

  const filteredApprovals = approvals.filter(item => {
    if (activeTab === 'pending') return item.status === 'pending_review';
    if (activeTab === 'approved') return item.status === 'approved';
    if (activeTab === 'rejected') return item.status === 'rejected';
    return true;
  });

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/40 backdrop-blur-xs flex justify-end">
      <div className="w-full max-w-xl bg-white dark:bg-gray-900 h-full shadow-2xl flex flex-col border-l border-gray-200 dark:border-gray-800">
        
        {/* Drawer Header */}
        <div className="p-5 border-b border-gray-200 dark:border-gray-800 flex justify-between items-center bg-gray-50 dark:bg-gray-800/50">
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-amber-500" />
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">AI Draft Quick Preview</h2>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => {
                onClose();
                navigate('/approvals');
              }}
              className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
            >
              Full Page Management <ExternalLink className="w-3 h-3" />
            </button>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 dark:hover:text-white p-1">✕</button>
          </div>
        </div>

        {/* Status Tabs */}
        <div className="flex border-b border-gray-200 dark:border-gray-800 px-5 pt-3 gap-2 bg-gray-50/50 dark:bg-gray-900">
          <button
            onClick={() => setActiveTab('pending')}
            className={`pb-2 px-3 text-xs font-semibold border-b-2 transition-colors ${
              activeTab === 'pending'
                ? 'border-amber-500 text-amber-600 dark:text-amber-400'
                : 'border-transparent text-gray-500 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Pending Review ({approvals.filter(i => i.status === 'pending_review').length})
          </button>
          <button
            onClick={() => setActiveTab('approved')}
            className={`pb-2 px-3 text-xs font-semibold border-b-2 transition-colors ${
              activeTab === 'approved'
                ? 'border-green-500 text-green-600 dark:text-green-400'
                : 'border-transparent text-gray-500 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Approved ({approvals.filter(i => i.status === 'approved').length})
          </button>
          <button
            onClick={() => setActiveTab('rejected')}
            className={`pb-2 px-3 text-xs font-semibold border-b-2 transition-colors ${
              activeTab === 'rejected'
                ? 'border-red-500 text-red-600 dark:text-red-400'
                : 'border-transparent text-gray-500 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Rejected ({approvals.filter(i => i.status === 'rejected').length})
          </button>
        </div>

        {/* Drawer Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading ? (
            <div className="text-center py-12 text-gray-400 text-sm">Loading approval records...</div>
          ) : filteredApprovals.length === 0 ? (
            <div className="text-center py-16 space-y-3">
              <div className="w-12 h-12 bg-gray-50 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto text-gray-400">
                <Check className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-gray-900 dark:text-white">No items found</h3>
              <p className="text-xs text-gray-500 max-w-xs mx-auto">There are no AI generated email drafts in this tab.</p>
            </div>
          ) : (
            filteredApprovals.map((item) => (
              <div key={item.id} className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-5 space-y-4 shadow-xs">
                
                {/* Email Context */}
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-xs text-gray-400">
                    <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> {new Date(item.created_at).toLocaleString()}</span>
                    <span className="font-semibold text-indigo-600 dark:text-indigo-400">{item.workflow_name}</span>
                  </div>
                  <h4 className="text-sm font-bold text-gray-900 dark:text-white">{item.email_subject}</h4>
                  <p className="text-xs text-gray-500">From: {item.email_sender}</p>
                </div>

                {/* Draft Content */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <label className="text-[11px] font-bold text-gray-400 uppercase tracking-wider flex items-center gap-1">
                      <Sparkles className="w-3.5 h-3.5 text-indigo-500" /> Proposed AI Response
                    </label>
                    {item.status === 'pending_review' && editingId !== item.id && (
                      <button
                        onClick={() => {
                          setEditingId(item.id);
                          setEditedText(item.edited_content || item.generated_content);
                        }}
                        className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
                      >
                        <Edit3 className="w-3 h-3" /> Edit Draft
                      </button>
                    )}
                  </div>

                  {editingId === item.id ? (
                    <textarea
                      rows={5}
                      value={editedText}
                      onChange={(e) => setEditedText(e.target.value)}
                      className="w-full text-xs p-3 rounded-lg border border-indigo-300 dark:border-indigo-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-white font-mono focus:ring-1 focus:ring-indigo-500"
                    />
                  ) : (
                    <div className="bg-gray-50 dark:bg-gray-900 p-3 rounded-lg text-xs font-mono text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-800 whitespace-pre-wrap">
                      {item.edited_content || item.generated_content}
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                {item.status === 'pending_review' && (
                  <div className="flex gap-2 pt-2 border-t border-gray-100 dark:border-gray-700">
                    <button
                      onClick={() => handleApprove(item.id)}
                      className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
                    >
                      <Check className="w-4 h-4" /> Approve & Send
                    </button>
                    <button
                      onClick={() => handleReject(item.id)}
                      className="px-4 bg-gray-100 dark:bg-gray-700 hover:bg-red-100 hover:text-red-700 text-gray-600 dark:text-gray-300 py-2 rounded-lg text-xs font-semibold flex items-center gap-1 transition-colors"
                    >
                      <X className="w-4 h-4" /> Reject
                    </button>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
