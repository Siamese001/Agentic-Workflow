# Codex Primary MCP Live Snapshot

Generated: 2026-06-16

Scope: current Codex-primary route evidence for `C:\Git\Agentic-Workflow-FRESH`.

This is an evidence snapshot, not a second MCP registry. Configured-server truth remains root `.mcp.json`; procedural routing remains `.codex/skills/mcp-integration/SKILL.md` and `.codex/mcp-notes.md`.

## Summary

| Server | Codex Status | Evidence | Run Policy |
| --- | --- | --- | --- |
| `memory` | callable_post_restart | `mcp__memory.mem_recall_session_start` returned durable entities and `mcp__memory.memory_health` returned `status=ok` after Codex restart. | Required for memory-backed session recall/writeback when available; still fails strict readiness when duplicate Codex-owned cohorts are present. |
| `GitKraken` | callable_partial | `mcp__GitKraken.git_status` returned repo status. | Use when exposed; native `git` is degraded fallback for missing tool operations. |
| `vector_db` | warming_timeout_post_restart | `mcp__vector_db.readiness` first reported Chroma ready and embedding model loading, then a follow-up readiness call timed out. | Use after readiness is healthy again; `rg` is lexical fallback only. |
| `adg_sqlite` | callable_post_restart | `mcp__adg_sqlite.adg_health` returned `status=ok`, SQLite healthy, Redis healthy, snapshot `06152026_1043`. | Use raw ADG MCP when exposed; direct SQLite remains the degraded fallback only when raw tools are absent. |
| `deepwiki` | not_callable_in_live_discovery | Tool discovery returned no callable DeepWiki tools. | Use GitHub, Tavily, web, or official docs as cited degraded substitutes. |
| `notion` | plugin_substitute | Codex Notion plugin route is the accepted substitute. | Fetch schema before manual Plans/Backlog writes. |
| `playwright` | substitute_callable | Browser/node routes are available. | Use Codex Browser/node verification unless raw parity is required. |
| `context7` | degraded_fallback | Raw Context7 tools not exposed. | Use primary official docs and cite them. |
| `tavily` | plugin_substitute | Plugin available and `TAVILY_API_KEY` configured. | Use for web search/extract/crawl/map when available. |
| `pytest_mcp` | dormant_by_policy | Dormant in `.codex/mcp-notes.md`. | Use `python -m pytest` with plugin autoload enabled. |
| `redis` | dormant_cli_fallback | Redis TCP reachable; standalone MCP dormant. | Treat Redis as ADG hot projection only. |
| `otel_mcp` | dormant_on_demand | Not exposed in this session. | Use only when collector prerequisites are ready. |

## Process Hygiene

The initial 2026-06-16 transport audit showed duplicate visible process cohorts for Memory and Vector DB. Follow-up manual cleanup cleared the duplicate OS cohorts but also produced closed Memory/Vector transports, proving that process age is not safe attachment evidence.

After a Codex restart, Memory, GitKraken, and ADG became callable again, but strict readiness still found duplicate Codex-owned cohorts for GitKraken, ADG, Memory, and Vector. `cleanup_duplicate_mcp_cohorts.py` now reports those Codex-owned duplicates but refuses `--apply` unless host-attached PID proof is supplied with `--codex-attached-pid <server>=<pid>`.

Repo-owned Python MCP servers now expose attached-PID proof through `mcp__memory.mem_process_identity`, `mcp__adg_sqlite.adg_process_identity`, and `mcp__vector_db.vector_process_identity`. If those tools are absent in a live Codex session, the MCP child is still running older source and should be restarted or reloaded before cleanup. Use each tool's returned `process.cleanup_arg` as the corresponding cleanup argument.

Process visibility is not callable proof. Strict preflight should use:

```bash
python scripts/governance/codex_readiness.py --require-clean-worktree --fail-duplicate-processes --json
```

When a route is proven callable by live Codex tools, pass that proof to shell-side readiness checks with `CODEX_MCP_CALLABLE_<SERVER_ID>=healthy`.
