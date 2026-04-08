variable "bucket_name" { type = string }
variable "location"    { type = string }
variable "labels"      { type = map(string) }

resource "google_storage_bucket" "this" {
  name                        = var.bucket_name
  location                    = var.location
  uniform_bucket_level_access = true
  force_destroy               = false
  labels                      = var.labels

  versioning { enabled = true }
}

output "bucket_name" { value = google_storage_bucket.this.name }
