# Terraform + Elastic Beanstalk (APIDevOps)

Esta carpeta contiene infraestructura modular en AWS para desplegar la API en Elastic Beanstalk.

## Componentes

- network: VPC, subredes privadas/publicas e internet gateway.
- compute_api: Elastic Beanstalk app/environment, IAM, S3 artifact y security group de app.
- database: RDS PostgreSQL y seguridad para permitir trafico desde la app.
 - monitoring: (removed)
- security: security group base adicional.

## Flujo recomendado

1. Crear el artefacto de aplicacion en la raiz del proyecto con nombre app.zip.
2. Entrar al ambiente deseado en environments/dev, environments/staging o environments/prod.
3. Ejecutar terraform init.
4. Ejecutar terraform plan.
5. Ejecutar terraform apply.

## Ejemplo (dev)

Desde la raiz del repo:

PowerShell (recomendado para EB):
python scripts/build_eb_bundle.py

Terraform:
terraform -chdir=terraform/environments/dev init
terraform -chdir=terraform/environments/dev plan
terraform -chdir=terraform/environments/dev apply

## Solucion a error de source bundle

Si aparece este error en Elastic Beanstalk:

- Instance deployment: Your source bundle has issues
- unzip ... appears to use backslashes as path separators

No uses Compress-Archive para este bundle. Usa siempre:
python scripts/build_eb_bundle.py

## Variables por ambiente

Cada ambiente define:

- app_version_label (dev-v1, staging-v1, prod-v1)
- source_bundle (../../../app.zip)
- application_env (APP_ENV)

## Nota

Para nuevas versiones, actualiza app_version_label en el ambiente correspondiente para publicar un nuevo Application Version en Elastic Beanstalk.
