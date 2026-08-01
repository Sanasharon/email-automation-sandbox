import React from "react";

type Priority = "High" | "Medium" | "Low" | string;

const colors: Record<Priority, string> = {
  High: "bg-red-100 text-red-800",
  Medium: "bg-amber-100 text-amber-800",
  Low: "bg-green-100 text-green-800",
  default: "bg-gray-100 text-gray-800",
};

export default function PriorityBadge({ priority, small=false }: { priority?: Priority, small?: boolean }) {
  if (!priority) return null;
  const cls = colors[priority as Priority] ?? colors.default;
  const size = small ? "px-2 py-0.5 text-xs" : "px-3 py-1 text-sm";
  return (
    <span className={`inline-flex items-center rounded-full ${cls} ${size}`}>
      {priority}
    </span>
  );
}