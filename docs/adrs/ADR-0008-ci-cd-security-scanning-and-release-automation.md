# ADR-0008: Automated CI/CD Security Scanning & Helm Release Packaging

## Status
Accepted

## Context
Deploying multi-tenant enterprise software requires continuous security vulnerability scanning, automated regression testing, and reproducible cloud infrastructure deployment.

## Decision
EKOS adopts:
1. **GitHub Actions Workflow**: Automated build execution, `unittest` execution, static code analysis, and container vulnerability scanning.
2. **Helm Charts**: Standardized Kubernetes release packaging (`deployment/helm/`) supporting production HPA autoscaling, ingress TLS termination, and secret management.

## Consequences
- **Positive**: Automated quality gate enforcement on all pull requests; single-command Kubernetes deployments.
- **Negative / Tradeoff**: Requires maintaining Helm chart `values.yaml` configurations alongside Terraform scripts.
