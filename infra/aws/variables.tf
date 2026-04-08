variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "aws_profile" {
  type    = string
  default = "default"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "project_name" {
  type    = string
  default = "nyc-taxi"
}

variable "vpc_id" { type = string }
variable "subnet_ids" { type = list(string) }

# RDS
variable "rds_instance_class" {
  type    = string
  default = "db.t3.micro"
}
variable "db_name" {
  type    = string
  default = "nyc_taxi"
}
variable "db_username" {
  type    = string
  default = "taxi_user"
}
variable "db_password" {
  type      = string
  sensitive = true
}

# EMR
variable "emr_release_label" {
  type    = string
  default = "emr-7.3.0"
}
variable "emr_master_type" {
  type    = string
  default = "m5.xlarge"
}
variable "emr_core_type" {
  type    = string
  default = "m5.xlarge"
}
variable "emr_core_count" {
  type    = number
  default = 2
}
variable "emr_subnet_id" {
  type = string
}

# MSK
variable "kafka_version" {
  type    = string
  default = "3.7.x"
}
variable "msk_broker_instance_type" {
  type    = string
  default = "kafka.t3.small"
}
variable "msk_broker_count" {
  type    = number
  default = 2
}
variable "msk_security_group_ids" {
  type    = list(string)
  default = []
}

# MWAA
variable "airflow_version" {
  type    = string
  default = "2.10.1"
}
