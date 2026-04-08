FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir confluent-kafka==2.5.3 pyarrow==17.0.0
COPY src /app/src
ENV PYTHONPATH=/app
CMD ["python", "-m", "src.kafka.producer", \
     "--data-dir", "/data/raw", \
     "--topic", "nyc-taxi.trips.raw", \
     "--bootstrap", "kafka:9092"]
