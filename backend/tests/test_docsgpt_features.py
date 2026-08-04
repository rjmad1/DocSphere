"""
EKOS Extended Feature Tests — DocsGPT-equivalent Capabilities
Integration tests for chat, crawling, voice, widgets, channels, prompts,
agent builder, API keys, analytics, and export/sharing endpoints.
"""

import unittest
from fastapi.testclient import TestClient
from backend.main import app


class TestChatEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_chat_message(self):
        payload = {
            "query": "What is enterprise architecture?",
            "tenant_id": "test-tenant",
            "top_k": 3,
            "include_sources": True,
        }
        response = self.client.post("/api/v1/chat/message", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("conversation_id", data)
        self.assertIn("message", data)
        self.assertIn("sources", data)

    def test_chat_with_existing_conversation(self):
        # Create first message
        payload = {"query": "Hello", "tenant_id": "test-tenant"}
        resp1 = self.client.post("/api/v1/chat/message", json=payload)
        conv_id = resp1.json()["conversation_id"]

        # Follow-up in same conversation
        payload2 = {
            "conversation_id": conv_id,
            "query": "Tell me more",
            "tenant_id": "test-tenant",
        }
        resp2 = self.client.post("/api/v1/chat/message", json=payload2)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.json()["conversation_id"], conv_id)

    def test_list_conversations(self):
        response = self.client.get("/api/v1/chat/conversations?tenant_id=test-tenant")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_get_conversation_not_found(self):
        response = self.client.get("/api/v1/chat/conversations/nonexistent-id")
        self.assertEqual(response.status_code, 404)

    def test_delete_conversation_not_found(self):
        response = self.client.delete("/api/v1/chat/conversations/nonexistent-id")
        self.assertEqual(response.status_code, 404)


class TestVoiceEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_voice_input(self):
        payload = {
            "audio_data": "dGVzdCBhdWRpbyBkYXRh",
            "format": "MP3",
            "tenant_id": "test-tenant",
        }
        response = self.client.post("/api/v1/chat/voice", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("transcript", data)
        self.assertIn("confidence", data)


class TestCrawlEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_crawl_single_page(self):
        payload = {
            "url": "https://example.com",
            "crawl_type": "SINGLE_PAGE",
            "max_pages": 1,
            "tenant_id": "test-tenant",
        }
        response = self.client.post("/api/v1/crawl", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("pages_crawled", data)
        self.assertEqual(data["status"], "SUCCESS")

    def test_crawl_sitemap(self):
        payload = {
            "url": "https://example.com/sitemap.xml",
            "crawl_type": "SITEMAP",
            "max_pages": 10,
            "tenant_id": "test-tenant",
        }
        response = self.client.post("/api/v1/crawl", json=payload)
        self.assertEqual(response.status_code, 200)


class TestWidgetEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_create_widget(self):
        payload = {
            "name": "Test Widget",
            "tenant_id": "test-tenant",
            "theme": "DARK",
            "greeting_message": "Hi there!",
        }
        response = self.client.post("/api/v1/widgets", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("widget_id", data)
        self.assertEqual(data["name"], "Test Widget")

    def test_list_widgets(self):
        response = self.client.get("/api/v1/widgets?tenant_id=test-tenant")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_get_widget_not_found(self):
        response = self.client.get("/api/v1/widgets/nonexistent-id")
        self.assertEqual(response.status_code, 404)

    def test_widget_embed_snippet(self):
        # Create widget first
        create_resp = self.client.post("/api/v1/widgets", json={
            "name": "Embed Test",
            "tenant_id": "test-tenant",
        })
        widget_id = create_resp.json()["widget_id"]

        response = self.client.get(f"/api/v1/widgets/{widget_id}/embed")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("script_tag", data)
        self.assertIn("react_component", data)


class TestChannelEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_slack_webhook(self):
        payload = {
            "type": "event_callback",
            "event": {
                "type": "message",
                "text": "What is EKOS?",
                "user": "U12345",
                "channel": "C12345",
                "ts": "1234567890.123456",
            },
        }
        response = self.client.post("/api/v1/channels/SLACK/webhook", json=payload)
        self.assertEqual(response.status_code, 200)

    def test_unsupported_channel(self):
        response = self.client.post(
            "/api/v1/channels/UNSUPPORTED/webhook", json={"test": True}
        )
        self.assertEqual(response.status_code, 400)


class TestPromptEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_list_prompts(self):
        response = self.client.get("/api/v1/prompts")
        self.assertEqual(response.status_code, 200)
        prompts = response.json()
        self.assertIsInstance(prompts, list)
        # Should have default templates
        self.assertGreater(len(prompts), 0)

    def test_create_prompt(self):
        payload = {
            "name": "Custom QA",
            "category": "QA",
            "system_prompt": "You are {{ assistant_name }}. Answer: {{ query }}",
            "description": "Custom QA prompt",
            "variables": ["assistant_name", "query"],
            "tenant_id": "test-tenant",
        }
        response = self.client.post("/api/v1/prompts", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Custom QA")

    def test_get_prompt_not_found(self):
        response = self.client.get("/api/v1/prompts/nonexistent-id")
        self.assertEqual(response.status_code, 404)


class TestAgentBuilderEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_create_agent(self):
        payload = {
            "name": "Support Bot",
            "description": "Technical support agent",
            "persona": "Helpful technical support specialist",
            "tenant_id": "test-tenant",
        }
        response = self.client.post("/api/v1/agents/builder", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Support Bot")

    def test_list_agents(self):
        response = self.client.get("/api/v1/agents/builder?tenant_id=test-tenant")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_list_tools(self):
        response = self.client.get("/api/v1/agents/tools")
        self.assertEqual(response.status_code, 200)
        tools = response.json()
        self.assertIsInstance(tools, list)
        # Should have built-in tools
        self.assertGreater(len(tools), 0)


class TestApiKeyEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_create_api_key(self):
        response = self.client.post(
            "/api/v1/keys?tenant_id=test-tenant&rate_limit=100"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("raw_key", data)
        self.assertIn("key_prefix", data)

    def test_list_api_keys(self):
        response = self.client.get("/api/v1/keys?tenant_id=test-tenant")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_revoke_key_not_found(self):
        response = self.client.delete("/api/v1/keys/nonexistent-id")
        self.assertEqual(response.status_code, 404)


class TestAnalyticsEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_submit_feedback(self):
        payload = {
            "conversation_id": "conv-001",
            "message_id": "msg-001",
            "rating": "THUMBS_UP",
            "comment": "Great answer!",
            "tenant_id": "test-tenant",
        }
        response = self.client.post("/api/v1/analytics/feedback", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["rating"], "THUMBS_UP")

    def test_get_analytics_summary(self):
        response = self.client.get(
            "/api/v1/analytics/summary?tenant_id=test-tenant&period=7d"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_queries", data)

    def test_list_feedback(self):
        response = self.client.get("/api/v1/analytics/feedback?tenant_id=test-tenant")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_popular_queries(self):
        response = self.client.get("/api/v1/analytics/popular?tenant_id=test-tenant")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_export_analytics(self):
        response = self.client.get("/api/v1/analytics/export?tenant_id=test-tenant")
        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.json())


class TestExportEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_create_share_link(self):
        response = self.client.post("/api/v1/share?conversation_id=conv-001")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("id", data)
        self.assertIn("access_token", data)

    def test_get_shared_not_found(self):
        response = self.client.get(
            "/api/v1/share/nonexistent?access_token=bad-token"
        )
        self.assertEqual(response.status_code, 404)

    def test_revoke_share_not_found(self):
        response = self.client.delete("/api/v1/share/nonexistent")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
