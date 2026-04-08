"""Monthly TLC data ingestion DAG: download → validate → upload to HDFS."""
from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag, task

DEFAULT_ARGS = {
    "owner": "hassanzaibhay",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    dag_id="ingest_monthly_data",
    description="Download, validate, and upload monthly NYC TLC parquet data",
    default_args=DEFAULT_ARGS,
    schedule="@monthly",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["nyc-taxi", "ingestion"],
)
def ingest_monthly_data() -> None:
    @task
    def download(year: int, month: int) -> str:
        import sys
        sys.path.insert(0, "/opt/airflow/src")
        from ingestion.download_tlc_data import download_one, file_url
        from pathlib import Path

        url = file_url("yellow", year, month)
        dest = Path(f"/opt/airflow/data/raw/yellow_tripdata_{year:04d}-{month:02d}.parquet")
        if not download_one(url, dest):
            raise RuntimeError(f"Download failed: {url}")
        return str(dest)

    @task
    def validate(path: str) -> str:
        import sys
        sys.path.insert(0, "/opt/airflow/src")
        from ingestion.validate_data import validate_file
        from pathlib import Path

        if not validate_file(Path(path)):
            raise RuntimeError(f"Validation failed: {path}")
        return path

    @task
    def upload(path: str) -> str:
        import sys
        sys.path.insert(0, "/opt/airflow/src")
        from ingestion.upload_to_hdfs import upload as upload_fn
        from pathlib import Path

        if not upload_fn(Path(path), "/data/nyc-taxi/raw"):
            raise RuntimeError(f"Upload failed: {path}")
        return path

    downloaded = download(2024, 1)
    validated = validate(downloaded)
    upload(validated)


ingest_monthly_data()
