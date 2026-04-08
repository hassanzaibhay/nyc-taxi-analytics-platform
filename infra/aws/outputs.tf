output "s3_bucket_name" { value = module.s3.bucket_name }
output "rds_endpoint"   { value = module.rds.endpoint }
output "emr_cluster_id" { value = module.emr.cluster_id }
output "msk_bootstrap_brokers" { value = module.msk.bootstrap_brokers }
output "mwaa_webserver_url" { value = module.mwaa.webserver_url }
