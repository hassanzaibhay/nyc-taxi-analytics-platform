# =============================================================================
# NYC Taxi Analytics Platform — Makefile
# Works on Windows Git Bash, macOS, and Linux. Uses `docker compose` (v2).
# =============================================================================

SHELL := /bin/bash
COMPOSE := docker compose
SERVICE ?=

.DEFAULT_GOAL := help

# === Infrastructure ===

.PHONY: help
help: ## Show all targets with descriptions
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

.PHONY: build
build: ## Pull/build all Docker images
	$(COMPOSE) build

.PHONY: up
up: ## Start the full cluster in detached mode
	$(COMPOSE) up -d

.PHONY: down
down: ## Stop all containers
	$(COMPOSE) down

.PHONY: restart
restart: down up ## Restart cluster

.PHONY: clean
clean: ## Stop containers, remove volumes, and clear data outputs
	$(COMPOSE) down -v
	rm -rf data/output data/processed

.PHONY: status
status: ## Show status of all containers
	$(COMPOSE) ps

.PHONY: logs
logs: ## Tail logs (use SERVICE=name to filter)
	$(COMPOSE) logs -f $(SERVICE)

.PHONY: shell-hadoop
shell-hadoop: ## Exec into namenode bash
	$(COMPOSE) exec namenode bash

.PHONY: shell-spark
shell-spark: ## Exec into spark-master bash
	$(COMPOSE) exec spark-master bash

.PHONY: shell-airflow
shell-airflow: ## Exec into airflow-webserver bash
	$(COMPOSE) exec airflow-webserver bash

.PHONY: shell-postgres
shell-postgres: ## Open psql in postgres
	$(COMPOSE) exec postgres psql -U taxi_user -d nyc_taxi

# === Data ===

.PHONY: download
download: ## Download TLC parquet files
	python -m src.ingestion.download_tlc_data

.PHONY: validate
validate: ## Run data quality checks
	python -m src.ingestion.validate_data

.PHONY: ingest
ingest: ## Upload raw Parquet files to HDFS
	docker compose cp data/raw/. namenode:/tmp/staging/
	docker compose cp scripts/ingest-to-hdfs.sh namenode:/tmp/ingest-to-hdfs.sh
	docker compose exec namenode bash /tmp/ingest-to-hdfs.sh

.PHONY: seed
seed: download validate ingest ## download + validate + ingest

# === Processing ===

.PHONY: convert-parquet
convert-parquet: ## Convert Parquet in HDFS to CSV for Hadoop Streaming
	$(COMPOSE) exec spark-master /opt/spark/bin/spark-submit --master 'local[*]' /opt/spark-jobs/utils/parquet_to_csv.py

.PHONY: run-hadoop
run-hadoop: convert-parquet ## Submit Hadoop MapReduce job
	bash scripts/submit-hadoop-job.sh

.PHONY: run-spark-batch
run-spark-batch: ## Submit Spark batch analytics jobs
	bash scripts/submit-spark-job.sh trip_analytics
	bash scripts/submit-spark-job.sh revenue_aggregation

.PHONY: run-spark-stream
run-spark-stream: ## Start Spark Structured Streaming job
	bash scripts/submit-spark-job.sh realtime_demand

.PHONY: run-kafka stop-kafka
run-kafka: ## Run the simulated Kafka producer (containerized)
	docker compose --profile producer up --build kafka-producer

stop-kafka: ## Stop the Kafka producer container
	docker compose --profile producer down

.PHONY: run-all-batch
run-all-batch: ingest run-hadoop run-spark-batch ## Full batch pipeline

# === Dashboard ===

.PHONY: dashboard
dashboard: ## Start API + frontend
	$(COMPOSE) up -d api frontend

.PHONY: api
api: ## Start FastAPI only
	$(COMPOSE) up -d api

.PHONY: frontend-dev
frontend-dev: ## Run React dev server with hot reload
	cd src/frontend && npm install && npm run dev

.PHONY: frontend-build
frontend-build: ## Build React production bundle
	cd src/frontend && npm install && npm run build

# === Testing ===

.PHONY: test
test: ## Run all tests
	pytest

.PHONY: test-mappers
test-mappers: ## Test Hadoop mappers/reducers
	pytest tests/test_mappers.py tests/test_reducers.py

.PHONY: test-spark
test-spark: ## Test Spark jobs
	pytest tests/test_spark_jobs.py

.PHONY: lint
lint: ## Run ruff + mypy
	ruff check src tests
	ruff format --check src tests
	mypy src

.PHONY: format
format: ## Run ruff format
	ruff format src tests
	ruff check --fix src tests

# === Cloud ===

.PHONY: tf-plan-aws
tf-plan-aws: ## Terraform plan for AWS
	cd infra/aws && terraform init && terraform plan -var-file=env/dev.tfvars

.PHONY: tf-apply-aws
tf-apply-aws: ## Terraform apply for AWS
	cd infra/aws && terraform apply -var-file=env/dev.tfvars

.PHONY: tf-destroy-aws
tf-destroy-aws: ## Terraform destroy for AWS
	cd infra/aws && terraform destroy -var-file=env/dev.tfvars

.PHONY: tf-plan-gcp
tf-plan-gcp: ## Terraform plan for GCP
	cd infra/gcp && terraform init && terraform plan

.PHONY: tf-apply-gcp
tf-apply-gcp: ## Terraform apply for GCP
	cd infra/gcp && terraform apply

.PHONY: tf-destroy-gcp
tf-destroy-gcp: ## Terraform destroy for GCP
	cd infra/gcp && terraform destroy

# === Convenience ===

.PHONY: wait
wait: ## Wait for all services to become healthy
	@echo "Waiting for services..."
	@sleep 30

.PHONY: urls
urls: ## Print all web UI URLs
	@echo "Frontend Dashboard : http://localhost:3000"
	@echo "FastAPI Docs       : http://localhost:8000/docs"
	@echo "Hadoop NameNode UI : http://localhost:9870"
	@echo "YARN ResourceMgr   : http://localhost:8088"
	@echo "Spark Master UI    : http://localhost:8080"
	@echo "Airflow            : http://localhost:8081 (admin/admin)"
	@echo "MinIO Console      : http://localhost:9001"

.PHONY: all
all: build up wait seed run-all-batch dashboard urls ## Full lifecycle: build → up → seed → batch → dashboard
