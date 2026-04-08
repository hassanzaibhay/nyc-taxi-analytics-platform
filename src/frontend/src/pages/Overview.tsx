import { useState } from 'react';
import { Car, DollarSign, Percent, Route } from 'lucide-react';
import KPICard from '../components/KPICard';
import DateRangeFilter from '../components/DateRangeFilter';
import RevenueTrend from '../components/charts/RevenueTrend';
import { useTripSummary } from '../hooks/useTrips';
import { useDailyRevenue } from '../hooks/useRevenue';
import type { DateRange } from '../types';

const fmtNum = (n: number) => n.toLocaleString(undefined, { maximumFractionDigits: 0 });
const fmtCurrency = (n: number) => `$${(n / 1000).toFixed(1)}k`;

export default function Overview() {
  const [range, setRange] = useState<DateRange>({});
  const summary = useTripSummary(range);
  const revenue = useDailyRevenue(range);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Overview</h2>
        <DateRangeFilter onChange={setRange} />
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard
          title="Total Trips"
          value={summary.data ? fmtNum(summary.data.total_trips) : '—'}
          icon={Car}
        />
        <KPICard
          title="Total Revenue"
          value={summary.data ? fmtCurrency(Number(summary.data.total_revenue)) : '—'}
          icon={DollarSign}
        />
        <KPICard
          title="Avg Fare"
          value={summary.data ? `$${Number(summary.data.avg_fare).toFixed(2)}` : '—'}
          icon={Route}
        />
        <KPICard
          title="Avg Tip %"
          value={summary.data ? `${Number(summary.data.avg_tip_pct).toFixed(1)}%` : '—'}
          icon={Percent}
        />
      </div>

      <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 shadow-sm">
        <h3 className="mb-4 text-sm font-semibold text-slate-500">Daily Revenue</h3>
        {revenue.isLoading ? (
          <div className="h-72 animate-pulse rounded bg-slate-100 dark:bg-slate-700" />
        ) : revenue.data && revenue.data.length > 0 ? (
          <RevenueTrend data={revenue.data} />
        ) : (
          <div className="flex h-72 items-center justify-center text-slate-400">
            No data for selected filters
          </div>
        )}
      </div>
    </div>
  );
}
