# 15. Operational Observability & Health

## Telemetry Metrics (`backend/shared/observability/metrics.py`)
- Prometheus endpoint exposed at `/metrics` measuring HTTP request rates, latencies, and active database connection gauges.

## OpenTelemetry Tracing (`backend/shared/observability/tracing.py`)
- Injects `trace_id` headers into request contexts and spans for distributed tracing.

## Health Diagnostics (`backend/shared/observability/health.py`)
- Deep diagnostic endpoint (`GET /health/deep`) probing PostgreSQL, Neo4j, Qdrant, and Redis connection health.
