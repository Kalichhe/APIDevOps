output "instance_public_ip" {
  description = "IP pública de la EC2 (usa esta en Postman)"
  value       = aws_eip.api_devops.public_ip
}

output "ssh_command" {
  description = "Comando para conectarte por SSH"
  value       = "ssh -i ~/.ssh/id_rsa ubuntu@${aws_eip.api_devops.public_ip}"
}

output "health_url" {
  description = "URL del healthcheck para Postman"
  value       = "http://${aws_eip.api_devops.public_ip}/health"
}

output "metrics_url" {
  description = "URL de métricas Prometheus"
  value       = "http://${aws_eip.api_devops.public_ip}/metrics"
}
