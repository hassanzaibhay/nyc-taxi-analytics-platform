variable "name"          { type = string }
variable "region"        { type = string }
variable "image_version" { type = string }
variable "labels"        { type = map(string) }

resource "google_composer_environment" "this" {
  name   = var.name
  region = var.region
  labels = var.labels

  config {
    software_config {
      image_version = var.image_version
    }
  }
}

output "airflow_uri" { value = google_composer_environment.this.config.0.airflow_uri }
