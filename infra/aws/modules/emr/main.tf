variable "cluster_name"  { type = string }
variable "release_label" { type = string }
variable "master_type"   { type = string }
variable "core_type"     { type = string }
variable "core_count"    { type = number }
variable "log_uri"       { type = string }
variable "subnet_id"     { type = string }

resource "aws_emr_cluster" "this" {
  name          = var.cluster_name
  release_label = var.release_label
  applications  = ["Hadoop", "Spark", "Hive"]
  log_uri       = var.log_uri
  service_role  = "EMR_DefaultRole"

  ec2_attributes {
    subnet_id        = var.subnet_id
    instance_profile = "EMR_EC2_DefaultRole"
  }

  master_instance_group {
    instance_type = var.master_type
  }

  core_instance_group {
    instance_type  = var.core_type
    instance_count = var.core_count
  }

  visible_to_all_users = true
}

output "cluster_id" { value = aws_emr_cluster.this.id }
