export function ruleLabel(rule) {
  if (rule == null) return '';
  if (typeof rule === 'string') return rule;
  const parts = [rule.category, rule.type, rule.department];
  if (rule.priority) parts.push(`Priority: ${rule.priority}`);
  return parts.filter(Boolean).join(' - ') || JSON.stringify(rule);
}

export function ruleKey(rule, idx) {
  if (!rule) return `rule_${idx}`;
  if (typeof rule === 'string') return rule;
  return String(rule.id ?? rule.key ?? `rule_${idx}`);
}