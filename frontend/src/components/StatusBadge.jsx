import { getStatusConfig } from '../config/statusConfig';

export const StatusBadge = ({ status }) => {
  const config = getStatusConfig(status);
  
  return (
    <span className={`text-[10px] px-2 py-0.5 font-bold rounded-full uppercase tracking-widest ${config.bgColor} ${config.textColor}`}>
      {config.label}
    </span>
  );
};
