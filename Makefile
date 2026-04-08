# =============================================================================
# NYC Taxi Analytics Platform — Makefile
# Cross-platform: Windows (cmd/PowerShell + choco make), macOS, Linux.
# All non-trivial shell logic runs INSIDE Docker containers.
# Host side uses only: docker, docker compose, git, python, npm, terraform.
# =============================================================================

COMPOSE := docker compose
SERVICE ?=

# Timestamp for Hadoop output dir — computed via python (cross-platform).
HADOOP_TS := $(shell python -c "import time;print(time.strftime('%Y%m%d%H%M%S'))")

.DEFAULT_GOAL := help

# === Help =====================================================================

.PHONY: help
help:
	@echo NYC Taxi Analytics Platform
	@echo Infrastructure:
	@echo   make build             Pull/build all Docker images
	@echo   make up                Start full cluster
	@echo   make down              Stop all containers
	@echo   make restart           Restart all containers
	@echo   make clean             Remove containers, volumes, and local output
	@echo   make status            Show container status
	@echo   make logs              Tail all logs - SERVICE=name to filter
	@echo Data:
	@echo   make download          Download TLC Parquet files
	@echo   make validate          Run data quality checks
	@echo   make ingest            Upload Parquet files to HDFS
	@echo   make convert-parquet   Convert Parquet to CSV for Hadoop
	@echo   make seed              download + validate + ingest
	@echo   make load-zones        Load NYC taxi zone lookup into PostgreSQL
	@echo Processing:
	@echo   make run-hadoop        Run Hadoop MapReduce job
	@echo   make run-spark-batch   Run all Spark batch jobs
	@echo   make run-spark-stream  Start Spark Streaming job
	@echo   make run-kafka         Start Kafka producer
	@echo   make stop-kafka        Stop Kafka producer
	@echo   make run-all-batch     Full batch pipeline
	@echo Dashboard:
	@echo   make dashboard         Start API + frontend
	@echo   make api               Start FastAPI only
	@echo   make frontend-dev      Run React dev server with hot reload
	@echo   make frontend-build    Build React production bundle
	@echo Cloud:
	@echo   make tf-plan-aws       Terraform plan for AWS
	@echo   make tf-apply-aws      Terraform apply for AWS
	@echo   make tf-plan-gcp       Terraform plan for GCP
	@echo   make tf-apply-gcp      Terraform apply for GCP
	@echo Utilities:
	@echo   make shell-hadoop      Shell into namenode
	@echo   make shell-spark       Shell into spark-master
	@echo   make shell-postgres    Open psql in postgres
	@echo   make test              Run tests
	@echo   make lint              Run ruff + mypy
	@echo   make format            Auto-format with ruff
	@echo   make urls              Show all web UI URLs

# === Infrastructure ===========================================================

.PHONY: build
build:
	$(COMPOSE) build

.PHONY: up
up:
	$(COMPOSE) up -d

.PHONY: down
down:
	$(COMPOSE) down

.PHONY: restart
restart: down up

.PHONY: clean
clean:
	$(COMPOSE) down -v
	python -c "import shutil; shutil.rmtree('data/output', ignore_errors=True); shutil.rmtree('data/processed', ignore_errors=True)"

.PHONY: status
status:
	$(COMPOSE) ps

.PHONY: logs
logs:
	$(COMPOSE) logs -f --tail=200 $(SERVICE)

.PHONY: shell-hadoop
shell-hadoop:
	$(COMPOSE) exec namenode bash

.PHONY: shell-spark
shell-spark:
	$(COMPOSE) exec spark-master bash

.PHONY: shell-airflow
shell-airflow:
	$(COMPOSE) exec airflow-webserver bash

.PHONY: shell-postgres
shell-postgres:
	$(COMPOSE) exec postgres psql -U taxi_user -d nyc_taxi

# === Data =====================================================================

.PHONY: download
download:
	python -m src.ingestion.download_tlc_data

.PHONY: validate
validate:
	python -m src.ingestion.validate_data

.PHONY: ingest
ingest:
	$(COMPOSE) cp data/raw/. namenode:/tmp/staging/
	$(COMPOSE) cp scripts/ingest-to-hdfs.sh namenode:/tmp/ingest-to-hdfs.sh
	$(COMPOSE) exec namenode bash /tmp/ingest-to-hdfs.sh

.PHONY: seed
seed: download validate ingest

.PHONY: load-zones
load-zones:
	bash scripts/load-zone-lookup.sh

# === Processing ===============================================================

.PHONY: convert-parquet
convert-parquet:
	$(COMPOSE) exec spark-master /opt/spark/bin/spark-submit --master local[*] /opt/spark-jobs/utils/parquet_to_csv.py

.PHONY: run-hadoop
run-hadoop: convert-parquet
	$(COMPOSE) exec -T namenode hadoop jar /opt/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.1.jar -files /opt/mapreduce/mapper_zone_aggregation.py,/opt/mapreduce/reducer_zone_aggregation.py -mapper "/usr/bin/python3 mapper_zone_aggregation.py" -reducer "/usr/bin/python3 reducer_zone_aggregation.py" -input /data/nyc-taxi/csv -output /data/nyc-taxi/output/zone-agg-$(HADOOP_TS)

.PHONY: run-spark-batch
run-spark-batch: _spark-trip-analytics _spark-revenue

.PHONY: _spark-trip-analytics
_spark-trip-analytics:
	$(COMPOSE) exec -T -e PYTHONPATH=/opt spark-master /opt/spark/bin/spark-submit --master spark://spark-master:7077 --conf spark.executorEnv.PYTHONPATH=/opt --packages org.postgresql:postgresql:42.7.4 /opt/src/spark/batch/trip_analytics.py --master spark://spark-master:7077 --input hdfs://namenode:8020/data/nyc-taxi/raw

.PHONY: _spark-revenue
_spark-revenue:
	$(COMPOSE) exec -T -e PYTHONPATH=/opt spark-master /opt/spark/bin/spark-submit --master spark://spark-master:7077 --conf spark.executorEnv.PYTHONPATH=/opt --packages org.postgresql:postgresql:42.7.4 /opt/src/spark/batch/revenue_aggregation.py --master spark://spark-master:7077 --input hdfs://namenode:8020/data/nyc-taxi/raw

.PHONY: run-spark-stream
run-spark-stream:
	$(COMPOSE) exec -T -e PYTHONPATH=/opt spark-master /opt/spark/bin/spark-submit --master spark://spark-master:7077 --conf spark.executorEnv.PYTHONPATH=/opt --packages org.postgresql:postgresql:42.7.4,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.4 /opt/src/spark/streaming/realtime_demand.py --master spark://spark-master:7077

.PHONY: run-kafka
run-kafka:
	$(COMPOSE) --profile producer up --build kafka-producer

.PHONY: stop-kafka
stop-kafka:
	$(COMPOSE) --profile producer down

.PHONY: run-all-batch
run-all-batch: ingest run-hadoop run-spark-batch

# === Dashboard ================================================================

.PHONY: dashboard
dashboard:
	$(COMPOSE) up -d api frontend

.PHONY: api
api:
	$(COMPOSE) up -d api

.PHONY: frontend-dev
frontend-dev:
	cd src/frontend && npm install && npm run dev

.PHONY: frontend-build
frontend-build:
	cd src/frontend && npm install && npm run build

# === Testing ==================================================================

.PHONY: test
test:
	pytest

.PHONY: test-mappers
test-mappers:
	pytest tests/test_mappers.py tests/test_reducers.py

.PHONY: test-spark
test-spark:
	pytest tests/test_spark_jobs.py

.PHONY: lint
lint:
	ruff check src tests
	ruff format --check src tests
	mypy src/api src/ingestion src/kafka --ignore-missing-imports

.PHONY: format
format:
	ruff format src tests
	ruff check --fix src tests

# === Cloud ====================================================================

.PHONY: tf-plan-aws
tf-plan-aws:
	cd infra/aws && terraform init && terraform plan -var-file=env/dev.tfvars

.PHONY: tf-apply-aws
tf-apply-aws:
	cd infra/aws && terraform apply -var-file=env/dev.tfvars

.PHONY: tf-destroy-aws
tf-destroy-aws:
	cd infra/aws && terraform destroy -var-file=env/dev.tfvars

.PHONY: tf-plan-gcp
tf-plan-gcp:
	cd infra/gcp && terraform init && terraform plan

.PHONY: tf-apply-gcp
tf-apply-gcp:
	cd infra/gcp && terraform apply

.PHONY: tf-destroy-gcp
tf-destroy-gcp:
	cd infra/gcp && terraform destroy

# === Convenience ==============================================================

.PHONY: urls
urls:
	@echo Frontend Dashboard : http://localhost:3000
	@echo FastAPI Docs       : http://localhost:8000/docs
	@echo Hadoop NameNode UI : http://localhost:9870
	@echo YARN ResourceMgr   : http://localhost:8088
	@echo Spark Master UI    : http://localhost:8080
	@echo Airflow            : http://localhost:8081   admin/admin
	@echo MinIO Console      : http://localhost:9001
	@echo Kafka external     : localhost:9094

.PHONY: all
all: build up seed run-all-batch dashboard urls
