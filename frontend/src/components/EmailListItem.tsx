import React from "react";
import PriorityBadge from "./PriorityBadge";
import CategoryChip from "./CategoryChip";

type Category = {
  category_id?: string;
  category_name: string;
  confidence?: number;
};

type EmailListItemProps = {
  email: {
    id: string;
    sender_email?: string;
    subject?: string;
    labels?: string[];
    priority?: "High" | "Medium" | "Low" | string;
    priority_confidence?: number;
    categories?: Category[];
    received_at?: string;
  };
  onOpen?: (id: string) => void;
};

export default function EmailListItem({ email, onOpen }: EmailListItemProps) {
  return (
    <div
      className="email-row flex items-center justify-between p-3 border-b"
      role="button"
      onClick={() => onOpen && onOpen(email.id)}
    >
      <div className="flex items-center space-x-3">
        <div className="w-56">
          <div className="text-sm font-medium">{email.subject ?? "(no subject)"}</div>
          <div className="text-xs text-gray-500">{email.sender_email}</div>
        </div>

        <div className="flex items-center space-x-1">
          {email.categories?.slice(0, 2).map((c) => (
            <CategoryChip
              key={c.category_id ?? c.category_name}
              name={c.category_name}
              confidence={c.confidence}
            />
          ))}
          {email.categories && email.categories.length > 2 && (
            <span className="text-xs text-gray-500">+{email.categories.length - 2}</span>
          )}
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <PriorityBadge priority={email.priority} small />
        <div className="text-xs text-gray-400">
          {email.received_at ? new Date(email.received_at).toLocaleString() : ""}
        </div>
      </div>
    </div>
  );
}