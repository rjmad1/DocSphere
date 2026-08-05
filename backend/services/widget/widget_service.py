import uuid
from typing import Dict, List, Optional
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger("EKOS-WidgetService")

class WidgetTheme(str, Enum):
    LIGHT = "LIGHT"
    DARK = "DARK"

class WidgetSize(str, Enum):
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"

class WidgetPosition(str, Enum):
    BOTTOM_RIGHT = "BOTTOM_RIGHT"
    BOTTOM_LEFT = "BOTTOM_LEFT"
    TOP_RIGHT = "TOP_RIGHT"
    TOP_LEFT = "TOP_LEFT"

class WidgetConfig(BaseModel):
    widget_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    tenant_id: str
    agent_id: Optional[str] = None
    theme: WidgetTheme = WidgetTheme.DARK
    primary_color: str = '#6366f1'
    logo_url: Optional[str] = None
    greeting_message: str = 'Hello! How can I help you?'
    placeholder_text: str = 'Ask a question...'
    position: WidgetPosition = WidgetPosition.BOTTOM_RIGHT
    size: WidgetSize = WidgetSize.MEDIUM
    allowed_domains: List[str] = Field(default_factory=list)
    api_key: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

class EmbedSnippet(BaseModel):
    widget_id: str
    script_tag: str
    react_component: str

class WidgetService:
    """Service to manage embeddable chat and search widgets."""
    
    def __init__(self):
        self._widgets: Dict[str, WidgetConfig] = {}
        logger.info("WidgetService initialized")

    def create_widget(self, config: WidgetConfig) -> WidgetConfig:
        self._widgets[config.widget_id] = config
        logger.info(f"Created widget {config.widget_id} for tenant {config.tenant_id}")
        return config

    def get_widget(self, widget_id: str) -> Optional[WidgetConfig]:
        return self._widgets.get(widget_id)

    def update_widget(self, widget_id: str, updates: Dict) -> Optional[WidgetConfig]:
        if widget_id not in self._widgets:
            return None
        
        current = self._widgets[widget_id].model_dump()
        current.update(updates)
        updated_config = WidgetConfig(**current)
        self._widgets[widget_id] = updated_config
        return updated_config

    def delete_widget(self, widget_id: str) -> bool:
        if widget_id in self._widgets:
            del self._widgets[widget_id]
            return True
        return False

    def list_widgets(self, tenant_id: str) -> List[WidgetConfig]:
        return [w for w in self._widgets.values() if w.tenant_id == tenant_id]

    def generate_embed_snippet(self, widget_id: str, base_url: str = 'https://api.docsphere.io') -> Optional[EmbedSnippet]:
        if widget_id not in self._widgets:
            return None
            
        script_tag = f'<script src="{base_url}/embed/widget.js" data-widget-id="{widget_id}"></script>'
        react_component = f'''import {{ ChatWidget }} from "@docsphere/widget";

export default function App() {{
  return <ChatWidget widgetId="{widget_id}" apiEndpoint="{base_url}" />;
}}'''
        
        return EmbedSnippet(
            widget_id=widget_id,
            script_tag=script_tag,
            react_component=react_component
        )

    def validate_domain(self, widget_id: str, origin: str) -> bool:
        widget = self.get_widget(widget_id)
        if not widget:
            return False
        if not widget.allowed_domains:
            return True
        return origin in widget.allowed_domains
