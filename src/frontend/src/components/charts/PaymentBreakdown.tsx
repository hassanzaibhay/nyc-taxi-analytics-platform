import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import type { PaymentBreakdown as PB } from '../../types';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444'];

export default function PaymentBreakdownChart({ data }: { data: PB[] }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <Pie
          data={data}
          dataKey="trip_count"
          nameKey="payment_type"
          innerRadius={60}
          outerRadius={100}
          paddingAngle={2}
        >
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  );
}
