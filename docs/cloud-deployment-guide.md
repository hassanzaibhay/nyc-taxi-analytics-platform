# Cloud Deployment Guide

## Prerequisites

- Terraform ≥ 1.6
- AWS CLI (for AWS) or gcloud CLI (for GCP) configured with credentials
- A VPC with at least 2 private subnets
- A strong DB password stored in your secret manager of choice

## AWS

### 1. Configure variables

```bash
cd infra/aws
cat > terraform.tfvars <<'EOF'
vpc_id        = "vpc-xxxxxxxx"
subnet_ids    = ["subnet-aaa", "subnet-bbb"]
emr_subnet_id = "subnet-aaa"
db_password   = "use-a-real-secret"
EOF
```

### 2. Plan and apply

```bash
terraform init
terraform plan -var-file=env/dev.tfvars
terraform apply -var-file=env/dev.tfvars
```

### 3. Outputs

After apply, Terraform prints the S3 bucket name, RDS endpoint, EMR cluster ID, MSK bootstrap brokers, and MWAA webserver URL.

### 4. Teardown

```bash
terraform destroy -var-file=env/dev.tfvars
```

## GCP

### 1. Configure variables

```bash
cd infra/gcp
cat > terraform.tfvars <<'EOF'
gcp_project_id = "your-gcp-project"
gcp_region     = "us-central1"
db_password    = "use-a-real-secret"
EOF
```

### 2. Plan and apply

```bash
terraform init
terraform plan
terraform apply
```

## Cost Estimation (rough, monthly, dev sizing)

| Service | AWS (USD) | GCP (USD) |
|---|---|---|
| Compute (EMR / Dataproc, 2 workers) | ~$250 | ~$220 |
| Object store (S3 / GCS, 100 GB) | ~$3 | ~$2 |
| Managed Kafka (MSK / Pub/Sub) | ~$120 | ~$40 |
| Managed Airflow (MWAA / Composer) | ~$350 | ~$380 |
| Managed PostgreSQL (RDS / Cloud SQL) | ~$15 | ~$10 |
| **Total (idle dev)** | **~$740** | **~$650** |

Tear environments down between work sessions to control cost.
