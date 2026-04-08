import { useQuery } from '@tanstack/react-query';
import { fetchDailyRevenue, fetchPaymentBreakdown } from '../api/client';
import type { DateRange } from '../types';

export const useDailyRevenue = (range: DateRange) =>
  useQuery({
    queryKey: ['daily-revenue', range],
    queryFn: () => fetchDailyRevenue(range),
  });

export const usePaymentBreakdown = (range: DateRange) =>
  useQuery({
    queryKey: ['payment-breakdown', range],
    queryFn: () => fetchPaymentBreakdown(range),
  });
