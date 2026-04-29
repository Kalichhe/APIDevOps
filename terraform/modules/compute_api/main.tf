data "aws_caller_identity" "current" {}

data "aws_elastic_beanstalk_solution_stack" "python" {
  most_recent = true
  name_regex  = "^64bit Amazon Linux.*running Python 3\\.[0-9]+$"
}

locals {
  app_name        = "${var.project_name}-${var.environment}-api"
  artifact_bucket = var.artifact_bucket_name != "" ? var.artifact_bucket_name : aws_s3_bucket.artifacts[0].id
}

resource "aws_s3_bucket" "artifacts" {
  count = var.artifact_bucket_name == "" ? 1 : 0

  bucket = "${var.project_name}-${var.environment}-eb-artifacts-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_object" "app_bundle" {
  bucket = local.artifact_bucket
  key    = "${var.app_version_label}.zip"
  source = var.source_bundle
  etag   = filemd5(var.source_bundle)
}

resource "aws_iam_role" "ec2" {
  name = "${var.project_name}-${var.environment}-eb-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ec2_web_tier" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier"
}

resource "aws_iam_role_policy_attachment" "ec2_worker_tier" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWorkerTier"
}

resource "aws_iam_role_policy_attachment" "ec2_multicontainer" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkMulticontainerDocker"
}

resource "aws_iam_instance_profile" "ec2" {
  name = "${var.project_name}-${var.environment}-eb-ec2-instance-profile"
  role = aws_iam_role.ec2.name
}

resource "aws_iam_role" "service" {
  name = "${var.project_name}-${var.environment}-eb-service-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "elasticbeanstalk.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "service_enhanced_health" {
  role       = aws_iam_role.service.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSElasticBeanstalkEnhancedHealth"
}

resource "aws_iam_role_policy_attachment" "service_managed_updates" {
  role       = aws_iam_role.service.name
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkManagedUpdatesCustomerRolePolicy"
}

resource "aws_security_group" "app" {
  name   = "${var.project_name}-${var.environment}-eb-app-sg"
  vpc_id = var.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_elastic_beanstalk_application" "this" {
  name        = local.app_name
  description = "Elastic Beanstalk application for ${var.project_name} ${var.environment}"
}

resource "aws_elastic_beanstalk_application_version" "this" {
  name        = var.app_version_label
  application = aws_elastic_beanstalk_application.this.name
  bucket      = aws_s3_object.app_bundle.bucket
  key         = aws_s3_object.app_bundle.key
}

resource "aws_elastic_beanstalk_environment" "this" {
  name                = "${var.project_name}-${var.environment}-env"
  application         = aws_elastic_beanstalk_application.this.name
  solution_stack_name = var.solution_stack_name != "" ? var.solution_stack_name : data.aws_elastic_beanstalk_solution_stack.python.name
  version_label       = aws_elastic_beanstalk_application_version.this.name

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "IamInstanceProfile"
    value     = aws_iam_instance_profile.ec2.name
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment"
    name      = "ServiceRole"
    value     = aws_iam_role.service.name
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment"
    name      = "EnvironmentType"
    value     = "LoadBalanced"
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment"
    name      = "LoadBalancerType"
    value     = "application"
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "VPCId"
    value     = var.vpc_id
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "Subnets"
    value     = join(",", var.subnet_ids)
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "ELBSubnets"
    value     = join(",", var.public_subnet_ids)
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "AssociatePublicIpAddress"
    value     = "true"
  }

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "SecurityGroups"
    value     = aws_security_group.app.id
  }

  dynamic "setting" {
    for_each = var.application_env
    content {
      namespace = "aws:elasticbeanstalk:application:environment"
      name      = setting.key
      value     = setting.value
    }
  }
}
