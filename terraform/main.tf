terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.3.0"
}

provider "aws" {
  region = var.aws_region
}

# ── Data: AMI Ubuntu 22.04 más reciente ──
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# ── VPC default ──
data "aws_vpc" "default" {
  default = true
}

# ── Security Group ──
resource "aws_security_group" "api_devops" {
  name        = "api-devops-sg"
  description = "Security group para API DevOps con Canary"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "API stable y canary"
    from_port   = 5000
    to_port     = 5001
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "api-devops-sg"
    Project = "APIDevOps"
  }
}

# ── Key Pair ──
resource "aws_key_pair" "deployer" {
  key_name   = "api-devops-key"
  public_key = file(pathexpand(var.public_key_path))
}

# ── EC2 Instance ──
resource "aws_instance" "api_devops" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = aws_key_pair.deployer.key_name
  vpc_security_group_ids = [aws_security_group.api_devops.id]

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  user_data = templatefile("${path.module}/userdata.sh", {
    docker_image_stable = var.docker_image_stable
    docker_image_canary = var.docker_image_canary
  })

  tags = {
    Name    = "api-devops-server"
    Project = "APIDevOps"
  }
}

# ── Elastic IP (IP pública fija) ──
resource "aws_eip" "api_devops" {
  instance = aws_instance.api_devops.id
  domain   = "vpc"

  tags = {
    Name    = "api-devops-eip"
    Project = "APIDevOps"
  }
}
