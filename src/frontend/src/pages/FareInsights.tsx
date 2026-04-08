import { useState } from 'react';
import DateRangeFilter from '../components/DateRangeFilter';
import PaymentBreakdownChart from '../components/charts/PaymentBreakdown';
import { usePaymentBreakdown } from '../hooks/useRevenue';
import type { DateRange } from '../types';

export default function FareInsights() {
  const [range, setRange] = useState<DateRange>({});
  const payments = usePaymentBreakdown(range);

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
          <p className="text-sm text-slate-500">
            Tip percentage analytics surface here once additional metrics are populated.
          </p>
        </div>
      </div>
    </div>
  );
}
