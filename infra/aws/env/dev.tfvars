environment        = "dev"
aws_region         = "us-east-1"
rds_instance_class = "db.t3.micro"
emr_master_type    = "m5.xlarge"
emr_core_type      = "m5.xlarge"
emr_core_count     = 2
msk_broker_instance_type = "kafka.t3.small"
msk_broker_count   = 2
# vpc_id, subnet_ids, emr_subnet_id, db_password must be supplied via secret store
