module "network" {
  source      = "./modules/network"
  project_name = var.project_name
  environment = var.environment
  vpc_cidr    = var.vpc_cidr
}

module "database" {
  source       = "./modules/database"
  project_name = var.project_name
  environment  = var.environment
  subnet_ids   = module.network.private_subnet_ids
  vpc_id       = module.network.vpc_id
  vpc_cidr     = var.vpc_cidr
  db_username  = var.db_username
  db_password  = var.db_password
}

module "compute_api" {
  source       = "./modules/compute_api"
  project_name = var.project_name
  environment  = var.environment
  subnet_ids   = module.network.public_subnet_ids
  public_subnet_ids = module.network.public_subnet_ids
  vpc_id       = module.network.vpc_id
  source_bundle = var.source_bundle
  app_version_label = var.app_version_label
  artifact_bucket_name = var.artifact_bucket_name
  solution_stack_name = var.solution_stack_name
  application_env = merge(var.application_env, {
    POSTGRES_USER     = var.db_username
    POSTGRES_PASSWORD = var.db_password
    POSTGRES_DB       = "apidevops"
    DATABASE_URL      = "postgresql://${var.db_username}:${var.db_password}@${module.database.database_endpoint}/apidevops"
  })
}


module "security" {
  source       = "./modules/security"
  project_name = var.project_name
  environment  = var.environment
  vpc_id       = module.network.vpc_id
}
