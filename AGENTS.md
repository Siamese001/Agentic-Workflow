# Agent Guidance — Agentic-Workflow

## Plan First. Execute Second.

Root `AGENTS.md` is always-on. Push specialized guidance to subdirectory `AGENTS.md` files or `.cursor/rules/` / skills.

**T2/T3** (2+ files, cross-layer, architecture, multi-file debug): first output = plan; invoke `structured-reasoning` skill → `SR_INTAKE` … `SR_VERIFY`. See `.cursor/rules/sequential-thinking-enforcement.mdc`.

**T0/T1**: single file ≤20 lines or questions — answer/edit directly.

**Layer separation:** Reasoning / Routing / Execution / Verification — no edits before `SR_APPROVAL`.

## MCP Quick Reference

> Stable IDs are the `mcpServers` keys in `.cursor/mcp.json` (Cursor project SSOT). Deprecated Windsurf compatibility copies are non-authoritative. Live tool prefixes like `mcp0_`, `mcp1_`, and so on can shift when server order changes. Resolve the live prefix from the current tool list in-session.

<!-- MCP-QUICK-REFERENCE:START -->

| Server ID | Use For | Example Tools | Notes | Skill |
|---|---|---|---|---|
| `GitKraken` | Git operations, GitLens, pull requests, issues | `git_status, git_add_or_commit, git_log_or_diff, pull_request_create` | Use as the git/PR authority. | [`gitkraken`](.cursor/skills/gitkraken/SKILL.md) |
| `adg_sqlite` | Dependency graph, blast radius, layer analysis, refactoring hotspots, graph-layer primitives (mv_*, v_p*, semantic edges) | `adg_health, adg_edge_fanout, adg_edge_fanin, adg_nodes_by_file, adg_nodes_by_layer, adg_violations, adg_p0_wave_plan` | Structural deps + T2/T3 plans; §22 graph layer (mv_*, P-views, semantic edges). | [`adg-sqlite`](.cursor/skills/adg-sqlite/SKILL.md) |
| `deepwiki` | External GitHub repository docs and wiki Q&A | `read_wiki_structure, read_wiki_contents, ask_question` | Do not use for this repo's own code. | [`deepwiki`](.cursor/skills/deepwiki/SKILL.md) |
| `filesystem` | Filesystem MCP operations and directory traversal | `read_text_file, read_multiple_files, directory_tree, write_file` | Prefer native reads for ordinary file reads when available. | [`filesystem-mcp`](.cursor/skills/filesystem-mcp/SKILL.md) |
| `memory` | Persistent cross-session knowledge graph | `mem_recall_session_start, create_entities, add_observations, search_nodes` | Read at session start; write back major decisions. | [`memory-mcp`](.cursor/skills/memory-mcp/SKILL.md) |
| `vector_db` | Semantic search and embeddings | `semantic_search, query_collection, vector_stats, list_collections` | Not for structural dependency analysis. | [`vector-db`](.cursor/skills/vector-db/SKILL.md) |
| `otel_mcp` | Telemetry, traces, anomalies, runtime ADG ingest | `otel_server_info, otel_trace, otel_anomalies, otel_ingest_to_runtime_adg` | Check otel_server_info before restart logic. | [`otel-telemetry`](.cursor/skills/otel-telemetry/SKILL.md) |
| `task_manager` | Task decomposition and task state tracking | `create_task, decompose_task, update_task, task_info` | Use when the user explicitly wants tracked multi-step work. | [`task-manager-mcp`](.cursor/skills/task-manager-mcp/SKILL.md) |
| `redis` | Redis cache health, keys, TTL, namespace stats | `redis_health, redis_keys, redis_hgetall, redis_namespace_stats` | Use for hot-cache inspection and invalidation. | [`redis-cache`](.cursor/skills/redis-cache/SKILL.md) |
| `pytest_mcp` | Test discovery, runs, and coverage | `discover_tests, run_tests, get_test_details, analyze_test_coverage` | Prefer over plain pytest CLI when possible. | [`pytest-mcp`](.cursor/skills/pytest-mcp/SKILL.md) |
| `playwright` | Browser automation, accessibility snapshots, end-to-end UI verification | `browser_navigate, browser_snapshot, browser_click, browser_fill_form, browser_evaluate, browser_take_screenshot` | Live UI/E2E; output in .playwright-mcp/ (gitignored). Close tabs after use. | [`playwright`](.cursor/skills/playwright/SKILL.md) |
| `notion` | Notion pages and project-management databases | `API-query-data-source, API-retrieve-a-page, API-patch-page` | Plans + Backlog only; five DBs archived → filesystem SSOT (see notion-archived-databases.mdc). | [`notion`](.cursor/skills/notion/SKILL.md) |
| `tavily` | AI-optimized web search, extraction, crawling, and site mapping | `tavily-search, tavily-extract, tavily-crawl, tavily-map` | Web search authority; requires TAVILY_API_KEY. | [`tavily-research`](.cursor/skills/tavily-research/SKILL.md) |
| `context7` | Up-to-date, versioned official documentation for external libraries | `resolve-library-id, get-library-docs` | External package docs; not this repo. CONTEXT7_API_KEY optional. | [`context7`](.cursor/skills/context7/SKILL.md) |

<!-- MCP-QUICK-REFERENCE:END -->

Per-server `SKILL.md` files under `.cursor/skills/<name>/` are **redirect stubs**; procedural SSOT is [`mcp-integration`](.cursor/skills/mcp-integration/SKILL.md) sections §1–§13.

## Notion Workspace Map

<!-- NOTION-MAP:START -->

Bot: **Agentic-Workflow** | Workspace: **Amit Ayer's Space**

| Database | Data Source ID (reads) | Database ID (writes) | Read Trigger | Write Trigger (auto-route) |
|----------|-----------------------|----------------------|--------------|----------------------------|
| Backlog Items | `fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7` | `aa8d2507-101e-4384-81d9-60ea3fe33876` | "plan status", "phase progress", "wave status", "what's blocked" — **but prefer the Backlog Snapshot page for top-N/dashboard queries (see below)** | On wave/phase completion or status change. Post-hook `post_cascade_deferred_scope_capture.py` auto-posts from DEFERRED_SCOPE markers with scorer-assigned P-Band. |
| Plans | `ac53d31b-3068-4039-9ebe-856c12caab32` | `6aba34d9-4d0b-4f4c-b956-b2bdea541ca9` | "which plans exist", "plan status", "is this plan on disk" — relation target from Backlog Items.Plan | On new plan file creation under `.cursor/plans/<slug>-<6hex>.md`. Create Plans row with Status=Not Started, Exists On Disk=true, Plan File Path set. |
| SC/AP Violation Backlog | ~~`803834e1-0af8-4c3c-b45a-f513f80a7fef`~~ | ~~`0a3b8072-eabd-4516-9473-3c321bb011ff`~~ | \u274c **ARCHIVED 2026-05-02** | Filesystem SSOT: `artifacts/adg/*.sqlite` + violation JSON. No Notion write. |
| Constitutional Rules Registry | ~~`9bd2523e-7a6e-434d-89a7-ce4166457069`~~ | ~~`1c1379bc-32ca-4216-898a-3672f0316f69`~~ | \u274c **ARCHIVED 2026-05-02** | Filesystem SSOT: `.cursor/rules/*.mdc`. No Notion write. |
| MCP Registry | ~~`e7b149b4-0496-4e98-a5dd-074dbe31881b`~~ | ~~`59693bbc-71b1-4c63-bc9f-b31eb8b08a0e`~~ | \u274c **ARCHIVED 2026-05-02** | Filesystem SSOT: `.cursor/mcp.json` only. Deprecated Windsurf compatibility copies are non-authoritative. |
| Anti-Pattern Burndown | `4599fe37-8c24-4d89-96af-438b99a967c4` | `80b30bc9-6622-4288-aa4c-6fc526b6a5c5` | "anti-pattern counts", "burndown trend", "ratchet ceiling" | On burndown run or ratchet adjustment |

**Query pattern (reads)**: `API-query-data-source` with `data_source_id` from column 2. Add `filter`/`sorts` as needed.
**Write pattern (creates)**: `API-post-page` with `parent: {type: "database_id", database_id: <column 3>}`. Using data_source_id for writes returns 404.

<!-- NOTION-MAP:END -->

Procedural routing, auto-events, archived DB policy: [agents-tier1-companion.md](.cursor/skills/mcp-integration/agents-tier1-companion.md) · skill [`notion`](.cursor/skills/notion/SKILL.md) · `.cursor/rules/notion-archived-databases.mdc`.

## Memory

First tool call each session: `mem_recall_session_start` (§17). Writeback major decisions via Memory MCP. Detail: `.cursor/rules/memory-management.mdc`, skill `memory-mcp`.

## Constitutional floor

- No PowerShell — `subprocess.run(argv, shell=False, timeout=30)`
- No `pytest.mark.skip` without `strict=True`
- No bare `except Exception` without guardian
- No edits during planning phase
- ADG before grep for structure (§28); grep for literals/TODOs only
- Full rules: `.cursor/rules/` · expanded lists: [agents-tier1-companion.md](.cursor/skills/mcp-integration/agents-tier1-companion.md)

## Cursor config & plans

Lookup: `.cursor/rules/cursor-config-lookup.mdc` · docs mirror `docs/cursor/`. Plans SSOT: `.cursor/plans/<name>-<6hex>.md` only.

## Pytest

`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` — load plugins via `-p` in `pytest.ini` `addopts`. See companion for duplicate-registration caveat.

## Core vs apps (summary)

Apps customize inputs; core enforces contracts. No app leakage in `agentic_core` without migration receipt. **Multi-provider X1D proof panels:** `agentic_core/runtime/judges/panel/` (`JudgePanelRunner`, transport preflight); `apps_rg` wires adapters via `x1d_panel_bridge` (see plan [core-judge-panel-harness-f3c8d1](.cursor/plans/core-judge-panel-harness-f3c8d1.md)). Detail: [agents-tier1-companion.md](.cursor/skills/mcp-integration/agents-tier1-companion.md) · [`agentic_core/AGENTS.md`](agentic_core/AGENTS.md) · `.cursor/rules/agentic-core-static.mdc`.

## Rules & skills SSOT (Cursor)

Procedural MCP / Notion / ledgers: [`mcp-integration`](.cursor/skills/mcp-integration/SKILL.md) · [agents-tier1-companion.md](.cursor/skills/mcp-integration/agents-tier1-companion.md). Plan lifecycle: [`plan-governance`](.cursor/skills/plan-governance/SKILL.md).

| Layer | Path | Notes |
|-------|------|-------|
| Always-on rules (Option A) | `.cursor/rules/000–003*.mdc` | Four `alwaysApply: true` |
| On-demand rules | `.cursor/rules/*.mdc` | `alwaysApply: false` + globs |
| Skills | `.cursor/skills/*/SKILL.md` | Progressive disclosure; per-server stubs redirect to `mcp-integration` §1–§13 |
| Hooks | `.cursor/hooks.json` | Post-agent SSOT: `after_agent_governance_dispatch.py` |
| Index | `.cursor/RULES_INDEX.md` | Generated; `#always-on-discipline` anchor |
| Deprecated Windsurf legacy | `.cursor/windsurf_compat/**` | Non-authoritative compatibility/archive only; edit `.cursor/**` SSOT files |

**Dedup:** Do not restate always-on invariants in skills or hook reminders. MCP procedure → `mcp-integration` sections, not redirect stub bodies. Author-Gate steps → `003-cursor-author-gate-hitl.mdc` only.

Governance inventory: [`governance_tier_inventory.json`](docs/reports/cursor/governance_tier_inventory.json) · dedup audit: [`governance_dedup_audit_20260526.md`](docs/reports/cursor/governance_dedup_audit_20260526.md) · closeout plan: [`governance-dedup-closeout-e8a4c2.md`](.cursor/plans/governance-dedup-closeout-e8a4c2.md).

## Codex backup adapter

Codex is a backup execution surface, not a second governance SSOT. When using Codex in this repo:

- Load the personal Codex skill `agentic-workflow-governance` before T2/T3 work.
- Use `.cursor/**`, `.cursor/mcp.json`, and `.cursor/hooks.json` as the authoritative migrated Cursor/Claude governance sources.
- Do not copy `.cursor` rule bodies into Codex skills; Codex skills should route to the SSOT and summarize only adapter behavior.
- If a Cursor/Claude MCP is unavailable in Codex, use the closest repo script fallback and report the unavailable MCP clearly.
- Validate the adapter with `python scripts/governance/verify_codex_backup.py` after changing Codex backup docs or skills.

Details: [`docs/codex-backup-adapter.md`](docs/codex-backup-adapter.md).
