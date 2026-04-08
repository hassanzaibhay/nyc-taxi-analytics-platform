variable "cluster_name"          { type = string }
variable "kafka_version"         { type = string }
variable "broker_instance_type"  { type = string }
variable "broker_count"          { type = number }
variable "subnet_ids"            { type = list(string) }
variable "security_group_ids"    { type = list(string) }

resource "aws_msk_cluster" "this" {
  cluster_name           = var.cluster_name
  kafka_version          = var.kafka_version
  number_of_broker_nodes = var.broker_count

  broker_node_group_info {
    instance_type   = var.broker_instance_type
    client_subnets  = var.subnet_ids
    security_groups = var.security_group_ids
    storage_info {
      ebs_storage_info { volume_size = 100 }
    }
  }

  encryption_info {
    encryption_in_transit {
      client_broker = "TLS"
      in_cluster    = true
    }
  }
}

output "bootstrap_brokers" { value = aws_msk_cluster.this.bootstrap_brokers_tls }
