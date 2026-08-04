"""
EKOS Document Parser & Ingestion Pipeline
Parses raw text, Markdown, and PDF document chunks into structured sections,
extracting canonical entities, headers, citations, and confidence scores.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EKOS-DocumentParser")

class ParsedChunk(BaseModel):
    chunk_id: str
    document_id: str
    section_heading: str
    text_content: str
    page_number: int
    character_offset: int
    detected_entities: List[str]
    confidence_score: float

class DocumentParser:
    def __init__(self):
        self.entity_pattern = re.compile(r'\b(?:REQ|CAP|ADR|SYS|FRS|RSK|TC|DOC|DOM)-\w+\b')

    def parse_text_content(self, document_id: str, raw_text: str, page_number: int = 1) -> List[ParsedChunk]:
        """Parses raw text content line-by-line into structured chunks with entity extraction."""
        logger.info(f"Parsing document '{document_id}' (Length: {len(raw_text)} chars)")
        chunks = []
        
        lines = raw_text.split("\n")
        current_heading = "General"
        buffer_text = []
        offset = 0
        chunk_idx = 1

        def flush_buffer():
            nonlocal chunk_idx, offset, buffer_text
            if not buffer_text:
                return
            combined_text = " ".join(buffer_text).strip()
            if not combined_text:
                return
            
            entities = list(set(self.entity_pattern.findall(combined_text)))
            chunks.append(ParsedChunk(
                chunk_id=f"chk_{document_id}_{chunk_idx}",
                document_id=document_id,
                section_heading=current_heading,
                text_content=combined_text,
                page_number=page_number,
                character_offset=offset,
                detected_entities=entities,
                confidence_score=0.95 if entities else 0.85
            ))
            chunk_idx += 1
            offset += len(combined_text)
            buffer_text = []

        for line in lines:
            line_str = line.strip()
            if not line_str:
                flush_buffer()
                continue

            if line_str.startswith("#"):
                flush_buffer()
                current_heading = line_str.lstrip("#").strip()
            else:
                buffer_text.append(line_str)

        flush_buffer()
        logger.info(f"Extracted {len(chunks)} parsed chunks from '{document_id}'")
        return chunks
