variable "aws_region" {
  description = "Región de AWS"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "Tipo de instancia EC2 (mínimo t3.medium para minikube)"
  type        = string
  default     = "t2.micro"
}

variable "public_key_path" {
  description = "Ruta a tu clave pública SSH (ej: ~/.ssh/id_rsa.pub)"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "docker_image_stable" {
  description = "Imagen Docker de la versión stable (ej: tuusuario/api-devops:stable)"
  type        = string
}

variable "docker_image_canary" {
  description = "Imagen Docker de la versión canary (ej: tuusuario/api-devops:canary)"
  type        = string
}
