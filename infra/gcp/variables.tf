variable "gcp_project_id" { type = string }
variable "gcp_region" {
  type    = string
  default = "us-central1"
}
variable "environment" {
  type    = string
  default = "dev"
}
variable "project_name" {
  type    = string
  default = "nyc-taxi"
}

variable "dataproc_master_type"  { type = string  default = "n2-standard-4" }
variable "dataproc_worker_type"  { type = string  default = "n2-standard-4" }
variable "dataproc_worker_count" { type = number  default = 2 }

variable "cloudsql_tier" { type = string default = "db-f1-micro" }
variable "db_name"       { type = string default = "nyc_taxi" }
variable "db_user"       { type = string default = "taxi_user" }
variable "db_password" {
  type      = string
  sensitive = true
}

variable "composer_image_version" {
  type    = string
  default = "composer-2.9.6-airflow-2.10.2"
}
