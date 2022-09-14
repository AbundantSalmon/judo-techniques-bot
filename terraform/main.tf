terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }

  backend "s3" {
    bucket = "abundant-salmon-terraform-state"
    key    = "judo-techniques-bot/terraform.tfstate"
    region = "us-east-2"
  }
}

provider "aws" {
  region = var.region
}

data "aws_ecr_repository" "judo-techniques-bot" {
  name = "judo-techniques-bot"
}

data "aws_kms_alias" "judo-techniques-bot" {
  name = "alias/aws/ssm" # change from default key when needed
}

data "aws_ssm_parameter" "db_host" {
  name            = "/judo-techniques-bot/db_host"
  with_decryption = false
}

data "aws_ssm_parameter" "db_name" {
  name            = "/judo-techniques-bot/db_name"
  with_decryption = false
}

data "aws_ssm_parameter" "db_pass" {
  name            = "/judo-techniques-bot/db_pass"
  with_decryption = false
}

data "aws_ssm_parameter" "db_port" {
  name            = "/judo-techniques-bot/db_port"
  with_decryption = false
}

data "aws_ssm_parameter" "db_user" {
  name            = "/judo-techniques-bot/db_user"
  with_decryption = false
}

data "aws_ssm_parameter" "reddit_client_id" {
  name            = "/judo-techniques-bot/reddit_client_id"
  with_decryption = false
}

data "aws_ssm_parameter" "reddit_client_secret" {
  name            = "/judo-techniques-bot/reddit_client_secret"
  with_decryption = false
}

data "aws_ssm_parameter" "reddit_password" {
  name            = "/judo-techniques-bot/reddit_password"
  with_decryption = false
}

data "aws_ssm_parameter" "reddit_username" {
  name            = "/judo-techniques-bot/reddit_username"
  with_decryption = false
}

data "aws_ssm_parameter" "sentry_dsn" {
  name            = "/judo-techniques-bot/sentry_dsn"
  with_decryption = false
}

data "aws_ssm_parameter" "subreddits" {
  name            = "/judo-techniques-bot/subreddits"
  with_decryption = false
}

data "aws_ssm_parameter" "user_agent" {
  name            = "/judo-techniques-bot/user_agent"
  with_decryption = false
}

resource "aws_security_group" "instance" {
  name = "judo-techniques-bot-instance"

  # ssh access TODO: remove on production
  # ingress {
  #   from_port   = 22
  #   to_port     = 22
  #   protocol    = "tcp"
  #   cidr_blocks = ["0.0.0.0/0"]
  # }

  # Allow the container to talk to the outside world
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_iam_role" "ec2-judo-techniques-bot" {
  name               = "ec2-judo-techniques-bot"
  description        = "Role to permit ec2 to get judo-techniques-bot parameters from Parameter Store and pull the docker container from ECR"
  assume_role_policy = <<EOF
                      {
                        "Version": "2012-10-17",
                        "Statement": [
                          {
                            "Action": "sts:AssumeRole",
                            "Principal": {
                              "Service": "ec2.amazonaws.com"
                            },
                            "Effect": "Allow",
                            "Sid": ""
                          }
                        ]
                      }
                      EOF
}

resource "aws_iam_role_policy" "ec2-judo-techniques-bot" {
  name   = "ec2-judo-techniques-bot"
  role   = aws_iam_role.ec2-judo-techniques-bot.name
  policy = <<EOF
{
"Version": "2012-10-17",
"Statement": [
  {
    "Effect": "Allow",
    "Action": ["ssm:GetParameters"],
    "Resource": [
      "${data.aws_ssm_parameter.db_host.arn}",
      "${data.aws_ssm_parameter.db_name.arn}",
      "${data.aws_ssm_parameter.db_pass.arn}",
      "${data.aws_ssm_parameter.db_port.arn}",
      "${data.aws_ssm_parameter.db_user.arn}",
      "${data.aws_ssm_parameter.reddit_client_id.arn}",
      "${data.aws_ssm_parameter.reddit_client_secret.arn}",
      "${data.aws_ssm_parameter.reddit_password.arn}",
      "${data.aws_ssm_parameter.reddit_username.arn}",
      "${data.aws_ssm_parameter.sentry_dsn.arn}",
      "${data.aws_ssm_parameter.subreddits.arn}",
      "${data.aws_ssm_parameter.user_agent.arn}"
    ]
  },
  {
    "Effect": "Allow",
    "Action": ["kms:Decrypt"],
    "Resource": ["${data.aws_kms_alias.judo-techniques-bot.arn}"]
  },
  {
    "Effect": "Allow",
    "Action": [
      "ecr:Describe*",
      "ecr:Get*",
      "ecr:List*",
      "ecr:BatchGetImage",
      "ecr:BatchCheckLayerAvailability"
    ],
    "Resource": ["${data.aws_ecr_repository.judo-techniques-bot.arn}"]
  },
  {
    "Effect": "Allow",
    "Action": [
      "ecr:GetAuthorizationToken"
    ],
    "Resource": "*"
  }
]
}
EOF
}

resource "aws_iam_instance_profile" "ec2-judo-techniques-bot" {
  name = "ec2-judo-techniques-bot"
  role = aws_iam_role.ec2-judo-techniques-bot.name
}

resource "aws_instance" "judo-techniques-bot" {
  ami                    = "ami-0568773882d492fc8"
  instance_type          = "t2.micro"
  vpc_security_group_ids = [aws_security_group.instance.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2-judo-techniques-bot.name

  user_data = <<-EOF
    #!/bin/bash
    mkdir -p ${var.env-location}
    touch ${var.env-file-location}
    aws configure set default.region ${var.region}
    echo "DB_HOST=$(aws ssm get-parameters --names ${data.aws_ssm_parameter.db_host.name} --query 'Parameters[0].Value' --output text)" >> ${var.env-file-location}
    echo "DB_NAME=$(aws ssm get-parameters --names ${data.aws_ssm_parameter.db_name.name} --query 'Parameters[0].Value' --output text)" >> ${var.env-file-location}
    echo "DB_USER=$(aws ssm get-parameters --names ${data.aws_ssm_parameter.db_user.name} --with-decryption --query 'Parameters[0].Value' --output text)" >> ${var.env-file-location}
    echo "DB_PORT=$(aws ssm get-parameters --names ${data.aws_ssm_parameter.db_port.name} --with-decryption --query 'Parameters[0].Value' --output text)" >> ${var.env-file-location}
    echo "DB_PASS=$(aws ssm get-parameters --names ${data.aws_ssm_parameter.db_pass.name} --with-decryption --query 'Parameters[0].Value' --output text)" >> ${var.env-file-location}
    echo "USER_AGENT=\"$(aws ssm get-parameters --names ${data.aws_ssm_parameter.user_agent.name} --query 'Parameters[0].Value' --output text)\"" >> ${var.env-file-location}
    echo "CLIENT_ID=$(aws ssm get-parameters --names ${data.aws_ssm_parameter.reddit_client_id.name} --with-decryption --query 'Parameters[0].Value' --output text)" >> ${var.env-file-location}
    echo "CLIENT_SECRET=$(aws ssm get-parameters --names ${data.aws_ssm_parameter.reddit_client_secret.name} --with-decryption --query 'Parameters[0].Value' --output text)" >> ${var.env-file-location}
    echo "REDDIT_USERNAME=$(aws ssm get-parameters --names ${data.aws_ssm_parameter.reddit_username.name} --query 'Parameters[0].Value' --output text)" >> ${var.env-file-location}
    echo "REDDIT_PASSWORD=$(aws ssm get-parameters --names ${data.aws_ssm_parameter.reddit_password.name} --with-decryption --query 'Parameters[0].Value' --output text)" >> ${var.env-file-location}
    echo "SUBREDDITS=$(aws ssm get-parameters --names ${data.aws_ssm_parameter.subreddits.name} --query 'Parameters[0].Value' --output text)" >> ${var.env-file-location}
    echo "SENTRY_DSN=$(aws ssm get-parameters --names ${data.aws_ssm_parameter.sentry_dsn.name} --query 'Parameters[0].Value' --output text)" >> ${var.env-file-location}
    echo "DATABASE_URI=postgresql+psycopg2://$(aws ssm get-parameters --names ${data.aws_ssm_parameter.db_user.name} --with-decryption --query 'Parameters[0].Value' --output text):$(aws ssm get-parameters --names ${data.aws_ssm_parameter.db_pass.name} --with-decryption --query 'Parameters[0].Value' --output text)@$(aws ssm get-parameters --names ${data.aws_ssm_parameter.db_host.name} --query 'Parameters[0].Value' --output text):$(aws ssm get-parameters --names ${data.aws_ssm_parameter.db_port.name} --with-decryption --query 'Parameters[0].Value' --output text)/$(aws ssm get-parameters --names ${data.aws_ssm_parameter.db_name.name} --query 'Parameters[0].Value' --output text)" >> ${var.env-file-location}

    amazon-linux-extras install docker
    service docker start
    chkconfig docker on

    aws ecr get-login-password --region ${var.region} | docker login --username AWS --password-stdin ${data.aws_ecr_repository.judo-techniques-bot.repository_url}
    docker pull ${data.aws_ecr_repository.judo-techniques-bot.repository_url}:latest
    docker run --restart=always -dit --env-file ${var.env-file-location} ${data.aws_ecr_repository.judo-techniques-bot.repository_url}:latest
    EOF

  tags = {
    Name = "judo-techniques-bot"
  }
}
