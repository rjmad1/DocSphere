# Architectural Decisions

This document summarizes the Architectural Decision Records (ADRs) that govern the design, databases, security, and operation of DocSphere.

---

## **ADR Summary Index**

### **ADR-0001: ASST Canonical Representation**
* **Context**: Require a unified schema to bind source specifications, requirements, and system capabilities.
* **Decision**: Adopted the **Active System Specification Template (ASST)** XML/JSON schema as the canonical intermediate representation, allowing bi-directional parsing between Markdown files and relational graphs.

### **ADR-0002: Neo4j & Qdrant Hybrid Retrieval**
* **Context**: Combining lexical keyword matching with vector embeddings search.
* **Decision**: Deployed a hybrid retrieval layer where **Neo4j** handles structural dependency traversals (e.g. tracking requirement overrides) and **Qdrant** executes fast cosine similarity searches.

### **ADR-0003: Progressive Autonomy Governance**
* **Context**: Controlling semi-autonomous changes proposed by AI agents.
* **Decision**: Implemented a human-in-the-loop review queue where high-risk changes require manual approval via the impact diff dashboard before graph propagation.

### **ADR-0004: Multi-Model LLM Routing**
* **Context**: Minimizing latency and LLM token costs for simple vs. complex queries.
* **Decision**: Configured a dynamic LLM gateway routing agent queries to light models (e.g. Gemini Flash) for extraction, and pro models (e.g. Gemini Pro) for change validation reasoning.

### **ADR-0005: Multi-Tenant Data Residency and CMEK**
* **Context**: Meeting regulatory policies for sensitive field-level PII attributes.
* **Decision**: Implemented Customer-Managed Encryption Keys (CMEK) via a shared security middleware performing base64-encoded **AES-256-GCM authenticated encryption** prior to indexing.

### **ADR-0006: Event-Driven ASST Sync**
* **Context**: Real-time synchronization of git commits and ingestion pipelines.
* **Decision**: Integrated Redis Pub/Sub channels to trigger async Celery tasks upon git branch pushes and webhook callbacks.

### **ADR-0007: Multi-Tenant RBAC and Security**
* **Context**: Enforcing logical tenant isolation boundaries at the API layer.
* **Decision**: Implemented an isolation middleware verifying `X-EKOS-Tenant-ID` and key claims on every incoming HTTP query and database connection context.

### **ADR-0008: CI/CD Security Scanning and Release Automation**
* **Context**: Mitigating deployment risk and verifying security compliance.
* **Decision**: Integrated automated dependency scanning and static analysis in pre-commit hooks, paired with visual regression browser testing.

### **ADR-0009: Audit Logging and Compliance**
* **Context**: Tracking agent activities, key revocation, and system changes.
* **Decision**: Authored a secure audit logger writing JSON-formatted actions to local read-only storage and SIEM endpoints.

### **ADR-0010: Disaster Recovery and Backup Strategy**
* **Context**: Guaranteeing resilience against server outages and data corruption.
* **Decision**: Implemented database snapshot scripts coupled with WORM (Write Once Read Many) backups for immutable audit log storage.
