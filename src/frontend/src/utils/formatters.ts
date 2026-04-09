export function formatNumber(n: number): string {
  if (!Number.isFinite(n)) return '—';
  if (Math.abs(n) >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (Math.abs(n) >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toLocaleString(undefined, { maximumFractionDigits: 0 });
}

export function formatCurrency(n: number): string {
  if (!Number.isFinite(n)) return '—';
  if (Math.abs(n) >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
  if (Math.abs(n) >= 1_000) return `$${(n / 1_000).toFixed(1)}K`;
  return `$${n.toFixed(2)}`;
}

export function formatPercent(n: number): string {
  if (!Number.isFinite(n)) return '—';
  return `${n.toFixed(1)}%`;
}

export function formatHour(hour: number): string {
  const h = ((hour % 24) + 24) % 24;
  if (h === 0) return '12am';
  if (h === 12) return '12pm';
  if (h < 12) return `${h}am`;
  return `${h - 12}pm`;
}

const BOROUGH_BORDER: Record<string, string> = {
  Manhattan: 'border-l-blue-500',
  Queens: 'border-l-emerald-500',
  Brooklyn: 'border-l-purple-500',
  Bronx: 'border-l-orange-500',
  'Staten Island': 'border-l-slate-500',
  EWR: 'border-l-rose-500',
};

export function boroughBorderClass(borough: string | null | undefined): string {
  if (!borough) return 'border-l-slate-300';
  return BOROUGH_BORDER[borough] ?? 'border-l-slate-300';
}
