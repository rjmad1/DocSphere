# API Catalog

This document catalogues all the unified REST and WebSocket endpoints exposed by the DocSphere (EKOS) gateway.

---

## **FastAPI REST Endpoints**

### **1. AI Agent Orchestrator**
* `POST /api/v1/agents/dispatch` — Dispatches a task to a registered agent. Returns a `TaskResponse`.
* `POST /api/v1/agents/builder` — Configures a custom agent definition.
* `GET /api/v1/agents/builder` — Lists all registered agents for a tenant.
* `GET /api/v1/agents/builder/{agent_id}` — Gets a specific agent definition.
* `DELETE /api/v1/agents/builder/{agent_id}` — Deletes an agent.
* `POST /api/v1/agents/builder/{agent_id}/execute` — Runs a custom agent query.
* `GET /api/v1/agents/tools` — Lists all available built-in tools.
* `POST /api/v1/agents/tools` — Registers a custom HTTP/Knowledge Query tool.

### **2. Conversational RAG Chat**
* `POST /api/v1/chat/message` — Submits a user query. Triggers hybrid Neo4j/Qdrant context extraction and returns a citation-grounded response.
* `GET /api/v1/chat/conversations` — Lists conversation histories for a tenant.
* `GET /api/v1/chat/conversations/{conversation_id}` — Gets a single conversation thread.
* `DELETE /api/v1/chat/conversations/{conversation_id}` — Deletes a conversation thread.
* `POST /api/v1/chat/voice` — Transcribes base64-encoded voice audio and processes it through the chat engine.

### **3. Knowledge Graph**
* `POST /api/v1/graph/entity` — Upserts an entity node (e.g. Requirement, Capability).
* `POST /api/v1/graph/relationship` — Creates a dependency edge between nodes.
* `GET /api/v1/graph/dependencies/{entity_id}` — Calculates transitive upstream/downstream requirement dependencies.

### **4. Policy & Governance**
* `POST /api/v1/policy/evaluate` — Evaluates a change severity and generates an approval chain SLA.

### **5. Embeddable Widgets**
* `POST /api/v1/widgets` — Registers a chat widget styling config.
* `GET /api/v1/widgets/{widget_id}/embed` — Generates script tag and React element embed code.

### **6. Channel webhook Integration**
* `POST /api/v1/channels/{channel_type}/webhook` — Event webhook routing endpoint for Slack, Discord, and Telegram message routers.

### **7. API Key Lifecycle**
* `POST /api/v1/keys` — Generates a raw API key prefix, hashes it, and maps authorization scopes.
* `GET /api/v1/keys` — Lists active keys.
* `DELETE /api/v1/keys/{key_id}` — Revokes/deactivates an API key.

### **8. Ingestion & Document Processing**
* `POST /api/v1/ingestion/crawl` — Dispatches a web page, sitemap, or recursive domain crawling task.
* `POST /api/v1/documents/generate` — Triggers a document generation task.
* `GET /api/v1/documents/status/{task_id}` — Checks background Celery worker task progress.

---

## **WebSockets**
* `GET /api/v1/ws/generation/{generation_id}` — WebSocket tunnel providing real-time document extraction and compilation updates.
