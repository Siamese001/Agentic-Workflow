---
name: mcp-integration
description: Routes Claude Code to the correct MCP server (filesystem, Redis, DeepWiki, Context7, Playwright, vector DB, Notion, Tavily, OTel, pytest, GitKraken, memory, task manager). Invoke when the user asks about MCP capabilities, tool choice, or cross-server workflows. For structural code deps use adg-sqlite; for Tavily-only web research prefer tavily-research.
metadata:
  enforcement_layer: behavioural
  enforcement_timing: before_work
  enforcement_type: tool_routing
---

# MCP Integration Guide

> **W4 indexed skill** — procedure bodies live under `sections/`; Tier-1 companion: [agents-tier1-companion.md](agents-tier1-companion.md); legacy overflow: [SUPPORTING.md](SUPPORTING.md).  
> **Excluded:** `adg-sqlite` (critical infrastructure — separate skill).

## Server Availability — read before routing (reconciled 2026-06-14)

> ⚠️ Not every section below maps to an installed server. The routing tables describe the
> **intended** surface; this block is the SSOT for what is actually callable. Cross-check
> against `.mcp.json` and `CLAUDE.md` § "Not in `.mcp.json`".

| Server | In `.mcp.json`? | Section | Use this instead when dormant |
|---|---|---|---|
| `adg_sqlite` | ✅ LIVE | (own skill) | — |
| `GitKraken` | ✅ LIVE | §11 | — |
| `context7` | ✅ LIVE | §4 | — |
| `deepwiki` | ✅ LIVE | §3 | — |
| `memory` | ✅ LIVE | §12 | — |
| `notion` | ✅ LIVE | §7 | — |
| `playwright` | ✅ LIVE | §5 | — |
| `vector_db` | ✅ LIVE | §6 | — |
| `filesystem` | ❌ DORMANT | §1 | native `read_file`/`write`/`list_dir` |
| `redis` | ❌ DORMANT | §2 | `redis-cli` via `run_command` |
| `tavily` | ❌ DORMANT* | §8 | native `WebSearch`/`WebFetch` |
| `otel_mcp` | ❌ DORMANT | §9 | re-add on demand for runtime trace debugging |
| `pytest_mcp` | ❌ DORMANT | §10 | `python -m pytest` via `run_command` |
| `task_manager` | ❌ DORMANT | §13 | native file tools / `structured-reasoning` |

\* `tavily` is not in `.mcp.json`, but a host-managed Tavily MCP may be **injected at session
start** in some environments (its `tavily_*` tools then appear in the deferred-tool list). When
present, prefer it for web search; when absent, fall back to native `WebSearch`/`WebFetch`. Either
way `.mcp.json` is unchanged — do not claim a repo-configured Tavily server.

The §1/§2/§8/§9/§10/§13 sections below remain as **dormant reference** so re-adding a server is a
one-step restore (`.claude/mcp-notes.md`). They are NOT evidence the server is currently callable.

## Quick Reference

| Need | Detail | MCP skill |
|------|--------|-----------|
| Batch / out-of-workspace files | [§1](sections/01-filesystem-mcp.md) | `filesystem-mcp` |
| Redis cache / ADG hot projection | [§2](sections/02-redis-cache.md) | `redis-cache` |
| External GitHub repo Q&A | [§3](sections/03-deepwiki.md) | `deepwiki` |
| Published library API docs | [§4](sections/04-context7.md) | `context7` |
| Browser E2E / UI proof | [§5](sections/05-playwright.md) | `playwright` |
| Semantic similarity search | [§6](sections/06-vector-db.md) | `vector-db` |
| Plans / backlog Notion rows | [§7](sections/07-notion.md) | `notion` |
| Web search / extract / crawl | [§8](sections/08-tavily-research.md) | `tavily-research` |
| Runtime traces / healing | [§9](sections/09-otel-telemetry.md) | `otel-telemetry` |
| Pytest discovery / runs | [§10](sections/10-pytest-mcp.md) | `pytest-mcp` |
| Git / PR / issues | [§11](sections/11-gitkraken.md) | `gitkraken` |
| Cross-session memory graph | [§12](sections/12-memory-mcp.md) | `memory-mcp` |
| Durable tracked tasks | [§13](sections/13-task-manager-mcp.md) | `task-manager-mcp` |

## Progressive disclosure index

Read **only** the section file matching the user intent — do not load all sections.

| § | File | Use when |
|---|------|----------|
| 1 | [sections/01-filesystem-mcp.md](sections/01-filesystem-mcp.md) | Multi-file batch reads, directory trees, cross-root moves |
| 2 | [sections/02-redis-cache.md](sections/02-redis-cache.md) | Cache health, TTL, namespace invalidation |
| 3 | [sections/03-deepwiki.md](sections/03-deepwiki.md) | Third-party GitHub architecture questions |
| 4 | [sections/04-context7.md](sections/04-context7.md) | External package versioned docs |
| 5 | [sections/05-playwright.md](sections/05-playwright.md) | Live UI verification, snapshots, E2E |
| 6 | [sections/06-vector-db.md](sections/06-vector-db.md) | Fuzzy / semantic code or doc search |
| 7 | [sections/07-notion.md](sections/07-notion.md) | Plan/backlog status writes (filesystem SSOT for rules/ADRs) |
| 8 | [sections/08-tavily-research.md](sections/08-tavily-research.md) | **Sole** authority for web search (not DeepWiki/Context7) |
| 9 | [sections/09-otel-telemetry.md](sections/09-otel-telemetry.md) | Runtime traces, anomalies, runtime ADG ingest |
| 10 | [sections/10-pytest-mcp.md](sections/10-pytest-mcp.md) | Structured pytest runs / coverage |
| 11 | [sections/11-gitkraken.md](sections/11-gitkraken.md) | Git state, PRs, issues (not raw shell git for queries) |
| 12 | [sections/12-memory-mcp.md](sections/12-memory-mcp.md) | Session start recall, decision writeback |
| 13 | [sections/13-task-manager-mcp.md](sections/13-task-manager-mcp.md) | User explicitly requests durable task tracking |

## Hard rules (all servers)

1. **Native Cursor tools first** for single-file read/write in workspace.
2. **ADG structural queries** → `adg-sqlite` MCP (never grep-for-deps).
3. **Web search** → Tavily only ([§8](sections/08-tavily-research.md)).
4. **Redis is projection** — SQLite ADG snapshot is canonical ([§2](sections/02-redis-cache.md)).
