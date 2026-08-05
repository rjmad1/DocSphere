"""
EKOS Prometheus Metrics & Business Instrumentation
Tracks request latency, hybrid search execution times, LLM token usage, document section generation times, and approval SLAs.
"""

from typing import Dict, Any
import time
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EKOS-Metrics")

class MetricsRegistry:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking
                if cls._instance is None:
                    cls._instance = super(MetricsRegistry, cls).__new__(cls)
                    cls._instance._counters = {
                        "http_requests_total": 0,
                        "graph_queries_total": 0,
                        "vector_searches_total": 0,
                        "llm_tokens_consumed_total": 0,
                        "documents_generated_total": 0,
                        "approvals_evaluated_total": 0,
                        "chat_messages_total": 0,
                        "voice_inputs_total": 0,
                        "crawl_requests_total": 0,
                        "audio_ingestions_total": 0,
                        "feedback_submitted_total": 0,
                        "channel_events_total": 0,
                    }
                    cls._instance._latencies = {
                        "hybrid_search_ms": [],
                        "document_generation_ms": []
                    }
                    cls._instance._counter_lock = threading.Lock()
        return cls._instance

    def increment_counter(self, metric_name: str, value: int = 1):
        with self._counter_lock:
            if metric_name in self._counters:
                self._counters[metric_name] += value
            else:
                # Allow dynamic counter registration
                self._counters[metric_name] = value

    def record_latency(self, metric_name: str, latency_ms: float):
        with self._counter_lock:
            if metric_name in self._latencies:
                self._latencies[metric_name].append(latency_ms)

    def export_metrics(self) -> Dict[str, Any]:
        """Exports Prometheus-compatible metrics payload."""
        summary_latencies = {}
        for k, v in self._latencies.items():
            summary_latencies[f"{k}_avg"] = round(sum(v) / len(v), 2) if v else 0.0
            summary_latencies[f"{k}_count"] = len(v)

        return {
            "counters": dict(self._counters),
            "latencies": summary_latencies
        }

metrics = MetricsRegistry()
