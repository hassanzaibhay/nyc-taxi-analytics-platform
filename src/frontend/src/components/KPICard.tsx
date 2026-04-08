import type { LucideIcon } from 'lucide-react';
import { TrendingDown, TrendingUp } from 'lucide-react';

interface Props {
  title: string;
  value: string;
  icon: LucideIcon;
  trend?: number;
}

export default function KPICard({ title, value, icon: Icon, trend }: Props) {
  const positive = (trend ?? 0) >= 0;
  return (
    <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-500 dark:text-slate-400">{title}</span>
        <Icon size={18} className="text-slate-400" />
      </div>
      <div className="mt-3 text-3xl font-semibold tracking-tight">{value}</div>
      {trend !== undefined && (
        <div
          className={`mt-2 flex items-center gap-1 text-xs font-medium ${
            positive ? 'text-emerald-600' : 'text-rose-600'
          }`}
        >
          {positive ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
          {Math.abs(trend).toFixed(1)}%
        </div>
      )}
    </div>
  );
}
