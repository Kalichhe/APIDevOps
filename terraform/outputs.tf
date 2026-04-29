output "vpc_id" {
  value = module.network.vpc_id
}

output "api_endpoint" {
  value = module.compute_api.api_endpoint
}

output "database_endpoint" {
  value = module.database.database_endpoint
}
