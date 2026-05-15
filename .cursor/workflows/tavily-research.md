---
description: Multi-source synthesized research with citations. The deepest, most expensive Tavily tool — use for ADR background, competitive analysis, or upstream-issue investigation.
---

# /tavily-research

Runs Tavily's research engine — multi-step, multi-source, citation-grounded synthesis. Internally chains many search/extract calls, returns a single comprehensive answer with sources. Slower and more expensive than `tavily-search`; use only when one-shot search would not suffice.

## When to use

- ADR background research (e.g. "compare retrieval-tool patterns across major agent frameworks").
- Upstream-issue deep dive ("what is the full state of the Anthropic MCP serialization race?").
- Competitive analysis ("research the AI coding assistant market").
- Multi-subtopic technical questions where you need a written synthesis, not a list of links.

## Steps

1. Confirm `TAVILY_API_KEY` is set.
2. Compose `input` — a thorough description of the research task. The more specific the input, the better the report. Multi-paragraph descriptions are fine.
3. Pick `model`:
   - `mini` — narrow tasks with few subtopics. Cheaper, faster.
   - `pro` — broad tasks with many subtopics. Slower (60–180 s), more thorough.
   - `auto` (default) — Tavily picks. Use when unsure.
4. Invoke `tavily-research` (sole MCP call this response — and likely sole tool of any kind for that response, since it can take 30–180 s).
5. Carry the report's citations forward — every claim Cursor Agent re-states in subsequent prose must keep its source URL.
6. If the report is reusable (upstream-issue dossier, competitive baseline), capture key findings in Memory MCP as a `ProceduralPattern` or `ProjectContext` entity (see `memory-notion-writeback.md`).

## Examples

| User prompt | Suggested params |
|---|---|
| "Research the AI agent framework landscape" | `input="Compare the major AI agent frameworks (LangGraph, CrewAI, AutoGen, Letta, Smolagents) on architecture, state model, tool routing, and production maturity. Focus on production deployments and recent changes (last 6 months)."`, `model="pro"` |
| "Research the upstream MCP transport race" | `input="Document the full state of anthropics/claude-agent-sdk-typescript#41 (SDK MCP server stream-closed errors during concurrent tool calls). Include related issues in claude-code repo, current workarounds, and any merged fixes."`, `model="pro"` |
| "Quick research on Python 3.13 async changes" | `input="Summarize what changed in Python 3.13 async (asyncio + new TaskGroup behavior + free-threading impact)."`, `model="mini"` |
| "Default investigation" | `model="auto"` |

## Cost / Latency Control

- Default to `model="auto"` unless the prompt explicitly requires `pro`-grade depth.
- Tavily limits this tool to 20 requests per minute.
- For super-narrow questions a `tavily-search` call is cheaper and almost as informative — escalate to research only if search results are clearly insufficient.

## Forbidden

- ❌ Pre-emptively running `tavily-research` "to be safe" before a question with a known cheap answer.
- ❌ Using this for code-architecture questions answerable from `adg_sqlite` / `vector_db`.
- ❌ Pairing with any other MCP call this response (constitutional §25).
