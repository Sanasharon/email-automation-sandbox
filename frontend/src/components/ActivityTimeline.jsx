import { getStatusConfig } from '../config/statusConfig';

export const ActivityTimeline = ({ activities }) => {
  if (!activities || activities.length === 0) {
    return <div className="p-6 text-center text-on-surface-variant text-body-md">No activity found</div>;
  }

  return (
    <div className="divide-y divide-outline-variant">
      {activities.map((activity, idx) => {
        const statusCfg = getStatusConfig(activity.status);
        
        // Define some icon mapping based on activity type or status
        let icon = 'info';
        if (activity.status === 'success' || activity.type === 'workflow_success') icon = 'check_circle';
        else if (activity.status === 'error' || activity.status === 'failed') icon = 'error';
        else if (activity.type === 'workflow_created') icon = 'add_circle';
        else if (activity.status === 'info') icon = 'settings_suggest';

        // Some quick logic to extract a "highlighted" text, usually the quotes part
        const parts = activity.title ? activity.title.split(/"([^"]+)"/) : [activity.task_name || 'System Activity'];
        
        return (
          <div key={activity.id} className="px-6 py-4 flex items-center hover:bg-surface-container-low transition-colors group">
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center mr-4 ${statusCfg.bgColor.replace('bg-', 'bg-opacity-10 bg-')}`}>
              <span className={`material-symbols-outlined text-[20px] ${statusCfg.textColor}`}>{icon}</span>
            </div>
            
            <div className="flex-1">
              <p className="font-body-md text-on-surface font-semibold">
                {parts.map((part, i) => 
                  i % 2 !== 0 ? <span key={i} className="text-primary">"{part}"</span> : part
                )}
              </p>
              <p className="text-label-md text-on-surface-variant">{activity.description}</p>
            </div>
            
            <div className="text-right ml-4">
              <p className="text-label-md text-on-surface-variant font-bold mb-1">
                {new Date(activity.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
              <span className={`text-[10px] px-2 py-0.5 font-bold rounded-full uppercase tracking-widest ${statusCfg.bgColor} ${statusCfg.textColor}`}>
                {statusCfg.label}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
};
