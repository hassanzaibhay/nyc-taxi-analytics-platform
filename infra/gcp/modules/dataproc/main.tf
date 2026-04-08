variable "cluster_name" { type = string }
variable "region"       { type = string }
variable "master_type"  { type = string }
variable "worker_type"  { type = string }
variable "worker_count" { type = number }
variable "labels"       { type = map(string) }

resource "google_dataproc_cluster" "this" {
  name   = var.cluster_name
  region = var.region
  labels = var.labels

  cluster_config {
    master_config {
      num_instances = 1
      machine_type  = var.master_type
    }
    worker_config {
      num_instances = var.worker_count
      machine_type  = var.worker_type
    }
    software_config {
      image_version = "2.2-debian12"
      optional_components = ["JUPYTER"]
    }
  }
}

output "cluster_name" { value = google_dataproc_cluster.this.name }
