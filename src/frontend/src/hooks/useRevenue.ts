import { useQuery } from '@tanstack/react-query';
import {
  fetchDailyRevenue,
  fetchFareDistribution,
  fetchPaymentBreakdown,
  fetchTipAnalysis,
} from '../api/client';
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

export const useTipAnalysis = (range: DateRange) =>
  useQuery({
    queryKey: ['tip-analysis', range],
    queryFn: () => fetchTipAnalysis(range),
  });

export const useFareDistribution = (range: DateRange) =>
  useQuery({
    queryKey: ['fare-distribution', range],
    queryFn: () => fetchFareDistribution(range),
  });
