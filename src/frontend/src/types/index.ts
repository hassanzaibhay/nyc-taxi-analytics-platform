export interface HourlyTrip {
  zone_id: number;
  hour_start: string;
  trip_count: number;
  avg_fare: number | null;
  avg_distance: number | null;
  total_revenue: number | null;
}

export interface TripSummary {
  total_trips: number;
  total_revenue: number;
  avg_fare: number;
  avg_tip_pct: number;
  avg_distance: number;
}

export interface ZoneDemandPoint {
  zone_id: number;
  hour: number;
  avg_trip_count: number;
  zone_name: string | null;
  borough: string | null;
}

export interface TopZone {
  zone_id: number;
  trip_count: number;
  total_revenue: number;
  zone_name: string | null;
  borough: string | null;
}

export interface FareBucket {
  fare_bucket: number;
  count: number;
}

export interface DailyRevenue {
  trip_date: string;
  total_trips: number;
  total_revenue: number;
  avg_fare: number;
  cash_pct: number | null;
  credit_pct: number | null;
}

export interface PaymentBreakdown {
  payment_type: string;
  trip_count: number;
  revenue: number;
}

export interface RealtimeDemand {
  zone_id: number;
  window_start: string;
  window_end: string;
  trip_count: number;
  avg_fare: number | null;
  zone_name: string | null;
  borough: string | null;
}

export interface DateRange {
  from?: string;
  to?: string;
}

export interface DataDateRange {
  min_date: string;
  max_date: string;
}

export interface TipByHour {
  hour: number;
  avg_tip_pct: number;
}
