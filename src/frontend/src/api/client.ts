import axios from 'axios';
import type {
  DailyRevenue,
  DataDateRange,
  DateRange,
  HourlyTrip,
  PaymentBreakdown,
  RealtimeDemand,
  TopZone,
  TripSummary,
  ZoneDemandPoint,
} from '../types';

const baseURL = import.meta.env.VITE_API_URL || '/api';

export const api = axios.create({
  baseURL: baseURL.endsWith('/api') ? baseURL : `${baseURL}/api`,
  timeout: 30_000,
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    console.error('[api]', err?.response?.status, err?.config?.url);
    return Promise.reject(err);
  },
);

const params = (range: DateRange) => ({
  date_from: range.from,
  date_to: range.to,
});

export const fetchDataDateRange = () =>
  api.get<DataDateRange>('/trips/date-range').then((r) => r.data);

export const fetchTripSummary = (range: DateRange) =>
  api.get<TripSummary>('/trips/summary', { params: params(range) }).then((r) => r.data);

export const fetchHourlyTrips = (range: DateRange, zoneId?: number) =>
  api
    .get<HourlyTrip[]>('/trips/hourly', { params: { ...params(range), zone_id: zoneId } })
    .then((r) => r.data);

export const fetchZoneDemand = (range: DateRange) =>
  api.get<ZoneDemandPoint[]>('/zones/demand', { params: params(range) }).then((r) => r.data);

export const fetchTopZones = (range: DateRange, n = 10) =>
  api.get<TopZone[]>('/zones/top', { params: { ...params(range), n } }).then((r) => r.data);

export const fetchDailyRevenue = (range: DateRange) =>
  api.get<DailyRevenue[]>('/revenue/daily', { params: params(range) }).then((r) => r.data);

export const fetchPaymentBreakdown = (range: DateRange) =>
  api
    .get<PaymentBreakdown[]>('/revenue/payment-breakdown', { params: params(range) })
    .then((r) => r.data);

export const fetchRealtimeDemand = () =>
  api.get<RealtimeDemand[]>('/realtime/demand').then((r) => r.data);
