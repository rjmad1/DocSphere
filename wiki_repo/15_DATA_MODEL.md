# Data Model

This document specifies the Pydantic data schemas and Graph database models defined in the DocSphere system.

---

## 1. Core Graph Models (Neo4j Schema)

### Node Entities:
* **`Requirement`**: id, label="Requirement", properties (title, description, raw_text, parsed_at).
* **`Capability`**: id, label="Capability", properties (name, description, owner).
* **`SystemParameter`**: id, label="SystemParameter", properties (name, type, default_value).
* **`Tenant`**: id, label="Tenant", properties (name, created_at, billing_tier).

### Relationship Edges:
* **`IMPLEMENTS`**: (Requirement) -> (Capability). Indicates that a requirement addresses a business capability.
* **`DEPENDS_ON`**: (Requirement) -> (Requirement). Indicates dependency constraint tracking.
* **`AFFECTS`**: (Requirement) -> (SystemParameter). Indicates that modifying the requirement alters system behavior.

---

## 2. Ingestion & Search Schemas

### `SearchQuery` (Pydantic):
* `query_text`: str
* `tenant_id`: str
* `top_k`: int = 5

### `ParsedChunk` (Pydantic):
* `chunk_id`: str (e.g. `chk_DOC-BRD-001_1`)
* `document_id`: str
* `section_heading`: str
* `text_content`: str
* `offset`: int
* `entities`: List[str]

---

## 3. Conversational RAG Chat Schemas

### `ChatMessage` (Pydantic):
* `id`: str (UUID)
* `role`: str ("user", "assistant", "system")
* `content`: str
* `citations`: List[str] = []
* `timestamp`: datetime

### `Conversation` (Pydantic):
* `id`: str (UUID)
* `tenant_id`: str
* `title`: str
* `messages`: List[ChatMessage]
* `created_at`: datetime
* `updated_at`: datetime

---

## 4. Security & Configuration Schemas

### `ApiKey` (Pydantic):
* `key_id`: str
* `key_hash`: str (SHA256 hex digest)
* `key_prefix`: str (First 8 chars)
* `tenant_id`: str
* `agent_id`: Optional[str]
* `scopes`: List[ApiKeyScope] (e.g. `CHAT`, `SEARCH`)
* `rate_limit_per_minute`: int = 60
* `is_active`: bool = True

### `WidgetConfig` (Pydantic):
* `widget_id`: str
* `name`: str
* `tenant_id`: str
* `theme`: WidgetTheme ("LIGHT", "DARK")
* `primary_color`: str
* `greeting_message`: str
* `allowed_domains`: List[str] = []
