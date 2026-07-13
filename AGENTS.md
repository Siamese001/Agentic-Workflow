# Agent Guidance — Agentic-Workflow

## Plan First. Execute Second.

Root `AGENTS.md` is the Codex-facing execution adapter. Codex is the primary local execution surface for readiness, run evidence, and verification receipts. Primary enforcement is Codex-owned, and `.codex` is the only repo governance tree. Do not recreate any legacy non-Codex governance directory.

**T2/T3** (2+ files, cross-layer, architecture, multi-file debug): enter native plan mode and present the plan for approval before any edit. Use the `structured-reasoning` skill only as decomposition / retrieval guidance inside that plan-mode workflow. See `.codex/rules/plan-first-enforcement.md`.

**T0/T1**: single file ≤20 lines or questions — answer/edit directly.

**Layer separation:** Reasoning / Routing / Execution / Verification — no edits before plan approval.

## MCP Quick Reference

> Stable IDs are the `mcpServers` keys in root `.mcp.json` (repo MCP SSOT). Live tool prefixes like `mcp0_`, `mcp1_`, and so on can shift when server order changes. Resolve the live prefix from the current tool list in-session.

<!-- MCP-QUICK-REFERENCE:START -->

| Server ID | Use For | Example Tools | Notes | Skill |
|---|---|---|---|---|
| `GitKraken` | Git operations, GitLens, pull requests, issues | `git_status, git_add_or_commit, git_log_or_diff, pull_request_create` | Use as the git/PR authority. | [`mcp-integration`](.codex/skills/mcp-integration/SKILL.md) |
| `adg_sqlite` | Dependency graph, blast radius, layer analysis, refactoring hotspots, graph-layer primitives (mv_*, v_p*, semantic edges) | `adg_health, adg_edge_fanout, adg_edge_fanin, adg_nodes_by_file, adg_nodes_by_layer, adg_violations, adg_p0_wave_plan` | Structural deps + T2/T3 plans; §22 graph layer (mv_*, P-views, semantic edges). | [`adg-sqlite`](.codex/skills/adg-sqlite/SKILL.md) |
| `deepwiki` | External GitHub repository docs and wiki Q&A | `read_wiki_structure, read_wiki_contents, ask_question` | Do not use for this repo's own code. | [`mcp-integration`](.codex/skills/mcp-integration/SKILL.md) |
| `filesystem` | Filesystem MCP operations and directory traversal | `read_text_file, read_multiple_files, directory_tree, write_file` | Prefer native reads for ordinary file reads when available. | [`mcp-integration`](.codex/skills/mcp-integration/SKILL.md) |
| `memory` | Persistent cross-session knowledge graph | `mem_recall_session_start, create_entities, add_observations, search_nodes` | Read at session start; write back major decisions. | [`mcp-integration`](.codex/skills/mcp-integration/SKILL.md) |
| `vector_db` | Semantic search and embeddings | `semantic_search, query_collection, vector_stats, list_collections` | Not for structural dependency analysis. | [`mcp-integration`](.codex/skills/mcp-integration/SKILL.md) |
| `playwright` | Browser automation, accessibility snapshots, end-to-end UI verification | `browser_navigate, browser_snapshot, browser_click, browser_fill_form, browser_evaluate, browser_take_screenshot` | Live UI/E2E; output in artifacts/mcp/playwright/ (gitignored). Close tabs after use. | [`mcp-integration`](.codex/skills/mcp-integration/SKILL.md) |
| `notion` | Notion pages and project-management databases | `API-query-data-source, API-retrieve-a-page, API-patch-page` | Manual page/DB read+write only; no plan-status enforcement (Notion plan/wave/status governance removed). | [`mcp-integration`](.codex/skills/mcp-integration/SKILL.md) |
| `context7` | Up-to-date, versioned official documentation for external libraries | `resolve-library-id, get-library-docs` | External package docs; not this repo. CONTEXT7_API_KEY optional. | [`mcp-integration`](.codex/skills/mcp-integration/SKILL.md) |

<!-- MCP-QUICK-REFERENCE:END -->

Server-specific MCP procedures are indexed by [`mcp-integration`](.codex/skills/mcp-integration/SKILL.md) sections §1–§13. `adg-sqlite` remains the dedicated structural-analysis skill.

## Notion Workspace Map

<!-- NOTION-MAP:START -->

Bot: **Agentic-Workflow** | Workspace: **Amit Ayer's Space**

| Database | Data Source ID (reads) | Database ID (writes) | Read Trigger | Write Trigger (auto-route) |
|----------|-----------------------|----------------------|--------------|----------------------------|
| Backlog Items | `fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7` | `aa8d2507-101e-4384-81d9-60ea3fe33876` | "plan status", "phase progress", "wave status", "what's blocked" — **but prefer the Backlog Snapshot page for top-N/dashboard queries (see below)** | On wave/phase completion or status change. The DEFERRED_SCOPE/NEXT_STEP auto-post hooks were retired (enforcement-surface-consolidation-d8b3f6 W7); out-of-scope work now surfaces via native spawn_task (constitutional §24 / ADR-096). The deferred_scope_scorer P-Band engine is retained for batch backlog scoring. |
| Plans | `ac53d31b-3068-4039-9ebe-856c12caab32` | `6aba34d9-4d0b-4f4c-b956-b2bdea541ca9` | "which plans exist", "plan status", "is this plan on disk" — relation target from Backlog Items.Plan | On new plan creation under `plans/<slug>-<6hex>.md` (repo-root SSOT). `.codex/plans/` is archive-only. Create Plans row with Status=Not Started, Exists On Disk=true, Plan File Path set. |
| SC/AP Violation Backlog | ~~`803834e1-0af8-4c3c-b45a-f513f80a7fef`~~ | ~~`0a3b8072-eabd-4516-9473-3c321bb011ff`~~ | \u274c **ARCHIVED 2026-05-02** | Filesystem SSOT: `artifacts/adg/*.sqlite` + violation JSON. No Notion write. |
| Constitutional Rules Registry | ~~`9bd2523e-7a6e-434d-89a7-ce4166457069`~~ | ~~`1c1379bc-32ca-4216-898a-3672f0316f69`~~ | \u274c **ARCHIVED 2026-05-02** | Filesystem SSOT: `.codex/rules/*.md`. No Notion write. |
| MCP Registry | ~~`e7b149b4-0496-4e98-a5dd-074dbe31881b`~~ | ~~`59693bbc-71b1-4c63-bc9f-b31eb8b08a0e`~~ | \u274c **ARCHIVED 2026-05-02** | Filesystem SSOT: root `.mcp.json` only. Deprecated compatibility copies are non-authoritative. |
| Anti-Pattern Burndown | ~~`4599fe37-8c24-4d89-96af-438b99a967c4`~~ | ~~`80b30bc9-6622-4288-aa4c-6fc526b6a5c5`~~ | ❌ **ARCHIVED 2026-05-11** (404 confirmed — DB not accessible to integration) | Filesystem SSOT: `artifacts/adg/` ratchet files are canonical. No Notion write. (See .codex/rules/notion-archived-databases.md.) |
| ADR Registry | ~~`e59d7640-dc09-48f9-8bdc-b0c94bf98c2a`~~ | ~~`6ed25e12-bd92-4352-ac7a-3a971311f024`~~ | ❌ **ARCHIVED 2026-05-02** | Filesystem SSOT: `docs/architecture/adr/ADR-NNN-*.md`. No Notion write. |
| Author-Gate Decision Ledger | ~~`5b60fdde-7259-491e-9f2d-e088f1f741ef`~~ | ~~`18bb9145-1320-4191-8b14-6c309776bcf5`~~ | ❌ **ARCHIVED 2026-05-02** | Filesystem SSOT: `.codex/state/refactor_decisions/refactor_decision_ledger.sqlite`. No Notion write. |

**Query pattern (reads)**: `API-query-data-source` with `data_source_id` from column 2. Add `filter`/`sorts` as needed.
**Write pattern (creates)**: `API-post-page` with `parent: {type: "database_id", database_id: <column 3>}`. Using data_source_id for writes returns 404.

<!-- NOTION-MAP:END -->

Procedural routing + manual-Notion-use note: [agents-tier1-companion.md](.codex/skills/mcp-integration/agents-tier1-companion.md). (Notion plan-status / wave / registration enforcement removed — `notion-wave-enforcement-removal`.)

## Memory

At session start, load native file memory from `memory/MEMORY.md`. For non-trivial work, also read `memory/codex/memory_summary.md` when Codex-specific run history, branch workflow memory, or repo-specific Codex skills could affect the task.

The knowledge-graph Memory MCP is optional for graph queries or writeback when its transport is healthy; if it fails, continue from file memory and do not retry-loop on the transport. Treat `C:\Users\amita\.codex\memories` and Codex product memories as global/user memory only; do not make them the SSOT for Agentic Workflow project memory.

## Constitutional floor

- Subprocess timeout always required — `subprocess.run(argv, shell=False, timeout=30)`. PowerShell is allowed as the primary Windows shell when commands remain bounded.
- No `pytest.mark.skip` without `strict=True`
- No bare `except Exception` without guardian
- No edits during planning phase
- ADG before grep for structure (§28); grep for literals/TODOs only
- Full rules: `AGENTS.md` + `docs/codex-primary-execution.md` · expanded lists: legacy compatibility notes only

## Plans

Lookup: `.codex/rules/codex-config-lookup.md` and `.codex/rules/plan-location.md`. New plans are disk-only under `plans/<name>-<6hex>.md`; `.codex/plans/` is an archive of migrated historical plans, not the write target for new work.

## Pytest

Pytest runs with plugin **autoload ON** (CI default); `addopts` carries `--timeout=180` but no `-p pytest_timeout`. **Do NOT** set `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` for ad-hoc runs — it strips pytest-timeout and `--timeout` aborts collection. See companion for the duplicate-registration caveat (don't add `-p pytest_timeout` either).

## Core vs apps (summary)

Apps customize inputs; core enforces contracts. No app leakage in `agentic_core` without migration receipt. **Multi-provider X1D proof panels:** `agentic_core/runtime/judges/panel/` (`JudgePanelRunner`, transport preflight); `apps_rg` wires adapters via `x1d_panel_bridge` (see plan [core-judge-panel-harness-f3c8d1](plans/core-judge-panel-harness-f3c8d1.md)). Detail: [`agentic_core/AGENTS.md`](agentic_core/AGENTS.md) · `.codex/rules/agentic-core-static.md` (legacy reference only).

## Rules & Skills SSOT

Procedural MCP / Notion / ledgers: `scripts/governance/**`, `.codex/**`, and `docs/reports/codex/**` cover the active Codex flow. Plan location (disk-only): [`plan-location.md`](.codex/rules/plan-location.md).

| Layer | Path | Notes |
|-------|------|-------|
| Always-on rules | `AGENTS.md` + `docs/codex-primary-execution.md` | Active Codex governance contract and rule floor |
| On-demand rules | `.codex/rules/*.md` + `scripts/governance/**` | Load by task surface and file scope |
| Skills | `.codex/skills/*/SKILL.md` | Repo-owned Codex procedural adapters |
| Hooks | `.codex/hooks.json` + `.codex/hooks/**` | Native Codex hook registry and hook entrypoints |
| Index | `docs/reports/codex/` + historical rule-index references | Generated route evidence and historical references only |
| Deprecated compatibility shims | docs/archive and `_legacy_*` shims | Non-authoritative compatibility/archive only; edit Codex-owned files |

**Dedup:** Do not restate always-on invariants in compatibility stubs or hook reminders. Active procedure lives in `AGENTS.md` and `docs/codex-primary-execution.md`; retired rule and skill names remain historical only.

Governance inventory: [`governance_tier_inventory.json`](docs/reports/cursor/governance_tier_inventory.json) · dedup audit: [`governance_dedup_audit_20260526.md`](docs/reports/cursor/governance_dedup_audit_20260526.md) · closeout plan: [`governance-dedup-closeout-e8a4c2.md`](plans/governance-dedup-closeout-e8a4c2.md).

## Codex primary execution adapter

Codex is the primary local execution surface for this repo. Repo-owned governance files remain the versioned rule inputs; Codex owns run readiness, execution evidence, and closeout receipts.

- Primary contract: [`docs/codex-primary-execution.md`](docs/codex-primary-execution.md).
- Repo-specific Codex enforcement files, including cadence automation contracts, live under `.codex/automations/`. The user profile at `C:\Users\amita\.codex\automations` may contain only generated launcher mirrors with repo path and digest metadata. Mirrors may carry UI/runtime fields copied from the repo contract (`prompt`, `model`, `reasoning_effort`, `execution_environment`, `cwds`) so Codex Desktop can display and run them, but they must validate exactly against the repo-owned contract and must not carry hand-edited or stale payloads, handoff metadata, runtime optimization metadata, or other independent contract authority.
- Before long Codex-primary runs, execute `python scripts/governance/codex_readiness.py --json`; add `--require-clean-worktree --fail-duplicate-processes` for strict proof/eval preflight.
- For post-publication closeout, use `python scripts/governance/codex_main_closeout.py --check --json --publication-only`; local cleanup may use `--apply` only for clean, ancestor-contained branches/worktrees.
- Direct PR completion commands (`gh pr merge` or push-to-main) must chain `codex_main_closeout.py --apply --fetch --json --publication-only` and `codex_main_closeout.py --check --fetch --json --publication-only` in the same shell command, then run strict topology closeout as evidence.
- Validate the repo-owned enforcement home with `python scripts/governance/verify_codex_enforcement_home.py --json`.
- Validate and run Codex preflights with `python scripts/governance/codex_readiness.py --json`; primary enforcement must not depend on any legacy non-Codex governance directory or hook parity path.
- Codex must ask a plain-text clarifying question directly in the assistant response before editing whenever a turn cannot proceed safely without a user choice; do not assume a branch or defer to a missing prompt surface.
- Substantial Codex runs should emit a JSON run receipt and validate it with `python scripts/governance/verify_codex_run_receipt.py <receipt.json>`.
- Validate this primary adapter with `python scripts/governance/verify_codex_primary.py` after changing Codex execution docs or scripts.
- Do not create a second rule or MCP registry. Codex consumes repo-owned rules under `.codex` and records live route evidence under `docs/reports/codex/`.

## Codex-Only Enforcement

The repo must stay Codex-only:

- Legacy non-Codex governance directories are forbidden.
- Active hook registration lives in `.codex/hooks.json`.
- Active hook entrypoints live in `.codex/hooks/**`.
- Active repo Codex governance assets live in `.codex/rules`, `.codex/skills`, `.codex/governance`, `.codex/schemas`, `.codex/templates`, and `.codex/state`.
- Active skills live only under `.codex/skills`; root `.agents` and `memory/codex/skills` must not contain Agentic-Workflow execution surfaces.
- Active plan files live under repo-root `plans/`; `.codex/plans` is archive-only.
- `scripts/governance/verify_codex_primary.py` is the guard for this contract and must pass after governance changes.
