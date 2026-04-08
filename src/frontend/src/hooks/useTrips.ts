import { useQuery } from '@tanstack/react-query';
import { fetchHourlyTrips, fetchTripSummary } from '../api/client';
import type { DateRange } from '../types';

export const useTripSummary = (range: DateRange) =>
  useQuery({
    queryKey: ['trip-summary', range],
    queryFn: () => fetchTripSummary(range),
  });

export const useHourlyTrips = (range: DateRange, zoneId?: number) =>
  useQuery({
    queryKey: ['hourly-trips', range, zoneId],
    queryFn: () => fetchHourlyTrips(range, zoneId),
  });
