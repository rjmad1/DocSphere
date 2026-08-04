"""
EKOS Main Application Server (FastAPI Production Entrypoint)
Exposes RESTful endpoints for Knowledge Graph, Hybrid Retrieval, Document Generation,
Multi-Agent Framework, Governance Policy Engine, Observability, and Health Diagnostics.
"""

from fastapi import FastAPI, HTTPException, Request, Depends, status
from pydantic import BaseModel
from typing import Dict, Any, List
import uvicorn
import logging

from backend.services.knowledge_engine.graph_service import KnowledgeGraphService, EntityNode, RelationshipEdge
from backend.services.knowledge_engine.retrieval_service import HybridRetrievalService, SearchQuery, SearchResult
from backend.services.agent_orchestrator.agent_framework import AgentOrchestrator, TaskRequest, TaskResponse
from backend.services.workflow_engine.policy_engine import PolicyEngineService, ApprovalRequest, ApprovalChain
from backend.services.document_service.generation_orchestrator import DocumentGenerationOrchestrator, GenerationRequest, GenerationStatus
from backend.shared.observability.health import DeepHealthCheckService
from backend.shared.observability.metrics import metrics
from backend.shared.observability.tracing import Tracer
from backend.shared.middleware.error_handlers import EKOSDomainException, ekos_exception_handler
from backend.shared.security.tenant_isolation import TenantSecurityContext, UserContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EKOS-MainServer")

app = FastAPI(
    title="Enterprise Knowledge Operating System (EKOS) API",
    version="1.0.0-MVP",
    description="Production-grade AI-native operating system for living enterprise knowledge and transformation."
)

# Register Exception Handler
app.add_exception_handler(EKOSDomainException, ekos_exception_handler)

# Core Service Singletons
graph_service = KnowledgeGraphService()
retrieval_service = HybridRetrievalService()
agent_orchestrator = AgentOrchestrator()
policy_engine = PolicyEngineService()
generation_orchestrator = DocumentGenerationOrchestrator()
health_check_service = DeepHealthCheckService()
security_context = TenantSecurityContext()

# Request Tracing Middleware
@app.middleware("http")
async def tracing_middleware(request: Request, call_next):
    trace_id = Tracer.start_trace("API-Gateway", request.url.path)
    metrics.increment_counter("http_requests_total")
    response = await call_next(request)
    Tracer.end_trace(trace_id, status=str(response.status_code))
    return response

@app.get("/health", tags=["Observability"])
async def health_check():
    return {"status": "healthy", "system": "EKOS Platform Engine", "version": "1.0.0-MVP"}

@app.get("/health/deep", tags=["Observability"])
async def deep_health_check():
    return await health_check_service.check_all_services()

@app.get("/metrics", tags=["Observability"])
async def get_metrics():
    return metrics.export_metrics()

# --- Knowledge Graph Endpoints ---
@app.post("/api/v1/graph/entity", response_model=Dict[str, Any], tags=["Knowledge Graph"])
async def upsert_entity(node: EntityNode):
    metrics.increment_counter("graph_queries_total")
    return await graph_service.upsert_entity(node)

@app.post("/api/v1/graph/relationship", response_model=Dict[str, Any], tags=["Knowledge Graph"])
async def create_relationship(edge: RelationshipEdge):
    metrics.increment_counter("graph_queries_total")
    return await graph_service.create_relationship(edge)

@app.get("/api/v1/graph/dependencies/{root_id}", response_model=Dict[str, Any], tags=["Knowledge Graph"])
async def get_dependencies(root_id: str, depth: int = 3):
    return await graph_service.traverse_dependencies(root_id, depth)

# --- Hybrid Retrieval Endpoints ---
@app.post("/api/v1/retrieval/search", response_model=List[SearchResult], tags=["Retrieval Engine"])
async def hybrid_search(query: SearchQuery):
    metrics.increment_counter("vector_searches_total")
    return await retrieval_service.search(query)

# --- Multi-Agent Orchestration Endpoints ---
@app.post("/api/v1/agents/dispatch", response_model=TaskResponse, tags=["AI Agents"])
async def dispatch_agent_task(task: TaskRequest):
    return await agent_orchestrator.dispatch_task(task)

# --- Policy & Governance Endpoints ---
@app.post("/api/v1/policy/evaluate", response_model=ApprovalChain, tags=["Governance"])
async def evaluate_policy(request: ApprovalRequest):
    metrics.increment_counter("approvals_evaluated_total")
    return policy_engine.evaluate_approval_chain(request)

# --- Document Generation Endpoints ---
@app.post("/api/v1/documents/generate", response_model=GenerationStatus, tags=["Document Engine"])
async def generate_document(request: GenerationRequest):
    metrics.increment_counter("documents_generated_total")
    return await generation_orchestrator.start_generation(request)

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
