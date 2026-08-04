"""
EKOS Centralized Prompt Management Engine
Renders, versions, and evaluates Jinja2 prompt templates with dynamic context injection
and safety guardrails.
"""

from typing import Dict, Any
from jinja2 import Template
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EKOS-PromptManager")

class PromptManager:
    def __init__(self):
        self._templates: Dict[str, str] = {
            "document_planning": """
            You are the Document Planner Agent for EKOS.
            Project Title: {{ project_title }}
            Target Template: {{ template_type }}
            Available Entities: {{ entity_ids | join(', ') }}
            
            Formulate a structured section execution plan ensuring 100% citation coverage.
            """,
            "requirement_extraction": """
            Extract all business and technical requirements from the text below:
            Source Document: {{ source_doc }}
            Context Chunk: {{ text_chunk }}
            
            Return JSON matching the Canonical Ontology BusinessRequirement schema.
            """
        }

    def render_prompt(self, template_name: str, context: Dict[str, Any]) -> str:
        if template_name not in self._templates:
            raise KeyError(f"Prompt template '{template_name}' not registered in PromptManager.")
        
        template = Template(self._templates[template_name])
        rendered = template.render(**context)
        logger.info(f"Rendered prompt template '{template_name}' successfully.")
        return rendered.strip()
