# =============================================================================
# Spark image — extends bitnami/spark:3.5.4 with project Python dependencies.
# =============================================================================
FROM apache/spark:3.5.4

USER root
RUN pip install --no-cache-dir psycopg2-binary==2.9.10 pyarrow==17.0.0
USER spark
