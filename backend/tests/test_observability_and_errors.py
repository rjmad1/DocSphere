import unittest
import asyncio
from backend.shared.observability.metrics import metrics
from backend.shared.observability.tracing import Tracer
from backend.shared.observability.health import DeepHealthCheckService
from backend.shared.middleware.error_handlers import EntityNotFoundError, PolicyViolationError

class TestObservabilityAndErrors(unittest.TestCase):
    def setUp(self):
        self.health_service = DeepHealthCheckService()

    def test_metrics_collection(self):
        metrics.increment_counter("http_requests_total", 5)
        metrics.record_latency("hybrid_search_ms", 120.5)
        exported = metrics.export_metrics()

        self.assertGreaterEqual(exported["counters"]["http_requests_total"], 5)
        self.assertIn("hybrid_search_ms_avg", exported["latencies"])

    def test_tracing_context(self):
        trace_id = Tracer.start_trace("TestService", "TestOperation")
        self.assertIsNotNone(trace_id)
        self.assertEqual(Tracer.get_current_trace_id(), trace_id)
        Tracer.end_trace(trace_id, status="OK")

    def test_deep_health_check(self):
        result = asyncio.run(self.health_service.check_all_services())
        self.assertEqual(result["status"], "UP")
        self.assertIn("neo4j_graph", result["components"])

    def test_domain_exceptions(self):
        err1 = EntityNotFoundError("REQ-99999")
        self.assertEqual(err1.status_code, 404)
        self.assertEqual(err1.code, "ENTITY_NOT_FOUND")

        err2 = PolicyViolationError("Missing required lead approval.")
        self.assertEqual(err2.status_code, 403)
        self.assertEqual(err2.code, "POLICY_VIOLATION")

if __name__ == "__main__":
    unittest.main()
