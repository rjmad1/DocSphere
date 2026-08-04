# ADR-0004: Task-Based Multi-Model LLM Gateway & Provider Fallback

## Status
Accepted

## Context
Relying on a single LLM vendor exposes the enterprise platform to vendor lock-in, API rate-limiting outages, pricing fluctuations, and suboptimal performance on specialized tasks (e.g., code generation vs structured extraction vs long-context reasoning).

## Decision
EKOS implements a pluggable **Multi-Model LLM Gateway** that routes prompts dynamically based on task type:
- *Reasoning & Planning*: GPT-4o / Claude 3.5 Sonnet
- *Entity Extraction*: Claude 3.5 Sonnet / GPT-4o-mini
- *Summarization*: Gemini 1.5 Flash / GPT-4o-mini

The gateway automatically fails over to secondary providers if the primary provider returns API errors or breaches latency SLAs.

## Consequences
- **Positive**: Eliminates single-vendor dependency; optimizes cost-per-token and execution latency; provides zero-downtime provider fallbacks.
- **Negative / Tradeoff**: Requires maintaining multi-provider prompt templates and testing output format consistency across models (managed via `PromptManager`).
