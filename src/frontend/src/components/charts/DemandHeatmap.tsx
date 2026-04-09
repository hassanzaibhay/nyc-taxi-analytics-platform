import type { ZoneDemandPoint } from '../../types';
import { formatHour, formatNumber } from '../../utils/formatters';

interface Props {
  data: ZoneDemandPoint[];
  topN?: number;
}

const HOUR_TICKS = [0, 3, 6, 9, 12, 15, 18, 21];

function interpolateColor(t: number): string {
  // white -> light blue -> deep blue
  const clamp = Math.max(0, Math.min(1, t));
  if (clamp < 0.5) {
    const k = clamp / 0.5;
    const r = Math.round(248 + (191 - 248) * k);
    const g = Math.round(250 + (219 - 250) * k);
    const b = Math.round(252 + (254 - 252) * k);
    return `rgb(${r}, ${g}, ${b})`;
  }
  const k = (clamp - 0.5) / 0.5;
  const r = Math.round(191 + (30 - 191) * k);
  const g = Math.round(219 + (64 - 219) * k);
  const b = Math.round(254 + (175 - 254) * k);
  return `rgb(${r}, ${g}, ${b})`;
}

export default function DemandHeatmap({ data, topN = 20 }: Props) {
  // Aggregate totals per zone and pick top N
  const totals = new Map<number, { total: number; name: string }>();
  data.forEach((d) => {
    const prev = totals.get(d.zone_id);
    const name = d.zone_name ?? `Zone ${d.zone_id}`;
    totals.set(d.zone_id, { total: (prev?.total ?? 0) + d.avg_trip_count, name });
  });
  const topZones = Array.from(totals.entries())
    .sort((a, b) => b[1].total - a[1].total)
    .slice(0, topN)
    .map(([id, meta]) => ({ id, name: meta.name }));

  const topIds = new Set(topZones.map((z) => z.id));
  const filtered = data.filter((d) => topIds.has(d.zone_id));
  const max = Math.max(...filtered.map((d) => d.avg_trip_count), 1);

  const lookup = new Map<string, number>();
  filtered.forEach((d) => lookup.set(`${d.zone_id}-${d.hour}`, d.avg_trip_count));

  return (
    <div className="space-y-3">
      <div className="overflow-x-auto">
        <table className="border-separate border-spacing-[2px] text-xs">
          <thead>
            <tr>
              <th className="w-44"></th>
              {Array.from({ length: 24 }, (_, h) => (
                <th
                  key={h}
                  className="w-8 text-center text-[10px] font-medium text-slate-500"
                >
                  {HOUR_TICKS.includes(h) ? formatHour(h) : ''}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {topZones.map((z) => (
              <tr key={z.id}>
                <td
                  className="pr-3 text-right text-[11px] text-slate-700 dark:text-slate-200 max-w-[176px] truncate"
                  title={z.name}
                >
                  {z.name}
                </td>
                {Array.from({ length: 24 }, (_, h) => {
                  const v = lookup.get(`${z.id}-${h}`) ?? 0;
                  return (
                    <td
                      key={h}
                      title={`${z.name}, ${formatHour(h)}: ${formatNumber(v)} trips`}
                      className="h-7 w-8 rounded-sm"
                      style={{ backgroundColor: interpolateColor(v / max) }}
                    />
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center gap-3 pl-44 text-[11px] text-slate-500">
        <span>Low</span>
        <div
          className="h-2 w-48 rounded"
          style={{
            background: `linear-gradient(to right, ${interpolateColor(0)}, ${interpolateColor(0.5)}, ${interpolateColor(1)})`,
          }}
        />
        <span>High demand</span>
      </div>
    </div>
  );
}
