resource "aws_db_subnet_group" "this" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = var.subnet_ids
}

resource "aws_security_group" "db" {
  name   = "${var.project_name}-${var.environment}-db-sg"
  vpc_id = var.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "this" {
  identifier            = "${var.project_name}-${var.environment}-db"
  engine                = "postgres"
  instance_class        = "db.t3.micro"
  allocated_storage     = 20
  db_name               = "apidevops"
  username              = var.db_username
  password              = var.db_password
  skip_final_snapshot   = true
  db_subnet_group_name  = aws_db_subnet_group.this.name
  vpc_security_group_ids = [aws_security_group.db.id]
}
