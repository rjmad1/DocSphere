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
from backend.shared.security.api_key_manager import ApiKeyManager, ApiKeyScope
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
api_key_manager = ApiKeyManager()
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
    try:
        return await agent_orchestrator.dispatch_task(task)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

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

# --- Conversational RAG Chat Endpoints ---
@app.post("/api/v1/chat/message", response_model=ChatResponse, tags=["Chat"])
async def chat_message(request: ChatRequest):
    metrics.increment_counter("chat_messages_total")
    return await chat_engine.chat(request)


@app.get("/api/v1/chat/conversations", tags=["Chat"])
async def list_conversations(tenant_id: str = "default"):
    return conversation_manager.list_conversations(tenant_id)


@app.get("/api/v1/chat/conversations/{conversation_id}", tags=["Chat"])
async def get_conversation(conversation_id: str):
    conv = conversation_manager.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@app.delete("/api/v1/chat/conversations/{conversation_id}", tags=["Chat"])
async def delete_conversation(conversation_id: str):
    if not conversation_manager.delete_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "deleted"}


# --- Voice Input Endpoint ---
@app.post("/api/v1/chat/voice", tags=["Chat"])
async def voice_input(request: VoiceInputRequest):
    metrics.increment_counter("voice_inputs_total")
    result = await audio_processor.process_voice_input(request)
    return result


# --- Web Crawling & Sitemap Endpoints ---
@app.post("/api/v1/crawl", response_model=CrawlResult, tags=["Ingestion"])
async def crawl_url(request: CrawlRequest):
    metrics.increment_counter("crawl_requests_total")
    return await web_crawler.crawl(request)


# --- Audio Ingestion Endpoint ---
@app.post("/api/v1/ingest/audio", tags=["Ingestion"])
async def ingest_audio(file_path: str, format: AudioFormat, tenant_id: str = "default"):
    metrics.increment_counter("audio_ingestions_total")
    return await audio_pipeline.ingest_audio(file_path, format, tenant_id)


# --- Widget Endpoints ---
@app.post("/api/v1/widgets", response_model=WidgetConfig, tags=["Widgets"])
async def create_widget(config: WidgetConfig):
    return widget_service.create_widget(config)


@app.get("/api/v1/widgets", tags=["Widgets"])
async def list_widgets(tenant_id: str = "default"):
    return widget_service.list_widgets(tenant_id)


@app.get("/api/v1/widgets/{widget_id}", tags=["Widgets"])
async def get_widget(widget_id: str):
    widget = widget_service.get_widget(widget_id)
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    return widget


@app.delete("/api/v1/widgets/{widget_id}", tags=["Widgets"])
async def delete_widget(widget_id: str):
    if not widget_service.delete_widget(widget_id):
        raise HTTPException(status_code=404, detail="Widget not found")
    return {"status": "deleted"}


@app.get("/api/v1/widgets/{widget_id}/embed", response_model=EmbedSnippet, tags=["Widgets"])
async def get_embed_snippet(widget_id: str, base_url: str = "https://api.docsphere.io"):
    snippet = widget_service.generate_embed_snippet(widget_id, base_url)
    if not snippet:
        raise HTTPException(status_code=404, detail="Widget not found")
    return snippet


# --- Channel Integration Endpoints ---
@app.post("/api/v1/channels/{channel_type}/webhook", tags=["Channels"])
async def channel_webhook(channel_type: str, request: Request):
    metrics.increment_counter("channel_events_total")
    body = await request.json()
    try:
        ct = ChannelType(channel_type.upper())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unsupported channel: {channel_type}")
    response = await channel_router.route_event(ct, body, tenant_id="default")
    if response:
        return response.model_dump()
    return {"status": "event_processed"}


# --- Prompt Management Endpoints ---
@app.post("/api/v1/prompts", response_model=PromptTemplate, tags=["Prompts"])
async def create_prompt(template: PromptTemplate):
    return prompt_manager.create_template(template)


@app.get("/api/v1/prompts", tags=["Prompts"])
async def list_prompts(tenant_id: str = None):
    return prompt_manager.list_templates(tenant_id=tenant_id)


@app.get("/api/v1/prompts/{template_id}", tags=["Prompts"])
async def get_prompt(template_id: str):
    template = prompt_manager.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return template


@app.delete("/api/v1/prompts/{template_id}", tags=["Prompts"])
async def delete_prompt(template_id: str):
    if not prompt_manager.delete_template(template_id):
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return {"status": "deleted"}


@app.post("/api/v1/prompts/{template_id}/render", response_model=RenderedPrompt, tags=["Prompts"])
async def render_prompt(template_id: str, context: Dict[str, Any]):
    result = prompt_manager.render_prompt(template_id, context)
    if not result:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return result


# --- Agent Builder Endpoints ---
@app.post("/api/v1/agents/builder", response_model=AgentDefinition, tags=["Agent Builder"])
async def create_agent_definition(definition: AgentDefinition):
    return agent_builder.create_agent(definition)


@app.get("/api/v1/agents/builder", tags=["Agent Builder"])
async def list_agent_definitions(tenant_id: str = "default"):
    return agent_builder.list_agents(tenant_id)


@app.get("/api/v1/agents/builder/{agent_id}", tags=["Agent Builder"])
async def get_agent_definition(agent_id: str):
    agent = agent_builder.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@app.delete("/api/v1/agents/builder/{agent_id}", tags=["Agent Builder"])
async def delete_agent_definition(agent_id: str):
    if not agent_builder.delete_agent(agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"status": "deleted"}


@app.post("/api/v1/agents/builder/{agent_id}/execute", tags=["Agent Builder"])
async def execute_custom_agent(agent_id: str, query: str, context: Dict[str, Any] = None):
    try:
        result = await agent_builder.execute_agent(agent_id, query, context)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/v1/agents/tools", tags=["Agent Builder"])
async def list_agent_tools():
    return agent_builder.list_tools()


@app.post("/api/v1/agents/tools", response_model=AgentToolDefinition, tags=["Agent Builder"])
async def register_agent_tool(tool: AgentToolDefinition):
    return agent_builder.register_tool(tool)


# --- API Key Management Endpoints ---
@app.post("/api/v1/keys", tags=["API Keys"])
async def create_api_key(tenant_id: str, agent_id: str = None, scopes: List[str] = None, rate_limit: int = 60):
    parsed_scopes = [ApiKeyScope(s) for s in (scopes or ["CHAT", "SEARCH"])]
    result = api_key_manager.create_key(tenant_id, agent_id, parsed_scopes, rate_limit)
    return result


@app.get("/api/v1/keys", tags=["API Keys"])
async def list_api_keys(tenant_id: str = "default"):
    return api_key_manager.list_keys(tenant_id)


@app.delete("/api/v1/keys/{key_id}", tags=["API Keys"])
async def revoke_api_key(key_id: str):
    if not api_key_manager.revoke_key(key_id):
        raise HTTPException(status_code=404, detail="API key not found")
    return {"status": "revoked"}


# --- Analytics & Feedback Endpoints ---
@app.post("/api/v1/analytics/feedback", response_model=FeedbackRecord, tags=["Analytics"])
async def submit_feedback(feedback: FeedbackRecord):
    metrics.increment_counter("feedback_submitted_total")
    return analytics_service.record_feedback(feedback)


@app.get("/api/v1/analytics/summary", tags=["Analytics"])
async def get_analytics_summary(tenant_id: str = "default", period: str = "7d"):
    return analytics_service.get_summary(tenant_id, period)


@app.get("/api/v1/analytics/feedback", tags=["Analytics"])
async def list_feedback(tenant_id: str = "default", conversation_id: str = None):
    return analytics_service.get_feedback(tenant_id, conversation_id)


@app.get("/api/v1/analytics/popular", tags=["Analytics"])
async def popular_queries(tenant_id: str = "default", limit: int = 10):
    return analytics_service.get_popular_queries(tenant_id, limit)


@app.get("/api/v1/analytics/export", tags=["Analytics"])
async def export_analytics(tenant_id: str = "default"):
    return {"data": analytics_service.export_analytics(tenant_id)}


# --- Chat Export & Sharing Endpoints ---
@app.post("/api/v1/export/conversation", tags=["Export"])
async def export_conversation(request: ExportRequest):
    result = export_service.export_conversation(request)
    if not result:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return result


@app.post("/api/v1/share", tags=["Export"])
async def create_share_link(conversation_id: str, expires_hours: int = None, is_public: bool = False):
    return share_service.create_share_link(conversation_id, expires_hours, is_public)


@app.get("/api/v1/share/{link_id}", tags=["Export"])
async def get_shared_conversation(link_id: str, access_token: str):
    conv = share_service.get_shared_conversation(link_id, access_token, conversation_manager)
    if not conv:
        raise HTTPException(status_code=404, detail="Share link not found or expired")
    return conv


@app.delete("/api/v1/share/{link_id}", tags=["Export"])
async def revoke_share_link(link_id: str):
    if not share_service.revoke_link(link_id):
        raise HTTPException(status_code=404, detail="Share link not found")
    return {"status": "revoked"}


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
