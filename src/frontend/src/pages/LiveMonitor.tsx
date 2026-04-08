import { useRealtime } from '../hooks/useRealtime';

const STATUS_COLOR = {
  connecting: 'bg-amber-500',
  connected: 'bg-emerald-500 animate-pulse',
  disconnected: 'bg-rose-500',
};

export default function LiveMonitor() {
  const { data, status } = useRealtime();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Live Monitor</h2>
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <span className={`h-2 w-2 rounded-full ${STATUS_COLOR[status]}`} />
          {status}
        </div>
      </div>

      {data.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-300 dark:border-slate-700 p-10 text-center text-slate-500">
          Waiting for live events from the streaming pipeline...
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6">
          {data.slice(0, 24).map((d) => (
            <div
              key={`${d.zone_id}-${d.window_start}`}
              className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-4 shadow-sm"
            >
              <div className="text-xs font-medium text-slate-500">Zone {d.zone_id}</div>
              <div className="mt-2 text-2xl font-semibold">{d.trip_count}</div>
              <div className="mt-1 text-xs text-slate-400">
                {d.avg_fare !== null ? `$${Number(d.avg_fare).toFixed(2)} avg` : '—'}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
