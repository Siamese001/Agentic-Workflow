---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\mcp-skill-installation-2ee0d2.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\mcp-skill-installation-2ee0d2.md'
source_sha256: 905d40fc5ab4ffe3a83089a6bf7a46024bcf24040ec173b4eae2bdbed9f2013b
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# MCP Skill Installation — Per-MCP Coverage

**Status:** Complete (W1–W4 Done)
**Author:** Cascade (T2)
**Doctrine:** Playwright "install vendor skills, don't author custom routing prose" — see https://playwright.dev/agent-cli/skills

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| W1 | W1.1 | Audit per-MCP skill coverage | ~1k | Done | Table below populated |
| W2 | W2.1–W2.6 | Install/wrap vendor skills (6 MCPs) | ~10k | Done | 5 new skills + tavily-research already existed |
| W3 | W3.1 | Confirm/stub house-skills (7 MCPs) | ~5k | Done | 8 in-house skills created/confirmed (excluding retired enhanced_http) |
| W4 | W4.1 | Add Skill column to AGENTS.md MCP Quick Reference via sync_mcp_config.py | ~2k | Done | 14/14 rows link to `.windsurf/skills/<slug>/SKILL.md`; 3 drift gates + 16/16 unit tests green |

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.1 | Per-MCP audit table | this file | none | 500 | Done |
| W2.1 | Playwright skill install | `.windsurf/skills/playwright/` | npx availability | 1500 | Pending |
| W2.2 | GitKraken skill install | `.windsurf/skills/gitkraken/` | gk CLI presence | 1500 | Pending |
| W2.3 | Notion skill install | `.windsurf/skills/notion/` | Claude Code plugin format | 2000 | Pending |
| W2.4 | Context7 skill install | `.windsurf/skills/context7/` | ctx7 CLI | 1500 | Pending |
| W2.5 | Tavily skill — verify | `.windsurf/skills/tavily-research/` | already exists | 500 | Done |
| W2.6 | DeepWiki skill install | `.windsurf/skills/deepwiki/` | mcp.directory zip | 1500 | Pending |
| W3.1 | House-skill stubs | 7 in-house MCPs | none | 5000 | Pending |
| W4.1 | AGENTS.md trim | `AGENTS.md` Quick Reference | sync_mcp_config.py drift | 2000 | Pending |

## Per-MCP Audit Table (W1.1 deliverable)

| # | MCP | Type | Vendor skill? | Source | House skill (existing) | Action |
|---|---|---|---|---|---|---|
| 1 | `io.windsurf/mcp-playwright` | Vendor | ✅ Yes | `playwright-cli install --skills` | none | W2.1 install |
| 2 | `GitKraken` | Vendor | ✅ Yes | gk CLI / mcp.directory | none | W2.2 install |
| 3 | `notion` | Vendor | ✅ Yes | Notion Claude Code plugin / mcp.directory | none | W2.3 install |
| 4 | `context7` | Vendor | ✅ Yes | `ctx7` CLI, registry at context7.com/skills | none | W2.4 install |
| 5 | `tavily` | Vendor | ✅ Yes | Tavily CLI Agent Skills | `tavily-research/` ✅ | W2.5 — already done (Windsurf-adapted) |
| 6 | `deepwiki` | Vendor | ✅ Yes | mcp.directory/skills/deepwiki | none | ✅ `deepwiki/` |
| 7 | `adg_sqlite` | In-house | ❌ N/A | n/a | `graph-analysis/` | ✅ `adg-sqlite/` (this MCP) + `graph-analysis/` (decision tree) |
| 8 | `memory` | In-house | ❌ N/A | n/a | `ledger-consulter-memory-recall/` partial | ✅ `memory-mcp/` |
| 9 | `otel_mcp` | In-house | ❌ N/A | n/a | none | ✅ `otel-telemetry/` |
| 10 | `pytest_mcp` | In-house | ❌ N/A | n/a | `testing-framework/` | ✅ `pytest-mcp/` (MCP-specific) + `testing-framework/` (rigor) |
| 11 | `redis` | In-house | ❌ N/A | n/a | none | ✅ `redis-cache/` |
| 12 | `task_manager` | In-house | ❌ N/A | n/a | none | ✅ `task-manager-mcp/` |
| 13 | `vector_db` | In-house | ❌ N/A | n/a | none | ✅ `vector-db/` |
| — | `enhanced_http` | RETIRED | n/a | retired 2026-04-27 per global_rules.md | n/a | No skill — server removed from registry |
| 14 | `filesystem` | In-house | ❌ N/A | n/a | none | ✅ `filesystem-mcp/` (when to use vs native) |

## ADG_GRAPH_LAYER_EVIDENCE

This plan modifies `.windsurf/skills/` content (not source code). To satisfy
constitutional §22 the relevant MVs are those that consume MCP-tool routing
metadata that skills inform:

- **`mv_mcp_contract_drift`** — confirms MCP-server tool prefixes referenced
  by new skills match the live `.windsurf/mcp_config.json` registration.
- **`mv_provider_surface_sprawl`** — keeps an eye on duplicate provider
  surfaces if a vendor skill overlaps an existing in-house skill.
- **`mv_tool_surface_overlap`** — flags any new skill that documents a
  tool already documented by an existing skill (avoid duplicate guidance).

Semantic edge: **`resolves_callsite`** (skills tell Cascade which MCP tools
to call; resolution lands in this edge type at runtime).

P-views: surface=none — `.windsurf/skills/` is documentation, not production
code, so no `v_p0_*` / `v_p1_*` match is expected.

## ADG_HOTSPOT_REPORT

| Hotspot | Layer | Fan-in | Archetype | Surface | Rationale |
|---|---|---|---|---|---|
| `.windsurf/skills/` (directory) | L_DOCS | high (every Cascade session reads this) | CENTRAL_DEPENDENCY | none | Skills directory drives MCP routing decisions for every turn |
| `.windsurf/mcp_config.json` | L_CONFIG | high (server registry) | CENTRAL_DEPENDENCY | Execution Surface | Each new skill must align with a registered MCP server |

## Notes

- Tavily already done (`tavily-research/` is the upstream-adapted skill).
- "Vendor skill" installations may not always produce a `playwright-cli`-equivalent. Where the vendor publishes via mcp.directory, the install is a curl+unzip; where they publish a Claude Code plugin, we extract the skill files and adapt the front-matter to Windsurf's format.
- All vendor skills get a thin Windsurf wrapper (front-matter + "see also" pointer to upstream) to play nicely with `.windsurf/skills/` discovery.
