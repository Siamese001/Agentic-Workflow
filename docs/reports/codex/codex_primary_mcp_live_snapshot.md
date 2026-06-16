# Codex Primary MCP Live Snapshot

Generated: 2026-06-16

Scope: current Codex-primary route evidence for `C:\Git\Agentic-Workflow-FRESH`.

This is an evidence snapshot, not a second MCP registry. Configured-server truth remains root `.mcp.json`; procedural routing remains `.claude/skills/mcp-integration/SKILL.md` and `.claude/mcp-notes.md`.

## Summary

| Server | Codex Status | Evidence | Run Policy |
| --- | --- | --- | --- |
| `memory` | transport_closed_after_cleanup | `mcp__memory.mem_recall_session_start` returned durable entities earlier; post-cleanup `mcp__memory.memory_health` returned `Transport closed`. | Required for memory-backed session recall/writeback when available; do not claim ready until the Codex MCP host restarts or reattaches and health passes. |
| `GitKraken` | callable_partial | `mcp__GitKraken.git_status` returned repo status. | Use when exposed; native `git` is degraded fallback for missing tool operations. |
| `vector_db` | transport_closed_after_cleanup | `mcp__vector_db.readiness` returned Chroma ready earlier; post-cleanup readiness returned `Transport closed`. | Use after readiness is healthy again; `rg` is lexical fallback only. |
| `adg_sqlite` | not_callable_in_live_discovery | Tool discovery returned no callable ADG tools. | Use newest `artifacts/adg/adg_indexed_*.sqlite` as degraded fallback. |
| `deepwiki` | not_callable_in_live_discovery | Tool discovery returned no callable DeepWiki tools. | Use GitHub, Tavily, web, or official docs as cited degraded substitutes. |
| `notion` | plugin_substitute | Codex Notion plugin route is the accepted substitute. | Fetch schema before manual Plans/Backlog writes. |
| `playwright` | substitute_callable | Browser/node routes are available. | Use Codex Browser/node verification unless raw parity is required. |
| `context7` | degraded_fallback | Raw Context7 tools not exposed. | Use primary official docs and cite them. |
| `tavily` | plugin_substitute | Plugin available and `TAVILY_API_KEY` configured. | Use for web search/extract/crawl/map when available. |
| `pytest_mcp` | dormant_by_policy | Dormant in `.claude/mcp-notes.md`. | Use `python -m pytest` with plugin autoload enabled. |
| `redis` | dormant_cli_fallback | Redis TCP reachable; standalone MCP dormant. | Treat Redis as ADG hot projection only. |
| `otel_mcp` | dormant_on_demand | Not exposed in this session. | Use only when collector prerequisites are ready. |

## Process Hygiene

The initial 2026-06-16 transport audit showed duplicate visible process cohorts for Memory and Vector DB. Follow-up cleanup cleared the duplicate OS cohorts; `audit_codex_mcp_transports.py` then reported `process_count=0` for both `memory` and `vector_db`.

Process visibility is not callable proof. The post-cleanup Memory and Vector tools returned `Transport closed`, so strict Codex-primary readiness requires a Codex MCP host restart/reload before those routes can be claimed callable again. Strict preflight should use:

```bash
python scripts/governance/codex_readiness.py --require-clean-worktree --fail-duplicate-processes --json
```

When a route is proven callable by live Codex tools, pass that proof to shell-side readiness checks with `CODEX_MCP_CALLABLE_<SERVER_ID>=healthy`.
