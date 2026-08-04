# Product Knowledge

This document captures the product vision, target personas, features, user journeys, roadmap, and DocsGPT capability parity matrix of DocSphere EKOS.

---

## 1. Product Vision
DocSphere EKOS (Enterprise Knowledge Representation and Operation System) is an enterprise-grade document intelligence system that bridges the gap between unstructured documents and structured enterprise architecture models. It establishes a "living digital twin" of requirements, capabilities, and system parameters, ensuring that changes in specification are automatically propagated and validated against structural architecture models.

---

## 2. Target Personas
* **Enterprise Architect / System Engineer**: Uses the graph viewer and impact analyzer to trace how change requests modify requirements, system capabilities, and downstream dependencies.
* **Knowledge Steward**: Responsible for ingesting new requirements specifications, running web crawls, verifying citations, and approving change impact diffs.
* **Security & Compliance Officer**: Monitors tenant isolation boundaries, rate-limit policies, audit logs, and CMEK configurations.
* **AI Copilot (Agent)**: Semi-autonomous services that execute tasks, run background analysis, and resolve policy parameters.

---

## 3. Product Parity check (DocSphere vs. DocsGPT)

| Feature Category | DocsGPT Capability | DocSphere Parity & Extension | Parity Status |
|---|---|---|---|
| **Conversational RAG** | Chat on documents, streaming answers, citation listings | Citations bound to graph nodes (ASST representation) with metadata | **Fully Parity+** |
| **Document Ingestion** | File uploads (PDF, TXT, MD), URL crawling | Local files + Web crawler, sitemap parser, recursive crawling | **Fully Parity+** |
| **Integrations** | Slack, Discord, Telegram adapters | Built-in channel adapters routing events to ChatEngine | **Fully Parity** |
| **Embeddable Widgets** | Chat widget embed code | Generates script tags and React components with light/dark theme | **Fully Parity+** |
| **Analytics & Feedback** | Query metrics, positive/negative ratings | Feedback logs + aggregated metrics + CSV/JSON export | **Fully Parity+** |
| **Agent Builder** | Prompt management, tool bindings | Jinja2 prompt template rendering, built-in tool execution | **Fully Parity+** |

---

## 4. Key Features & Capabilities
* **TipTap ASST Editor**: Rich editor in center panel with inline requirement tags and citations.
* **Cytoscape Graph Visualizer**: Traverses and renders entity relationships in real-time.
* **Side-by-side Diff Viewer**: Highlights current active baseline vs. recommended updates.
* **CMEK Encryption**: AES-256-GCM authenticated encryption for sensitive fields.
* **Redis Celery Worker Pipeline**: Background worker queue for high-performance indexing.
* **Federated Graph Mesh**: Traverses dependencies across multiple repositories.

---

## 5. Capability Roadmap
* **Milestone 1 (MVP)**: Completed. Laying the foundations of database, services, and three-panel layout.
* **Milestone 2 (Parity & Security)**: Completed. Full DocsGPT parity features, real Celery worker, real Neo4j/Qdrant adapters, and AES-256-GCM CMEK implementation.
* **Milestone 3 (Cloud Scale)**: Planned. Multi-region DB replication, Kubernetes scaling, and single-sign-on (SSO).
