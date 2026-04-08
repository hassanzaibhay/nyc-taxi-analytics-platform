terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.70"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile

  default_tags {
    tags = {
      project     = "nyc-taxi-analytics"
      environment = var.environment
      owner       = "hassanzaibhay"
      managed_by  = "terraform"
    }
  }
}

module "s3" {
  source      = "./modules/s3"
  bucket_name = "${var.project_name}-${var.environment}-data"
}

module "rds" {
  source         = "./modules/rds"
  identifier     = "${var.project_name}-${var.environment}"
  instance_class = var.rds_instance_class
  db_name        = var.db_name
  db_username    = var.db_username
  db_password    = var.db_password
  vpc_id         = var.vpc_id
  subnet_ids     = var.subnet_ids
}

module "emr" {
  source        = "./modules/emr"
  cluster_name  = "${var.project_name}-${var.environment}"
  release_label = var.emr_release_label
  master_type   = var.emr_master_type
  core_type     = var.emr_core_type
  core_count    = var.emr_core_count
  log_uri       = "s3://${module.s3.bucket_name}/emr-logs/"
  subnet_id     = var.emr_subnet_id
}

module "msk" {
  source              = "./modules/msk"
  cluster_name        = "${var.project_name}-${var.environment}"
  kafka_version       = var.kafka_version
  broker_instance_type = var.msk_broker_instance_type
  broker_count        = var.msk_broker_count
  subnet_ids          = var.subnet_ids
  security_group_ids  = var.msk_security_group_ids
}

module "mwaa" {
  source             = "./modules/mwaa"
  environment_name   = "${var.project_name}-${var.environment}"
  source_bucket_arn  = module.s3.bucket_arn
  dag_s3_path        = "dags/"
  vpc_id             = var.vpc_id
  subnet_ids         = var.subnet_ids
  airflow_version    = var.airflow_version
}
