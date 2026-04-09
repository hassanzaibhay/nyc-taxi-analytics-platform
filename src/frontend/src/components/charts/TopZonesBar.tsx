import {
  Bar,
  BarChart,
  CartesianGrid,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { TopZone } from '../../types';
import { formatNumber } from '../../utils/formatters';

export default function TopZonesBar({ data }: { data: TopZone[] }) {
  const rows = [...data]
    .sort((a, b) => b.trip_count - a.trip_count)
    .map((d) => ({
      ...d,
      label: d.zone_name
        ? `${d.zone_name}${d.borough ? ` (${d.borough})` : ''}`
        : `Zone ${d.zone_id}`,
    }));

  return (
    <ResponsiveContainer width="100%" height={Math.max(320, rows.length * 32)}>
      <BarChart data={rows} layout="vertical" margin={{ top: 10, right: 80, left: 10, bottom: 20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis type="number" stroke="#94a3b8" fontSize={11} tickFormatter={formatNumber} />
        <YAxis
          type="category"
          dataKey="label"
          stroke="#475569"
          fontSize={11}
          width={180}
          interval={0}
        />
        <Tooltip
          formatter={(value: number) => [formatNumber(value), 'Trips']}
          labelFormatter={(label: string) => label}
        />
        <Bar dataKey="trip_count" fill="#3B82F6" radius={[0, 4, 4, 0]}>
          <LabelList
            dataKey="trip_count"
            position="right"
            formatter={(v: number) => formatNumber(v)}
            style={{ fill: '#475569', fontSize: 11 }}
          />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
