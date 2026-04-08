-- =============================================================================
-- NYC Taxi Analytics Platform — PostgreSQL bootstrap
-- =============================================================================

CREATE DATABASE nyc_taxi;
CREATE USER taxi_user WITH ENCRYPTED PASSWORD 'taxi_pass';
GRANT ALL PRIVILEGES ON DATABASE nyc_taxi TO taxi_user;

CREATE USER airflow WITH ENCRYPTED PASSWORD 'airflow';
CREATE DATABASE airflow OWNER airflow;
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;

\c nyc_taxi;

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS realtime;

GRANT ALL ON SCHEMA raw TO taxi_user;
GRANT ALL ON SCHEMA analytics TO taxi_user;
GRANT ALL ON SCHEMA realtime TO taxi_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT ALL ON TABLES TO taxi_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA realtime GRANT ALL ON TABLES TO taxi_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA raw GRANT ALL ON TABLES TO taxi_user;

CREATE TABLE IF NOT EXISTS analytics.hourly_zone_demand (
    zone_id              INTEGER     NOT NULL,
    hour_start           TIMESTAMP   NOT NULL,
    trip_count           INTEGER     NOT NULL,
    avg_fare             NUMERIC(10,2),
    avg_distance         NUMERIC(10,2),
    avg_duration_minutes NUMERIC(10,2),
    total_revenue        NUMERIC(12,2),
    avg_tip_percentage   NUMERIC(5,2),
    PRIMARY KEY (zone_id, hour_start)
);

CREATE TABLE IF NOT EXISTS analytics.daily_summary (
    trip_date           DATE PRIMARY KEY,
    total_trips         INTEGER,
    total_revenue       NUMERIC(14,2),
    avg_fare            NUMERIC(10,2),
    avg_trip_distance   NUMERIC(10,2),
    cash_payment_pct    NUMERIC(5,2),
    credit_payment_pct  NUMERIC(5,2),
    avg_passenger_count NUMERIC(4,2)
);

CREATE TABLE IF NOT EXISTS realtime.zone_demand_live (
    zone_id      INTEGER   NOT NULL,
    window_start TIMESTAMP NOT NULL,
    window_end   TIMESTAMP NOT NULL,
    trip_count   INTEGER,
    avg_fare     NUMERIC(10,2),
    updated_at   TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (zone_id, window_start)
);

CREATE INDEX IF NOT EXISTS idx_hourly_zone_demand_hour ON analytics.hourly_zone_demand(hour_start);
CREATE INDEX IF NOT EXISTS idx_daily_summary_date     ON analytics.daily_summary(trip_date);
CREATE INDEX IF NOT EXISTS idx_realtime_window        ON realtime.zone_demand_live(window_start);

GRANT ALL ON ALL TABLES IN SCHEMA analytics TO taxi_user;
GRANT ALL ON ALL TABLES IN SCHEMA realtime TO taxi_user;

ALTER SCHEMA analytics OWNER TO taxi_user;
ALTER SCHEMA realtime  OWNER TO taxi_user;
ALTER SCHEMA raw       OWNER TO taxi_user;
ALTER TABLE analytics.hourly_zone_demand OWNER TO taxi_user;
ALTER TABLE analytics.daily_summary       OWNER TO taxi_user;
ALTER TABLE realtime.zone_demand_live     OWNER TO taxi_user;
