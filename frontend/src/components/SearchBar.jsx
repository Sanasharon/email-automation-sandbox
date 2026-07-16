import { useState, useEffect } from 'react';
import { Search } from 'lucide-react';

export const SearchBar = ({ onSearch, placeholder = 'Search...' }) => {
  const [query, setQuery] = useState('');

  useEffect(() => {
    const timer = setTimeout(() => {
      onSearch(query);
    }, 300); // 300ms debounce
    return () => clearTimeout(timer);
  }, [query, onSearch]);

  return (
    <div className="relative w-full max-w-md">
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <Search size={16} className="text-on-surface-variant" />
      </div>
      <input
        type="text"
        className="block w-full pl-10 pr-3 py-2 border border-outline-variant rounded-md leading-5 bg-surface placeholder-on-surface-variant text-on-surface focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary sm:text-body-md"
        placeholder={placeholder}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
    </div>
  );
};
