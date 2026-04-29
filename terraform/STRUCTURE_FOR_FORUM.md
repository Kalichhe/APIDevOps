# Estructura Terraform Modular - APIDevOps

## Arbol de carpetas

terraform/
├── main.tf
├── variables.tf
├── outputs.tf
├── provider.tf
├── modules/
│ ├── network/
│ │ ├── main.tf
│ │ ├── variables.tf
│ │ └── outputs.tf
│ ├── compute_api/
│ │ ├── main.tf
│ │ ├── variables.tf
│ │ └── outputs.tf
│ ├── database/
│ │ ├── main.tf
│ │ ├── variables.tf
│ │ └── outputs.tf
│ ├── monitoring/
│ │ ├── main.tf
│ │ ├── variables.tf
│ │ └── outputs.tf
│ └── security/
│ ├── main.tf
│ ├── variables.tf
│ └── outputs.tf
└── environments/
├── dev/
│ ├── main.tf
│ └── terraform.tfvars
├── staging/
│ ├── main.tf
│ └── terraform.tfvars
└── prod/
├── main.tf
└── terraform.tfvars

## Diagrama Mermaid (para exportar o capturar como imagen)

```mermaid
flowchart TB
  A[terraform-apidevops] --> A1[main.tf]
  A --> A2[provider.tf]
  A --> A3[variables.tf]
  A --> A4[outputs.tf]
  A --> B[modules]
  A --> C[environments]

  B --> B1[network]
  B1 --> B11[main.tf]
  B1 --> B12[variables.tf]
  B1 --> B13[outputs.tf]

  B --> B2[compute_api]
  B2 --> B21[main.tf]
  B2 --> B22[variables.tf]
  B2 --> B23[outputs.tf]

  B --> B3[database]
  B3 --> B31[main.tf]
  B3 --> B32[variables.tf]
  B3 --> B33[outputs.tf]

  %% monitoring removed

  B --> B5[security]
  B5 --> B51[main.tf]
  B5 --> B52[variables.tf]
  B5 --> B53[outputs.tf]

  C --> C1[dev]
  C1 --> C11[main.tf]
  C1 --> C12[terraform.tfvars]

  C --> C2[staging]
  C2 --> C21[main.tf]
  C2 --> C22[terraform.tfvars]

  C --> C3[prod]
  C3 --> C31[main.tf]
  C3 --> C32[terraform.tfvars]
```
