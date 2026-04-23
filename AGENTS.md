# Agent Guidance — Agentic-Workflow

## Plan First. Execute Second.

## AGENTS.md Scope

- Root-level `AGENTS.md` is always on for the whole workspace.
- Subdirectory `AGENTS.md` files are supported for directory-scoped guidance.
- Keep root guidance global, and push specialized instructions down into subdirectories when scope is narrower.

**For complex tasks (T2/T3), the first output MUST be a plan — never edits.**

A task is T2/T3 if it involves:
- 2 or more files
- Cross-layer changes (e.g. L0→L3)
- Architecture decisions
- Multi-file debugging
- New features or refactoring affecting more than one module

**For T2/T3 tasks**, invoke the `structured-reasoning` skill. Emit `SR_INTAKE` → `SR_PLAN` → gather evidence → `SR_APPROVAL: APPROVED` → `SR_EXECUTE` → `SR_VERIFY`. See `.windsurf/rules/sequential-thinking-enforcement.md` for the full packet shape.

**T0/T1 tasks** (single file, ≤20 lines, questions) are exempt — answer or edit directly.

## Layer Separation

Keep Reasoning / Routing / Execution / Verification separate. No edits before `SR_APPROVAL`.

## MCP Quick Reference

> Stable IDs are the `mcpServers` keys in `.windsurf/mcp_config.json`. Live tool prefixes like `mcp0_`, `mcp1_`, and so on can shift when server order changes. Resolve the live prefix from the current tool list in-session.

<!-- MCP-QUICK-REFERENCE:START -->

| Server ID | Use For | Example Tools | Notes |
|---|---|---|---|
| `GitKraken` | Git operations, GitLens, pull requests, issues | `git_status, git_add_or_commit, git_log_or_diff, pull_request_create` | Use as the git/PR authority. |
| `adg_sqlite` | Dependency graph, blast radius, layer analysis, refactoring hotspots, graph-layer primitives (mv_*, v_p*, semantic edges) | `adg_health, adg_edge_fanout, adg_edge_fanin, adg_nodes_by_file, adg_nodes_by_layer, adg_violations, adg_p0_wave_plan` | Primary authority for structural dependencies AND refactoring analysis. Constitutional §22: mv_* materialized views, v_p0_*/v_p1_*/v_p2_*/v_p3_* P-views, and semantic edges (flows_to, reads_from, writes_to, emits_side_effect, controls_flow, resolves_callsite) MUST drive T2/T3 refactoring plans. |
| `deepwiki` | External GitHub repository docs and wiki Q&A | `read_wiki_structure, read_wiki_contents, ask_question` | Do not use for this repo's own code. |
| `enhanced_http` | Programmatic HTTP calls, webhooks, endpoint checks | `http_get, http_post, test_connectivity, batch_requests` | Use for autonomous/programmatic HTTP only. |
| `filesystem` | Filesystem MCP operations and directory traversal | `read_text_file, read_multiple_files, directory_tree, write_file` | Prefer native reads for ordinary file reads when available. |
| `memory` | Persistent cross-session knowledge graph | `mem_recall_session_start, create_entities, add_observations, search_nodes` | Read at session start; write back major decisions. |
| `vector_db` | Semantic search and embeddings | `semantic_search, query_collection, vector_stats, list_collections` | Not for structural dependency analysis. |
| `otel_mcp` | Telemetry, traces, anomalies, runtime ADG ingest | `otel_server_info, otel_trace, otel_anomalies, otel_ingest_to_runtime_adg` | Check otel_server_info before restart logic. |
| `task_manager` | Task decomposition and task state tracking | `create_task, decompose_task, update_task, task_info` | Use when the user explicitly wants tracked multi-step work. |
| `redis` | Redis cache health, keys, TTL, namespace stats | `redis_health, redis_keys, redis_hgetall, redis_namespace_stats` | Use for hot-cache inspection and invalidation. |
| `pytest_mcp` | Test discovery, runs, and coverage | `discover_tests, run_tests, get_test_details, analyze_test_coverage` | Prefer over plain pytest CLI when possible. |
| `notion` | Notion pages and project-management databases | `API-query-data-source, API-retrieve-a-page, API-patch-page` | Use for ADRs, HITL ledgers, MCP registry, and plan/status data. |

<!-- MCP-QUICK-REFERENCE:END -->
## Notion Workspace Map

<!-- NOTION-MAP:START -->

Bot: **Agentic-Workflow** | Workspace: **Amit Ayer's Space**

| Database | Data Source ID (reads) | Database ID (writes) | Read Trigger | Write Trigger (auto-route) |
|----------|-----------------------|----------------------|--------------|----------------------------|
| Backlog Items | `fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7` | `aa8d2507-101e-4384-81d9-60ea3fe33876` | "plan status", "phase progress", "wave status", "what's blocked" — **but prefer the Backlog Snapshot page for top-N/dashboard queries (see below)** | On wave/phase completion or status change. Post-hook `post_cascade_deferred_scope_capture.py` auto-posts from DEFERRED_SCOPE markers with scorer-assigned P-Band. |
| Plans | `ac53d31b-3068-4039-9ebe-856c12caab32` | `6aba34d9-4d0b-4f4c-b956-b2bdea541ca9` | "which plans exist", "plan status", "is this plan on disk" — relation target from Backlog Items.Plan | On new plan file creation under `.windsurf/plans/<slug>-<6hex>.md`. Create Plans row with Status=Active, Exists On Disk=true, Plan File Path set. |
| SC/AP Violation Backlog | `803834e1-0af8-4c3c-b45a-f513f80a7fef` | `0a3b8072-eabd-4516-9473-3c321bb011ff` | "SC/AP violations", "check severity", "promotion status" | When `generate_full_adg` emits new SC/AP rows |
| HITL Decision Ledger | `5b60fdde-7259-491e-9f2d-e088f1f741ef` | `18bb9145-1320-4191-8b14-6c309776bcf5` | "HITL decisions", "past decisions", "decision history" | Immediately after any scored `ask_user_question` resolution |
| Constitutional Rules Registry | `9bd2523e-7a6e-434d-89a7-ce4166457069` | `1c1379bc-32ca-4216-898a-3672f0316f69` | "constitutional rules", "rule status" | On rule addition/modification |
| MCP Registry | `e7b149b4-0496-4e98-a5dd-074dbe31881b` | `59693bbc-71b1-4c63-bc9f-b31eb8b08a0e` | "MCP status", "which MCPs are active", "server registry" | On ANY `mcp_config.json` change or gate-behavior change |
| SVP Engineering Reviews | `814e26d3-d665-4472-9b92-c7e0f89241d0` | `6660be70-638e-4698-826a-aa7e8c17d7fd` | "SVP review", "module certification", "test pass rate" | On SVP review completion |
| ADR Registry | `e59d7640-dc09-48f9-8bdc-b0c94bf98c2a` | `6ed25e12-bd92-4352-ac7a-3a971311f024` | "ADR status", "architectural decisions", "which ADRs" | On every new ADR spec file — POST row with ADR ID, Status, Impact Layers, Summary, Filename |
| Anti-Pattern Burndown | `4599fe37-8c24-4d89-96af-438b99a967c4` | `80b30bc9-6622-4288-aa4c-6fc526b6a5c5` | "anti-pattern counts", "burndown trend", "ratchet ceiling" | On burndown run or ratchet adjustment |

**Query pattern (reads)**: `API-query-data-source` with `data_source_id` from column 2. Add `filter`/`sorts` as needed.
**Write pattern (creates)**: `API-post-page` with `parent: {type: "database_id", database_id: <column 3>}`. Using data_source_id for writes returns 404.

<!-- NOTION-MAP:END -->

### Backlog Snapshot — preferred read path (added 2026-04-23)

For any **dashboard / top-N / "what's the current state of the backlog"** question, prefer **one** `API-get-block-children` call on the Backlog Snapshot page over paginating Wave/Phase Convergence:

- **Page ID**: `34b27693-f55c-81b4-93ba-efec5755a20e`
- **Content**: top-25 open P1+P2 by Impact Score, band distribution, stale flags — pre-rendered markdown
- **Size**: ~5 KB vs. ~170 KB for full paginated query
- **Regenerate**: `python tools/notion/snapshot_renderer.py --regenerate` (~4 s, uses only the typed fields backfilled in W1/W2)

Use `API-query-data-source` on Wave/Phase Convergence only when you need a specific filter/sort not in the snapshot (e.g., all rows linked to a specific `Plan` relation).

### Auto-Routing Rules (proactive — do NOT wait for a prompt)

Cascade MUST route these events to Notion without being asked. Filesystem remains SSOT for the full artifact; Notion holds the searchable row.

| Event in Cascade | Filesystem Artifact | Notion Write (parallel) |
|---|---|---|
| Create `docs/architecture/adr/ADR-NNN-*.md` | ADR markdown | `API-post-page` into ADR Registry with ADR ID, Status, Decision Date, Impact Layers, Summary, Filename, Deciders |
| Modify `.windsurf/mcp_config.json` (add/remove/reconfigure server) | JSON edit | `API-patch-page` (or post new) into MCP Registry with Notes + updated Last Validated; link ADR if applicable |
| Change gate behavior in `.windsurf/scripts/pre_mcp_gate.py` | Python edit | `API-patch-page` affected MCP Registry entries with Notes (behavior description) + Linked ADR |
| Resolve a scored HITL decision via `ask_user_question` | — | `API-post-page` into HITL Decision Ledger with decision type, options, selection, rationale |
| Run `generate_full_adg.py` and produce SC/AP defects | `artifacts/adg/*.sqlite`, violation JSON | `API-post-page` per NEW violation into SC/AP Violation Backlog |
| Write RCA in `docs/reports/plans/*.md` | Markdown | Link from relevant registry row (no new database — RCA detail lives on disk) |

**Non-goals**: do NOT duplicate narrative content in Notion. Store the row; link the file.

### Sync Enforcement

Two existing gates validate AGENTS.md ↔ `.windsurf/mcp_config.json` consistency. Both are wired into pre-commit (`.pre-commit-config.yaml`) and invoked by `run_contract_gates.py`:

| Gate | Scope |
|---|---|
| `ops_scripts/ci/check_mcp_sync_integrity.py` | **Strict**: compares exact Quick Reference content against the canonical output of `.windsurf/scripts/sync_mcp_config.py`. Fails if any row drifts. |
| `ops_scripts/ci/check_agents_mcp_coverage.py` | **Coverage**: every `mcpServers` key in mcp_config.json must appear as a row in the Quick Reference. |

Run manually:
```bash
python ops_scripts/ci/check_mcp_sync_integrity.py  # strict content check
python ops_scripts/ci/check_agents_mcp_coverage.py # coverage check
```

Auto-regeneration (when drift is detected):
```bash
python .windsurf/scripts/sync_mcp_config.py  # rewrites AGENTS.md Quick Reference block
```

## Memory Lifecycle

Detailed read/write/maintain triggers and entity-type conventions live in `.windsurf/rules/agents-memory-lifecycle.md` (model_decision). Key session-start requirement: **first tool call of every session is `mem_recall_session_start`** (constitutional §17).

## Constitutional Constraints (always-on)

- No PowerShell — use `subprocess.run(argv, shell=False)` or `run_command`
- No `pytest.mark.skip` without `strict=True`
- No `except Exception` without guardian exemption
- No edits during planning phase
- ADG graph is the primary analysis primitive — not grep

Full rules: `.windsurf/rules/` and `.windsurf/RULES_INDEX.md`

## Windsurf Configuration Docs

See `.windsurf/rules/windsurf-config-lookup.md` for the full local-first lookup order. Local docs mirror: `docs/windsurf/`. Plans SSOT: `.windsurf/plans/<name>-<6hex>.md` — never `C:\Users\*\` or `docs/reports/plans/`.
