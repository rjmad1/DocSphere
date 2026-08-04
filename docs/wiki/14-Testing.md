# 14. Testing Architecture & Verification

## Test Execution
Run the complete backend unit test suite:
```bash
python -m unittest discover -s backend/tests
```

## Test Modules Matrix (`backend/tests/`)
- `test_production_stack.py`: Ingestion, AST parsing, and LLM gateway tests.
- `test_enterprise_security.py`: Zero-trust RBAC and CMEK encryption tests.
- `test_observability_and_errors.py`: Prometheus metrics, OpenTelemetry, and RFC 7807 error middleware tests.
- `test_fastapi_endpoints.py`: FastAPI endpoint contract tests.
- `test_connectors.py`: Jira & Confluence connector tests.
- `test_reasoning_and_validation.py`: Graph reasoning engine & input sanitizer tests.
- `test_audit_logger.py`: Cryptographic SHA-256 audit logger tests.
- `test_roadmap_features.py`: WORM backups, SLA webhooks, SAP ALM, ServiceNow, and multi-region cluster tests.
- `test_opportunity_backlog.py`: WebSocket sync, GitHub listener, and federated graph mesh tests.
