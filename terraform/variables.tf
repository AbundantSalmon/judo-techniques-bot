variable "region" {
  default     = "us-east-2"
  description = "AWS region to deploy to"
}

variable "cluster_name" {
  default     = "jtb_ecs-cluster"
  description = "Name of the ECS cluster"
}

locals {

  name = replace(var.cluster_name, " ", "_")
  tags = {
    Name   = var.cluster_name,
    Module = "ECS Cluster"
  }
}
