# 04. AI Platform & Agent Orchestration

## Agent Framework & Registry (`backend/services/agent_orchestrator/agent_framework.py`)
- Defines `BaseAgent` interface and `RequirementAnalyzerAgent` (`ai/agents/requirement_analyzer.py`).
- Implements step-by-step reasoning: Analyze → Identify Entities → Compute Risk → Draft ASST Nodes.

## Multi-Model LLM Gateway (`backend/services/agent_orchestrator/llm_gateway.py`)
- Routes tasks based on task capability matrices (ADR-0004):
  - `reasoning` → OpenAI `gpt-4o`
  - `extraction` → Anthropic `claude-3-5-sonnet`
  - `summarization` → Google Gemini `gemini-1.5-pro`
- Tracks token usage and estimates API costs.

## Prompt Management (`ai/orchestration/prompt-manager.py`)
- Centralized Jinja2 template suite rendering prompts for document generation and impact analysis.
