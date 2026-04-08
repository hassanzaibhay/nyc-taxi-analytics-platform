output "gcs_bucket"          { value = module.gcs.bucket_name }
output "dataproc_cluster"    { value = module.dataproc.cluster_name }
output "pubsub_topic"        { value = module.pubsub.topic_id }
output "cloudsql_connection" { value = module.cloudsql.connection_name }
output "composer_uri"        { value = module.composer.airflow_uri }
