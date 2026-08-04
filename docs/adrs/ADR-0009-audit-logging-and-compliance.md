# ADR-0009: Immutable Cryptographic Audit Logging for Compliance

## Status
Accepted

## Context
Regulated enterprises (financial services, healthcare, SAP transformations) require tamper-proof audit trails for all document modifications, state transitions, security events, and approval decisions to pass SOC2 Type II, ISO 27001, and HIPAA audits.

## Decision
EKOS implements a **Cryptographic Audit Logger**:
1. Every state mutation records actor ID, action type, timestamp, delta JSON, and evidence citations.
2. Each audit log entry generates a SHA-256 cryptographic checksum chained to the previous log entry's hash, forming an immutable audit chain.

## Consequences
- **Positive**: Guarantees tamper-proof audit verification; simplifies SOC2 compliance audits.
- **Negative / Tradeoff**: Requires database storage for audit log records (mitigated via partitioned storage table).
