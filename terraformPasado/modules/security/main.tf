resource "aws_security_group" "app_default" {
  name   = "${var.project_name}-${var.environment}-default-sg"
  vpc_id = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
