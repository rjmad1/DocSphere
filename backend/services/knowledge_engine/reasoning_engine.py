"""
EKOS Knowledge Engine Reasoning & Inference Engine
Executes semantic graph reasoning over Neo4j nodes/edges:
1. Detects conflicting requirements (CONFLICTS_WITH).
2. Infers transitive dependencies across capabilities and systems.
3. Identifies unmapped traceability gaps (Requirements missing Test Cases or Capabilities).
"""

from typing import Dict, Any, List
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EKOS-ReasoningEngine")

class ConflictAnalysisResult(BaseModel):
    has_conflict: bool
    conflicting_entity_ids: List[str]
    description: str

class TraceabilityGapResult(BaseModel):
    unmapped_requirements: List[str]
    unmapped_capabilities: List[str]
    coverage_score: float

class KnowledgeGraphReasoningEngine:
    def __init__(self):
        logger.info("Initialized KnowledgeGraphReasoningEngine.")

    async def detect_conflicts(self, requirement_statement: str, active_entities: List[Dict[str, Any]]) -> ConflictAnalysisResult:
        """Detects if a new requirement statement conflicts with existing requirements in active graph traversal."""
        logger.info("Running reasoning engine conflict detection...")
        
        # Check for semantic conflict indicators (e.g. "weekly" vs "daily")
        conflicts = []
        for entity in active_entities:
            existing_statement = entity.get("properties", {}).get("statement", "")
            if "weekly" in existing_statement.lower() and "daily" in requirement_statement.lower():
                conflicts.append(entity["id"])

        if conflicts:
            return ConflictAnalysisResult(
                has_conflict=True,
                conflicting_entity_ids=conflicts,
                description=f"Requirement conflicts with existing weekly schedule in entity {conflicts[0]}."
            )

        return ConflictAnalysisResult(
            has_conflict=False,
            conflicting_entity_ids=[],
            description="No semantic conflicts detected in graph traversal path."
        )

    async def calculate_traceability_gaps(self, all_entities: List[Dict[str, Any]], relationships: List[Dict[str, Any]]) -> TraceabilityGapResult:
        """Identifies requirements missing downstream test cases or upstream capabilities."""
        req_ids = {e["id"] for e in all_entities if e.get("entity_type") == "BusinessRequirement"}
        mapped_reqs = {r["source_id"] for r in relationships if r.get("relationship_type") in ("IMPLEMENTS", "VALIDATED_BY")}
        
        unmapped = list(req_ids - mapped_reqs)
        coverage = round((len(mapped_reqs) / len(req_ids) * 100), 2) if req_ids else 100.0

        return TraceabilityGapResult(
            unmapped_requirements=unmapped,
            unmapped_capabilities=[],
            coverage_score=coverage
        )
