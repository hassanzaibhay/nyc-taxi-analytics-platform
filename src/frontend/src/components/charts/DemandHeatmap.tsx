import type { ZoneDemandPoint } from '../../types';

interface Props {
  data: ZoneDemandPoint[];
  maxZones?: number;
}

export default function DemandHeatmap({ data, maxZones = 30 }: Props) {
  const zones = Array.from(new Set(data.map((d) => d.zone_id))).slice(0, maxZones);
  const max = Math.max(...data.map((d) => d.avg_trip_count), 1);

  const cellColor = (v: number) => {
    const intensity = Math.min(v / max, 1);
    return `rgba(59, 130, 246, ${0.1 + intensity * 0.9})`;
  };

  const lookup = new Map<string, number>();
  data.forEach((d) => lookup.set(`${d.zone_id}-${d.hour}`, d.avg_trip_count));

  return (
    <div className="overflow-x-auto">
      <table className="border-separate border-spacing-1 text-xs">
        <thead>
          <tr>
            <th className="w-16"></th>
            {Array.from({ length: 24 }, (_, h) => (
              <th key={h} className="w-8 text-center text-slate-500">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {zones.map((z) => (
            <tr key={z}>
              <td className="text-right pr-2 text-slate-500">Zone {z}</td>
              {Array.from({ length: 24 }, (_, h) => {
                const v = lookup.get(`${z}-${h}`) ?? 0;
                return (
                  <td
                    key={h}
                    title={`Zone ${z}, ${h}:00 → ${v.toFixed(1)} trips`}
                    className="h-6 w-8 rounded"
                    style={{ backgroundColor: cellColor(v) }}
                  />
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
