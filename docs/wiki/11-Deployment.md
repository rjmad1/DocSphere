# 11. Deployment & Infrastructure

## Local Development (Docker Compose)
```bash
docker-compose up -d
```

## Cloud Infrastructure (Terraform AWS EKS)
Defined in `deployment/terraform/infrastructure.tf` establishing VPC subnets, AWS EKS clusters, and managed node groups.

## Kubernetes Helm Release
Defined in `deployment/helm/Chart.yaml` and `values.yaml` supporting HPA autoscaling (3 to 10 replicas based on 75% CPU target).
