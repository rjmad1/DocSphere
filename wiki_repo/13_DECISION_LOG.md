# Decision Log

This document records the core architectural and product design decisions, their rationale, alternatives considered, and down-stream impacts.

---

## **Architectural Decision Logs**

### **Decision 1: Deploy a Hybrid Neo4j & Qdrant Search Architecture**
* **Status**: Approved & Implemented
* **Rationale**: Simple vector databases cannot map deep requirement relationships (e.g. tracking requirement overrides across folders). Using a hybrid structure:
  * **Neo4j** traverses nodes (`Requirement`, `Capability`) and dependencies.
  * **Qdrant** executes semantic similarity vector queries.
* **Alternatives**: Relational database (too slow for graph traversal), only Qdrant (lacks relationship integrity).
* **Impact**: Resolves DocsGPT feature limitations while providing enterprise-grade dependency lookup.

### **Decision 2: Offload Workflows to Redis-Backed Celery Workers**
* **Status**: Approved & Implemented
* **Rationale**: Ingesting files and running impact analyses are CPU-intensive. Processing them in the main FastAPI gateway thread degrades performance. Offloading to separate worker processes via Celery handles scale.
* **Alternatives**: Native python async tasks (blocking).
* **Impact**: Increases operational footprint but guarantees gateway reliability.

### **Decision 3: Maintain Strict In-Memory Fallbacks for Local Testing**
* **Status**: Approved & Implemented
* **Rationale**: Requiring a running Neo4j, Qdrant, and Redis instance locally makes automated tests fragile and prevents fast CI/CD execution.
* **Alternatives**: Mocking with docker-compose on every test execution (too slow).
* **Impact**: Keeps test execution time under 10 seconds with **zero external dependencies**.

### **Decision 4: Authenticated AES-256-GCM Envelope Encryption (CMEK)**
* **Status**: Approved & Implemented
* **Rationale**: Field-level encryption is required for regulatory compliance when storing PII or proprietary specifications. Standard AES-256-GCM provides both encryption and data integrity checks.
* **Alternatives**: Simple XOR (insecure), raw AES-CBC (prone to padding attacks).
* **Impact**: CPU overhead is negligible; secures tenant data at rest.
