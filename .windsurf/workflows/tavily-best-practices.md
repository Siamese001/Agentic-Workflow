---
description: Surface Tavily's best-practices guidance for incorporating Tavily web search/extract/crawl/research into a feature you are building.
---

# /tavily-best-practices

Meta-workflow. Use when the user asks Cascade to **build something that uses Tavily** (a chatbot with real-time search, a lead-enrichment tool, a news dashboard, a competitive-intel agent), not when they ask Cascade to **search the web for them**.

## When to use

- "Add Tavily search to my chatbot" → use this workflow to design the integration.
- "Build a lead-enrichment tool that uses Tavily extract" → use this workflow to design the integration.
- "Build a news monitoring dashboard with Tavily" → use this workflow to design the integration.
- "Implement a RAG pipeline using Tavily extract on industry reports" → use this workflow to design the integration.

If the user just wants Cascade itself to search/extract/crawl/research, use the per-tool workflows instead (`/tavily-search`, `/tavily-extract`, `/tavily-crawl`, `/tavily-map`, `/tavily-research`).

## Steps

1. Read the `tavily-research` skill at `.windsurf/skills/tavily-research/SKILL.md` and its decision tree at `.windsurf/skills/tavily-research/tool_decision_tree.md`.
2. Read the upstream best-practices guidance at <https://docs.tavily.com/documentation/agent-skills> §"What You Can Build" — it covers the four reference patterns:
   - **AI Chatbot with Real-Time Search** — `tavily-search` per user turn, with cite-back.
   - **News Monitoring Dashboard** — scheduled `tavily-search` with `time_range` + sentiment scoring on top of results.
   - **Lead Enrichment Tool** — `tavily-extract` (advanced) on company URLs, structured-output extraction on top.
   - **Competitive Intelligence Agent** — `tavily-crawl` of competitor docs/pricing pages with `instructions=` semantic focus, periodic re-crawl with diff.
3. Identify which pattern the user's request maps to (or whether it's a hybrid).
4. Design the integration with these constitutional constraints in mind:
   - **API key handling**: never hardcode `TAVILY_API_KEY`. Use OS env or a secrets manager. Same pattern as `NOTION_TOKEN` in this repo.
   - **Rate limiting**: Tavily research caps at 20 req/min; search at higher. Build retry-with-backoff in your `httpx` client (the `enhanced_http` MCP was retired 2026-04-27).
   - **Citation**: every Tavily-derived fact in the user-facing surface must carry its source URL.
   - **Bounded crawl**: any crawl must have `select_paths` and `limit` set.
   - **Test isolation**: in CI, mock the Tavily client — never call the live API in unit tests.
5. Plan the implementation per `structured-reasoning` if it crosses ≥2 layers (T2/T3) — this is usually the case for "build a tool that uses Tavily".

## References

- Skill: `.windsurf/skills/tavily-research/SKILL.md`
- Decision tree: `.windsurf/skills/tavily-research/tool_decision_tree.md`
- Upstream best-practices: <https://docs.tavily.com/documentation/agent-skills>
- Tavily SDK docs (Python/JS clients): <https://docs.tavily.com/sdk>
- API reference: <https://docs.tavily.com/api-reference>

## Forbidden

- ❌ Building a Tavily-using feature without `structured-reasoning` for T2/T3 scope.
- ❌ Hardcoded API keys.
- ❌ Unbounded crawls in production code.
- ❌ Tavily-derived facts in the UI without inline source URLs.
