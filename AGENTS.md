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

**For T2/T3 tasks, emit this block before any tool calls:**

```
## SR_INTAKE
Objective: <one sentence>
Constraints: [list]
Assumptions: [list]
Tier: T2 | T3

## SR_PLAN
1. [verb-first step]
2. ...
N. [verification step]

Tools needed: [list]
Risks: [list]
```

Then gather evidence (reads only). Then emit `SR_APPROVAL: APPROVED` before any writes or edits.

**T0/T1 tasks (single file, ≤20 lines, questions) are exempt — answer or edit directly.**

## Layer Separation

Keep these four layers separate at all times:

| Layer | Rule |
|-------|------|
| Reasoning | Native Cascade only — no tool calls |
| Routing | Tool selection and MCP health checks only |
| Execution | Edits/writes/commands — only after SR_APPROVAL |
| Verification | Tests, diffs, health checks — after execution |

## MCP Quick Reference

> Stable IDs are the `mcpServers` keys in `.windsurf/mcp_config.json`. Live tool prefixes like `mcp0_`, `mcp1_`, and so on can shift when server order changes. Resolve the live prefix from the current tool list in-session.

<!-- MCP-QUICK-REFERENCE:START -->

| Server ID | Use For | Example Tools | Notes |
|---|---|---|---|
| `GitKraken` | Git operations, GitLens, pull requests, issues | `git_status, git_add_or_commit, git_log_or_diff, pull_request_create` | Use as the git/PR authority. |
| `adg_sqlite` | Dependency graph, blast radius, layer analysis | `adg_health, adg_edge_fanout, adg_edge_fanin, adg_nodes_by_file` | Primary authority for structural dependencies. |
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

| Database | Data Source ID | Read Trigger (query) | Write Trigger (auto-route) |
|----------|---------------|-----------------|--------------------------|
| Wave/Phase Convergence | `fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7` | "plan status", "phase progress", "wave status", "what's blocked" | On wave/phase completion or status change |
| SC/AP Violation Backlog | `803834e1-0af8-4c3c-b45a-f513f80a7fef` | "SC/AP violations", "check severity", "promotion status" | When `generate_full_adg` emits new SC/AP rows |
| HITL Decision Ledger | `5b60fdde-7259-491e-9f2d-e088f1f741ef` | "HITL decisions", "past decisions", "decision history" | Immediately after any scored `ask_user_question` resolution |
| Constitutional Rules Registry | `9bd2523e-7a6e-434d-89a7-ce4166457069` | "constitutional rules", "rule status" | On rule addition/modification |
| MCP Registry | `e7b149b4-0496-4e98-a5dd-074dbe31881b` | "MCP status", "which MCPs are active", "server registry" | On ANY `mcp_config.json` change or gate-behavior change |
| SVP Engineering Reviews | `814e26d3-d665-4472-9b92-c7e0f89241d0` | "SVP review", "module certification", "test pass rate" | On SVP review completion |
| ADR Registry | `e59d7640-dc09-48f9-8bdc-b0c94bf98c2a` | "ADR status", "architectural decisions", "which ADRs" | On every new ADR spec file — POST row with ADR ID, Status, Impact Layers, Summary, Filename |
| Anti-Pattern Burndown | `4599fe37-8c24-4d89-96af-438b99a967c4` | "anti-pattern counts", "burndown trend", "ratchet ceiling" | On burndown run or ratchet adjustment |

**Query pattern**: `API-query-data-source` with `data_source_id` from table above. Add `filter`/`sorts` as needed.

<!-- NOTION-MAP:END -->

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

- Live tool prefixes are dynamic. Use stable server IDs from `.windsurf/mcp_config.json` and resolve the current `mcpN_` prefix from the tool list visible in-session.
- Local docs: `docs/windsurf/llms-full.txt` (broad coverage), `docs/windsurf/*.md` (per-topic Markdown)
- Check local docs first. Use web search only for version-sensitive or newly-changed features.
- Prefer `docs/windsurf/changelog.md` when the question may depend on recent product changes.
- If local docs conflict with observed product behavior, note possible staleness and verify against live docs.
- Hooks: `command`, `show_output`, `working_directory` only — `file_pattern` is non-standard and FORBIDDEN.
- Skills: entry file MUST be `SKILL.md` (uppercase). Supporting files live alongside it in the skill directory.
- Rules: `model_decision` and `glob` triggers MUST have a single-sentence `description` field in frontmatter.
- Plans SSOT: `.windsurf/plans/<name>-<6hex>.md` — never `C:\Users\*\` or `docs/reports/plans/`.
