# ADR-0005: Multi-Tenant Data Isolation & Customer-Managed Encryption Keys (CMEK)

## Status
Accepted

## Context
Enterprise customers require absolute zero-trust isolation between organizational workspaces and support for Customer-Managed Encryption Keys (CMEK) to comply with data residency, HIPAA, SOC2 Type II, and GDPR regulations.

## Decision
EKOS implements:
1. **Mandatory DB-Level Filtering**: Every database query (SQL, Cypher, Qdrant payload filters) automatically appends the verified `tenant_id` extracted from JWT tokens.
2. **CMEK Envelope Encryption**: Field-level encryption for sensitive attributes (PII, financial metrics, proprietary architectural decisions) using customer-controlled master keys.

## Consequences
- **Positive**: Guarantees zero cross-tenant data leakage; ensures full regulatory compliance for regulated enterprise deployments.
- **Negative / Tradeoff**: Minor key retrieval latency for encrypted payload fields (mitigated via KMS key caching).
