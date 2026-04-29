variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "source_bundle" {
  description = "Path to application ZIP bundle"
  type        = string
}

variable "app_version_label" {
  description = "Application version label for Elastic Beanstalk"
  type        = string
}

variable "artifact_bucket_name" {
  description = "Optional existing S3 bucket name for app artifacts"
  type        = string
  default     = ""
}

variable "solution_stack_name" {
  description = "Elastic Beanstalk solution stack"
  type        = string
  default     = ""
}

variable "application_env" {
  description = "Environment variables injected into Beanstalk app"
  type        = map(string)
  default     = {}
}
