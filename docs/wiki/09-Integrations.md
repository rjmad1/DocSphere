# 09. External System Integrations

## Enterprise Connectors (`backend/services/connectors/`)
- `jira_connector.py`: Bi-directionally maps Jira User Stories to `BusinessRequirement` (`REQ-`) and Jira Tests to `TestCase` (`TC-`).
- `confluence_connector.py`: Converts Confluence pages into ASST document trees.
- `sap_alm_connector.py`: Ingests SAP Cloud ALM Solution Documentation (`PROC-`, `SPEC-`).
- `servicenow_connector.py`: Synchronizes ServiceNow Change Requests (`CHG-`) and Incident tickets (`INC-`).

## Event Webhooks & Commit Listeners
- `github_commit_listener.py`: Parses incoming GitHub push webhooks into ASST AST nodes.
- `notification_service.py`: Dispatches PagerDuty incident triggers and Slack alerts for governance SLA breaches.
