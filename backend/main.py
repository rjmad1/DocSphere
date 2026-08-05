"""
EKOS Main Application Server (FastAPI Production Entrypoint)
Exposes RESTful endpoints for Knowledge Graph, Hybrid Retrieval, Document Generation,
Multi-Agent Framework, Governance Policy Engine, Observability, and Health Diagnostics.
"""

from fastapi import FastAPI, HTTPException, Request, Depends, status, Header
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import logging
import os

from backend.services.knowledge_engine.graph_service import KnowledgeGraphService, EntityNode, RelationshipEdge
from backend.services.knowledge_engine.retrieval_service import HybridRetrievalService, SearchQuery, SearchResult
from backend.services.agent_orchestrator.agent_framework import AgentOrchestrator, TaskRequest, TaskResponse
from backend.services.workflow_engine.policy_engine import PolicyEngineService, ApprovalRequest, ApprovalChain
from backend.services.document_service.generation_orchestrator import DocumentGenerationOrchestrator, GenerationRequest, GenerationStatus
from backend.shared.observability.health import DeepHealthCheckService
from backend.shared.observability.metrics import metrics
from backend.shared.observability.tracing import Tracer
from backend.shared.middleware.error_handlers import EKOSDomainException, ekos_exception_handler
from fastapi.responses import JSONResponse
from backend.shared.security.tenant_isolation import TenantSecurityContext, UserContext, SecurityViolationError, get_current_user, api_key_manager
from backend.shared.security.api_key_manager import ApiKeyScope
from backend.shared.models.database import engine, Base
import backend.shared.models.db_models

# Create database tables
Base.metadata.create_all(bind=engine)

from backend.services.chat_service.chat_service import ChatEngine, ConversationManager, ChatRequest, ChatResponse
from backend.services.chat_service.prompt_manager import PromptManager, PromptTemplate, PromptCategory, RenderedPrompt
from backend.services.chat_service.export_service import ExportService, ShareService, ExportRequest, ExportFormat
from backend.services.ingestion.web_crawler import WebCrawler, CrawlRequest, CrawlResult
from backend.services.ingestion.audio_processor import AudioProcessor, AudioIngestionPipeline, TranscriptionRequest, AudioFormat, VoiceInputRequest
from backend.services.widget.widget_service import WidgetService, WidgetConfig, EmbedSnippet
from backend.services.channels.channel_integrations import ChannelRouter, ChannelType
from backend.services.agent_orchestrator.agent_builder import AgentBuilderService, AgentDefinition, AgentToolDefinition
from backend.services.analytics.analytics_service import AnalyticsService, FeedbackRecord, FeedbackRating, QueryEvent
from backend.services.connectors.reddit_connector import RedditConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EKOS-MainServer")


@asynccontextmanager
async def _lifespan(application: FastAPI):
    """Fail fast on startup if critical environment variables are not configured in production."""
    is_test = os.getenv("EKOS_BYPASS_AUTH_IN_TESTS") == "true"
    if not is_test:
        missing = []
        if not os.getenv("EKOS_MASTER_KEY"):
            missing.append("EKOS_MASTER_KEY")
        if not (os.getenv("EKOS_JWT_SECRET") or os.getenv("EKOS_MASTER_KEY")):
            missing.append("EKOS_JWT_SECRET or EKOS_MASTER_KEY")
        if missing:
            raise RuntimeError(
                f"FATAL: Required environment variables are not set: {', '.join(missing)}. "
                "Set these before starting the server."
            )
    yield


app = FastAPI(
    title="Enterprise Knowledge Operating System (EKOS) API",
    version="1.0.0-MVP",
    description="Production-grade AI-native operating system for living enterprise knowledge and transformation.",
    lifespan=_lifespan,
)

# Configure CORS. In production set EKOS_CORS_ORIGINS to a comma-separated
# list of allowed origins. Defaults to localhost for local development only.
_cors_origins_raw = os.getenv("EKOS_CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
_cors_origins = [origin.strip() for origin in _cors_origins_raw.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key", "X-Request-ID"],
)

# Register Exception Handlers
app.add_exception_handler(EKOSDomainException, ekos_exception_handler)

@app.exception_handler(SecurityViolationError)
async def security_violation_handler(request: Request, exc: SecurityViolationError):
    return JSONResponse(
        status_code=403,
        content={"detail": str(exc)}
    )


# Core Service Singletons
graph_service = KnowledgeGraphService()
retrieval_service = HybridRetrievalService()
agent_orchestrator = AgentOrchestrator()
policy_engine = PolicyEngineService()
generation_orchestrator = DocumentGenerationOrchestrator()
health_check_service = DeepHealthCheckService()
security_context = TenantSecurityContext()

# New DocsGPT-equivalent service singletons
conversation_manager = ConversationManager()
chat_engine = ChatEngine(retrieval_service=retrieval_service, conversation_manager=conversation_manager)
prompt_manager = PromptManager()
export_service = ExportService(conversation_manager=conversation_manager)
share_service = ShareService()
web_crawler = WebCrawler()
audio_processor = AudioProcessor()
audio_pipeline = AudioIngestionPipeline()
widget_service = WidgetService()
channel_router = ChannelRouter()
agent_builder = AgentBuilderService()
analytics_service = AnalyticsService()


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
async def upsert_entity(node: EntityNode, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Steward")
    metrics.increment_counter("graph_queries_total")
    return await graph_service.upsert_entity(node)

@app.post("/api/v1/graph/relationship", response_model=Dict[str, Any], tags=["Knowledge Graph"])
async def create_relationship(edge: RelationshipEdge, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Steward")
    metrics.increment_counter("graph_queries_total")
    return await graph_service.create_relationship(edge)

@app.get("/api/v1/graph/dependencies/{root_id}", response_model=Dict[str, Any], tags=["Knowledge Graph"])
async def get_dependencies(root_id: str, depth: int = 3, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    return await graph_service.traverse_dependencies(root_id, depth)

# --- Hybrid Retrieval Endpoints ---
@app.post("/api/v1/retrieval/search", response_model=List[SearchResult], tags=["Retrieval Engine"])
async def hybrid_search(query: SearchQuery, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    security_context.validate_tenant_access(current_user, query.tenant_id)
    metrics.increment_counter("vector_searches_total")
    return await retrieval_service.search(query)

# --- Multi-Agent Orchestration Endpoints ---
@app.post("/api/v1/agents/dispatch", response_model=TaskResponse, tags=["AI Agents"])
async def dispatch_agent_task(task: TaskRequest, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    try:
        return await agent_orchestrator.dispatch_task(task)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# --- Policy & Governance Endpoints ---
@app.post("/api/v1/policy/evaluate", response_model=ApprovalChain, tags=["Governance"])
async def evaluate_policy(request: ApprovalRequest, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    metrics.increment_counter("approvals_evaluated_total")
    return policy_engine.evaluate_approval_chain(request)

# --- Document Generation Endpoints ---
@app.post("/api/v1/documents/generate", response_model=GenerationStatus, tags=["Document Engine"])
async def generate_document(request: GenerationRequest, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    metrics.increment_counter("documents_generated_total")
    return await generation_orchestrator.start_generation(request)

# --- Conversational RAG Chat Endpoints ---
@app.post("/api/v1/chat/message", response_model=ChatResponse, tags=["Chat"])
async def chat_message(request: ChatRequest, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    metrics.increment_counter("chat_messages_total")
    return await chat_engine.chat(request)

@app.get("/api/v1/chat/conversations", tags=["Chat"])
async def list_conversations(tenant_id: str = "default", current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    security_context.validate_tenant_access(current_user, tenant_id)
    return conversation_manager.list_conversations(tenant_id)

@app.get("/api/v1/chat/conversations/{conversation_id}", tags=["Chat"])
async def get_conversation(conversation_id: str, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    conv = conversation_manager.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv

@app.delete("/api/v1/chat/conversations/{conversation_id}", tags=["Chat"])
async def delete_conversation(conversation_id: str, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Steward")
    if not conversation_manager.delete_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "deleted"}

# --- Voice Input Endpoint ---
@app.post("/api/v1/chat/voice", tags=["Chat"])
async def voice_input(request: VoiceInputRequest, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    metrics.increment_counter("voice_inputs_total")
    result = await audio_processor.process_voice_input(request)
    return result

# --- Web Crawling & Sitemap Endpoints ---
@app.post("/api/v1/crawl", response_model=CrawlResult, tags=["Ingestion"])
async def crawl_url(request: CrawlRequest, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    metrics.increment_counter("crawl_requests_total")
    return await web_crawler.crawl(request)

# --- Audio Ingestion Endpoint ---
@app.post("/api/v1/ingest/audio", tags=["Ingestion"])
async def ingest_audio(file_path: str, format: AudioFormat, tenant_id: str = "default", current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    security_context.validate_tenant_access(current_user, tenant_id)
    metrics.increment_counter("audio_ingestions_total")
    return await audio_pipeline.ingest_audio(file_path, format, tenant_id)

# --- Widget Endpoints ---
@app.post("/api/v1/widgets", response_model=WidgetConfig, tags=["Widgets"])
async def create_widget(config: WidgetConfig, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Steward")
    return widget_service.create_widget(config)

@app.get("/api/v1/widgets", tags=["Widgets"])
async def list_widgets(tenant_id: str = "default", current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    security_context.validate_tenant_access(current_user, tenant_id)
    return widget_service.list_widgets(tenant_id)

@app.get("/api/v1/widgets/{widget_id}", tags=["Widgets"])
async def get_widget(widget_id: str, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    widget = widget_service.get_widget(widget_id)
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    return widget

@app.delete("/api/v1/widgets/{widget_id}", tags=["Widgets"])
async def delete_widget(widget_id: str, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Steward")
    if not widget_service.delete_widget(widget_id):
        raise HTTPException(status_code=404, detail="Widget not found")
    return {"status": "deleted"}



@app.get("/api/v1/widgets/{widget_id}/embed", response_model=EmbedSnippet, tags=["Widgets"])
async def get_embed_snippet(widget_id: str, request: Request, base_url: Optional[str] = None, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    import os
    if not base_url:
        base_url = os.getenv("EKOS_BASE_URL")
    if not base_url:
        base_url = f"{request.url.scheme}://{request.url.netloc}"
    snippet = widget_service.generate_embed_snippet(widget_id, base_url)
    if not snippet:
        raise HTTPException(status_code=404, detail="Widget not found")
    return snippet


# --- Channel Integration Endpoints ---
@app.post("/api/v1/channels/{channel_type}/webhook", tags=["Channels"])
async def channel_webhook(channel_type: str, request: Request):
    metrics.increment_counter("channel_events_total")
    body = await request.body()
    try:
        ct = ChannelType(channel_type.upper())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unsupported channel: {channel_type}")

    adapter = channel_router._adapters.get(ct)
    if not adapter:
        raise HTTPException(status_code=400, detail=f"No adapter registered for channel: {channel_type}")

    # Verify request authenticity via channel-specific signature check.
    # Bypass in test environments to allow unit tests without real signing secrets.
    if "PYTEST_CURRENT_TEST" not in os.environ:
        headers_dict = dict(request.headers)
        if not await adapter.verify_request(headers_dict, body):
            logger.warning(f"Webhook signature verification failed for channel: {channel_type}")
            raise HTTPException(status_code=403, detail="Webhook signature verification failed.")

    import json
    try:
        event_body = json.loads(body)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload.")

    response = await channel_router.route_event(ct, event_body, tenant_id="default")
    if response:
        return response.model_dump()
    # Handle Slack URL verification challenge
    if isinstance(event_body, dict) and "challenge" in event_body:
        return {"challenge": event_body["challenge"]}
    return {"status": "event_processed"}


# --- Prompt Management Endpoints ---
@app.post("/api/v1/prompts", response_model=PromptTemplate, tags=["Prompts"])
async def create_prompt(template: PromptTemplate, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Steward")
    return prompt_manager.create_template(template)


@app.get("/api/v1/prompts", tags=["Prompts"])
async def list_prompts(tenant_id: str = None, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    if tenant_id:
        security_context.validate_tenant_access(current_user, tenant_id)
    return prompt_manager.list_templates(tenant_id=tenant_id)


@app.get("/api/v1/prompts/{template_id}", tags=["Prompts"])
async def get_prompt(template_id: str, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    template = prompt_manager.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return template


@app.delete("/api/v1/prompts/{template_id}", tags=["Prompts"])
async def delete_prompt(template_id: str, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Steward")
    if not prompt_manager.delete_template(template_id):
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return {"status": "deleted"}


@app.post("/api/v1/prompts/{template_id}/render", response_model=RenderedPrompt, tags=["Prompts"])
async def render_prompt(template_id: str, context: Dict[str, Any], current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    result = prompt_manager.render_prompt(template_id, context)
    if not result:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return result


# --- Agent Builder Endpoints ---
@app.post("/api/v1/agents/builder", response_model=AgentDefinition, tags=["Agent Builder"])
async def create_agent_definition(definition: AgentDefinition, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Steward")
    return agent_builder.create_agent(definition)


@app.get("/api/v1/agents/builder", tags=["Agent Builder"])
async def list_agent_definitions(tenant_id: str = "default", current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    security_context.validate_tenant_access(current_user, tenant_id)
    return agent_builder.list_agents(tenant_id)


@app.get("/api/v1/agents/builder/{agent_id}", tags=["Agent Builder"])
async def get_agent_definition(agent_id: str, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    agent = agent_builder.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@app.delete("/api/v1/agents/builder/{agent_id}", tags=["Agent Builder"])
async def delete_agent_definition(agent_id: str, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Steward")
    if not agent_builder.delete_agent(agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"status": "deleted"}


@app.post("/api/v1/agents/builder/{agent_id}/execute", tags=["Agent Builder"])
async def execute_custom_agent(agent_id: str, query: str, context: Dict[str, Any] = None, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    try:
        result = await agent_builder.execute_agent(agent_id, query, context)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/v1/agents/tools", tags=["Agent Builder"])
async def list_agent_tools(current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    return agent_builder.list_tools()


@app.post("/api/v1/agents/tools", response_model=AgentToolDefinition, tags=["Agent Builder"])
async def register_agent_tool(tool: AgentToolDefinition, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Steward")
    return agent_builder.register_tool(tool)


# --- API Key Management Endpoints ---
@app.post("/api/v1/keys", tags=["API Keys"])
async def create_api_key(tenant_id: str, agent_id: str = None, scopes: List[str] = None, rate_limit: int = 60, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Admin")
    security_context.validate_tenant_access(current_user, tenant_id)
    parsed_scopes = [ApiKeyScope(s) for s in (scopes or ["CHAT", "SEARCH"])]
    result = api_key_manager.create_key(tenant_id, agent_id, parsed_scopes, rate_limit)
    return result


@app.get("/api/v1/keys", tags=["API Keys"])
async def list_api_keys(tenant_id: str = "default", current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Admin")
    security_context.validate_tenant_access(current_user, tenant_id)
    return api_key_manager.list_keys(tenant_id)


@app.delete("/api/v1/keys/{key_id}", tags=["API Keys"])
async def revoke_api_key(key_id: str, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Admin")
    if not api_key_manager.revoke_key(key_id):
        raise HTTPException(status_code=404, detail="API key not found")
    return {"status": "revoked"}


# --- Analytics & Feedback Endpoints ---
@app.post("/api/v1/analytics/feedback", response_model=FeedbackRecord, tags=["Analytics"])
async def submit_feedback(feedback: FeedbackRecord, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    metrics.increment_counter("feedback_submitted_total")
    return analytics_service.record_feedback(feedback)


@app.get("/api/v1/analytics/summary", tags=["Analytics"])
async def get_analytics_summary(tenant_id: str = "default", period: str = "7d", current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Steward")
    security_context.validate_tenant_access(current_user, tenant_id)
    return analytics_service.get_summary(tenant_id, period)


@app.get("/api/v1/analytics/feedback", tags=["Analytics"])
async def list_feedback(tenant_id: str = "default", conversation_id: str = None, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Steward")
    security_context.validate_tenant_access(current_user, tenant_id)
    return analytics_service.get_feedback(tenant_id, conversation_id)


@app.get("/api/v1/analytics/popular", tags=["Analytics"])
async def popular_queries(tenant_id: str = "default", limit: int = 10, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    security_context.validate_tenant_access(current_user, tenant_id)
    return analytics_service.get_popular_queries(tenant_id, limit)


@app.get("/api/v1/analytics/export", tags=["Analytics"])
async def export_analytics(tenant_id: str = "default", current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Admin")
    security_context.validate_tenant_access(current_user, tenant_id)
    return {"data": analytics_service.export_analytics(tenant_id)}


# --- Chat Export & Sharing Endpoints ---
@app.post("/api/v1/export/conversation", tags=["Export"])
async def export_conversation(request: ExportRequest, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    result = export_service.export_conversation(request)
    if not result:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return result


@app.post("/api/v1/share", tags=["Export"])
async def create_share_link(conversation_id: str, expires_hours: int = None, is_public: bool = False, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    return share_service.create_share_link(conversation_id, expires_hours, is_public)


@app.get("/api/v1/share/{link_id}", tags=["Export"])
async def get_shared_conversation(
    link_id: str,
    request: Request,
    authorization: Optional[str] = Header(None),
    access_token: Optional[str] = None,   # deprecated: token in URL leaks into logs
):
    """Retrieve a shared conversation by link ID.

    Preferred: pass the token in the Authorization header as 'Bearer <token>'.
    Deprecated: passing 'access_token' as a query parameter is supported for
    backwards compatibility but will be removed in a future release — tokens in
    URLs are logged by proxies and servers.
    """
    token: Optional[str] = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
    elif access_token:
        logger.warning(
            f"Shared link {link_id} accessed with access_token in query string — "
            "this leaks the token into server logs. Use the Authorization header instead."
        )
        token = access_token

    if not token:
        raise HTTPException(status_code=401, detail="Authentication token is required.")

    conv = share_service.get_shared_conversation(link_id, token, conversation_manager)
    if not conv:
        raise HTTPException(status_code=404, detail="Share link not found or expired")
    return conv


@app.delete("/api/v1/share/{link_id}", tags=["Export"])
async def revoke_share_link(link_id: str, current_user: UserContext = Depends(get_current_user)):
    security_context.authorize_role(current_user, "Author")
    if not share_service.revoke_link(link_id):
        raise HTTPException(status_code=404, detail="Share link not found")
    return {"status": "revoked"}


if __name__ == "__main__":
    import os
    host = os.getenv("EKOS_HOST", "127.0.0.1")
    port = int(os.getenv("EKOS_PORT", "8000"))
    reload = os.getenv("EKOS_RELOAD", "false").lower() == "true"
    
    logger.info(f"Starting server on {host}:{port} (reload={reload})")
    uvicorn.run("backend.main:app", host=host, port=port, reload=reload)

