---
trigger: model_decision
description: Converted from Cursor rule constitutional.md Demoted from always_on 2026-05-26 (governance-dedup-closeout-e8a4c2 W4). Cursor SSOT: .cursor/rules/constitutional.mdc (alwaysApply: false).
---

> See `.windsurf/RULES_INDEX.md#always-on-discipline` for shared retrieval / enforcement guidance.

# Constitutional Floor

> ⛔ Applies every task, every tier, every session. No exceptions.

## Hard Constraints

0. **No PowerShell, subprocess timeout required.** `subprocess.run(argv, shell=False, timeout=30)`. (Slot §14 retained for stable numbering.)
1. **No test skipping.** No `pytest.mark.skip`, no `xfail` without `strict=True`.
2. **No editing while exploring.** All five repair gates must pass before any edit.
3. **No agent deletion without authorization.** AGENT-DELETION-AUTHORIZED marker, 90-day deprecation, zero references.
4. **CI enforces all of this.** `python ops_scripts/ci/run_contract_gates.py`
5. **ADG before T2/T3 work.** Ingest `artifacts/adg/adg_indexed_<ts>.sqlite` before any query/edit. Regenerate: `python tools/generate_full_adg.py`.
6. **Author-Gate for ambiguous decisions.** Score 0.00–1.00, filter at 0.72, dominance ≥0.85+gap ≥0.12 → surface alone. See `author-gate-enforcement.md`.
7. **RCA auto-closure.** Execute corrective actions immediately. Never leave RCA unresolved.
8. **Guardian exemptions require Author-Gate.** `# guardian: allow-<type> -- <specific justification>`. Generic words forbidden. Gate: `guardian_exemption_gate.py`.
9. **SVP Engineering persona for T3 architecture.** Operational simplicity, dependency hygiene, archival over deletion, ADRs, zero-regression.
10. **Zero-loss refactor.** After removing boilerplate, check for hollow files. Gate: `zero_loss_refactor_verifier.py`.
11. **Terminal process lifecycle.** All `run_command`/subprocess must terminate. Gate: `check_terminal_cleanup.py`.
12. **No imports from `archives/` in production.** Gate: `check_no_archives_imports.py`.
13. **MCP green light before T2/T3.** Redis hot cache (`adg_redis_ingest.py --check`) → `adg_health` fallback. Both red = BLOCKED.
14. **Subprocess timeout required.** See §0.
15. **Precise exception handling.** Catch specific types. Bare `except:` and `except Exception` without guardian comment FORBIDDEN.
16. **Query progress bar mandatory.** Operations >5s, loops >10 lines, heavy-named functions (`scan_*`/`build_*`/`query_*`) >12 lines. Gate: `check_query_progress_bar.py`. See `query-progress-bar.md`.
17. **Memory lifecycle mandatory.** Call `mem_recall_session_start` at session start. Write back significant decisions / patterns via `create_entities`/`add_observations`. See AGENTS.md Memory Lifecycle.

### Process Discipline (§18–§21)

18. **No hidden scope expansion.** State scope growth in the working packet; keep changes bounded.
19. **Mode separation mandatory.** `analyze` (no edits) / `plan` (no edits) / `edit` / `verify`. Don't blur.
20. **Fact grading mandatory.** Classify claims as **DIRECTLY OBSERVED** / **DERIVED** / **UNRESOLVED**. Don't present unresolved as fact.
21. **Zero-loss overwrite discipline.** When overwriting rule/skill/workflow: preserve constraints + script-relied references; remove redundancy; don't silently delete operational intent.

22. **ADG graph layer is primary for refactoring.** MVs (`mv_*`), semantic edges (`flows_to`/`emits_side_effect`/`resolves_callsite`/`controls_flow`/`reads_from`/`writes_to`), P-views (`v_p0_*`..`v_p3_*`) MUST drive T2/T3 plans — not raw `edges`/`violations`. Plans missing `## ADG_GRAPH_LAYER_EVIDENCE` invalid. Gate: `check_graph_layer_evidence.py`. See `adg-graph-layer-enforcement.md`.
23. **ADG canonical invariants.** SQLite=truth, Redis=hot projection, MCP=read-only gateway. ADG wins vs text-search/intuition. Hotspot rows MUST classify by archetype (`CENTRAL_DEPENDENCY`/`ORCHESTRATOR`/`STATE_NODE`/`SAFETY_GATEKEEPER`) + cross-ref 5 Surfaces (Execution/Write/Security/State/Observability). Layer multipliers: L0/L5 ×2.0, L3/L4 ×1.75, L1/L2 ×1.0, L6 ×0.75. Static ADG (`adg_sqlite`) ≠ Runtime ADG (`otel_mcp`). Detail: `adg-canonical-invariants.md`.
24. **Deferred-scope capture mandatory.** `DEFERRED_SCOPE:` marker line in the response that introduces it (plain text, before any Notion `API-post-page`). Hook auto-scores P1..P5 and posts to Wave/Phase Convergence DB. Never hand-assign `[Pn]`. Pre-commit: `check_deferred_scope_markers.py`. See `deferred-scope-capture.md`.
25. **MCP serialization (remote MCPs only).** Remote MCPs (notion, tavily, deepwiki, context7, GitKraken) one-per-response, no siblings. Local stdio MCPs (adg_sqlite, redis, memory, filesystem, vector_db, pytest_mcp, otel_mcp, task_manager, mcp-playwright) batch freely. Detail + bypass: `mcp-serialization.md`. Audit: `post_cascade_mcp_serialization_audit.py`.
26. **No interactive pagers in `run_command`.** `more`/`less`/`most`/`more.com` (pipe or bare) FORBIDDEN — Cursor Agent can't send keystrokes; pagers hang the turn. Pattern: redirect to file (`> out.txt`) + `read_file`. Long-running: `Blocking=false` + `WaitMsBeforeAsync`. Gate: `pre_run_gate.py`.
27. **Windsurf config schema purity.** `.windsurf/hooks.json` (only `command`+`working_directory`+`show_output`) and `.windsurf/mcp_config.json` (only `command`+`args`+`env`+`disabled`) MUST contain ONLY official-schema fields. Unknown keys silently disable subsystem. Gate: `check_windsurf_config_schema.py`.
28. **SQLite-direct fallback supersedes grep for dependency analysis.** Hierarchy: (1) `adg_sqlite` MCP → (2) direct `sqlite3` of latest `artifacts/adg/adg_indexed_<ts>.sqlite` → (3) grep ONLY if BOTH fail AND `DEGRADED_FALLBACK: reason=<mcp_err>+<sqlite_err>` emitted. §25 is NEVER an excuse for grep — only for SQLite. Audit: `post_cascade_adg_audit.py`. Bypass: `ADG_SQLITE_FALLBACK_BYPASS=1`.
29. **Closed-loop router evidence mandatory.** All 10 routers (L0/bandit, L0/r5, L1/c0, L2/cascade, L3/shape, L3/reroute, L4/uwg, L5/hitl, L6/promo, L6/regret) MUST emit `ROUTER_DECISION:` + `emit_ledger_event` same code path. `L6/promo` promote: Wilson≥0.60, z≥1.96, uplift>0, n≥30. `L6/regret`: non-empty `by_layer_json`. Detail: `closed-loop-router-enforcement.md`. Audit: `post_cascade_router_decision_audit.py`. Bypass: `ROUTER_ENFORCEMENT_BYPASS=1`.
30. **Author-Gate capture health mandatory.** Refactor-class response MUST emit `DECISION_CAPTURED:` via `tools/capture/append_marker.py`. SSOT: SQLite at `.windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite`. Pipeline: marker → `markers.jsonl` → `queue_to_ledger.py` → SQLite → `tools/notion/sync_decision_ledger.py` (Notion mirror). CI: `check_decision_ledger_sqlite_freshness.py`. Bypass: `DECISION_LEDGER_FRESHNESS_BYPASS=1`.
31. **SSOT folder routing for new files.** `check_*`/`*_gate.py` → `ops_scripts/ci/`; calibration/binder/poller → `ops_scripts/calibration/`; `purge_*`/`cleanup_*` → `ops_scripts/maintenance/`; `pre_*`/`post_*` hooks → `.windsurf/scripts/`; else → `tools/<domain>/`. Pre-existing files exempt. Detail: `ssot-folder-enforcement.md`. Hook: `pre_write_gate.py`. Bypass: `SSOT_FOLDER_BYPASS=1`.
32. **Fort Knox certification integrity (two arms).** **agentic_core**: claims emerge ONLY from `tools/cert/compile_requirement_signoff.py` consuming `certification/evidence_assertions.jsonl`. Canary `RTC-REQ-001`. **apps_e2e**: claims emerge ONLY from `tools/cert/compile_apps_e2e_signoff.py` consuming `certification/apps_evidence_assertions.jsonl`; consolidated by `tools/certification/generate_apps_100pct_runtime_proof.py`. Canary `APPS-REQ-001`. CI gate T7s.4: `check_apps_fortknox_signed_proof.py`. Compiler outputs (`*.json/sha256/merkle.json/signature.json`) MUST NOT be hand-edited. Author-Gate `certification_claim` fires before SIGNED_OFF prose. Detail: `fortknox-certification-discipline.md` + skill `fortknox-evidence`. Bypass: `FORTKNOX_DISCIPLINE_BYPASS=1`.
33. **Two-tier compliance (Anthropic).** `trigger: always_on` rules MUST sum ≤51,200 bytes. Procedural detail → skills; invariants → rules; deterministic enforcement → hooks. Gate: `check_always_on_token_budget.py` (T7r). Bypass: `ALWAYS_ON_BUDGET_BYPASS=1`.
34. **Per-turn retrieval budgets.** `grep_search`+`code_search` ≤3/response (audit: `post_cascade_grep_budget_audit.py`, bypass `GREP_BUDGET_BYPASS=1`). File reads (native `read_file`/`read_notebook`/`read_url_content` + MCP `read_text_file`/`read_file`/`read_multiple_files`) ≤10/response (audit: `post_cascade_read_budget_audit.py`, bypass `READ_BUDGET_BYPASS=1`). Token-burn telemetry: `post_cascade_token_telemetry.py` → `artifacts/windsurf/turn_budget.jsonl`; weekly: `ops_scripts/calibration/token_burn_weekly_report.py`. Detail: `scope-containment.md`.
35. **Author-Gate queue drain mandatory.** After ANY wave/phase completion (`WAVE_COMPLETE:`, `PHASE_COMPLETE:`, `wave_execution_state.py complete`, plan row → `✅ DONE`), Cursor Agent MUST emit next pending `AUTHOR_GATE_PACKET:` from `.windsurf/state/author_gate_queue/<slug>.jsonl` same/next response. Helper: `_author_gate_queue.py`. Plan-time seeding: `AG_QUEUE_SEED:` markers (captured by `post_cascade_ag_queue_seed_capture.py`). Pre-hook: `pre_user_prompt_ag_queue_surface.py`. Audit: `post_cascade_ag_queue_drain_audit.py`. Pre-commit: `check_ag_queue_seed_markers.py`. Detail: `author-gate-queue-drain.md`. Bypass: `AG_QUEUE_DRAIN_BYPASS=1`.
36. **Plan–Notion registration mandatory.** Every new `.windsurf/plans/<slug>-<6hex>.md` MUST emit `PLAN_CREATED:` marker AND post Plans DB row (Slug, Status, Exists On Disk, Plan File Path, Summary, AI Summary) before wave execution. `wave_execution_state.py start` blocks unregistered plans. Cursor Agent MUST NOT claim registration without a live `API-query-data-source` call same-response. Helper: `_plan_registration.py`. Pre-commit T7u: `check_plan_registration_freshness.py`. Detail: `plan-registration-enforcement.md`. Bypass: `PLAN_REGISTRATION_BYPASS=1`.

## Tier Classification

| Tier | Scope | ADG Requirement |
|------|-------|----------------|
| **T0 — Question** | No code changes | ADG cache optional |
| **T1 — Trivial** | ≤1 file, ≤20 lines | Scoped tests only |
| **T2 — Scoped** | 2–5 files, single layer | Query ADG blast radius |
| **T3 — Architectural** | >5 files or cross-layer | Full ADG protocol mandatory |

ADG graph is the **primary** analysis primitive. `grep_search` for dependency analysis FORBIDDEN. Decision tree: `.windsurf/skills/graph-analysis/tool_routing_decision_tree.md` (auto-load via `graph-analysis` skill). Any query about imports / consumers / references / blast radius / layers / function-or-class names → ADG MCP, never grep. Literal text / TODOs / non-Python content → `grep_search` allowed.

**Degraded fallback** (§28): before grep for any graph query, call `adg_health`. Fallback only when health red AND response contains `DEGRADED_FALLBACK: reason=<...>`. Silent fallback = `severity: critical` in `adg_first_violations.jsonl`. Enforcement chain: `graph-analysis` skill (auto-load) → `pre_prompt_classifier.py` step 0 → this rule → `post_cascade_adg_audit.py`.

## Quick Gates

- Plan SSOT: `.windsurf/plans/<name>-<6hex>.md` — never `docs/reports/plans/` for plans
- Python file I/O: `encoding="utf-8"`
- `grep_search` permitted only to confirm literals, never for dependency tracing

## Extended Doctrine (model_decision rules — load on demand)

`adg-repair-discipline.md` · `anti-pattern-author-gate.md` · `author-gate-enforcement.md` · `sequential-thinking-enforcement.md` · `global_rules.md` · `adg-test-accelerator-enforcement.md` · `memory-management.md` · `adg-hotspot-enforcement.md` · `adg-graph-layer-enforcement.md` · `deferred-scope-capture.md`
