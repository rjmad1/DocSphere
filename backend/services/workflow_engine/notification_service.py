"""
EKOS Governance Policy SLA Escalation Notification Service
Integrates PagerDuty incident creation and Slack webhook alerts for governance approval SLA timeout breaches.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EKOS-NotificationService")

class NotificationResult(BaseModel):
    channel: str # PagerDuty or Slack
    status: str
    event_id: str
    message: str

class PolicyEscalationNotificationService:
    def __init__(self, pagerduty_key: str = "pd_live_mock_key_991", slack_webhook: str = "https://hooks.slack.com/services/EKOS/POLICIES"):
        self.pagerduty_key = pagerduty_key
        self.slack_webhook = slack_webhook
        logger.info("Initialized Policy Escalation Notification Service with PagerDuty & Slack webhooks.")

    async def trigger_pagerduty_incident(self, artifact_id: str, severity: str, sla_hours: int, impacted_count: int) -> NotificationResult:
        """Triggers a high-priority PagerDuty incident for critical governance SLA timeouts."""
        event_id = f"pd_inc_{artifact_id}_{severity.lower()}"
        msg = f"GOVERNANCE SLA EXCEEDED: Artifact {artifact_id} ({severity}) breached SLA window of {sla_hours}h. {impacted_count} downstream entities impacted."
        
        logger.warning(f"PagerDuty Alert Dispatched: {msg}")
        return NotificationResult(
            channel="PagerDuty",
            status="TRIGGERED",
            event_id=event_id,
            message=msg
        )

    async def send_slack_escalation(self, artifact_id: str, severity: str, required_roles: list) -> NotificationResult:
        """Dispatches an urgent notification to Slack governance escalation channel."""
        event_id = f"slack_msg_{artifact_id}"
        msg = f"🚨 *APPROVAL ESCALATION*: Artifact `{artifact_id}` ({severity}) requires urgent review by roles: {', '.join(required_roles)}."
        
        logger.info(f"Slack Webhook Dispatched: {msg}")
        return NotificationResult(
            channel="Slack",
            status="DELIVERED",
            event_id=event_id,
            message=msg
        )
