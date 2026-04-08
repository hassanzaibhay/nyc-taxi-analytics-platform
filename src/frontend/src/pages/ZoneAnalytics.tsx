import { useState } from 'react';
import DateRangeFilter from '../components/DateRangeFilter';
import DemandHeatmap from '../components/charts/DemandHeatmap';
import TopZonesBar from '../components/charts/TopZonesBar';
import { useTopZones, useZoneDemand } from '../hooks/useZones';
import type { DateRange } from '../types';

export default function ZoneAnalytics() {
  const [range, setRange] = useState<DateRange>({});
  const demand = useZoneDemand(range);
  const top = useTopZones(range, 10);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Zone Analytics</h2>
        <DateRangeFilter onChange={setRange} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 shadow-sm">
          <h3 className="mb-4 text-sm font-semibold text-slate-500">Demand Heatmap (zone × hour)</h3>
          {demand.data ? <DemandHeatmap data={demand.data} /> : <div className="h-64 animate-pulse rounded bg-slate-100" />}
        </div>
        <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 shadow-sm">
          <h3 className="mb-4 text-sm font-semibold text-slate-500">Top 10 Zones</h3>
          {top.data ? <TopZonesBar data={top.data} /> : <div className="h-64 animate-pulse rounded bg-slate-100" />}
        </div>
      </div>
    </div>
  );
}
