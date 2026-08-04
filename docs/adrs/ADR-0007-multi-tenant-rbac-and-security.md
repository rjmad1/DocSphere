# ADR-0007: Granular Multi-Tenant RBAC Matrix & Token Context Isolation

## Status
Accepted

## Context
Enterprise operations require role-based access control (RBAC) with discrete permission boundaries across business personas (Business Analyst, Enterprise Architect, System Admin, Security Officer) to prevent unauthorized entity modifications or policy bypasses.

## Decision
EKOS implements a strictly enforced role hierarchy:
- `Author`: Drafts documents, submits requirements for review.
- `Steward`: Validates citations, approves Level 1 / Level 2 changes.
- `Approver`: Validates major / breaking baseline changes and policy overrides.
- `Admin`: Configures tenant parameters, identity providers, and CMEK master keys.

All API requests pass through context-aware security middleware enforcing mandatory tenant context propagation and role permission checks.

## Consequences
- **Positive**: Zero unauthorized state mutations; full SOC2 Type II compliance.
- **Negative / Tradeoff**: Requires token authorization header on all non-public endpoints.
