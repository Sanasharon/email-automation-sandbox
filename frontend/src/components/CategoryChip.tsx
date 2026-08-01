import React from "react";

export default function CategoryChip({ name, confidence }: { name: string, confidence?: number }) {
  return (
    <span title={confidence ? `Confidence: ${(confidence*100).toFixed(0)}%` : undefined}
          className="inline-flex items-center bg-slate-100 text-slate-800 px-2 py-0.5 rounded-md text-sm mr-1">
      {name}
    </span>
  );
}