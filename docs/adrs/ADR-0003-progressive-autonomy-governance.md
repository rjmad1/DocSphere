# ADR-0003: Progressive Autonomy for Living Documentation Governance

## Status
Accepted

## Context
Automated downstream document updates without human intervention introduce compliance, legal, and operational risks in enterprise transformation projects. Conversely, manual updates across dozens of artifacts lead to stale documentation.

## Decision
EKOS implements **Progressive Autonomy**:
1. AI agents continuously monitor upstream changes, run change impact traversals over Neo4j, and generate side-by-side visual diffs.
2. Changes are *never* automatically published or propagated to downstream baseline specifications without passing through a policy-defined human approval gate (`Steward`, `Lead Architect`, `Security Officer`).

## Consequences
- **Positive**: Balances high-speed automated impact analysis with strict enterprise governance and risk mitigation.
- **Positive**: Complete immutable audit logging of every approval, rejection, and recommendation.
- **Negative / Tradeoff**: Dependent on human approver SLA response times (mitigated via automated SLA reminder escalation).
