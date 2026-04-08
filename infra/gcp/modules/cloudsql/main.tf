variable "instance_name" { type = string }
variable "region"        { type = string }
variable "tier"          { type = string }
variable "db_name"       { type = string }
variable "db_user"       { type = string }
variable "db_password" {
  type      = string
  sensitive = true
}

resource "google_sql_database_instance" "this" {
  name             = var.instance_name
  region           = var.region
  database_version = "POSTGRES_16"

  settings {
    tier = var.tier
    backup_configuration { enabled = true }
    ip_configuration { ipv4_enabled = true }
  }

  deletion_protection = false
}

resource "google_sql_database" "db" {
  name     = var.db_name
  instance = google_sql_database_instance.this.name
}

resource "google_sql_user" "user" {
  name     = var.db_user
  instance = google_sql_database_instance.this.name
  password = var.db_password
}

output "connection_name" { value = google_sql_database_instance.this.connection_name }
