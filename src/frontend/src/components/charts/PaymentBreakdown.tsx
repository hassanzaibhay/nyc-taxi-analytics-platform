import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import type { PaymentBreakdown as PB } from '../../types';
import { formatNumber } from '../../utils/formatters';

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
  const rows = data.map((d) => {
    const pct = (d.trip_count / total) * 100;
    return {
      ...d,
      name: `${formatName(d.payment_type)} — ${formatNumber(d.trip_count)} (${pct.toFixed(0)}%)`,
      shortName: formatName(d.payment_type),
      pct,
    };
  });

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={rows}
          dataKey="trip_count"
          nameKey="shortName"
          innerRadius={50}
          outerRadius={85}
          paddingAngle={2}
          label={({ shortName, pct }: { shortName: string; pct: number }) =>
            `${shortName} ${pct.toFixed(0)}%`
          }
          labelLine={false}
        >
          {rows.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          formatter={(value: number, _name, entry) => {
            const pct = (entry?.payload as { pct?: number } | undefined)?.pct ?? 0;
            return [`${formatNumber(value)} trips (${pct.toFixed(1)}%)`, 'Count'];
          }}
        />
        <Legend
          verticalAlign="bottom"
          height={48}
          iconType="circle"
          payload={rows.map((r, i) => ({
            value: r.name,
            type: 'circle',
            id: r.shortName,
            color: COLORS[i % COLORS.length],
          }))}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
