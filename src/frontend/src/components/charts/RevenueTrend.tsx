import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { DailyRevenue } from '../../types';
import { formatCurrency } from '../../utils/formatters';

export default function RevenueTrend({ data }: { data: DailyRevenue[] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data} margin={{ left: 10, right: 10 }}>
        <defs>
          <linearGradient id="rev" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#3B82F6" stopOpacity={0.4} />
            <stop offset="100%" stopColor="#3B82F6" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="trip_date" stroke="#94a3b8" fontSize={12} />
        <YAxis
          stroke="#94a3b8"
          fontSize={12}
          tickFormatter={(v: number) => formatCurrency(v)}
          width={70}
        />
        <Tooltip
          formatter={(value: number) => [formatCurrency(value), 'Revenue']}
          labelFormatter={(label: string) => `Date: ${label}`}
        />
        <Area
          type="monotone"
          dataKey="total_revenue"
          stroke="#3B82F6"
          fill="url(#rev)"
          strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
