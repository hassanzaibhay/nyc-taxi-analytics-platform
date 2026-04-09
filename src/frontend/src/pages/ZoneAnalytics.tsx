import { useMemo, useState } from 'react';
import DateRangeFilter from '../components/DateRangeFilter';
import DemandHeatmap from '../components/charts/DemandHeatmap';
import TopZonesBar from '../components/charts/TopZonesBar';
import { useTopZones, useZoneDemand } from '../hooks/useZones';
import type { DateRange, ZoneDemandPoint } from '../types';
import { formatHour, formatNumber } from '../utils/formatters';

interface PeakRow {
  zone_id: number;
  name: string;
  borough: string | null;
  peak_hour: number;
  peak_value: number;
}

function computePeakHours(data: ZoneDemandPoint[], n = 5): PeakRow[] {
  const byZone = new Map<
    number,
    {
      name: string;
      borough: string | null;
      total: number;
      peak_hour: number;
      peak_value: number;
    }
  >();
  for (const d of data) {
    const name = d.zone_name ?? `Zone ${d.zone_id}`;
    const prev = byZone.get(d.zone_id) ?? {
      name,
      borough: d.borough ?? null,
      total: 0,
      peak_hour: 0,
      peak_value: 0,
    };
    prev.total += d.avg_trip_count;
    if (d.avg_trip_count > prev.peak_value) {
      prev.peak_hour = d.hour;
      prev.peak_value = d.avg_trip_count;
    }
    byZone.set(d.zone_id, prev);
  }
  return Array.from(byZone.entries())
    .sort((a, b) => b[1].total - a[1].total)
    .slice(0, n)
    .map(([zone_id, v]) => ({
      zone_id,
      name: v.name,
      borough: v.borough,
      peak_hour: v.peak_hour,
      peak_value: v.peak_value,
    }));
}

export default function ZoneAnalytics() {
  const [range, setRange] = useState<DateRange>({});
  const demand = useZoneDemand(range);
  const top = useTopZones(range, 10);

  const peaks = useMemo(() => computePeakHours(demand.data ?? [], 5), [demand.data]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Zone Analytics</h2>
        <DateRangeFilter onChange={setRange} />
      </div>

      <div className="w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 shadow-sm">
        <h3 className="mb-1 text-sm font-semibold text-slate-700 dark:text-slate-200">
          Demand Heatmap
        </h3>
        <p className="mb-4 text-xs text-slate-500">
          Top 20 zones by trip volume, aggregated by hour of day
        </p>
        {demand.data ? (
          <DemandHeatmap data={demand.data} topN={20} />
        ) : (
          <div className="h-80 animate-pulse rounded bg-slate-100" />
        )}
      </div>

      <div className="w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 shadow-sm">
        <h3 className="mb-1 text-sm font-semibold text-slate-700 dark:text-slate-200">
          Top 10 Zones
        </h3>
        <p className="mb-4 text-xs text-slate-500">Ranked by total trips</p>
        {top.data ? (
          <TopZonesBar data={top.data} />
        ) : (
          <div className="h-80 animate-pulse rounded bg-slate-100" />
        )}
      </div>

      <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 shadow-sm">
        <h3 className="mb-1 text-sm font-semibold text-slate-700 dark:text-slate-200">
          Peak Hours Summary
        </h3>
        <p className="mb-4 text-xs text-slate-500">When each top zone sees its busiest hour</p>
        {peaks.length === 0 ? (
          <div className="h-20 animate-pulse rounded bg-slate-100" />
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
                <th className="py-2">Zone</th>
                <th className="py-2">Borough</th>
                <th className="py-2">Peak Hour</th>
                <th className="py-2 text-right">Trips at Peak</th>
              </tr>
            </thead>
            <tbody>
              {peaks.map((p) => (
                <tr
                  key={p.zone_id}
                  className="border-b border-slate-100 dark:border-slate-700 last:border-0"
                >
                  <td className="py-2 font-medium">{p.name}</td>
                  <td className="py-2 text-slate-500">{p.borough ?? '—'}</td>
                  <td className="py-2 text-slate-500">{formatHour(p.peak_hour)}</td>
                  <td className="py-2 text-right font-semibold text-blue-600">
                    {formatNumber(p.peak_value)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
