"""
EKOS OpenTelemetry Tracing & Context Propagation
Provides span management and trace ID propagation across microservice calls.
"""

import uuid
import contextvars
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EKOS-Tracing")

current_trace_id = contextvars.ContextVar("current_trace_id", default=None)

class Tracer:
    @staticmethod
    def start_trace(service_name: str, operation_name: str) -> str:
        trace_id = str(uuid.uuid4())
        current_trace_id.set(trace_id)
        logger.info(f"[TraceId: {trace_id}] Started Span: {service_name}.{operation_name}")
        return trace_id

    @staticmethod
    def get_current_trace_id() -> Optional[str]:
        return current_trace_id.get()

    @staticmethod
    def end_trace(trace_id: str, status: str = "OK"):
        logger.info(f"[TraceId: {trace_id}] Completed Span: Status={status}")
