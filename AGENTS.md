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

| Server ID | Use For | Example Tools | Notes | Skill |
|---|---|---|---|---|
| `GitKraken` | Git operations, GitLens, pull requests, issues | `git_status, git_add_or_commit, git_log_or_diff, pull_request_create` | Use as the git/PR authority. | [`gitkraken`](.windsurf/skills/gitkraken/SKILL.md) |
| `adg_sqlite` | Dependency graph, blast radius, layer analysis, refactoring hotspots, graph-layer primitives (mv_*, v_p*, semantic edges) | `adg_health, adg_edge_fanout, adg_edge_fanin, adg_nodes_by_file, adg_nodes_by_layer, adg_violations, adg_p0_wave_plan` | Primary authority for structural dependencies AND refactoring analysis. Constitutional §22: mv_* materialized views, v_p0_*/v_p1_*/v_p2_*/v_p3_* P-views, and semantic edges (flows_to, reads_from, writes_to, emits_side_effect, controls_flow, resolves_callsite) MUST drive T2/T3 refactoring plans. | [`adg-sqlite`](.windsurf/skills/adg-sqlite/SKILL.md) |
| `deepwiki` | External GitHub repository docs and wiki Q&A | `read_wiki_structure, read_wiki_contents, ask_question` | Do not use for this repo's own code. | [`deepwiki`](.windsurf/skills/deepwiki/SKILL.md) |
| `filesystem` | Filesystem MCP operations and directory traversal | `read_text_file, read_multiple_files, directory_tree, write_file` | Prefer native reads for ordinary file reads when available. | [`filesystem-mcp`](.windsurf/skills/filesystem-mcp/SKILL.md) |
| `memory` | Persistent cross-session knowledge graph | `mem_recall_session_start, create_entities, add_observations, search_nodes` | Read at session start; write back major decisions. | [`memory-mcp`](.windsurf/skills/memory-mcp/SKILL.md) |
| `vector_db` | Semantic search and embeddings | `semantic_search, query_collection, vector_stats, list_collections` | Not for structural dependency analysis. | [`vector-db`](.windsurf/skills/vector-db/SKILL.md) |
| `otel_mcp` | Telemetry, traces, anomalies, runtime ADG ingest | `otel_server_info, otel_trace, otel_anomalies, otel_ingest_to_runtime_adg` | Check otel_server_info before restart logic. | [`otel-telemetry`](.windsurf/skills/otel-telemetry/SKILL.md) |
| `task_manager` | Task decomposition and task state tracking | `create_task, decompose_task, update_task, task_info` | Use when the user explicitly wants tracked multi-step work. | [`task-manager-mcp`](.windsurf/skills/task-manager-mcp/SKILL.md) |
| `redis` | Redis cache health, keys, TTL, namespace stats | `redis_health, redis_keys, redis_hgetall, redis_namespace_stats` | Use for hot-cache inspection and invalidation. | [`redis-cache`](.windsurf/skills/redis-cache/SKILL.md) |
| `pytest_mcp` | Test discovery, runs, and coverage | `discover_tests, run_tests, get_test_details, analyze_test_coverage` | Prefer over plain pytest CLI when possible. | [`pytest-mcp`](.windsurf/skills/pytest-mcp/SKILL.md) |
| `io.windsurf/mcp-playwright` | Browser automation, accessibility snapshots, end-to-end UI verification | `browser_navigate, browser_snapshot, browser_click, browser_fill_form, browser_evaluate, browser_take_screenshot` | Official Microsoft @playwright/mcp thin npx wrapper. Use for live UI/E2E checks, not for static HTML fetching (use direct httpx in code or read_url_content for one-off fetches). Output lands in repo-root .playwright-mcp/ (gitignored). Always close tabs after use. | [`playwright`](.windsurf/skills/playwright/SKILL.md) |
| `notion` | Notion pages and project-management databases | `API-query-data-source, API-retrieve-a-page, API-patch-page` | Use for Plans DB, Backlog Items, and Anti-Pattern Burndown. MCP Registry, ADR Registry, Constitutional Rules Registry, SC/AP Violation Backlog, and Author-Gate Decision Ledger are **archived** — filesystem SSOT only. | [`notion`](.windsurf/skills/notion/SKILL.md) |
| `tavily` | AI-optimized web search, extraction, crawling, and site mapping | `tavily-search, tavily-extract, tavily-crawl, tavily-map` | Sole authority for web search. Use for upstream-issue research (Anthropic MCP race, chromadb bugs), ADR background, and domain research not answerable by deepwiki (GitHub-only) or one-off URL fetch via read_url_content. Requires TAVILY_API_KEY OS env var. | [`tavily-research`](.windsurf/skills/tavily-research/SKILL.md) |
| `context7` | Up-to-date, versioned official documentation for external libraries | `resolve-library-id, get-library-docs` | Use for external-package docs (chromadb, FastMCP, sentence-transformers, playwright, pytorch). Distinct from deepwiki (GitHub repo wiki/Q&A) and adg_sqlite (this repo's own code). No API key required; CONTEXT7_API_KEY optional for higher limits. | [`context7`](.windsurf/skills/context7/SKILL.md) |

<!-- MCP-QUICK-REFERENCE:END -->
## Notion Workspace Map

<!-- NOTION-MAP:START -->

Bot: **Agentic-Workflow** | Workspace: **Amit Ayer's Space**

| Database | Data Source ID (reads) | Database ID (writes) | Read Trigger | Write Trigger (auto-route) |
|----------|-----------------------|----------------------|--------------|----------------------------|
| Backlog Items | `fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7` | `aa8d2507-101e-4384-81d9-60ea3fe33876` | "plan status", "phase progress", "wave status", "what's blocked" — **but prefer the Backlog Snapshot page for top-N/dashboard queries (see below)** | On wave/phase completion or status change. Post-hook `post_cascade_deferred_scope_capture.py` auto-posts from DEFERRED_SCOPE markers with scorer-assigned P-Band. |
| Plans | `ac53d31b-3068-4039-9ebe-856c12caab32` | `ac53d31b-3068-4039-9ebe-856c12caab32` | "which plans exist", "plan status", "is this plan on disk" — relation target from Backlog Items.Plan | On new plan file creation under `.windsurf/plans/<slug>-<6hex>.md`: emit `PLAN_CREATED:` marker AND post Plans row with Slug, Status (Not Started/In Progress), Exists On Disk=true, Plan File Path, Summary, AI Summary. **Enforced by constitutional §36** — `wave_execution_state.py start` blocks on unregistered plans. CI gate T7u: `check_plan_registration_freshness.py`. **Wave/phase auto-sync (2026-05-10, plan `notion-wave-lifecycle-autosync-f4a2b8`)**: `wave_execution_state.py {start,wave-progress,complete}` and `post_cascade_wave_lifecycle_capture.py` patch Status + Summary via direct HTTP (sanctioned non-MCP path per `notion-plan-wave-deferral.md`); CI backstop NP4 `check_plan_notion_wave_freshness.py`. Bypass: `PLAN_REGISTRATION_BYPASS=1`, `WAVE_LIFECYCLE_NOTION_BYPASS=1`, `WAVE_LIFECYCLE_CAPTURE_BYPASS=1`. |
| SC/AP Violation Backlog | ~~`803834e1-0af8-4c3c-b45a-f513f80a7fef`~~ | ~~`0a3b8072-eabd-4516-9473-3c321bb011ff`~~ | ❌ **ARCHIVED 2026-05-02** | Filesystem SSOT: `artifacts/adg/*.sqlite` + violation JSON. No Notion write. |
| Constitutional Rules Registry | ~~`9bd2523e-7a6e-434d-89a7-ce4166457069`~~ | ~~`1c1379bc-32ca-4216-898a-3672f0316f69`~~ | ❌ **ARCHIVED 2026-05-02** | Filesystem SSOT: `.windsurf/rules/*.md`. No Notion write. |
| MCP Registry | ~~`e7b149b4-0496-4e98-a5dd-074dbe31881b`~~ | ~~`59693bbc-71b1-4c63-bc9f-b31eb8b08a0e`~~ | ❌ **ARCHIVED 2026-05-02** | Filesystem SSOT: `.windsurf/mcp_config.json`. No Notion write. |
| Anti-Pattern Burndown | `4599fe37-8c24-4d89-96af-438b99a967c4` | `80b30bc9-6622-4288-aa4c-6fc526b6a5c5` | "anti-pattern counts", "burndown trend", "ratchet ceiling" | On burndown run or ratchet adjustment |

**Query pattern (reads)**: `API-query-data-source` with `data_source_id` from column 2.
**Write pattern (creates)**: `API-post-page` with `parent: {type: "data_source_id", data_source_id: <column 2>}`. The legacy `database_id` parent type returns 404 for Plans DB as of 2026-05-06.

**Backlog Items → Plan linkage invariant (NP3, plan `backlog-plan-linkage-enforcement-a4b2f1`):** Every Backlog Items row must have a `Plan` relation OR a non-empty `Plan File` slug. True orphans (neither) are flagged by CI gate NP3 (`ops_scripts/ci/check_notion_backlog_plan_linkage.py`). Fix procedure: re-run `tools/notion/backfill_backlog_plan_relation.py`. Authoritative-source policy: Plan-derived Status wins only when Backlog Status is the scorer-default (`Draft`); Layer and Plan File are always Backlog-authoritative. Rule: `.windsurf/rules/notion-backlog-plan-linkage.md`.

<!-- NOTION-MAP:END -->

### Filesystem-SSOT Canonical Sources (No Notion Mirror)

| Content | Canonical Path | Notion Mirror? | Notes |
|---------|----------------|----------------|-------|
| Rules | `.windsurf/rules/*.md` | **NO** — archived 2026-05-02 | 47 rules, filesystem-SSOT only. Use `rg` to search. |
| ADRs | `docs/architecture/adr/*.md` | **NO** — since 2026-05-02 | Filename + metadata in frontmatter. Use `rg` to search. |
| Plans | `.windsurf/plans/<slug>-<6hex>.md` | Row in Plans DB only | Full content on disk; Notion holds status/summary row. |
| Calibration Reports | `docs/reports/calibration/<YYYY-Www>.md` | **NO** — by design | Weekly reports filesystem-only per operator decision 2026-04-24. |

> ⛔ **Do NOT attempt to sync rules or ADRs to Notion.** The Constitutional Rules Registry and ADR Registry databases were archived on 2026-05-02 as part of Notion consolidation. Filesystem is the sole SSOT.

### Plans + Backlog Status Taxonomy (extracted 2026-05-02)

The 5-status taxonomy (🟢Live · 🟡Draft · 🔵Completed · 🟣Retired · ⚪Archived), Plans-DB invariants (Live ⇒ Exists On Disk=true · 14-day edit recency · descope path), Backlog-DB shared-taxonomy deltas, migration history, and the **Backlog Snapshot read-path** (page `34b27693-f55c-81b4-93ba-efec5755a20e`, regenerator `python tools/notion/snapshot_renderer.py --regenerate`) all live in conditional rule `@.windsurf/rules/notion-plans-taxonomy.md`. Auto-loads when working with Notion Plans / Backlog Items / status / taxonomy queries.

### Auto-Routing Rules (proactive — do NOT wait for a prompt)

Cascade MUST route these events to Notion without being asked. Filesystem remains SSOT for the full artifact; Notion holds the searchable row.

| Event in Cascade | Filesystem Artifact | Notion Write (parallel) |
|---|---|---|
| Create `docs/architecture/adr/ADR-NNN-*.md` | ADR markdown | **No Notion write** — on-disk ADR file IS the SSOT since commit `b11200e833` (2026-05-02 consolidation). Filename + metadata live in the markdown frontmatter. Use `rg` over `docs/architecture/adr/` for search. |
| Modify `.windsurf/mcp_config.json` (add/remove/reconfigure server) | JSON edit | **No Notion write** — MCP Registry archived 2026-05-02. Document in commit message. Filesystem SSOT only. |
| Change gate behavior in `.windsurf/scripts/pre_mcp_gate.py` | Python edit | **No Notion write** — MCP Registry archived 2026-05-02. Document in commit message. Filesystem SSOT only. |
| Resolve a scored `ask_user_question` (Author-Gate decision) | `.windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite` | **No Notion write** — Author-Gate Decision Ledger archived 2026-05-02. SQLite ledger + `DECISION_CAPTURED:` marker is the SSOT (constitutional §30). |
| Run `generate_full_adg.py` and produce SC/AP defects | `artifacts/adg/*.sqlite`, violation JSON | **No Notion write** — SC/AP Violation Backlog archived 2026-05-02. Violations recorded in ADG SQLite snapshot only. |
| Write RCA in `docs/reports/plans/*.md` | Markdown | Link from relevant registry row (no new database — RCA detail lives on disk) |
| `generate_mutation_rejection_report.py` finds a newly-accepted mutation (Constitutional §32) | `artifacts/certification/fortknox_mutation_rejection_report.json` | **No Notion write** — SC/AP Violation Backlog archived 2026-05-02. Regression logged in `artifacts/certification/fortknox_mutation_rejection_report.json` only. |
| Trust level changes in Fort Knox bundle (e.g. `DEVELOPMENT_PROOF` → `INTEGRITY_PROOF`) | `artifacts/certification/final_requirement_signoff_report.json` | **No Notion write** — trust-level transitions are recorded in the certification bundle's `trust_level` field (verifiable via `scripts/verify_final_requirement_signoff_bundle.py`). If human-readable narrative is needed, author an ADR markdown file at `docs/architecture/adr/` (on-disk SSOT). |
| Positive-control set grows (new `RTC-REQ-*` joins SIGNED_OFF via compiler run) | `certification/evidence_assertions.jsonl` (new rows) + compiler output | `API-patch-page` Wave/Phase Convergence row for that req with Status → Done and evidence pointers |

> ⛔ **Archived Notion databases (2026-05-02 consolidation):** MCP Registry, Constitutional Rules Registry, SC/AP Violation Backlog, ADR Registry, and Author-Gate Decision Ledger are all archived. All formerly targeted writes to these databases are now filesystem-only. Do NOT attempt to write to these databases. See `.windsurf/rules/notion-archived-databases.md`.

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

## Test Environment — `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`

The dev environment sets `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` globally as a security-conscious hardening measure (prevents pytest from auto-loading plugins via `setuptools` entry points). With autoload disabled, pytest plugins must be loaded **explicitly** via the `-p` flag in `pytest.ini` `addopts`, otherwise pytest reports plugin-supplied flags as "unrecognized arguments" even when the plugins ARE installed in `site-packages`.

The fix lives in `pytest.ini`:

```
addopts = -p xdist -n 24 --dist=worksteal --timeout=180 ...
```

**If you add a new pytest plugin** (e.g. `pytest-mock`, `pytest-cov`), prepend `-p <import-name>` to `addopts` BEFORE any flag the plugin supplies. Caveat: if the plugin is already loaded transitively (e.g. via a `conftest.py` `pytest_plugins = [...]` entry, like `pytest-timeout` is here), do NOT add an explicit `-p` for it — pytest will refuse to register the same module under two different names. Failure precedent: 2026-04-30 — `pytest-xdist 3.8.0` and `pytest-timeout 2.4.0` were installed but pytest 9.0.3 refused to recognize `-n` / `--dist` / `--timeout` until `-p xdist` was added explicitly. Adding `-p pytest_timeout` triggered a duplicate-registration error because pytest-timeout was already being loaded by a conftest.

## Intelligence Ledger Family (ADR-050)

Ten per-decision-class SQLite ledgers under `artifacts/ledgers/` capture prediction vs outcome for every high-leverage decision Cascade makes. Use `LedgerConsulter("<name>").lookup(...)` to pull precedent **before** acting.

| Ledger | Writer Hook | Consulting Skill | Captures |
|---|---|---|---|
| `tool_routing` | `post_cascade_adg_audit.py` | `ledger-consulter-tool-routing` | grep-for-deps audits, retrieval-tool choice |
| `refactor_outcome` | `post_commit_outcome_binder.py` | `ledger-consulter-refactor-outcome` | commit-bound refactor-class decisions |
| `prompt_classifier` | `pre_prompt_classifier.py` (predict) + `ops_scripts/calibration/prompt_classifier_binder.py` (bind) | `ledger-consulter-prompt-classifier` | T0/T1/T2/T3 tier predictions with actual files_edited/lines/layers |
| `mcp_invocation` | `post_mcp_audit.py` | `ledger-consulter-mcp-invocation` | per-MCP latency, server, tool |
| `hotspot_defect` | `ops_scripts/calibration/hotspot_defect_join.py` | `ledger-consulter-hotspot-defect` | predicted rank vs 30d churn |
| `deferred_scope_calibration` | `ops_scripts/calibration/deferred_scope_poller.py` | `ledger-consulter-deferred-scope-calibration` | P-band vs days-to-done |
| `guardian_exemption` | `post_write_audit.py` | `ledger-consulter-guardian-exemption` | new `# guardian: allow-*` comments |
| `progress_eta` | `tools/progress_display.py` | `ledger-consulter-progress-eta` | ProgressReporter predicted vs actual |
| `memory_recall` | `post_cascade_writeback_audit.py` | `ledger-consulter-memory-recall` | writeback-signal corroboration rate |
| `test_selection` | `post_run_audit.py` (predict) + `ops_scripts/calibration/test_selection_binder.py` (bind) | `ledger-consulter-test-selection` | pytest triage selection with pass/fail outcome from `.pytest_cache/v/cache/lastfailed` |

**Invariants**: writer contract via `tools/ledgers/hook_helpers.emit_ledger_event` only; fail-soft; idempotent on `event_id`; additive schema only. See `.windsurf/rules/intelligence-ledger-family.md` and ADR-050 for full rationale.

**Weekly report**: `python ops_scripts/calibration/ledger_weekly_report.py` → `docs/reports/calibration/<YYYY-Www>.md`.

**CI gate**: `python ops_scripts/ci/check_ledger_writer_contract.py` validates schema, writer-hook existence, consulting-skill existence.

**Calibration surface**: on-disk only. Weekly reports at `docs/reports/calibration/<YYYY-Www>.md` are the SSOT; no mirror database exists in Notion by design (operator decision 2026-04-24). Revisit after 30 days of accumulated signal if cross-session visibility becomes necessary.

## Apps Test Surface Taxonomy

> ⛔ All `apps_<x>` test files MUST live in one of the 3 canonical surfaces. `apps_<x>/tests/` directories are **FORBIDDEN**. See `.windsurf/rules/apps-test-surface-taxonomy.md` and ADR-082.

| Surface | Canonical Path | Content |
|---|---|---|
| Unit | `tests/unit/<app>/` | Isolated unit tests; mirrors `apps_<app>/` structure |
| Integration | `tests/<app>/` | Integration/E2E tests requiring real dependencies |
| Contract | `tests/_apps_contract/test_<app>_*.py` | Cross-app contract and governance tests |

**Enforcement**: CI gate `TSP1` — `ops_scripts/ci/check_apps_test_surface_parity.py` (advisory; fail-closed via `APPS_TEST_SURFACE_FAIL_CLOSED=1`; bypass via `APPS_TEST_SURFACE_BYPASS=1`).

**Rule**: `.windsurf/rules/apps-test-surface-taxonomy.md` — load when editing `apps_*/` trees or relocating test files.
