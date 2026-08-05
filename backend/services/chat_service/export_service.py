import uuid
import json
import csv
import io
from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field
import logging

from backend.services.chat_service.chat_service import ConversationManager, Conversation

logger = logging.getLogger("EKOS-ExportService")

class ExportFormat(str, Enum):
    """Supported export formats."""
    JSON = "json"
    MARKDOWN = "markdown"
    CSV = "csv"

class ExportRequest(BaseModel):
    """Request to export a conversation."""
    conversation_id: str
    format: ExportFormat
    include_metadata: bool = True

class ExportResult(BaseModel):
    """Result of an export request."""
    conversation_id: str
    format: ExportFormat
    content: str
    filename: str

class ShareLink(BaseModel):
    """Represents a shared link for a conversation."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    access_token: str = Field(default_factory=lambda: str(uuid.uuid4()))
    is_public: bool = False

class ExportService:
    """Service for exporting chat conversations."""
    def __init__(self, conversation_manager: ConversationManager):
        self.conversation_manager = conversation_manager
        logger.info("ExportService initialized")

    def export_conversation(self, request: ExportRequest) -> Optional[ExportResult]:
        conversation = self.conversation_manager.get_conversation(request.conversation_id)
        if not conversation:
            logger.error(f"Conversation {request.conversation_id} not found for export")
            return None

        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{conversation.id}_{timestamp_str}"
        content = ""

        if request.format == ExportFormat.JSON:
            conv_dict = conversation.model_dump()
            if not request.include_metadata:
                conv_dict.pop("tenant_id", None)
            content = json.dumps(conv_dict, indent=2, default=str)
            filename += ".json"
            
        elif request.format == ExportFormat.MARKDOWN:
            content += f"# {conversation.title}\n"
            if request.include_metadata:
                content += f"**ID:** {conversation.id}\n"
                content += f"**Created:** {conversation.created_at}\n\n"
                
            for msg in conversation.messages:
                content += f"### {msg.role.capitalize()} ({msg.timestamp})\n"
                content += f"{msg.content}\n\n"
            filename += ".md"
            
        elif request.format == ExportFormat.CSV:
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Timestamp", "Role", "Content"])
            for msg in conversation.messages:
                writer.writerow([msg.timestamp.isoformat(), msg.role, msg.content])
            content = output.getvalue()
            filename += ".csv"
            
        return ExportResult(
            conversation_id=conversation.id,
            format=request.format,
            content=content,
            filename=filename
        )

class ShareService:
    """Service for managing shared conversations."""
    def __init__(self):
        self._links: Dict[str, ShareLink] = {}
        self.conversation_manager = None  # To be injected if needed, or used directly if passed in get_shared_conversation
        logger.info("ShareService initialized")

    def create_share_link(self, conversation_id: str, expires_hours: Optional[int] = None, is_public: bool = False) -> ShareLink:
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_hours) if expires_hours else None
        link = ShareLink(
            conversation_id=conversation_id,
            expires_at=expires_at,
            is_public=is_public
        )
        self._links[link.id] = link
        return link

    def get_shared_conversation(self, link_id: str, access_token: str, conversation_manager: ConversationManager) -> Optional[Conversation]:
        link = self._links.get(link_id)
        if not link:
            return None

        if link.expires_at and datetime.now(timezone.utc) > link.expires_at:
            return None
            
        if not link.is_public and link.access_token != access_token:
            return None
            
        return conversation_manager.get_conversation(link.conversation_id)

    def revoke_link(self, link_id: str) -> bool:
        if link_id in self._links:
            del self._links[link_id]
            return True
        return False

    def list_links(self, conversation_id: Optional[str] = None) -> List[ShareLink]:
        if conversation_id:
            return [link for link in self._links.values() if link.conversation_id == conversation_id]
        return list(self._links.values())
