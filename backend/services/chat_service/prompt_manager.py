import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

try:
    import jinja2
except ImportError:
    jinja2 = None

logger = logging.getLogger("EKOS-PromptManager")

class PromptCategory(str, Enum):
    """Categories for prompt templates."""
    SYSTEM = "SYSTEM"
    QA = "QA"
    SUMMARIZATION = "SUMMARIZATION"
    EXTRACTION = "EXTRACTION"
    CUSTOM = "CUSTOM"

class PromptTemplate(BaseModel):
    """Definition of a reusable prompt template."""
    template_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: PromptCategory
    system_prompt: str
    description: str
    variables: List[str] = Field(default_factory=list)
    tenant_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_default: bool = False

class RenderedPrompt(BaseModel):
    """Result of rendering a prompt template with context."""
    template_id: str
    rendered_content: str
    variables_used: Dict[str, str] = Field(default_factory=dict)

class PromptManager:
    """Service for managing and rendering prompt templates."""
    
    def __init__(self):
        """Initialize the prompt manager with default templates."""
        self._templates: Dict[str, PromptTemplate] = {}
        logger.info("Initializing PromptManager with default templates.")
        
        default_qa = PromptTemplate(
            name="default_qa",
            category=PromptCategory.QA,
            description="Default QA template with sources.",
            system_prompt=(
                "You are DocSphere, an enterprise knowledge assistant. Today is {{ system_date }}. "
                "Answer based on the following sources:\n"
                "{% for source in sources %}\n[{{ loop.index }}] {{ source }}\n{% endfor %}\n\n"
                "User question: {{ query }}"
            ),
            variables=["system_date", "sources", "query"],
            is_default=True
        )
        self._templates[default_qa.template_id] = default_qa
        
        technical_support = PromptTemplate(
            name="technical_support",
            category=PromptCategory.SYSTEM,
            description="Technical support persona.",
            system_prompt=(
                "You are a technical support specialist for {{ organization_name }}. "
                "Use the following documentation to provide accurate, step-by-step answers:\n"
                "{% for source in sources %}\n[{{ loop.index }}] {{ source }}\n{% endfor %}\n\n"
                "User query: {{ query }}"
            ),
            variables=["organization_name", "sources", "query"],
            is_default=True
        )
        self._templates[technical_support.template_id] = technical_support
        
        summarizer = PromptTemplate(
            name="summarizer",
            category=PromptCategory.SUMMARIZATION,
            description="Content summarizer.",
            system_prompt="Summarize the following content concisely:\n\n{{ content }}",
            variables=["content"],
            is_default=True
        )
        self._templates[summarizer.template_id] = summarizer

    def create_template(self, template: PromptTemplate) -> PromptTemplate:
        """Create a new prompt template."""
        self._templates[template.template_id] = template
        logger.info(f"Created template: {template.template_id}")
        return template

    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Retrieve a prompt template by ID."""
        return self._templates.get(template_id)

    def update_template(self, template_id: str, updates: Dict[str, Any]) -> Optional[PromptTemplate]:
        """Update an existing prompt template."""
        if template_id not in self._templates:
            return None
        
        template = self._templates[template_id]
        template_data = template.model_dump()
        template_data.update(updates)
        template_data["updated_at"] = datetime.now(timezone.utc)
        
        updated_template = PromptTemplate(**template_data)
        self._templates[template_id] = updated_template
        logger.info(f"Updated template: {template_id}")
        return updated_template

    def delete_template(self, template_id: str) -> bool:
        """Delete a prompt template."""
        if template_id in self._templates:
            del self._templates[template_id]
            logger.info(f"Deleted template: {template_id}")
            return True
        return False

    def list_templates(self, tenant_id: Optional[str] = None, category: Optional[PromptCategory] = None) -> List[PromptTemplate]:
        """List templates, optionally filtered by tenant and category."""
        templates = list(self._templates.values())
        if tenant_id:
            templates = [t for t in templates if t.tenant_id == tenant_id or t.is_default]
        if category:
            templates = [t for t in templates if t.category == category]
        return templates

    def render_prompt(self, template_id: str, context: Dict[str, Any]) -> RenderedPrompt:
        """Render a prompt template with the provided context."""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template with ID {template_id} not found.")
        
        rendered_content = ""
        variables_used = {k: str(v) for k, v in context.items() if k in template.variables}
        
        if jinja2:
            try:
                jinja_template = jinja2.Template(template.system_prompt)
                rendered_content = jinja_template.render(**context)
            except Exception as e:
                logger.error(f"Error rendering jinja2 template {template_id}: {e}")
                raise
        else:
            # Fallback to simple format if jinja2 is missing
            try:
                rendered_content = template.system_prompt.format(**context)
            except KeyError as e:
                logger.warning(f"Fallback formatting missed key {e} for template {template_id}")
                rendered_content = template.system_prompt
                
        logger.debug(f"Rendered prompt {template_id}")
        return RenderedPrompt(
            template_id=template_id,
            rendered_content=rendered_content,
            variables_used=variables_used
        )
