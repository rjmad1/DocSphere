# 00. Project Overview

## Core Mission
DocSphere / EKOS (Enterprise Knowledge Operating System) is an enterprise platform designed to transform static, fragmented technical documentation into an active, self-governing knowledge graph.

## Scope & Value Proposition
- **Zero Documentation Drift**: Ensures 100% synchronization between markdown documentation trees and underlying graph models via an Abstract Semantic Syntax Tree (ASST) middle-layer.
- **Deterministic Blast Radius Calculation**: Evaluates upstream change impacts across code, specs, and operational controls before deployment.
- **Progressive Autonomy**: AI agents propose change diffs; human Stewards/Approvers approve changes based on impact severity and SLA rules.

## Technology Stack
- **Backend API**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy.
- **Databases**: Neo4j (Graph), Qdrant (Vector), PostgreSQL (Relational), Redis (Cache & Async Lock).
- **AI Framework**: Task-based Multi-Model LLM Gateway (OpenAI, Anthropic, Google Gemini).
- **Frontend Workspace**: React, Next.js, TipTap Rich Text Editor, Cytoscape.js Graph Explorer.
- **Infrastructure**: Kubernetes (Helm), Terraform (AWS EKS), Docker Compose.
