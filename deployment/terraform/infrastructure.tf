# EKOS Terraform Multi-Cloud Infrastructure Base

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

# EKS Cluster Provisioning for EKOS Platform
module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  version         = "~> 19.0"
  cluster_name    = "ekos-production-cluster"
  cluster_version = "1.28"

  vpc_id     = var.vpc_id
  subnet_ids = var.subnet_ids

  eks_managed_node_groups = {
    knowledge_engine_nodes = {
      min_size     = 3
      max_size     = 10
      desired_size = 3

      instance_types = ["m6i.xlarge"]
      capacity_type  = "ON_DEMAND"
    }
  }
}

output "eks_cluster_endpoint" {
  value = module.eks.cluster_endpoint
}
