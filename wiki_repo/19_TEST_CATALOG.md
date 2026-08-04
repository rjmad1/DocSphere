# Test Catalog

This document catalogues all unit, integration, and E2E browser automated test suites implemented in the DocSphere repository.

---

## 1. Pytest Backend Suites (`/backend/tests`)
A total of 114 test cases verifying all service functions with **97% code coverage**.

### Test Target Files:
* **`test_agent_framework.py`**: Asserts custom agent executor reasoning, tool dispatching, and execution results.
* **`test_audit_logger.py`**: Verifies JSON formatting and file writes in the security audit logging service.
* **`test_connectors.py`**: Verifies SAP ALM, Jira, Confluence, Reddit, and ServiceNow connector sync and health check outputs.
* **`test_coverage_completion.py`**: Main integration suite asserting multi-region cluster routing, WORM backups, API gateway routers, widgets, and key managers.
* **`test_coverage_gap_filler.py`**: Pushes coverage boundaries by mocking Neo4j transaction handlers, Qdrant similarity objects, and Telegram secret token validation.
* **`test_docsgpt_features.py`**: Asserts feature parity: chat widgets, conversation endpoints, and exports.
* **`test_enterprise_security.py`**: Asserts envelope AES-256-GCM CMEK encryption validity, decrypt string lengths, and tenant middleware isolation bounds.
* **`test_fastapi_endpoints.py`**: Asserts gateway controller status responses.
* **`test_graph_service.py`**: Asserts dependency path tracing and neighbor calculations.
* **`test_observability_and_errors.py`**: Asserts metrics logging, trace context propagation, and API error handlers.
* **`test_policy_engine.py`**: Asserts governance severities, SLAs, and approval loops.
* **`test_production_stack.py`**: Exercises production DB driver integration adapters.
* **`test_reasoning_and_validation.py`**: Asserts change validation trace matrices.
* **`test_retrieval_service.py`**: Asserts hybrid keyword-vector extraction context grounded answers.

---

## 2. Playwright E2E Browser Specs (`/playwright`)
A total of 12 browser E2E test runs executed on Chromium and Mobile Chrome.

### Test Target Files:
* **`accessibility/wcag-compliance.spec.ts`**: Validates markup accessibility and screen reader readiness.
* **`ai/copilot-reasoning.spec.ts`**: Triggers agent reasoning tasks via the UI and checks results.
* **`e2e/document-ingestion-to-diff.spec.ts`**: Main path: types text inside the editor pane, clicks save, updates Cy graph, and verifies diff differences in side panels.
* **`performance/latency-budget.spec.ts`**: Verifies page load budgets are under 500ms.
* **`security/token-isolation.spec.ts`**: Asserts that headers isolate views on different domains.
* **`visual/regression-check.spec.ts`**: Compares screen rendering against standard baseline screenshots.
