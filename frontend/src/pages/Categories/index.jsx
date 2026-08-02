import React, { useEffect, useState } from 'react';
import { api } from '../../api/client';
import { Tags } from 'lucide-react';

export function Categories() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const res = await api.getCategories();
        const arr = Array.isArray(res) ? res : (res?.data ?? []);
        if (!mounted) return;
        setCategories(Array.isArray(arr) ? arr : []);
      } catch (e) {
        console.error('Failed to fetch categories', e);
        if (!mounted) return;
        setError(e?.message || 'Failed to load categories');
      } finally {
        if (!mounted) return;
        setLoading(false);
      }
    }
    load();
    return () => { mounted = false; };
  }, []);

  return (
    <div className="p-4">
      <div className="flex items-center gap-3 mb-4">
        <Tags className="w-6 h-6 text-gray-700" />
        <h1 className="text-2xl font-semibold">Categories</h1>
      </div>

      {loading ? (
        <div className="text-sm text-gray-500">Loading categories...</div>
      ) : error ? (
        <div className="text-sm text-red-600">Error: {error}</div>
      ) : categories.length === 0 ? (
        <div className="text-sm text-gray-500">No categories found.</div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {categories.map((c, idx) => (
            <div
              key={c.category ?? idx}
              className="p-3 border rounded-lg bg-white dark:bg-gray-800"
            >
              <div className="text-sm font-medium">
                {c.category ?? 'Unnamed category'}
              </div>
              <div className="text-xs text-gray-500 mt-1 flex flex-wrap gap-x-2 gap-y-1">
                {c.department && <span>{c.department}</span>}
                {c.priority && <span>Priority: {c.priority}</span>}
                {c.type && <span className="text-gray-400">({c.type})</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Categories;