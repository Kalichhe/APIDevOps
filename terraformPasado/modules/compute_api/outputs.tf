output "api_endpoint" {
  value = aws_elastic_beanstalk_environment.this.cname
}

output "app_security_group_id" {
  value = aws_security_group.app.id
}
