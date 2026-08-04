# 13. Development Guide & Coding Standards

## Development Guidelines
1. **Python Standards**: Python 3.11+ with Pydantic v2 schemas and explicit type hints. Use `datetime.timezone.utc` for UTC timestamps.
2. **Package Conventions**: Use snake_case directory names under `backend/services/` (`knowledge_engine`, `document_service`, `agent_orchestrator`, `workflow_engine`, `ingestion`, `connectors`).
3. **Commit Messages**: Follow Conventional Commits format (`feat(...)`, `fix(...)`, `docs(...)`, `refactor(...)`).
