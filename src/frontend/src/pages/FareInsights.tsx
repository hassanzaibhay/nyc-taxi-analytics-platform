import { useMemo, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import DateRangeFilter from '../components/DateRangeFilter';
import PaymentBreakdownChart from '../components/charts/PaymentBreakdown';
import { useFareDistribution, usePaymentBreakdown, useTipAnalysis } from '../hooks/useRevenue';
import { useTripSummary } from '../hooks/useTrips';
import type { DateRange } from '../types';
import {
  formatCurrency,
  formatHour,
  formatNumber,
  formatPercent,
} from '../utils/formatters';

const BUCKET_SIZE = 10;
const MAX_BUCKET = 100;

export default function FareInsights() {
  const [range, setRange] = useState<DateRange>({});
  const payments = usePaymentBreakdown(range);
  const tips = useTipAnalysis(range);
  const fares = useFareDistribution({ ...range });
  const summary = useTripSummary(range);

  // Aggregate buckets into $10 bins and collapse everything above $100 into "$100+"
  const fareRows = useMemo(() => {
    const bins = new Map<number, number>();
    let overflow = 0;
    for (const b of fares.data ?? []) {
      if (b.fare_bucket >= MAX_BUCKET) {
        overflow += b.count;
        continue;
      }
      const bin = Math.floor(b.fare_bucket / BUCKET_SIZE) * BUCKET_SIZE;
      bins.set(bin, (bins.get(bin) ?? 0) + b.count);
    }
    const rows = Array.from(bins.entries())
      .sort((a, b) => a[0] - b[0])
      .map(([bin, count]) => ({
        bin,
        count,
        label: `$${bin}`,
      }));
    if (overflow > 0) rows.push({ bin: MAX_BUCKET, count: overflow, label: '$100+' });
    return rows;
  }, [fares.data]);

  const peakBucket = useMemo(() => {
    if (fareRows.length === 0) return null;
    return fareRows.reduce((a, b) => (a.count > b.count ? a : b));
  }, [fareRows]);

  const avgTip = useMemo(() => {
    if (!tips.data || tips.data.length === 0) return 0;
    return tips.data.reduce((s, t) => s + t.avg_tip_pct, 0) / tips.data.length;
  }, [tips.data]);

  const peakTipHour = useMemo(() => {
    if (!tips.data || tips.data.length === 0) return null;
    return tips.data.reduce((a, b) => (a.avg_tip_pct > b.avg_tip_pct ? a : b));
  }, [tips.data]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Fare Insights</h2>
        <DateRangeFilter onChange={setRange} />
      </div>

      {/* Fare Distribution — full width */}
      <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 shadow-sm">
        <div className="mb-4 flex items-start justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-200">
              Fare Distribution
            </h3>
            <p className="text-xs text-slate-500">Trip counts grouped into $10 fare ranges</p>
          </div>
          {peakBucket && (
            <div className="text-right text-xs text-slate-500">
              Most trips fall in the
              <span className="ml-1 font-semibold text-blue-600">
                {peakBucket.label === '$100+' ? '$100+' : `${peakBucket.label}–$${peakBucket.bin + BUCKET_SIZE}`}
              </span>{' '}
              range
            </div>
          )}
        </div>
        {fares.isLoading ? (
          <div className="h-64 animate-pulse rounded bg-slate-100" />
        ) : fareRows.length > 0 ? (
          <ResponsiveContainer width="100%" height={360}>
            <BarChart data={fareRows} margin={{ top: 10, right: 30, left: 20, bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey="label"
                tick={{ fontSize: 12 }}
                interval={0}
                label={{ value: 'Fare range (USD)', position: 'insideBottom', offset: -15 }}
              />
              <YAxis
                tick={{ fontSize: 12 }}
                tickFormatter={formatNumber}
                label={{ value: 'Trips', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip
                formatter={(value: number) => [formatNumber(value), 'Trips']}
                labelFormatter={(label: string) => `Fare range: ${label}`}
              />
              <Bar dataKey="count" fill="#3B82F6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex h-64 items-center justify-center text-sm text-slate-500">
            No fare data available for this range.
          </div>
        )}
      </div>

      {/* Payment Breakdown + Key Metrics */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 shadow-sm">
          <h3 className="mb-1 text-sm font-semibold text-slate-700 dark:text-slate-200">
            Payment Type Breakdown
          </h3>
          <p className="mb-4 text-xs text-slate-500">Share of trips by payment method</p>
          {payments.data ? (
            <PaymentBreakdownChart data={payments.data} />
          ) : (
            <div className="h-64 animate-pulse rounded bg-slate-100" />
          )}
        </div>

        <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 shadow-sm">
          <h3 className="mb-1 text-sm font-semibold text-slate-700 dark:text-slate-200">
            Key Metrics
          </h3>
          <p className="mb-4 text-xs text-slate-500">Summary for the selected date range</p>
          {summary.data ? (
            <ul className="space-y-3 text-sm">
              <li className="flex items-center justify-between border-b border-slate-100 pb-2 dark:border-slate-700">
                <span className="text-slate-500">Total trips</span>
                <span className="font-semibold">{formatNumber(summary.data.total_trips)}</span>
              </li>
              <li className="flex items-center justify-between border-b border-slate-100 pb-2 dark:border-slate-700">
                <span className="text-slate-500">Total revenue</span>
                <span className="font-semibold">
                  {formatCurrency(Number(summary.data.total_revenue))}
                </span>
              </li>
              <li className="flex items-center justify-between border-b border-slate-100 pb-2 dark:border-slate-700">
                <span className="text-slate-500">Avg fare</span>
                <span className="font-semibold">
                  {formatCurrency(Number(summary.data.avg_fare))}
                </span>
              </li>
              <li className="flex items-center justify-between border-b border-slate-100 pb-2 dark:border-slate-700">
                <span className="text-slate-500">Avg tip</span>
                <span className="font-semibold">
                  {formatPercent(Number(summary.data.avg_tip_pct))}
                </span>
              </li>
              <li className="flex items-center justify-between">
                <span className="text-slate-500">Avg distance</span>
                <span className="font-semibold">
                  {Number(summary.data.avg_distance).toFixed(2)} mi
                </span>
              </li>
            </ul>
          ) : (
            <div className="h-48 animate-pulse rounded bg-slate-100" />
          )}
        </div>
      </div>

      {/* Tip Analysis — full width */}
      <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 shadow-sm">
        <div className="mb-4 flex items-start justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-200">
              Tip % by Hour of Day
            </h3>
            <p className="text-xs text-slate-500">
              Green bars are above average, amber bars are below
            </p>
          </div>
          {peakTipHour && (
            <div className="text-right text-xs text-slate-500">
              Peak tipping hour:
              <span className="ml-1 font-semibold text-emerald-600">
                {formatHour(peakTipHour.hour)} ({formatPercent(peakTipHour.avg_tip_pct)})
              </span>
            </div>
          )}
        </div>
        {tips.isLoading ? (
          <div className="h-64 animate-pulse rounded bg-slate-100" />
        ) : tips.data && tips.data.length > 0 ? (
          <ResponsiveContainer width="100%" height={360}>
            <BarChart data={tips.data} margin={{ top: 10, right: 30, left: 20, bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey="hour"
                tick={{ fontSize: 11 }}
                tickFormatter={(h: number) => formatHour(h)}
                interval={2}
                label={{ value: 'Hour of day', position: 'insideBottom', offset: -15 }}
              />
              <YAxis
                tick={{ fontSize: 12 }}
                tickFormatter={(v: number) => `${v}%`}
                label={{ value: 'Avg Tip %', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip
                formatter={(value: number) => [`${value.toFixed(2)}%`, 'Avg Tip']}
                labelFormatter={(hour: number) => formatHour(hour)}
              />
              <ReferenceLine
                y={avgTip}
                stroke="#64748b"
                strokeDasharray="4 4"
                label={{
                  value: `Avg ${formatPercent(avgTip)}`,
                  position: 'right',
                  fill: '#64748b',
                  fontSize: 11,
                }}
              />
              <Bar dataKey="avg_tip_pct" radius={[4, 4, 0, 0]}>
                {tips.data.map((t) => (
                  <Cell
                    key={t.hour}
                    fill={t.avg_tip_pct >= avgTip ? '#10B981' : '#F59E0B'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex h-64 items-center justify-center text-sm text-slate-500">
            No tip data available for this range.
          </div>
        )}
      </div>
    </div>
  );
}
