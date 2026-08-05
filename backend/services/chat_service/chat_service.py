import uuid
from typing import List, Dict, Optional, AsyncGenerator
from datetime import datetime, timezone
import asyncio
from pydantic import BaseModel, Field
import logging

from backend.services.knowledge_engine.retrieval_service import HybridRetrievalService, SearchQuery, SearchResult

logger = logging.getLogger("EKOS-ChatService")

class ChatMessage(BaseModel):
    """Represents a single message in a conversation."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str  # user, assistant, system
    content: str
    citations: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Conversation(BaseModel):
    """Represents a chat conversation."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    title: str
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatRequest(BaseModel):
    """Request to send a message and get a response."""
    conversation_id: Optional[str] = None
    query: str
    tenant_id: str
    top_k: int = 5
    include_sources: bool = True
    stream: bool = False

class ChatResponse(BaseModel):
    """Response containing the assistant's message and sources."""
    conversation_id: str
    message: ChatMessage
    sources: List[dict] = Field(default_factory=list)

class ConversationManager:
    """Manages chat conversations."""
    def __init__(self):
        self._conversations: Dict[str, Conversation] = {}
        logger.info("ConversationManager initialized")

    def create_conversation(self, tenant_id: str, title: str) -> Conversation:
        conversation = Conversation(tenant_id=tenant_id, title=title)
        self._conversations[conversation.id] = conversation
        return conversation

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        return self._conversations.get(conversation_id)

    def list_conversations(self, tenant_id: str) -> List[Conversation]:
        return [conv for conv in self._conversations.values() if conv.tenant_id == tenant_id]

    def add_message(self, conversation_id: str, message: ChatMessage) -> Optional[Conversation]:
        conversation = self._conversations.get(conversation_id)
        if conversation:
            conversation.messages.append(message)
            conversation.updated_at = datetime.now(timezone.utc)
        return conversation

    def delete_conversation(self, conversation_id: str) -> bool:
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
            return True
        return False

class ChatEngine:
    """Core conversational RAG engine."""
    def __init__(self, retrieval_service: HybridRetrievalService, conversation_manager: ConversationManager):
        self.retrieval_service = retrieval_service
        self.conversation_manager = conversation_manager
        logger.info("ChatEngine initialized")

    async def chat(self, request: ChatRequest) -> ChatResponse:
        # Create conversation if it doesn't exist
        conversation_id = request.conversation_id
        if not conversation_id:
            conversation = self.conversation_manager.create_conversation(
                tenant_id=request.tenant_id, 
                title=f"Chat: {request.query[:20]}..."
            )
            conversation_id = conversation.id
        else:
            conversation = self.conversation_manager.get_conversation(conversation_id)
            if not conversation:
                # Fallback if invalid id is provided
                conversation = self.conversation_manager.create_conversation(
                    tenant_id=request.tenant_id, 
                    title=f"Chat: {request.query[:20]}..."
                )
                conversation_id = conversation.id

        # Add user message
        user_message = ChatMessage(role="user", content=request.query)
        self.conversation_manager.add_message(conversation_id, user_message)

        # Retrieve context
        search_query = SearchQuery(
            query_text=request.query, 
            tenant_id=request.tenant_id, 
            top_k=request.top_k
        )
        search_results = await self.retrieval_service.search(search_query)

        # Build context from results
        sources = []
        citations = []
        context_str = ""
        for i, res in enumerate(search_results):
            sources.append({
                "entity_id": res.document_id,
                "score": res.score,
                "snippet": res.text_content,
                "source": res.citation.get("source", "Unknown") if res.citation else "Unknown",
            })
            citations.append(res.document_id)
            context_str += f"[{i+1}] Source {res.document_id}: {res.text_content}\n"

        # Create assistant response
        formatted_sources = "\n".join([f"[{i+1}] {s['source']}" for i, s in enumerate(sources)])
        assistant_content = f"Based on {len(search_results)} sources: [Grounded answer for: {request.query}]\n\nSources:\n{formatted_sources}"
        
        assistant_message = ChatMessage(
            role="assistant", 
            content=assistant_content,
            citations=citations
        )
        self.conversation_manager.add_message(conversation_id, assistant_message)

        return ChatResponse(
            conversation_id=conversation_id,
            message=assistant_message,
            sources=sources if request.include_sources else []
        )

    async def stream_chat(self, request: ChatRequest) -> AsyncGenerator[ChatResponse, None]:
        # Simple simulation of streaming by yielding chunks
        full_response = await self.chat(request)
        words = full_response.message.content.split(" ")
        
        chunk_content = ""
        for word in words:
            chunk_content += word + " "
            chunk_message = ChatMessage(
                id=full_response.message.id,
                role=full_response.message.role,
                content=chunk_content.strip(),
                citations=full_response.message.citations,
                timestamp=full_response.message.timestamp
            )
            yield ChatResponse(
                conversation_id=full_response.conversation_id,
                message=chunk_message,
                sources=full_response.sources
            )
            await asyncio.sleep(0.05)
