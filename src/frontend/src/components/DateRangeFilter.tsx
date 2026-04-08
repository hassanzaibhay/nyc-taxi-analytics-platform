import { useEffect, useState } from 'react';
import { format, parseISO, subDays } from 'date-fns';
import type { DateRange } from '../types';
import { useDataDateRange } from '../hooks/useDateRange';

interface Props {
  onChange: (range: DateRange) => void;
}

const presets = [
  { label: '7d', days: 7 },
  { label: '30d', days: 30 },
  { label: '90d', days: 90 },
  { label: 'All', days: -1 },
];

export default function DateRangeFilter({ onChange }: Props) {
  const { minDate, maxDate, isLoading } = useDataDateRange();
  const [active, setActive] = useState<string>('30d');

  const apply = (days: number, label: string) => {
    if (!minDate || !maxDate) return;
    setActive(label);
    const max = parseISO(maxDate);
    if (days < 0) {
      onChange({ from: minDate, to: maxDate });
    } else {
      const from = subDays(max, days - 1);
      const min = parseISO(minDate);
      onChange({
        from: format(from < min ? min : from, 'yyyy-MM-dd'),
        to: maxDate,
      });
    }
  };

  // Apply default preset once data range loads.
  useEffect(() => {
    if (minDate && maxDate) apply(30, '30d');
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [minDate, maxDate]);

  return (
    <div className="flex items-center gap-2">
      {presets.map((p) => (
        <button
          key={p.label}
          disabled={isLoading}
          onClick={() => apply(p.days, p.label)}
          className={`rounded-lg border px-3 py-1.5 text-sm font-medium transition ${
            active === p.label
              ? 'border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300'
              : 'border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
          }`}
        >
          {p.label === 'All' ? 'All Data' : `Last ${p.label}`}
        </button>
      ))}
    </div>
  );
}
