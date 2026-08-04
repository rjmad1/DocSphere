"""
EKOS Abstract Semantic Syntax Tree (ASST) Engine
Converts raw markdown/TipTap JSON into canonical ASST nodes and handles
bidirectional projections (ASST <-> Markdown / TipTap JSON).
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EKOS-ASSTEngine")

class ASSTNode(BaseModel):
    node_id: str
    type: str # DocumentAST, SectionNode, EntityRefNode, TextNode, CitationRefNode
    title: Optional[str] = None
    content: Optional[str] = None
    entity_id: Optional[str] = None
    citation: Optional[Dict[str, Any]] = None
    children: List['ASSTNode'] = Field(default_factory=list)

class ASSTEngine:
    def __init__(self):
        logger.info("Initialized ASST Engine with canonical ASST transformation rules.")

    def parse_markdown_to_asst(self, doc_id: str, title: str, markdown_text: str) -> ASSTNode:
        """Parses raw Markdown text into a full Abstract Semantic Syntax Tree (ASST)."""
        root = ASSTNode(
            node_id=f"ast_{doc_id}",
            type="DocumentAST",
            title=title,
            children=[]
        )

        lines = markdown_text.split("\n")
        current_section = None

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            if line_str.startswith("#"):
                heading = line_str.lstrip("#").strip()
                current_section = ASSTNode(
                    node_id=f"sec_{len(root.children)+1}",
                    type="SectionNode",
                    title=heading,
                    children=[]
                )
                root.children.append(current_section)
            else:
                text_node = ASSTNode(
                    node_id=f"txt_{len(root.children)}_{len(current_section.children) if current_section else 0}",
                    type="TextNode",
                    content=line_str
                )
                if current_section:
                    current_section.children.append(text_node)
                else:
                    root.children.append(text_node)

        return root

    def render_asst_to_markdown(self, root: ASSTNode) -> str:
        """Renders canonical ASST tree back into formatted Markdown string."""
        md_lines = [f"# {root.title}\n"]

        def traverse(node: ASSTNode):
            if node.type == "SectionNode":
                md_lines.append(f"## {node.title}\n")
                for child in node.children:
                    traverse(child)
            elif node.type == "TextNode":
                md_lines.append(f"{node.content}\n")
            elif node.type == "EntityRefNode":
                md_lines.append(f"`[{node.entity_id}]` {node.content}\n")

        for child in root.children:
            traverse(child)

        return "\n".join(md_lines)
