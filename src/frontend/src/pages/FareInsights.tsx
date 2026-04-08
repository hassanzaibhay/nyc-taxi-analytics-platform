import { useState } from 'react';
import DateRangeFilter from '../components/DateRangeFilter';
import PaymentBreakdownChart from '../components/charts/PaymentBreakdown';
import { usePaymentBreakdown, useTipAnalysis } from '../hooks/useRevenue';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { DateRange } from '../types';

export default function FareInsights() {
  const [range, setRange] = useState<DateRange>({});
  const payments = usePaymentBreakdown(range);
  const tips = useTipAnalysis(range);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Fare Insights</h2>
        <DateRangeFilter onChange={setRange} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 shadow-sm">
          <h3 className="mb-4 text-sm font-semibold text-slate-500">Payment Type Breakdown</h3>
          {payments.data ? (
            <PaymentBreakdownChart data={payments.data} />
          ) : (
            <div className="h-64 animate-pulse rounded bg-slate-100" />
          )}
        </div>
        <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 shadow-sm">
          <h3 className="mb-4 text-sm font-semibold text-slate-500">Tip Analysis</h3>
          {tips.isLoading ? (
            <div className="h-64 animate-pulse rounded bg-slate-100" />
          ) : tips.data && tips.data.length > 0 ? (
            <ResponsiveContainer width="100%" height={256}>
              <BarChart data={tips.data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis
                  dataKey="hour"
                  label={{ value: 'Hour of Day', position: 'insideBottom', offset: -4 }}
                  tick={{ fontSize: 12 }}
                />
                <YAxis
                  label={{ value: 'Avg Tip %', angle: -90, position: 'insideLeft' }}
                  tick={{ fontSize: 12 }}
                />
                <Tooltip
                  formatter={(value: number) => [`${value}%`, 'Avg Tip']}
                  labelFormatter={(hour: number) => `Hour ${hour}:00`}
                />
                <Bar dataKey="avg_tip_pct" fill="#10B981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex h-64 items-center justify-center text-sm text-slate-500">
              No tip data available for this range.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
