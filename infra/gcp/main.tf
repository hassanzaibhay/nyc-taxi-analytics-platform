terraform {
  required_version = ">= 1.6"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.6"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

locals {
  labels = {
    project     = "nyc-taxi-analytics"
    environment = var.environment
    owner       = "hassanzaibhay"
    managed_by  = "terraform"
  }
}

module "gcs" {
  source      = "./modules/gcs"
  bucket_name = "${var.project_name}-${var.environment}-data"
  location    = var.gcp_region
  labels      = local.labels
}

module "dataproc" {
  source        = "./modules/dataproc"
  cluster_name  = "${var.project_name}-${var.environment}"
  region        = var.gcp_region
  master_type   = var.dataproc_master_type
  worker_type   = var.dataproc_worker_type
  worker_count  = var.dataproc_worker_count
  labels        = local.labels
}

module "pubsub" {
  source     = "./modules/pubsub"
  topic_name = "${var.project_name}-${var.environment}-trips"
  labels     = local.labels
}

module "cloudsql" {
  source        = "./modules/cloudsql"
  instance_name = "${var.project_name}-${var.environment}"
  region        = var.gcp_region
  tier          = var.cloudsql_tier
  db_name       = var.db_name
  db_user       = var.db_user
  db_password   = var.db_password
}

module "composer" {
  source        = "./modules/composer"
  name          = "${var.project_name}-${var.environment}"
  region        = var.gcp_region
  image_version = var.composer_image_version
  labels        = local.labels
}
