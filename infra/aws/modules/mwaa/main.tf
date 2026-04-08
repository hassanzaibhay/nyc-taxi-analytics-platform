variable "environment_name"  { type = string }
variable "source_bucket_arn" { type = string }
variable "dag_s3_path"       { type = string }
variable "vpc_id"            { type = string }
variable "subnet_ids"        { type = list(string) }
variable "airflow_version"   { type = string }

resource "aws_iam_role" "mwaa" {
  name = "${var.environment_name}-mwaa"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "airflow-env.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_mwaa_environment" "this" {
  name              = var.environment_name
  airflow_version   = var.airflow_version
  source_bucket_arn = var.source_bucket_arn
  dag_s3_path       = var.dag_s3_path
  execution_role_arn = aws_iam_role.mwaa.arn

  network_configuration {
    subnet_ids         = slice(var.subnet_ids, 0, 2)
    security_group_ids = []
  }

  webserver_access_mode = "PUBLIC_ONLY"
  environment_class     = "mw1.small"
}

output "webserver_url" { value = aws_mwaa_environment.this.webserver_url }
