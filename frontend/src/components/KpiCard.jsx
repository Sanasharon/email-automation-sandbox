export const KpiCard = ({ label, value, trend, status }) => {
  return (
    <div className="flat-card p-6 flex flex-col justify-between">
      <span className="text-label-md text-on-surface-variant font-medium">{label}</span>
      <div className="flex items-baseline mt-2 gap-2">
        <span className={`text-display-lg font-display-lg ${status === 'error' ? 'text-error' : status === 'success' ? 'text-[#1A7F37]' : 'text-on-surface'}`}>
          {value}
        </span>
        {trend && (
          <span className={`text-[10px] font-bold ${trend.direction === 'up' ? 'text-[#1A7F37]' : trend.direction === 'down' ? 'text-error' : 'text-on-surface-variant'}`}>
            {trend.direction === 'up' ? '↑' : trend.direction === 'down' ? '↓' : ''} {trend.value}
          </span>
        )}
      </div>
    </div>
  );
};
