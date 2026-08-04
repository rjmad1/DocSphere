import logging
import uuid
import json
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

try:
    import backend.shared.observability.metrics.metrics as metrics
except ImportError:
    # Mock fallback for standalone testing if metrics module doesn't exist yet
    class MockMetrics:
        def increment_counter(self, name: str, value: int = 1, tags: Dict = None):
            pass
    metrics = MockMetrics()

logger = logging.getLogger("EKOS-AnalyticsService")

class FeedbackRating(str, Enum):
    """Ratings for user feedback."""
    THUMBS_UP = "THUMBS_UP"
    THUMBS_DOWN = "THUMBS_DOWN"

class FeedbackRecord(BaseModel):
    """Record of user feedback on a response."""
    feedback_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    message_id: str
    rating: FeedbackRating
    comment: Optional[str] = None
    tenant_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class QueryEvent(BaseModel):
    """Record of a search or chat query event."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    query_text: str
    response_length: int
    sources_count: int
    latency_ms: int
    model_used: str
    tokens_used: int = 0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AnalyticsSummary(BaseModel):
    """Aggregated analytics for a tenant."""
    tenant_id: str
    period: str
    total_queries: int
    avg_latency_ms: float
    positive_feedback_count: int
    negative_feedback_count: int
    top_queries: List[Dict[str, Any]]
    sources_hit_count: Dict[str, int]

class AnalyticsService:
    """Service for tracking usage analytics and user feedback."""
    
    def __init__(self):
        """Initialize the analytics service with in-memory storage."""
        self._events: List[QueryEvent] = []
        self._feedback: List[FeedbackRecord] = []
        logger.info("Initialized AnalyticsService.")

    def record_query(self, event: QueryEvent) -> None:
        """Record a query event and increment metrics."""
        self._events.append(event)
        
        tags = {"tenant_id": event.tenant_id, "model": event.model_used}
        if hasattr(metrics, 'increment_counter'):
            metrics.increment_counter("query_events_total", tags=tags)
        
        logger.debug(f"Recorded query event for tenant {event.tenant_id}")

    def record_feedback(self, feedback: FeedbackRecord) -> FeedbackRecord:
        """Record a user feedback on a response."""
        self._feedback.append(feedback)
        
        tags = {"tenant_id": feedback.tenant_id, "rating": feedback.rating.value}
        if hasattr(metrics, 'increment_counter'):
            metrics.increment_counter("feedback_events_total", tags=tags)
            
        logger.info(f"Recorded {feedback.rating} feedback for tenant {feedback.tenant_id}")
        return feedback

    def get_summary(self, tenant_id: str, period: str = '7d') -> AnalyticsSummary:
        """Get an aggregated analytics summary for a tenant."""
        # Note: Period parsing is mocked, assumes '7d' for placeholder logic
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)
        
        tenant_events = [e for e in self._events if e.tenant_id == tenant_id and e.timestamp >= cutoff_date]
        tenant_feedback = [f for f in self._feedback if f.tenant_id == tenant_id and f.created_at >= cutoff_date]
        
        total_queries = len(tenant_events)
        avg_latency = sum(e.latency_ms for e in tenant_events) / total_queries if total_queries > 0 else 0.0
        
        positive = sum(1 for f in tenant_feedback if f.rating == FeedbackRating.THUMBS_UP)
        negative = sum(1 for f in tenant_feedback if f.rating == FeedbackRating.THUMBS_DOWN)
        
        return AnalyticsSummary(
            tenant_id=tenant_id,
            period=period,
            total_queries=total_queries,
            avg_latency_ms=avg_latency,
            positive_feedback_count=positive,
            negative_feedback_count=negative,
            top_queries=self.get_popular_queries(tenant_id, limit=5),
            sources_hit_count={"doc_id_1": 42, "doc_id_2": 15}  # Simulated aggregation
        )

    def get_feedback(self, tenant_id: str, conversation_id: Optional[str] = None) -> List[FeedbackRecord]:
        """Retrieve feedback records for a tenant."""
        records = [f for f in self._feedback if f.tenant_id == tenant_id]
        if conversation_id:
            records = [f for f in records if f.conversation_id == conversation_id]
        return records

    def get_popular_queries(self, tenant_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve the most popular queries for a tenant."""
        # Simple frequency count of exact matches
        query_counts: Dict[str, int] = {}
        for event in self._events:
            if event.tenant_id == tenant_id:
                query_counts[event.query_text] = query_counts.get(event.query_text, 0) + 1
                
        sorted_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"query": q, "count": c} for q, c in sorted_queries[:limit]]

    def export_analytics(self, tenant_id: str, format: str = 'json') -> str:
        """Export analytics data as a serialized string."""
        summary = self.get_summary(tenant_id)
        if format.lower() == 'json':
            return summary.model_dump_json(indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
