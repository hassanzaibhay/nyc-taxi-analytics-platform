import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { TopZone } from '../../types';

export default function TopZonesBar({ data }: { data: TopZone[] }) {
  const rows = data.map((d) => ({
    ...d,
    label: d.zone_name ? `${d.zone_name}${d.borough ? ` (${d.borough})` : ''}` : `Zone ${d.zone_id}`,
  }));
  return (
    <ResponsiveContainer width="100%" height={320}>
      <BarChart data={rows} layout="vertical" margin={{ left: 30 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis type="number" stroke="#94a3b8" fontSize={12} />
        <YAxis type="category" dataKey="label" stroke="#94a3b8" fontSize={11} width={160} />
        <Tooltip />
        <Bar dataKey="trip_count" fill="#3B82F6" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
