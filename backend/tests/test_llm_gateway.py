"""Unit tests for Multi‑Model LLM Gateway (llm_gateway.py)"""
import pytest
from backend.services.agent_orchestrator.llm_gateway import (
    MultiModelLLMGateway,
    LLMRequest,
    LLMResponse,
)

@pytest.fixture
def gateway():
    return MultiModelLLMGateway()

@pytest.mark.asyncio
async def test_routing_to_preferred_model(gateway):
    req = LLMRequest(task_type="reasoning", prompt="test", preferred_model="claude-3-5-sonnet")
    resp = await gateway.generate_response(req)
    assert resp.provider == "anthropic"
    assert resp.selected_model == "claude-3-5-sonnet"

@pytest.mark.asyncio
async def test_fallback_on_unavailable_model(gateway):
    # Simulate primary model unavailable by setting impossible preferred_model
    req = LLMRequest(task_type="extraction", prompt="test", preferred_model="nonexistent")
    resp = await gateway.generate_response(req)
    # Should fall back to first in matrix
    assert resp.provider == "anthropic"

@pytest.mark.asyncio
async def test_cost_calculation(gateway):
    req = LLMRequest(task_type="coding", prompt="hello world", max_tokens=100)
    resp = await gateway.generate_response(req)
    # Basic sanity: tokens_used > 0 and cost_usd > 0
    assert resp.tokens_used > 0
    assert resp.cost_usd > 0

@pytest.mark.asyncio
async def test_latency_recorded(gateway):
    req = LLMRequest(task_type="summarization", prompt="summarize this")
    resp = await gateway.generate_response(req)
    assert resp.latency_ms > 0
