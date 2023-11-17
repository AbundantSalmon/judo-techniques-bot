terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.26.0"
    }
  }

  cloud {
    organization = "AbundantSalmon"
    workspaces { name = "judo-techniques-bot" }
  }
}


provider "aws" {
  region = var.region
}

data "aws_ecr_repository" "judo-techniques-bot" {
  name = "judo-techniques-bot"
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

resource "aws_ecs_cluster" "jtb_ecs-cluster" {
  name = var.cluster_name
}

data "aws_iam_policy_document" "ec2_instance_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}
resource "aws_iam_role" "ec2_instance_role" {
  assume_role_policy = data.aws_iam_policy_document.ec2_instance_assume_role_policy.json
  name               = "EcsCluster${local.name}Ec2InstanceRole"
  tags               = local.tags
}

resource "aws_iam_role_policy_attachment" "ecs_instance_role" {
  role       = aws_iam_role.ec2_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}
resource "aws_iam_instance_profile" "ecs_node" {
  name = "EcsCluster${local.name}Ec2InstanceProfile"
  role = aws_iam_role.ec2_instance_role.name
  tags = local.tags
}

resource "aws_launch_template" "launch_template" {
  name = "EcsCluster${local.name}LaunchTemplate"
  iam_instance_profile {
    arn = aws_iam_instance_profile.ecs_node.arn
  }
  image_id               = "ami-02a9f359257caf3f2"
  instance_type          = "t4g.nano"
  vpc_security_group_ids = [aws_security_group.ecs_security_group.id]
  update_default_version = true
  user_data = base64encode(
    <<EOF
#!/bin/bash
echo "ECS_CLUSTER=${aws_ecs_cluster.jtb_ecs-cluster.name}" >> /etc/ecs/ecs.config
dnf update
dnf install -y ec2-instance-connect
EOF
  )

  tag_specifications {
    resource_type = "instance"
    tags          = local.tags
  }
}

data "aws_iam_policy_document" "ecs_task_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_task_role" {
  assume_role_policy = data.aws_iam_policy_document.ecs_task_role_policy.json
  name               = "EcsCluster${local.name}DefaultTaskRole"
  tags               = local.tags
}

resource "aws_iam_role_policy" "ecs_task_ssm_parameters_policy" {
  name = "EcsCluster${local.name}SSMParametersPolicy"
  role = aws_iam_role.ecs_task_role.name
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : ["ssm:GetParameters"],
        "Resource" : [
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
    ]
  })
}

resource "aws_iam_role_policy_attachment" "default_task_role" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_ecs_task_definition" "jtb_task_definition" {
  family                   = "EcsCluster${local.name}TaskDefinition"
  network_mode             = "host"
  requires_compatibilities = ["EC2"]
  execution_role_arn       = aws_iam_role.ecs_task_role.arn
  memory                   = 427
  tags                     = local.tags

  container_definitions = jsonencode([
    {
      name  = "jtb"
      image = "${data.aws_ecr_repository.judo-techniques-bot.repository_url}:latest"
      secrets : [
        {
          "name" : "DB_HOST",
          "valueFrom" : data.aws_ssm_parameter.db_host.arn
        },
        {
          "name" : "DB_NAME",
          "valueFrom" : data.aws_ssm_parameter.db_name.arn
        },
        { "name" : "DB_USER", "valueFrom" : data.aws_ssm_parameter.db_user.arn
        },
        { "name" : "DB_PORT", "valueFrom" : data.aws_ssm_parameter.db_port.arn },
        { "name" : "DB_PASS", "valueFrom" : data.aws_ssm_parameter.db_pass.arn },
        { "name" : "USER_AGENT", "valueFrom" : data.aws_ssm_parameter.user_agent.arn },
        { "name" : "CLIENT_ID", "valueFrom" : data.aws_ssm_parameter.reddit_client_id.arn },
        { "name" : "CLIENT_SECRET", "valueFrom" : data.aws_ssm_parameter.reddit_client_secret.arn },
        { "name" : "REDDIT_USERNAME", "valueFrom" : data.aws_ssm_parameter.reddit_username.arn },
        { "name" : "REDDIT_PASSWORD", "valueFrom" : data.aws_ssm_parameter.reddit_password.arn },
        { "name" : "SUBREDDITS", "valueFrom" : data.aws_ssm_parameter.subreddits.arn },
        { "name" : "SENTRY_DSN", "valueFrom" : data.aws_ssm_parameter.sentry_dsn.arn },
      ]
    },
  ])
}

resource "aws_ecs_service" "jtb_service" {
  name            = "EcsCluster${local.name}Service"
  cluster         = aws_ecs_cluster.jtb_ecs-cluster.id
  task_definition = aws_ecs_task_definition.jtb_task_definition.arn
  launch_type     = "EC2"
  desired_count   = 1
  tags            = local.tags

  depends_on = [aws_security_group.ecs_security_group]
}

resource "aws_autoscaling_group" "autoscaling_group" {
  launch_template {
    id      = aws_launch_template.launch_template.id
    version = aws_launch_template.launch_template.latest_version
  }
  availability_zones        = ["us-east-2a"]
  min_size                  = 1
  max_size                  = 1
  desired_capacity          = 1
  health_check_type         = "EC2"
  health_check_grace_period = 300
  termination_policies      = ["OldestInstance"]

  instance_maintenance_policy {
    min_healthy_percentage = 100
    max_healthy_percentage = 200
  }

  instance_refresh {
    strategy = "Rolling"
    preferences {
      min_healthy_percentage = 100
    }
  }

  tag {
    key                 = "Name"
    value               = var.cluster_name
    propagate_at_launch = true
  }
  tag {
    key                 = "Module"
    value               = "ECS Cluster"
    propagate_at_launch = true
  }
  tag {
    key                 = "AmazonECSManaged"
    value               = true
    propagate_at_launch = true
  }
}

resource "aws_ecs_capacity_provider" "capacity_provider" {
  name = "Cluster${local.name}CapacityProvider"
  tags = local.tags

  auto_scaling_group_provider {
    auto_scaling_group_arn = aws_autoscaling_group.autoscaling_group.arn
  }
}
resource "aws_ecs_cluster_capacity_providers" "capacity_providers" {
  cluster_name       = aws_ecs_cluster.jtb_ecs-cluster.name
  capacity_providers = [aws_ecs_capacity_provider.capacity_provider.name]
}

resource "aws_security_group" "ecs_security_group" {
  name = "EcsCluster${local.name}SecurityGroup"
  tags = local.tags


  # Allow the container to talk to the outside world
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
