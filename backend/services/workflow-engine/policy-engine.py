"""
EKOS Policy Engine - Governance & Approval Workflow
Evaluates document and artifact changes against dynamic approval routing policies,
computing risk scores, SLA timers, and escalation pathways.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EKOS-PolicyEngine")

class ApprovalRequest(BaseModel):
    artifact_id: str
    artifact_type: str  # BRD, FRS, ADR, SolutionDesign
    change_severity: str  # MINOR, MAJOR, BREAKING
    risk_score: float = Field(..., ge=0.0, le=1.0)
    impacted_entity_count: int
    author_id: str

class ApprovalChain(BaseModel):
    artifact_id: str
    required_roles: List[str]
    escalation_pathway: List[str]
    sla_hours: int
    auto_escalate: bool = True

class PolicyEngineService:
    def __init__(self):
        logger.info("Initialized PolicyEngineService with canonical governance rules.")

    def evaluate_approval_chain(self, request: ApprovalRequest) -> ApprovalChain:
        """Determines approval chain based on risk score, change severity, and entity impact."""
        logger.info(f"Evaluating approval policy for {request.artifact_id} ({request.artifact_type}) - Severity: {request.change_severity}")
        
        required_roles = ["Steward"]
        sla_hours = 24

        if request.change_severity == "BREAKING" or request.risk_score > 0.7:
            required_roles.extend(["Lead Enterprise Architect", "Security Officer", "Business Owner"])
            sla_hours = 8
        elif request.change_severity == "MAJOR" or request.risk_score > 0.4:
            required_roles.extend(["Lead Architect", "Business Analyst Lead"])
            sla_hours = 12

        return ApprovalChain(
            artifact_id=request.artifact_id,
            required_roles=required_roles,
            escalation_pathway=["Lead Architect", "Chief of Staff Agent", "Human Program Director"],
            sla_hours=sla_hours,
            auto_escalate=True
        )
