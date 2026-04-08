"""Post-batch data quality checks against PostgreSQL analytics tables."""
from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag, task

DEFAULT_ARGS = {
    "owner": "hassanzaibhay",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    dag_id="data_quality_checks",
    description="Quality checks on analytics tables",
    default_args=DEFAULT_ARGS,
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["nyc-taxi", "quality"],
)
def data_quality_checks() -> None:
    @task
    def check_row_counts() -> None:
        from airflow.providers.postgres.hooks.postgres import PostgresHook

        hook = PostgresHook(postgres_conn_id="postgres_default")
        for table in ("analytics.hourly_zone_demand", "analytics.daily_summary"):
            count = hook.get_first(f"SELECT COUNT(*) FROM {table}")[0]
            if count == 0:
                raise ValueError(f"{table} is empty")

    @task
    def check_value_ranges() -> None:
        from airflow.providers.postgres.hooks.postgres import PostgresHook

        hook = PostgresHook(postgres_conn_id="postgres_default")
        bad = hook.get_first(
            "SELECT COUNT(*) FROM analytics.hourly_zone_demand WHERE avg_fare < 0"
        )[0]
        if bad > 0:
            raise ValueError(f"{bad} rows with negative fares")

    check_row_counts() >> check_value_ranges()


data_quality_checks()
