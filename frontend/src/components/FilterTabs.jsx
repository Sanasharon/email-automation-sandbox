export const FilterTabs = ({ tabs, activeTab, onChange }) => {
  return (
    <div className="flex border-b border-outline-variant overflow-x-auto">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={`px-4 py-3 text-label-bold whitespace-nowrap border-b-2 transition-colors ${
            activeTab === tab.id
              ? 'border-primary text-primary'
              : 'border-transparent text-on-surface-variant hover:text-on-surface hover:bg-surface-container-highest'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
};
