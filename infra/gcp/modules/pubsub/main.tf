variable "topic_name" { type = string }
variable "labels"     { type = map(string) }

resource "google_pubsub_topic" "this" {
  name   = var.topic_name
  labels = var.labels
}

output "topic_id" { value = google_pubsub_topic.this.id }
