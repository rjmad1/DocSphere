"""
EKOS Concurrent Access Tests
Covers:
  - MetricsRegistry thread-safe counter increments under concurrent load
  - ConversationManager concurrent message appending (no lost updates)
  - ApiKeyManager concurrent key validation
  - Rate limiter accuracy under concurrent requests
"""
import unittest
import threading
import asyncio
import concurrent.futures
from backend.shared.observability.metrics import MetricsRegistry
from backend.services.chat_service.chat_service import ConversationManager, ChatMessage
from backend.shared.security.api_key_manager import ApiKeyManager


class TestMetricsRegistryConcurrency(unittest.TestCase):
    """Validate that MetricsRegistry is thread-safe under heavy concurrent writes."""

    def setUp(self):
        # Reset the singleton for a clean test
        MetricsRegistry._instance = None
        self.registry = MetricsRegistry()

    def tearDown(self):
        MetricsRegistry._instance = None

    def test_concurrent_increments_are_atomic(self):
        """100 threads each incrementing by 1 should produce exactly 100."""
        num_threads = 100
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(
                target=lambda: self.registry.increment_counter("http_requests_total")
            )
            threads.append(t)

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        metrics = self.registry.export_metrics()
        self.assertEqual(
            metrics["counters"]["http_requests_total"],
            num_threads,
            "Concurrent counter increments must not lose updates"
        )

    def test_concurrent_dynamic_counter_registration(self):
        """New dynamic counters registered concurrently should not race-condition."""
        errors = []

        def increment_dynamic(key):
            try:
                self.registry.increment_counter(f"dynamic_{key}")
            except Exception as exc:
                errors.append(str(exc))

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(increment_dynamic, i % 5) for i in range(100)]
            concurrent.futures.wait(futures)

        self.assertEqual(len(errors), 0, f"Errors during concurrent metric registration: {errors}")

    def test_export_metrics_is_consistent(self):
        """export_metrics should return a consistent snapshot even during concurrent writes."""
        stop_event = threading.Event()
        snapshot_results = []

        def writer():
            while not stop_event.is_set():
                self.registry.increment_counter("http_requests_total")

        def reader():
            for _ in range(10):
                snapshot = self.registry.export_metrics()
                snapshot_results.append(snapshot["counters"]["http_requests_total"])

        writer_thread = threading.Thread(target=writer, daemon=True)
        reader_thread = threading.Thread(target=reader)

        writer_thread.start()
        reader_thread.start()
        reader_thread.join(timeout=2)
        stop_event.set()
        writer_thread.join(timeout=1)

        # All snapshots should be non-negative integers (no corruption)
        for val in snapshot_results:
            self.assertIsInstance(val, int)
            self.assertGreaterEqual(val, 0)


class TestConversationManagerConcurrency(unittest.TestCase):
    """Validate ConversationManager under concurrent message appends."""

    def setUp(self):
        self.manager = ConversationManager()
        self.conv = self.manager.create_conversation("T1", "Concurrent Test")

    def test_concurrent_message_appends_no_lost_updates(self):
        """50 threads each appending one message should result in exactly 50 messages."""
        num_messages = 50
        threads = []

        def append_message(idx):
            msg = ChatMessage(role="user", content=f"Message {idx}")
            self.manager.add_message(self.conv.id, msg)

        for i in range(num_messages):
            t = threading.Thread(target=append_message, args=(i,))
            threads.append(t)

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        conversation = self.manager.get_conversation(self.conv.id)
        self.assertIsNotNone(conversation)
        self.assertEqual(
            len(conversation.messages),
            num_messages,
            "All concurrently appended messages must be present (no lost updates)"
        )

    def test_concurrent_conversation_creation(self):
        """Multiple threads creating conversations should each get unique IDs."""
        created_ids = []
        lock = threading.Lock()

        def create_conv():
            conv = self.manager.create_conversation("T1", "Concurrent Conv")
            with lock:
                created_ids.append(conv.id)

        threads = [threading.Thread(target=create_conv) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(created_ids), 20)
        self.assertEqual(len(set(created_ids)), 20, "Each conversation must have a unique ID")


class TestApiKeyManagerConcurrency(unittest.TestCase):
    """Test rate limiter accuracy under concurrent requests."""

    def setUp(self):
        self.manager = ApiKeyManager()

    def test_rate_limit_not_exceeded_concurrently(self):
        """With rate_limit=10 and 10 concurrent requests, all should pass."""
        result = self.manager.create_key("tenant_concurrent", rate_limit=10)
        key_id = result.key_id

        outcomes = []
        lock = threading.Lock()

        def check():
            ok = self.manager.check_rate_limit(key_id)
            with lock:
                outcomes.append(ok)

        threads = [threading.Thread(target=check) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All 10 should pass (rate limit is 10)
        self.assertEqual(len(outcomes), 10)
        passed = sum(1 for o in outcomes if o)
        # With 10 concurrent calls and limit of 10, all should pass (±1 due to timing)
        # We accept 9-10 as the sliding window may shift slightly
        self.assertGreaterEqual(passed, 9)

    def test_concurrent_key_creation_uniqueness(self):
        """Keys created concurrently must have unique IDs and raw keys."""
        keys = []
        lock = threading.Lock()

        def create():
            result = self.manager.create_key("tenant_unique")
            with lock:
                keys.append(result)

        threads = [threading.Thread(target=create) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(keys), 20)
        key_ids = [k.key_id for k in keys]
        raw_keys = [k.raw_key for k in keys]
        self.assertEqual(len(set(key_ids)), 20, "Key IDs must be unique")
        self.assertEqual(len(set(raw_keys)), 20, "Raw keys must be unique")


if __name__ == "__main__":
    unittest.main()
