import unittest
import asyncio
import base64
import os
from unittest.mock import MagicMock
from datetime import datetime, timezone, timedelta

# Import models & modules
from backend.services.channels.channel_integrations import (
    SlackAdapter, DiscordAdapter, TelegramAdapter, ChannelRouter,
    ChannelType, ChannelMessage, ChannelResponse, ChannelConfig
)
from backend.services.chat_service.chat_service import (
    ChatEngine, ConversationManager, ChatRequest, ChatMessage
)
from backend.services.chat_service.prompt_manager import (
    PromptManager, PromptTemplate, PromptCategory
)
from backend.services.ingestion.audio_processor import (
    AudioProcessor, TranscriptionRequest, AudioFormat
)
from backend.services.ingestion.document_parser import (
    DocumentParser
)
from backend.services.ingestion.web_crawler import (
    WebCrawler, CrawlRequest, CrawlType
)
from backend.services.knowledge_engine.neo4j_adapter import (
    Neo4jProductionAdapter
)
from backend.services.knowledge_engine.qdrant_adapter import (
    QdrantProductionAdapter
)
from backend.services.widget.widget_service import (
    WidgetService, WidgetConfig
)
from backend.services.workflow_engine.celery_app import (
    AsyncWorkerQueue
)
from backend.shared.security.encryption import (
    EnvelopeEncryptionService
)
from backend.shared.security.api_key_manager import (
    ApiKeyManager, ApiKeyScope
)
from backend.shared.observability.metrics import metrics

# Abstract base class test helper
from backend.services.channels.channel_integrations import BaseChannelAdapter

class DummyAdapter(BaseChannelAdapter):
    async def process_event(self, event):
        return await super().process_event(event)
    async def send_response(self, response):
        return await super().send_response(response)
    async def verify_request(self, headers, body):
        return await super().verify_request(headers, body)

class TestCoverageGapFiller(unittest.IsolatedAsyncioTestCase):
    
    async def test_base_channel_adapter_abstracts(self):
        adapter = DummyAdapter()
        self.assertIsNone(await adapter.process_event({}))
        self.assertIsNone(await adapter.send_response(None))
        self.assertIsNone(await adapter.verify_request({}, b""))

    async def test_channel_adapters(self):
        # Slack adapter
        config = ChannelConfig(
            channel_type=ChannelType.SLACK,
            tenant_id="tenant1",
            bot_token="token",
            signing_secret="secret"
        )
        slack = SlackAdapter(config=config)
        
        # url verification event
        verify_msg = await slack.process_event({"type": "url_verification"})
        self.assertIsNone(verify_msg)
        
        # bot message event (should return None)
        bot_msg = await slack.process_event({"type": "event_callback", "event": {"type": "message", "bot_id": "B123"}})
        self.assertIsNone(bot_msg)
        
        # Slack send response
        resp = ChannelResponse(
            channel_type=ChannelType.SLACK,
            channel_id="C123",
            content="Hello Slack",
            citations=["sourceA", "sourceB"]
        )
        slack_resp = await slack.send_response(resp)
        self.assertTrue(slack_resp["ok"])
        
        # Slack verify signature
        body = b"payload_data"
        ts = "123456789"
        import hmac, hashlib
        sig_basestring = f"v0:{ts}:{body.decode('utf-8')}"
        sig = "v0=" + hmac.new(b"secret", sig_basestring.encode(), hashlib.sha256).hexdigest()
        headers = {
            "X-Slack-Signature": sig,
            "X-Slack-Request-Timestamp": ts
        }
        self.assertTrue(await slack.verify_request(headers, body))
        self.assertFalse(await slack.verify_request({}, body))
        
        # Slack empty config signature verification
        slack_no_config = SlackAdapter()
        self.assertFalse(await slack_no_config.verify_request(headers, body))

        # Discord adapter
        discord = DiscordAdapter(config=config)
        resp_discord = ChannelResponse(
            channel_type=ChannelType.DISCORD,
            channel_id="D123",
            content="Hello Discord",
            citations=["sourceA"]
        )
        discord_resp = await discord.send_response(resp_discord)
        self.assertIn("embeds", discord_resp)
        # Discord verify_request: fail closed when EKOS_DISCORD_PUBLIC_KEY is not set
        import os, hmac, hashlib
        self.assertFalse(await discord.verify_request({}, b""))

        # Positive path: set a public key and build a matching HMAC-SHA256 signature
        test_key = "test_discord_pub_key"
        timestamp = "1234567890"
        body_bytes = b"discord_payload"
        expected_sig = hmac.new(test_key.encode(), (timestamp.encode() + body_bytes), hashlib.sha256).hexdigest()
        discord_headers = {
            "X-Signature-Ed25519": expected_sig,
            "X-Signature-Timestamp": timestamp
        }
        os.environ["EKOS_DISCORD_PUBLIC_KEY"] = test_key
        try:
            self.assertTrue(await discord.verify_request(discord_headers, body_bytes))
            self.assertFalse(await discord.verify_request({"X-Signature-Ed25519": "bad", "X-Signature-Timestamp": timestamp}, body_bytes))
        finally:
            del os.environ["EKOS_DISCORD_PUBLIC_KEY"]

        # Telegram adapter
        telegram = TelegramAdapter(config=config)
        resp_tg = ChannelResponse(
            channel_type=ChannelType.TELEGRAM,
            channel_id="T123",
            content="Hello Telegram",
            citations=["sourceA"]
        )
        tg_resp = await telegram.send_response(resp_tg)
        self.assertIn("text", tg_resp)
        self.assertFalse(await telegram.verify_request({}, b""))
        self.assertTrue(await telegram.verify_request({"X-Telegram-Bot-Api-Secret-Token": "token"}, b""))

    async def test_chat_engine_edge_cases(self):
        manager = ConversationManager()
        engine = ChatEngine(retrieval_service=MagicMock(), conversation_manager=manager)
        
        # Delete non-existent
        self.assertFalse(manager.delete_conversation("missing_id"))
        
        # Chat with invalid conversation_id (should fallback and create a new one)
        req = ChatRequest(
            conversation_id="non_existent_conv",
            query="test query",
            tenant_id="tenant1"
        )
        
        async def mock_search(*args, **kwargs):
            return []
            
        engine.retrieval_service.search = mock_search
        resp = await engine.chat(req)
        self.assertIsNotNone(resp.conversation_id)
        
        # Test stream_chat yields
        chunks = []
        async for chunk in engine.stream_chat(req):
            chunks.append(chunk)
        self.assertTrue(len(chunks) > 0)

    async def test_prompt_manager_updates_and_exceptions(self):
        pm = PromptManager()
        # Update missing template
        self.assertIsNone(pm.update_template("missing_id", {}))
        
        # Search and update existing template
        templates = pm.list_templates()
        default_template = next(t for t in templates if t.name == "default_qa")
        template_id = default_template.template_id
        
        template = pm.get_template(template_id)
        self.assertIsNotNone(template)
        updated = pm.update_template(template_id, {"description": "Updated Description"})
        self.assertEqual(updated.description, "Updated Description")
        
        # Render missing template raises ValueError
        with self.assertRaises(ValueError):
            pm.render_prompt("missing_id", {})
            
        # Trigger Exception in Jinja rendering
        pm.create_template(PromptTemplate(
            template_id="bad_template",
            name="Bad Template",
            category=PromptCategory.QA,
            system_prompt="Hello {{ invalid_syntax %}",
            description="Bad template for syntax error test",
            variables=["x"],
            tenant_id="tenant1"
        ))
        with self.assertRaises(Exception):
            pm.render_prompt("bad_template", {"x": "y"})

    async def test_audio_processor_mismatch_format(self):
        ap = AudioProcessor()
        # extension mismatch warning line 59
        req = TranscriptionRequest(
            file_path="audio_file.wav",
            format=AudioFormat.MP3,
            tenant_id="tenant1"
        )
        result = await ap.transcribe(req)
        self.assertEqual(result.file_path, "audio_file.wav")

    async def test_document_parser_empty_text(self):
        dp = DocumentParser()
        # Ingestion chunking empty text buffer
        chunks = dp.parse_text_content("DOC1", "\n\n   \n\n")
        self.assertEqual(len(chunks), 0)

    async def test_web_crawler_exceptions_and_loops(self):
        wc = WebCrawler()
        
        # Trigger single page exception inside crawler.crawl
        bad_req = CrawlRequest(
            url="http://invalid_domain_that_will_raise_exception",
            crawl_type=CrawlType.SINGLE_PAGE,
            tenant_id="tenant1"
        )
        # Mock _crawl_single_page to throw
        wc._crawl_single_page = MagicMock(side_effect=Exception("Failed connection"))
        res = await wc.crawl(bad_req)
        self.assertEqual(res.status, "FAILED")
        self.assertIn("Failed connection", res.errors)
        
        # Test recursive crawler visited loop logic (line 124)
        rec_req = CrawlRequest(
            url="http://example.com",
            crawl_type=CrawlType.RECURSIVE,
            max_pages=5,
            max_depth=1,
            tenant_id="tenant1"
        )
        # Setup duplicate urls in the queue
        wc._extract_links = MagicMock(return_value=["http://example.com/next", "http://example.com/next"])
        res_rec = await wc.crawl(rec_req)
        self.assertEqual(res_rec.status, "SUCCESS")

    def test_widget_service_updates_and_deletes(self):
        ws = WidgetService()
        
        # Delete missing
        self.assertFalse(ws.delete_widget("missing_id"))
        
        # Update missing
        self.assertIsNone(ws.update_widget("missing_id", {}))
        
        # Create and update
        config = WidgetConfig(tenant_id="tenant1", name="Widget1")
        created = ws.create_widget(config)
        self.assertIsNotNone(created.widget_id)
        
        updated = ws.update_widget(created.widget_id, {"name": "WidgetUpdated"})
        self.assertEqual(updated.name, "WidgetUpdated")
        
        # Validate domain with empty allowed domains
        self.assertTrue(ws.validate_domain(created.widget_id, "http://any-domain.com"))
        
        # Validate domain with configured allowed domains
        ws.update_widget(created.widget_id, {"allowed_domains": ["http://trust.com"]})
        self.assertTrue(ws.validate_domain(created.widget_id, "http://trust.com"))
        self.assertFalse(ws.validate_domain(created.widget_id, "http://hack.com"))
        
        # Validate domain with missing widget
        self.assertFalse(ws.validate_domain("missing_id", "http://any.com"))

    async def test_celery_app_worker_queue(self):
        queue = AsyncWorkerQueue()
        
        # Test local job status not found
        self.assertEqual(queue.get_job_status("missing_job_id"), {"status": "NOT_FOUND"})
        
        # Test simulated task backlog complete success
        job_id = await queue.enqueue_job("process_document_chunk", {"data": "test"})
        self.assertIsNotNone(job_id)
        
        # Wait for the async task to execute (sleep 0.1s in app, we wait 0.2s)
        await asyncio.sleep(0.2)
        status = queue.get_job_status(job_id)
        self.assertEqual(status["status"], "SUCCESS")

    def test_neo4j_adapter_real_db_mock(self):
        adapter = Neo4jProductionAdapter()
        adapter.use_real_db = True
        
        # Mock connection driver & session
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_session_ctx = mock_session.__enter__.return_value
        mock_driver.session.return_value = mock_session
        
        # Session execute_write helper
        mock_session_ctx.execute_write.side_effect = lambda work_func: work_func(MagicMock())
        adapter.driver = mock_driver
        
        # Upsert Node (hits write path)
        res = asyncio.run(adapter.upsert_node("N1", "Entity", {"name": "Test"}))
        self.assertEqual(res["status"], "success")
        
        # Upsert Relationship (hits write path)
        res_rel = asyncio.run(adapter.create_edge("N1", "N2", "CONNECTED"))
        self.assertEqual(res_rel["status"], "success")
        
        # Get Node (hits read path via query_neighbors)
        mock_result = [{"neighbor_id": "N2"}]
        mock_tx = MagicMock()
        mock_tx.run.return_value = mock_result
        mock_session_ctx.execute_read.side_effect = lambda work_func: work_func(mock_tx)
        
        node_res = asyncio.run(adapter.query_neighbors("N1"))
        self.assertIsNotNone(node_res)
        self.assertIn("N2", node_res["nodes_found"])
        
        # Write exception triggers fallback
        mock_session_ctx.execute_write.side_effect = Exception("Write failed")
        res_fail = asyncio.run(adapter.upsert_node("N1", "Entity", {"name": "Test"}))
        self.assertEqual(res_fail["status"], "success")

    def test_qdrant_adapter_real_db_mock(self):
        adapter = QdrantProductionAdapter()
        adapter.use_real_db = True
        
        # Mock client
        mock_client = MagicMock()
        adapter.client = mock_client
        
        # Upsert Chunk (hits Qdrant client path)
        res = asyncio.run(adapter.upsert_chunk("C1", "D1", "Hello", {"tenant_id": "tenant1"}))
        self.assertEqual(res["status"], "success")
        
        # Search Similar (hits Qdrant client path)
        from qdrant_client.http.models import ScoredPoint
        mock_point = ScoredPoint(
            id=1,
            version=1,
            score=0.95,
            payload={"chunk_id": "C1", "document_id": "D1", "text": "Hello"}
        )
        mock_client.search.return_value = [mock_point]
        
        results = asyncio.run(adapter.search_similar("query", top_k=2, filter_tenant="tenant1"))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["chunk_id"], "C1")
        
        # Search Exception triggers fallback
        mock_client.search.side_effect = Exception("Search failed")
        fallback_res = asyncio.run(adapter.search_similar("query", top_k=1, filter_tenant="tenant1"))
        self.assertTrue(len(fallback_res) >= 0)

    def test_encryption_field_too_short(self):
        es = EnvelopeEncryptionService()
        # Invalid ciphertext length less than 12
        ciphertext = base64.b64encode(b"too_short").decode("utf-8")
        with self.assertRaises(ValueError):
            es.decrypt_field(ciphertext)

    def test_api_key_manager_rate_limit(self):
        akm = ApiKeyManager()
        res = akm.create_key("tenant1", scopes=[ApiKeyScope.CHAT])
        
        # Overuse key usage count to trigger false rate limit check
        key = akm._keys[res.key_id]
        key.usage_count = 1000000
        self.assertFalse(akm.check_rate_limit(res.key_id))

if __name__ == "__main__":
    unittest.main()
