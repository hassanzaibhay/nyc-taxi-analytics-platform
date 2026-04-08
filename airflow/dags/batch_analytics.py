"""Daily batch analytics DAG: Hadoop MR + Spark batch jobs."""
from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

DEFAULT_ARGS = {
    "owner": "hassanzaibhay",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="batch_analytics",
    description="Hadoop MR + Spark batch analytics over NYC TLC data",
    default_args=DEFAULT_ARGS,
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["nyc-taxi", "batch"],
) as dag:

    run_hadoop_zone = BashOperator(
        task_id="hadoop_zone_aggregation",
        bash_command=(
            "hadoop jar ${HADOOP_STREAMING_JAR} "
            "-files /opt/mapreduce/mapper_zone_aggregation.py,"
            "/opt/mapreduce/reducer_zone_aggregation.py "
            "-mapper mapper_zone_aggregation.py "
            "-reducer reducer_zone_aggregation.py "
            "-input /data/nyc-taxi/raw "
            "-output /data/nyc-taxi/output/zone-agg-{{ ds_nodash }}"
        ),
    )

    run_trip_analytics = SparkSubmitOperator(
        task_id="spark_trip_analytics",
        application="/opt/airflow/src/spark/batch/trip_analytics.py",
        conn_id="spark_default",
        application_args=[
            "--input",
            "hdfs://namenode:8020/data/nyc-taxi/raw",
            "--master",
            "spark://spark-master:7077",
        ],
    )

    run_revenue = SparkSubmitOperator(
        task_id="spark_revenue_aggregation",
        application="/opt/airflow/src/spark/batch/revenue_aggregation.py",
        conn_id="spark_default",
        application_args=[
            "--input",
            "hdfs://namenode:8020/data/nyc-taxi/raw",
            "--master",
            "spark://spark-master:7077",
        ],
    )

    run_hadoop_zone >> run_trip_analytics >> run_revenue
