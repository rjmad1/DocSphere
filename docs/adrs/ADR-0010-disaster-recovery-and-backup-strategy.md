# ADR-0010: Disaster Recovery & Automated Snapshot Backup Strategy

## Status
Accepted

## Context
High-availability enterprise operations require strict Recovery Point Objectives (RPO < 15 minutes) and Recovery Time Objectives (RTO < 1 hour) across hybrid and cloud deployments.

## Decision
EKOS implements:
1. **Automated Graph & Vector Snapshots**: Scheduled hourly snapshots for Neo4j knowledge graph and Qdrant vector collections.
2. **Point-in-Time Relational Recovery**: PostgreSQL continuous WAL archiving enabling point-in-time state restoration.
3. **Multi-Region Replication**: Asynchronous read-replica replication across cloud availability zones.

## Consequences
- **Positive**: Guarantees zero data loss in regional failover scenarios; satisfies enterprise SLA requirements.
- **Negative / Tradeoff**: Increases cloud storage backup costs (mitigated via tiered backup lifecycle policies).
