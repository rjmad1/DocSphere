# API Catalog

This document catalogues all the unified REST and WebSocket endpoints exposed by the DocSphere (EKOS) gateway.

---

## **Authorization Headers**
All endpoints (except public/fallback routes) enforce zero-trust authentication. Secure headers should be passed as follows:
* **JWT Bearer Token**: `Authorization: Bearer <JWT_Token>`
* **API Key**: `X-API-Key: <API_Key_Token>` or `Authorization: Bearer ds_<API_Key_Token>`

---

## **FastAPI REST Endpoints**

### **1. AI Agent Orchestrator**
* `POST /api/v1/agents/dispatch` — Dispatches a task to a registered agent. Requires role `Author`.
* `POST /api/v1/agents/builder` — Configures a custom agent definition. Requires role `Admin`.
* `GET /api/v1/agents/builder` — Lists all registered agents for a tenant. Requires role `Steward`.
* `GET /api/v1/agents/builder/{agent_id}` — Gets a specific agent definition. Requires role `Steward`.
* `DELETE /api/v1/agents/builder/{agent_id}` — Deletes an agent. Requires role `Admin`.
* `POST /api/v1/agents/builder/{agent_id}/execute` — Runs a custom agent query. Requires role `Author`.
* `GET /api/v1/agents/tools` — Lists all available built-in tools. Requires role `Author`.
* `POST /api/v1/agents/tools` — Registers a custom tool. Requires role `Steward`.

### **2. Conversational RAG Chat**
* `POST /api/v1/chat/message` — Submits a user query. Triggers hybrid context extraction and returns a citation-grounded response. Requires role `Author`.
* `GET /api/v1/chat/conversations` — Lists conversation histories for a tenant. Requires role `Author`.
* `GET /api/v1/chat/conversations/{conversation_id}` — Gets a single conversation thread. Requires role `Author`.
* `DELETE /api/v1/chat/conversations/{conversation_id}` — Deletes a conversation thread. Requires role `Author`.
* `POST /api/v1/chat/voice` — Transcribes base64-encoded voice audio. Requires role `Author`.

### **3. Knowledge Graph**
* `POST /api/v1/graph/entity` — Upserts an entity node (e.g. Requirement). Requires role `Steward`.
* `POST /api/v1/graph/relationship` — Creates a dependency edge. Requires role `Steward`.
* `GET /api/v1/graph/dependencies/{entity_id}` — Calculates requirement dependencies. Requires role `Author`.

### **4. Policy & Governance**
* `POST /api/v1/policy/evaluate` — Evaluates a change severity and approval chain. Requires role `Author`.

### **5. Embeddable Widgets**
* `POST /api/v1/widgets` — Registers a chat widget styling config. Requires role `Admin`.
* `GET /api/v1/widgets/{widget_id}/embed` — Generates script tag and React element embed code. Requires role `Admin`.

### **6. Channel webhook Integration**
* `POST /api/v1/channels/{channel_type}/webhook` — Webhook routing endpoint for Slack, Discord, and Telegram message routers.

### **7. API Key Lifecycle**
* `POST /api/v1/keys` — Generates and maps API keys. Requires role `Admin`.
* `GET /api/v1/keys` — Lists active keys. Requires role `Admin`.
* `DELETE /api/v1/keys/{key_id}` — Revokes/deactivates an API key. Requires role `Admin`.

### **8. Ingestion & Document Processing**
* `POST /api/v1/ingestion/crawl` — Dispatches crawling tasks. Requires role `Steward`.
* `POST /api/v1/documents/generate` — Triggers a document generation task. Requires role `Author`.
* `GET /api/v1/documents/status/{task_id}` — Checks Celery task progress. Requires role `Author`.

### **9. Chat Export & Sharing**
* `POST /api/v1/export/conversation` — Exports conversation. Requires role `Author`.
* `POST /api/v1/share` — Creates share links. Requires role `Author`.
* `GET /api/v1/share/{link_id}` — Retrieves shared conversation. Requires `Authorization: Bearer <token>` in header (preferred) or `access_token` query parameter (deprecated due to proxy url logging risk).
* `DELETE /api/v1/share/{link_id}` — Revokes a share link. Requires role `Author`.

---

## **WebSockets**
* `GET /api/v1/ws/generation/{generation_id}` — WebSocket tunnel providing real-time document extraction and compilation updates.
