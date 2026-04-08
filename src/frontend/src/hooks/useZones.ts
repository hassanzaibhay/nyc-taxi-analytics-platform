import { useQuery } from '@tanstack/react-query';
import { fetchTopZones, fetchZoneDemand } from '../api/client';
import type { DateRange } from '../types';

export const useZoneDemand = (range: DateRange) =>
  useQuery({
    queryKey: ['zone-demand', range],
    queryFn: () => fetchZoneDemand(range),
  });

export const useTopZones = (range: DateRange, n = 10) =>
  useQuery({
    queryKey: ['top-zones', range, n],
    queryFn: () => fetchTopZones(range, n),
  });
