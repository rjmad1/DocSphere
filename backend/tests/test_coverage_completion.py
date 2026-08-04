import unittest
import asyncio
import os
import base64
import json
import sys
import importlib
import math
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from backend.main import app
from backend.shared.security.encryption import EnvelopeEncryptionService
from backend.shared.security.api_key_manager import ApiKeyManager, ApiKeyScope, ApiKey
from backend.shared.security.tenant_isolation import TenantSecurityContext, UserContext, SecurityViolationError
from backend.shared.security.input_validator import InputSanitizer, InputSecurityValidationError
from backend.shared.security.audit_logger import CryptographicAuditLogger
from backend.shared.security.worm_backup import WORMBackupService
from backend.shared.middleware.error_handlers import PolicyViolationError, EntityNotFoundError
from backend.services.chat_service.export_service import ExportService, ShareService, ExportRequest, ExportFormat
from backend.services.chat_service.chat_service import ConversationManager, ChatMessage, Conversation
from backend.services.chat_service.prompt_manager import PromptManager, PromptTemplate, PromptCategory
from backend.services.connectors.reddit_connector import RedditConnector
from backend.services.connectors.base_connector import BaseEnterpriseConnector, SyncResult
from backend.services.connectors.confluence_connector import ConfluenceConnector
from backend.services.connectors.jira_connector import JiraConnector
from backend.services.connectors.sap_alm_connector import SAPCloudALMConnector
from backend.services.connectors.servicenow_connector import ServiceNowConnector
from backend.services.knowledge_engine.graph_service import KnowledgeGraphService, EntityNode, RelationshipEdge
from backend.services.knowledge_engine.neo4j_adapter import Neo4jProductionAdapter
from backend.services.knowledge_engine.qdrant_adapter import QdrantProductionAdapter
from backend.services.ingestion.web_crawler import WebCrawler, CrawlRequest
from backend.services.ingestion.audio_processor import AudioProcessor, AudioIngestionPipeline, TranscriptionRequest, AudioFormat, VoiceInputRequest
from backend.services.ingestion.document_parser import DocumentParser
from backend.services.document_service.generation_orchestrator import DocumentGenerationOrchestrator, GenerationRequest
from backend.services.document_service.asst_engine import ASSTEngine, ASSTNode
from backend.services.workflow_engine.celery_app import process_document_chunk_task, compute_change_impact_task, AsyncWorkerQueue, celery_app
from backend.services.workflow_engine.policy_engine import ApprovalRequest, PolicyEngineService
from backend.services.agent_orchestrator.agent_builder import AgentBuilderService, AgentDefinition, AgentToolDefinition
from backend.services.analytics.analytics_service import AnalyticsService, QueryEvent, FeedbackRecord, FeedbackRating

class DummyConnector(BaseEnterpriseConnector):
    async def fetch_updates(self, since_timestamp=None):
        return await super().fetch_updates(since_timestamp)
    async def sync_to_ekos(self, external_items):
        return await super().sync_to_ekos(external_items)

class TestCoverageCompletion(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.encryption = EnvelopeEncryptionService()

    # 1. Encryption Fallbacks
    def test_encryption_empty_and_errors(self):
        self.assertEqual(self.encryption.encrypt_field(""), "")
        self.assertEqual(self.encryption.decrypt_field(""), "")
        
        with self.assertRaises(Exception):
            self.encryption.decrypt_field("short")
            
        with self.assertRaises(Exception):
            self.encryption.decrypt_field(base64.b64encode(b"invalid_nonce_but_long_enough").decode())

    # 2. Api Key Manager Branches
    def test_api_key_manager_branches(self):
        manager = ApiKeyManager()
        result = manager.create_key("tenant_1", expires_hours=1)
        self.assertIsNotNone(result.raw_key)
        
        key = manager.validate_key(result.raw_key)
        self.assertIsNotNone(key)
        self.assertTrue(manager.check_rate_limit(key.key_id))
        
        self.assertIsNone(manager.validate_key("ds_nonexistentkey12345"))
        self.assertFalse(manager.check_rate_limit("nonexistent_id"))
        
        self.assertTrue(manager.revoke_key(key.key_id))
        self.assertFalse(manager.revoke_key("nonexistent_id"))
        self.assertIsNone(manager.validate_key(result.raw_key))
        
        result_expired = manager.create_key("tenant_1", expires_hours=-1)
        self.assertIsNone(manager.validate_key(result_expired.raw_key))

    # 3. Export Service Formats
    def test_export_service_formats(self):
        conv_manager = ConversationManager()
        conv = conv_manager.create_conversation("tenant_1", "Test Conversation")
        conv_manager.add_message(conv.id, ChatMessage(role="user", content="Hello"))
        conv_manager.add_message(conv.id, ChatMessage(role="assistant", content="Hi there", citations=["doc1"]))
        
        export_service = ExportService(conv_manager)
        
        # JSON
        req_json = ExportRequest(conversation_id=conv.id, format=ExportFormat.JSON, include_metadata=False)
        res_json = export_service.export_conversation(req_json)
        self.assertIn("Hi there", res_json.content)
        
        # Markdown
        req_md = ExportRequest(conversation_id=conv.id, format=ExportFormat.MARKDOWN, include_metadata=True)
        res_md = export_service.export_conversation(req_md)
        self.assertIn("# Test Conversation", res_md.content)
        
        # CSV
        req_csv = ExportRequest(conversation_id=conv.id, format=ExportFormat.CSV)
        res_csv = export_service.export_conversation(req_csv)
        self.assertIn("user,Hello", res_csv.content)
        
        # Missing
        req_missing = ExportRequest(conversation_id="missing_id", format=ExportFormat.JSON)
        self.assertIsNone(export_service.export_conversation(req_missing))

    # 4. Share Service Scenarios
    def test_share_service_scenarios(self):
        conv_manager = ConversationManager()
        conv = conv_manager.create_conversation("tenant_1", "Shared Conversation")
        share_service = ShareService()
        
        link = share_service.create_share_link(conv.id, expires_hours=1, is_public=False)
        shared = share_service.get_shared_conversation(link.id, link.access_token, conv_manager)
        self.assertEqual(shared.id, conv.id)
        
        self.assertIsNone(share_service.get_shared_conversation(link.id, "wrong_token", conv_manager))
        
        link_expired = share_service.create_share_link(conv.id, expires_hours=-1)
        self.assertIsNone(share_service.get_shared_conversation(link_expired.id, link_expired.access_token, conv_manager))
        self.assertIsNone(share_service.get_shared_conversation("missing_link", "token", conv_manager))
        
        self.assertTrue(share_service.revoke_link(link.id))
        self.assertFalse(share_service.revoke_link("missing_link"))
        
        link1 = share_service.create_share_link(conv.id)
        self.assertEqual(len(share_service.list_links(conv.id)), 2)
        self.assertGreaterEqual(len(share_service.list_links()), 2)

    # 5. Prompt Manager & Fallback Simple Format Template Rendering
    def test_prompt_manager_branches(self):
        manager = PromptManager()
        self.assertIsNone(manager.update_template("missing_id", {}))
        self.assertFalse(manager.delete_template("missing_id"))
        
        result = manager.list_templates(tenant_id="tenant_1", category=PromptCategory.SYSTEM)
        self.assertTrue(len(result) > 0)
        
        with self.assertRaises(ValueError):
            manager.render_prompt("missing_id", {})
            
        template_id = None
        for t in manager.list_templates():
            if t.name == "default_qa":
                template_id = t.template_id
                break
        self.assertIsNotNone(template_id)
        res = manager.render_prompt(template_id, {"query": "What is EKOS?", "system_date": "2026-08-04", "sources": ["src1"]})
        self.assertIn("What is EKOS?", res.rendered_content)

    # 6. Import fallback testing using sys.modules mock reloading
    def test_import_fallbacks(self):
        orig_jinja2 = sys.modules.get("jinja2")
        sys.modules["jinja2"] = None
        
        try:
            import backend.services.chat_service.prompt_manager as pm
            importlib.reload(pm)
            
            p_manager = pm.PromptManager()
            simple_temp = pm.PromptTemplate(
                name="simple_temp",
                category=pm.PromptCategory.SYSTEM,
                description="Simple format",
                system_prompt="Hello {name}",
                variables=["name"]
            )
            p_manager.create_template(simple_temp)
            
            res = p_manager.render_prompt(simple_temp.template_id, {"name": "World"})
            self.assertEqual(res.rendered_content, "Hello World")
            
            template_id = None
            for t in p_manager.list_templates():
                if t.name == "default_qa":
                    template_id = t.template_id
                    break
            self.assertIsNotNone(template_id)
            res_fallback = p_manager.render_prompt(template_id, {"query": "Hello"})
            self.assertEqual(res_fallback.rendered_content, p_manager.get_template(template_id).system_prompt)
        finally:
            if orig_jinja2:
                sys.modules["jinja2"] = orig_jinja2
            else:
                del sys.modules["jinja2"]
            import backend.services.chat_service.prompt_manager as pm
            importlib.reload(pm)

    # 7. Connectors & Error Handlers
    def test_connectors_and_errors(self):
        graph = KnowledgeGraphService()
        engine = ASSTEngine()
        confluence = ConfluenceConnector({}, engine)
        res = asyncio.run(confluence.sync_to_ekos([{"page_id": "P1"}]))
        self.assertEqual(len(res.errors), 1)
        
        jira = JiraConnector({}, graph)
        res_jira = asyncio.run(jira.sync_to_ekos([{"issue_key": "J1"}]))
        self.assertEqual(len(res_jira.errors), 1)

        sap = SAPCloudALMConnector({}, graph)
        res_sap = asyncio.run(sap.sync_to_ekos([{"process_id": "S1"}]))
        self.assertEqual(len(res_sap.errors), 1)

        snow = ServiceNowConnector({}, graph)
        res_snow = asyncio.run(snow.sync_to_ekos([{"sys_id": "SN1"}]))
        self.assertEqual(len(res_snow.errors), 1)

        dummy = DummyConnector("Dummy", {})
        asyncio.run(dummy.fetch_updates())
        asyncio.run(dummy.sync_to_ekos([]))

    # 8. Reddit Connector Methods
    def test_reddit_connector(self):
        conn = RedditConnector()
        updates = asyncio.run(conn.fetch_updates())
        self.assertEqual(len(updates), 5)
        
        res = asyncio.run(conn.sync_to_ekos(updates))
        self.assertEqual(res.items_scanned, 5)
        
        posts = asyncio.run(conn.get_subreddit_posts("general", 2))
        self.assertEqual(len(posts), 2)
        
        comments = asyncio.run(conn.get_thread_comments("thread_1"))
        self.assertEqual(len(comments), 3)
        
        ingest_res = asyncio.run(conn.ingest_subreddit("general", 2))
        self.assertEqual(ingest_res["documents_extracted"], 2)

    # 9. Web Ingestion & In-Memory Recurse Crawling
    def test_web_crawler_scenarios(self):
        crawler = WebCrawler()
        
        # Test Sitemap
        req_site = CrawlRequest(url="https://test.com/sitemap.xml", crawl_type="SITEMAP", max_pages=1, tenant_id="tenant_1")
        res_site = asyncio.run(crawler.crawl(req_site))
        self.assertEqual(res_site.pages_crawled, 1)
        
        # Test Recursive
        req_recur = CrawlRequest(url="https://test.com", crawl_type="RECURSIVE", max_pages=3, max_depth=1, tenant_id="tenant_1")
        res_recur = asyncio.run(crawler.crawl(req_recur))
        self.assertGreaterEqual(res_recur.pages_crawled, 1)
        
        # Validate Extract Text and Links
        text = crawler._extract_text("<html><body>  Hello   World  </body></html>")
        self.assertEqual(text, "Hello World")
        
        links = crawler._extract_links("<html><body><a href='/page1'>P1</a><a href='https://test.com/page2'>P2</a></body></html>", "https://test.com")
        self.assertIn("https://test.com/page1", links)

        # Force sitemap crawl exception path coverage
        crawler_err = WebCrawler()
        crawler_err._crawl_single_page = MagicMock(side_effect=Exception("sitemap exception"))
        req_site_err = CrawlRequest(url="https://test.com/sitemap.xml", crawl_type="SITEMAP", max_pages=2, tenant_id="tenant_1")
        res_site_err = asyncio.run(crawler_err.crawl(req_site_err))
        self.assertEqual(res_site_err.pages_crawled, 0)

        # Force recursive crawl exception path coverage
        crawler_rec_err = WebCrawler()
        crawler_rec_err._crawl_single_page = MagicMock(side_effect=Exception("recursive exception"))
        req_rec_err = CrawlRequest(url="https://test.com", crawl_type="RECURSIVE", max_pages=2, tenant_id="tenant_1")
        res_rec_err = asyncio.run(crawler_rec_err.crawl(req_rec_err))
        self.assertEqual(res_rec_err.pages_crawled, 0)

    # 10. Voice Ingestion Pipeline & Audio Formats
    def test_audio_processor_and_pipeline(self):
        proc = AudioProcessor()
        self.assertFalse(proc._validate_format("test.mp3", AudioFormat.WAV))
        self.assertTrue(proc._validate_format("test.mp3", AudioFormat.MP3))
        
        pipeline = AudioIngestionPipeline()
        res = asyncio.run(pipeline.ingest_audio("test_recording.mp3", AudioFormat.MP3, "tenant_1"))
        self.assertEqual(res["status"], "SUCCESS")

    # 11. Document Generation Orchestrator
    def test_generation_orchestrator(self):
        orchestrator = DocumentGenerationOrchestrator()
        req = GenerationRequest(
            document_title="Reconciliation Spec",
            template_type="FRS",
            project_id="PROJ-01",
            input_source_ids=["SRC-01"],
            tenant_id="tenant_1"
        )
        res = asyncio.run(orchestrator.start_generation(req))
        self.assertEqual(res.status, "DRAFTING")

    # 12. ASST Engine Nodes
    def test_asst_engine_nodes(self):
        engine = ASSTEngine()
        asst = engine.parse_markdown_to_asst("D1", "T1", "Lead Text\n## Section 1\nSome other text.")
        self.assertEqual(asst.children[0].type, "TextNode")
        
        ref_node = ASSTNode(node_id="ref1", type="EntityRefNode", content="Ref", entity_id="REQ-1")
        asst.children.append(ref_node)
        md = engine.render_asst_to_markdown(asst)
        self.assertIn("`[REQ-1]` Ref", md)

    # 13. Celery App Async Queue Status & Real task delays
    def test_celery_worker_queue(self):
        queue = AsyncWorkerQueue()
        status = queue.get_job_status("celery_dummy-uuid")
        self.assertEqual(status["status"], "ERROR")
        
        # Test task invocations directly
        self.assertEqual(process_document_chunk_task({"chunk_id": "c1"})["chunk_id"], "c1")
        self.assertEqual(compute_change_impact_task({"entity_id": "e1"})["entity_id"], "e1")

        # Mock celery tasks delay failure
        orig_delay = process_document_chunk_task.delay
        process_document_chunk_task.delay = MagicMock(side_effect=Exception("celery failed"))
        job_id = asyncio.run(queue.enqueue_job("process_document_chunk", {"chunk_id": "c1"}))
        self.assertTrue(job_id.startswith("job_"))
        process_document_chunk_task.delay = orig_delay

    # 14. Input Sanitizer XSS Validation
    def test_input_sanitizer_xss(self):
        self.assertEqual(InputSanitizer.sanitize_string(""), "")
        with self.assertRaises(InputSecurityValidationError):
            InputSanitizer.sanitize_string("<script>alert(1)</script>")

    # 15. Tenant Isolation Filter
    def test_tenant_filter(self):
        context = UserContext(user_id="U1", tenant_id="T1", roles=["Author"], email="u1@test.com")
        sec = TenantSecurityContext()
        filtered = sec.filter_db_query({"id": "node_1"}, context)
        self.assertEqual(filtered["tenant_id"], "T1")

    # 16. Agent Builder Edge Cases
    def test_agent_builder(self):
        service = AgentBuilderService()
        self.assertIsNone(service.update_agent("missing_id", {}))
        self.assertFalse(service.delete_agent("missing_id"))
        with self.assertRaises(ValueError):
            asyncio.run(service.execute_agent("missing_id", "query"))
            
        # Create, execute, update, delete Agent builder coverage
        agent_def = AgentDefinition(
            name="A1", description="D1", persona="P1", enabled_tools=["web_search"], knowledge_source_ids=["k1"], tenant_id="T1"
        )
        service.create_agent(agent_def)
        self.assertEqual(service.get_agent(agent_def.agent_id).name, "A1")
        
        # Execute agent success
        res = asyncio.run(service.execute_agent(agent_def.agent_id, "Hello"))
        self.assertIn("Hello", res.response)
        
        # Execute agent inactive failure
        service.update_agent(agent_def.agent_id, {"is_active": False})
        with self.assertRaises(ValueError):
            asyncio.run(service.execute_agent(agent_def.agent_id, "Hello"))
            
        # Delete agent success
        self.assertTrue(service.delete_agent(agent_def.agent_id))

    # 17. Analytics Service Summary
    def test_analytics_service(self):
        service = AnalyticsService()
        service.record_query(QueryEvent(tenant_id="T1", query_text="Q1", response_length=10, sources_count=1, latency_ms=10, model_used="gpt-4"))
        service.record_feedback(FeedbackRecord(conversation_id="C1", message_id="M1", rating=FeedbackRating.THUMBS_UP, tenant_id="T1"))
        
        feedbacks = service.get_feedback("T1", conversation_id="C1")
        self.assertEqual(len(feedbacks), 1)
        
        with self.assertRaises(ValueError):
            service.export_analytics("T1", format="xml")

    # 18. Database Adapters Mock-Failures and Cosine Similarity checks
    def test_db_adapters_exceptions_and_logic(self):
        # Qdrant client exception simulation
        qdrant = QdrantProductionAdapter()
        qdrant.use_real_db = True
        qdrant.client = MagicMock()
        qdrant.client.upsert.side_effect = Exception("qdrant upsert error")
        qdrant.client.search.side_effect = Exception("qdrant search error")
        
        # Upsert should fallback to in-memory on error
        asyncio.run(qdrant.upsert_chunk("c1", "d1", "text", {}))
        self.assertEqual(len(asyncio.run(qdrant.search_similar("text"))), 1)
        
        # Neo4j client exception simulation
        neo4j = Neo4jProductionAdapter()
        neo4j.use_real_db = True
        neo4j.driver = MagicMock()
        neo4j.driver.session.side_effect = Exception("neo4j session error")
        
        # Operations should fallback to in-memory on error
        asyncio.run(neo4j.upsert_node("n1", "Label", {}))
        asyncio.run(neo4j.create_edge("n1", "n2", "REL"))
        res = asyncio.run(neo4j.query_neighbors("n1"))
        self.assertIn("n2", res["nodes_found"])

    # 19. WORM Backups manifest exception
    def test_worm_backup_manifest_exceptions(self):
        worm = WORMBackupService()
        with self.assertRaises(ValueError):
            worm.create_snapshot("T1", [])

    # 20. Cryptographic Audit Logger Tampering
    def test_cryptographic_audit_logger_tampering(self):
        audit = CryptographicAuditLogger()
        audit.log_event("user1", "read", "node1", {"tenant_id": "T1"})
        audit.log_event("user1", "read", "node2", {"tenant_id": "T1"})
        
        # Test initial chain is valid
        self.assertTrue(audit.verify_chain_integrity())
        
        # Tamper prev hash
        audit._audit_chain[1].previous_hash = "tampered"
        self.assertFalse(audit.verify_chain_integrity())
        
        # Tamper checksum
        audit._audit_chain[1].previous_hash = audit._audit_chain[0].checksum_hash
        audit._audit_chain[1].checksum_hash = "tampered"
        self.assertFalse(audit.verify_chain_integrity())

    # 21. Document Parser Empty/Whitespace buffers
    def test_document_parser_whitespace_buffers(self):
        parser = DocumentParser()
        # White spaces only should flush buffer without creating chunk
        res = parser.parse_text_content("DOC1", " \n \n ")
        self.assertEqual(len(res), 0)

    # 22. Policy Engine Severity MAJOR and SLA branches
    def test_policy_engine_major_severity(self):
        policy = PolicyEngineService()
        res = policy.evaluate_approval_chain(ApprovalRequest(
            artifact_id="A1", artifact_type="BRD", change_severity="MAJOR", risk_score=0.5, impacted_entity_count=2, author_id="U1"
        ))
        self.assertIn("Lead Architect", res.required_roles)
        self.assertEqual(res.sla_hours, 12)

    # 23. API Endpoint Router Validations
    def test_api_endpoints_coverage(self):
        # 1. DELETE conversation
        response = self.client.delete("/api/v1/chat/conversations/nonexistent_id")
        self.assertEqual(response.status_code, 404)
        
        # 2. DELETE shared link
        response = self.client.delete("/api/v1/chat/shared/nonexistent_id")
        self.assertEqual(response.status_code, 404)
        
        # 3. POST Crawl recursive
        response = self.client.post("/api/v1/crawl", json={
            "url": "https://test.com", "crawl_type": "RECURSIVE", "tenant_id": "tenant_1"
        })
        self.assertEqual(response.status_code, 200)

        # 4. POST Ingest Audio
        response = self.client.post("/api/v1/ingest/audio?file_path=test.mp3&format=MP3&tenant_id=tenant_1")
        self.assertEqual(response.status_code, 200)

        # 5. POST Live Voice
        response = self.client.post("/api/v1/chat/voice", json={
            "audio_data": "YmFzZTY0", "format": "MP3", "tenant_id": "tenant_1"
        })
        self.assertEqual(response.status_code, 200)

        # 6. Widget configurations
        config = {
            "name": "Support widget", "tenant_id": "tenant_1"
        }
        res_config = self.client.post("/api/v1/widgets", json=config)
        self.assertEqual(res_config.status_code, 200)
        widget_id = res_config.json()["widget_id"]

        # GET config valid
        self.assertEqual(self.client.get(f"/api/v1/widgets/{widget_id}").status_code, 200)
        # GET embed valid
        self.assertEqual(self.client.get(f"/api/v1/widgets/{widget_id}/embed").status_code, 200)
        # DELETE config valid
        self.assertEqual(self.client.delete(f"/api/v1/widgets/{widget_id}").status_code, 200)

        # GET config missing
        self.assertEqual(self.client.get("/api/v1/widgets/missing_id").status_code, 404)
        # GET embed missing
        self.assertEqual(self.client.get("/api/v1/widgets/missing_id/embed").status_code, 404)

        # 7. Channel webhook routing
        # Slack
        self.assertEqual(self.client.post("/api/v1/channels/slack/webhook", json={"type": "url_verification", "challenge": "ch1"}).status_code, 200)
        self.assertEqual(self.client.post("/api/v1/channels/slack/webhook", json={"event": {"type": "message", "text": "Hi", "channel": "C1", "user": "U1"}}).status_code, 200)
        # Slack event processed fallback returning event_processed
        self.assertEqual(self.client.post("/api/v1/channels/slack/webhook", json={"event": {"type": "message", "channel": "C1", "user": "U1"}}).status_code, 200)
        
        # Discord
        self.assertEqual(self.client.post("/api/v1/channels/discord/webhook", json={"content": "Hi", "author": {"username": "user", "id": "1", "bot": False}, "channel_id": "C2"}).status_code, 200)
        # Telegram
        self.assertEqual(self.client.post("/api/v1/channels/telegram/webhook", json={"message": {"text": "Hi", "from": {"username": "user", "id": 1}, "chat": {"id": 2}}}).status_code, 200)
        # Unsupported channel type
        self.assertEqual(self.client.post("/api/v1/channels/unsupported/webhook", json={}).status_code, 400)
        
        # 8. Custom Agent building
        agent = {
            "name": "Support Agent", "description": "Support Agent Description", "persona": "Helpful support", "tenant_id": "tenant_1", "knowledge_source_ids": ["doc_1"], "enabled_tools": ["web_search"]
        }
        res_agent = self.client.post("/api/v1/agents/builder", json=agent)
        self.assertEqual(res_agent.status_code, 200)
        agent_id = res_agent.json()["agent_id"]

        # GET agent definition
        self.assertEqual(self.client.get(f"/api/v1/agents/builder/{agent_id}").status_code, 200)
        self.assertEqual(self.client.get("/api/v1/agents/builder/missing_id").status_code, 404)
        
        # Execute agent valid
        self.assertEqual(self.client.post(f"/api/v1/agents/builder/{agent_id}/execute?query=Hello").status_code, 200)
        # Execute agent missing
        self.assertEqual(self.client.post("/api/v1/agents/builder/missing_id/execute?query=Hello").status_code, 404)
        
        # DELETE agent definition
        self.assertEqual(self.client.delete(f"/api/v1/agents/builder/{agent_id}").status_code, 200)
        self.assertEqual(self.client.delete("/api/v1/agents/builder/missing_id").status_code, 404)

        # 9. Key lifecycles
        res_key = self.client.post("/api/v1/keys?tenant_id=tenant_1")
        self.assertEqual(res_key.status_code, 200)
        key_id = res_key.json()["key_id"]

        # Delete Key missing
        self.assertEqual(self.client.delete("/api/v1/keys/missing_id").status_code, 404)
        # Delete Key valid
        self.assertEqual(self.client.delete(f"/api/v1/keys/{key_id}").status_code, 200)

        # 10. Analytics routes
        self.assertEqual(self.client.get("/api/v1/analytics/summary?tenant_id=tenant_1").status_code, 200)
        self.assertEqual(self.client.get("/api/v1/analytics/popular?tenant_id=tenant_1").status_code, 200)
        self.assertEqual(self.client.get("/api/v1/analytics/export?tenant_id=tenant_1").status_code, 200)

        # 11. Prompts routing
        prompt = {
            "name": "Custom", "category": "CUSTOM", "system_prompt": "Prompt text", "description": "Custom prompt template", "variables": []
        }
        res_prompt = self.client.post("/api/v1/prompts", json=prompt)
        self.assertEqual(res_prompt.status_code, 200)
        prompt_id = res_prompt.json()["template_id"]

        # GET prompt
        self.assertEqual(self.client.get(f"/api/v1/prompts/{prompt_id}").status_code, 200)
        self.assertEqual(self.client.get("/api/v1/prompts/missing_id").status_code, 404)

        # POST render prompt
        self.assertEqual(self.client.post(f"/api/v1/prompts/{prompt_id}/render", json={}).status_code, 200)

        # DELETE prompt
        self.assertEqual(self.client.delete(f"/api/v1/prompts/{prompt_id}").status_code, 200)
        self.assertEqual(self.client.delete("/api/v1/prompts/missing_id").status_code, 404)

        # 12. Share conversation links
        # Create share
        res_share = self.client.post("/api/v1/share?conversation_id=c1")
        self.assertEqual(res_share.status_code, 200)
        share_id = res_share.json()["id"]
        access_token = res_share.json()["access_token"]

        # GET share missing
        self.assertEqual(self.client.get("/api/v1/share/missing_id?access_token=1").status_code, 404)
        
        # DELETE share link
        self.assertEqual(self.client.delete(f"/api/v1/share/{share_id}").status_code, 200)
        self.assertEqual(self.client.delete("/api/v1/share/missing_id").status_code, 404)

        # 13. Export conversation missing
        self.assertEqual(self.client.post("/api/v1/export/conversation", json={"conversation_id": "missing_id", "format": "json"}).status_code, 404)

        # 14. Graph endpoints
        # POST edge
        self.assertEqual(self.client.post("/api/v1/graph/relationship", json={"source_id": "REQ-01", "target_id": "CAP-01", "relationship_type": "IMPLEMENTS"}).status_code, 200)
        # GET dependencies
        self.assertEqual(self.client.get("/api/v1/graph/dependencies/REQ-01").status_code, 200)

        # 15. Agent dispatch
        response = self.client.post("/api/v1/agents/dispatch", json={
            "task_id": "T1",
            "target_agent_id": "A1",
            "prompt_context": {},
            "required_outputs": ["out1"]
        })
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()
