variable "project_name" {
  description = "Project name prefix"
  type        = string
  default     = "apidevops"
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
}

variable "db_username" {
  description = "Database master username"
  type        = string
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

variable "source_bundle" {
  description = "Path to the application zip bundle uploaded to Beanstalk"
  type        = string
  default     = "../app.zip"
}

variable "app_version_label" {
  description = "Application version label for Elastic Beanstalk"
  type        = string
  default     = "v1"
}

variable "artifact_bucket_name" {
  description = "Optional existing artifact S3 bucket for app bundles"
  type        = string
  default     = ""
}

variable "solution_stack_name" {
  description = "Elastic Beanstalk solution stack"
  type        = string
  default     = ""
}

variable "application_env" {
  description = "Environment variables for the application"
  type        = map(string)
  default     = {}
}
