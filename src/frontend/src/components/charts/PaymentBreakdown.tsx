import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import type { PaymentBreakdown as PB } from '../../types';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#64748B'];

const PAYMENT_NAMES: Record<string, string> = {
  credit_card: 'Credit Card',
  cash: 'Cash',
  no_charge: 'No Charge',
  dispute: 'Dispute',
  unknown: 'Unknown',
  voided: 'Voided',
  '1': 'Credit Card',
  '2': 'Cash',
  '3': 'No Charge',
  '4': 'Dispute',
  '5': 'Unknown',
  '6': 'Voided',
};

const formatName = (raw: string) => PAYMENT_NAMES[raw] ?? raw;

export default function PaymentBreakdownChart({ data }: { data: PB[] }) {
  const total = data.reduce((sum, d) => sum + d.trip_count, 0) || 1;
  const rows = data.map((d) => ({
    ...d,
    name: formatName(d.payment_type),
    pct: (d.trip_count / total) * 100,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={rows}
          dataKey="trip_count"
          nameKey="name"
          innerRadius={55}
          outerRadius={95}
          paddingAngle={2}
          label={({ name, pct }: { name: string; pct: number }) =>
            `${name} ${pct.toFixed(0)}%`
          }
          labelLine={false}
        >
          {rows.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          formatter={(value: number, _n: string, entry: { payload: { pct: number } }) => [
            `${value.toLocaleString()} trips (${entry.payload.pct.toFixed(1)}%)`,
            'Count',
          ]}
        />
        <Legend verticalAlign="bottom" height={32} iconType="circle" />
      </PieChart>
    </ResponsiveContainer>
  );
}
