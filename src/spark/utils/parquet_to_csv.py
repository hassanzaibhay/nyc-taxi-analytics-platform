"""Convert NYC TLC Parquet files in HDFS to CSV for Hadoop Streaming."""
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("parquet-to-csv").getOrCreate()
df = spark.read.parquet("hdfs://namenode:8020/data/nyc-taxi/raw/*.parquet")
(
    df.coalesce(4)
    .write.mode("overwrite")
    .option("header", "true")
    .csv("hdfs://namenode:8020/data/nyc-taxi/csv/")
)
spark.stop()
