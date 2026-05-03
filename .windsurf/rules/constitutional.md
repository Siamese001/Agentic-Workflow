---
trigger: always_on
---

> See `.windsurf/RULES_INDEX.md#always-on-discipline` for shared retrieval / enforcement guidance.

# Constitutional Floor

> ⛔ These constraints apply to every task, every tier, every session. No exceptions.

## Hard Constraints

### Tool Prefix Stability

Server IDs in `.windsurf/mcp_config.json` are stable. Live tool prefixes such as `mcp0_`, `mcp1_`, and `mcp2_` can shift whenever server order changes. In rule text, prefer stable server IDs plus bare tool names, then resolve the live prefix from the active tool list.

0. **No PowerShell, subprocess timeout required.** Use `subprocess.run(argv, shell=False, timeout=30)`. No exceptions. (Was duplicated as §14 — merged 2026-05-01.)
1. **No test skipping.** No `pytest.mark.skip`, no `xfail` without `strict=True`.
2. **No editing while exploring.** All five repair gates must pass before any edit.
3. **No agent deletion without authorization.** Requires AGENT-DELETION-AUTHORIZED marker, 90-day deprecation, zero references.
4. **CI enforces all of this.** `python ops_scripts/ci/run_contract_gates.py`
5. **ADG before T2/T3 work.** Ingest `artifacts/adg/adg_indexed_<timestamp>.sqlite` before any query or edit. Regenerate: `python tools/generate_full_adg.py`.
6. **Author-Gate for ambiguous decisions.** Score candidates 0.00–1.00, filter at 0.72, apply dominance rule (≥0.85, gap ≥0.12 → surface alone). See `author-gate-enforcement.md`.
7. **RCA auto-closure.** Execute corrective actions immediately. Never leave RCA unresolved.
8. **Guardian exemptions require Author-Gate.** Format: `# guardian: allow-<type> -- <specific justification>`. Generic words forbidden. Gate: `guardian_exemption_gate.py`.
9. **SVP Engineering persona for T3 architecture.** Prioritize: operational simplicity, dependency hygiene, archival over deletion, ADRs, zero-regression.
10. **Zero-loss refactor.** After removing boilerplate, check for hollow files. Gate: `zero_loss_refactor_verifier.py`.
11. **Terminal process lifecycle.** All `run_command`/subprocess calls must terminate when query completes. Gate: `check_terminal_cleanup.py`.
12. **No imports from `archives/` in production.** CI gate: `check_no_archives_imports.py`.
13. **MCP green light before T2/T3.** Check Redis hot cache first (`adg_redis_ingest.py --check`). Fallback: `adg_health`. Both red = BLOCKED.
14. **Subprocess timeout required.** See §0 (merged 2026-05-01). Slot kept for stable rule numbering — gates and prose may continue to reference §14.
15. **Precise exception handling.** Catch specific types. Bare `except:` FORBIDDEN. `except Exception` without guardian comment FORBIDDEN.
16. **Query progress bar mandatory.** All operations >5s, loops >10 lines, or heavy-named functions (`scan_*`, `build_*`, `query_*`, etc.) >12 lines MUST display a colored progress bar. CI gate: `check_query_progress_bar.py`. See `query-progress-bar.md`.
17. **Memory lifecycle mandatory.** At the start of every conversation, call `mem_recall_session_start` to load persistent project context. After significant architecture decisions, Author-Gate resolutions, or new patterns, write to memory via `create_entities`/`add_observations`. See AGENTS.md Memory Lifecycle section.

### Process Discipline (§18–§21)

18. **No hidden scope expansion.** Do not quietly widen scope. If the task grows, state it in the working packet and keep the change bounded.
19. **Mode separation is mandatory.** Separate `analyze` (inspect, no edits), `plan` (sequence, no edits), `edit` (make the change), and `verify` (prove the change). Do not blur these modes.
20. **Fact grading is mandatory.** Classify claims as **DIRECTLY OBSERVED**, **DERIVED**, or **UNRESOLVED**. Do not present unresolved items as facts.
21. **Zero-loss overwrite discipline.** When overwriting a rule, skill, or workflow: preserve useful constraints, remove redundancy, clarify triggers, preserve references relied on by scripts, and do not silently delete operational intent.

22. **ADG graph layer is primary for refactoring.** Materialized views (`mv_*`), semantic edges (`flows_to`, `emits_side_effect`, `resolves_callsite`, `controls_flow`, `reads_from`, `writes_to`), and pre-built P-views (`v_p0_*`, `v_p1_*`, `v_p2_*`, `v_p3_*`) MUST drive T2/T3 refactoring plans — not just raw `edges`/`violations` tables. Plans missing the `## ADG_GRAPH_LAYER_EVIDENCE` section are invalid. Gate: `check_graph_layer_evidence.py`. See `adg-graph-layer-enforcement.md`.
23. **ADG canonical invariants.** (a) SQLite=truth, Redis=hot projection, MCP=read-only gateway — no divergence. (b) ADG wins conflicts vs text-search/intuition. (c) Hotspot rows MUST classify by archetype (`CENTRAL_DEPENDENCY`/`ORCHESTRATOR`/`STATE_NODE`/`SAFETY_GATEKEEPER`) + cross-ref 5 Surfaces (Execution/Write/Security/State/Observability). (d) Layer multipliers: L0/L5 ×2.0, L3/L4 ×1.75, L1/L2 ×1.0, L6 ×0.75. (e) Static ADG (`adg_sqlite`) ≠ Runtime ADG (`otel_mcp`). (f) ADG queries > hardcoded paths/layers. Detail: `adg-canonical-invariants.md`.
24. **Deferred-scope capture mandatory.** Every deferred scope item MUST be captured with a `DEFERRED_SCOPE:` marker line in the Cascade response that introduces it (plain text, before any Notion `API-post-page`). Post-hook `post_cascade_deferred_scope_capture.py` auto-scores priority (P1..P5) and auto-posts to Wave/Phase Convergence DB. Priority is deterministic — never hand-assign `[Pn]`. Pre-session hook surfaces unresolved pendings; recovery script retries failed posts. Pre-commit gate `check_deferred_scope_markers.py` blocks plan-file commits with prose deferred-scope language without matching markers. See `deferred-scope-capture.md`.
25. **MCP serialization mandatory (remote MCPs only).** Remote network-bound MCPs (notion, tavily, deepwiki, context7, GitKraken) MUST be one-per-response with no sibling tool calls. Local stdio MCPs (adg_sqlite, redis, memory, filesystem, vector_db, pytest_mcp, otel_mcp, task_manager, mcp-playwright) batch freely. Procedural detail + sunset + bypass: `mcp-serialization.md`. Audit: `post_cascade_mcp_serialization_audit.py`.
26. **No interactive pagers in `run_command`.** `more`, `less`, `most`, `more.com` — pipe or bare — FORBIDDEN. Cascade's terminal cannot send keystrokes; pagers hang the turn forever (Python `timeout=` does NOT help — shell pipeline blocks, not Python). Required pattern: redirect to file (`> out.txt`) + `read_file`. For long-running shell, set `Blocking=false` + `WaitMsBeforeAsync`. Gate: `pre_run_gate.py`.
27. **Windsurf config schema purity.** `.windsurf/hooks.json` (per entry: `command`+`working_directory`+`show_output` only) and `.windsurf/mcp_config.json` (per server: `command`+`args`+`env`+`disabled` only) MUST contain ONLY official-schema fields. Unknown keys silently disable the subsystem (precedent: 2026-04-23 `powershell` field killed the post-cascade chain). CI gate: `check_windsurf_config_schema.py`.
28. **SQLite-direct fallback supersedes grep for dependency analysis.** Fallback hierarchy: (1) `adg_sqlite` MCP → (2) direct `sqlite3` query of latest `artifacts/adg/adg_indexed_<ts>.sqlite` → (3) grep ONLY if BOTH fail AND `DEGRADED_FALLBACK: reason=<mcp_err>+<sqlite_err>` is emitted. MCP serialization (§25) is NEVER an excuse for grep — it is an excuse for SQLite. Audit: `post_cascade_adg_audit.py` (severity: critical when snapshot exists). Bypass: `ADG_SQLITE_FALLBACK_BYPASS=1`.
29. **Closed-loop router evidence mandatory.** All 10 routers (L0/bandit, L0/r5, L1/c0, L2/cascade, L3/shape, L3/reroute, L4/uwg, L5/hitl, L6/promo, L6/regret) MUST emit `ROUTER_DECISION:` + `emit_ledger_event` in the same code path. `L6/promo` promote: requires Wilson≥0.60, z≥1.96, uplift>0, n≥30. `L6/regret`: non-empty `by_layer_json`. Detail: `closed-loop-router-enforcement.md`. Audit: `post_cascade_router_decision_audit.py`. CI: `check_router_calibration_evidence.py`. Bypass: `ROUTER_ENFORCEMENT_BYPASS=1`.
30. **Author-Gate capture health mandatory.** Every refactor-class response MUST emit `DECISION_CAPTURED:` via `tools/capture/append_marker.py` (post_cascade hook unreliable). SSOT: SQLite at `.windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite`. Pipeline: marker → `markers.jsonl` → `queue_to_ledger.py` → SQLite → `tools/notion/sync_decision_ledger.py` (Notion is mirror). CI: `check_decision_ledger_sqlite_freshness.py`. Bypass: `DECISION_LEDGER_FRESHNESS_BYPASS=1`.
31. **SSOT folder routing for new files.** NEW Python files land in canonical folders. `check_*`/`*_gate.py` → `ops_scripts/ci/`; calibration/binder/poller → `ops_scripts/calibration/`; `purge_*`/`cleanup_*` → `ops_scripts/maintenance/`; `pre_*`/`post_*` hooks → `.windsurf/scripts/`; else → `tools/<domain>/`. Pre-existing files exempt. Detail: `ssot-folder-enforcement.md`. Hook: `pre_write_gate.py`. Bypass: `SSOT_FOLDER_BYPASS=1`.

32. **Fort Knox certification integrity (two arms).** **agentic_core arm**: claims emerge ONLY from `scripts/compile_requirement_signoff.py` consuming `certification/evidence_assertions.jsonl`. Producers: `tools/cert/*.py` (excluding `apps_e2e/`), `scripts/verify_*_gate.py`, `scripts/verify_rtc_*.py`. Canary `RTC-REQ-001`. **apps_e2e arm**: claims emerge ONLY from `scripts/compile_apps_e2e_signoff.py` consuming `certification/apps_evidence_assertions.jsonl`; consolidated by `tools/certification/generate_apps_100pct_runtime_proof.py`. Producers: `tools/cert/apps_e2e/*.py`, `scripts/compile_apps_e2e_signoff.py`. Canary `APPS-REQ-001`. CI gate T7s.4: `check_apps_fortknox_signed_proof.py`. Plan SSOT: `apps-fort-knox-parity-c5d9a3.md`. **Both arms**: compiler outputs (`*.json/sha256/merkle.json/signature.json`) MUST NOT be hand-edited. Author-Gate `certification_claim` fires before SIGNED_OFF prose. Detail: `fortknox-certification-discipline.md` + skill `fortknox-evidence`. Bypass: `FORTKNOX_DISCIPLINE_BYPASS=1` (shared).

33. **Two-tier compliance (Anthropic).** `trigger: always_on` rules MUST sum ≤51,200 bytes. Procedural detail → skills; invariants → rules; deterministic enforcement → hooks. CI gate: `check_always_on_token_budget.py` (T7r). Bypass: `ALWAYS_ON_BUDGET_BYPASS=1`.

34. **Per-turn retrieval budgets.** Combined `grep_search` + `code_search` invocations ≤ 3 per response (audit: `post_cascade_grep_budget_audit.py`, bypass `GREP_BUDGET_BYPASS=1`). Combined file-read invocations (`read_file`, `read_notebook`, `read_url_content`, MCP `read_text_file`/`read_file`/`read_multiple_files`) ≤ 10 per response (audit: `post_cascade_read_budget_audit.py`, bypass `READ_BUDGET_BYPASS=1`). Per-turn token-burn telemetry: `post_cascade_token_telemetry.py` → `artifacts/windsurf/turn_budget.jsonl`; weekly rollup `ops_scripts/calibration/token_burn_weekly_report.py`. Detail: `scope-containment.md`.

35. **Author-Gate queue drain mandatory.** After ANY wave/phase completion marker (`WAVE_COMPLETE:`, `PHASE_COMPLETE:`, `wave_execution_state.py complete`, or plan row flip to `✅ DONE`), Cascade MUST emit the next pending `AUTHOR_GATE_PACKET:` from `.windsurf/state/author_gate_queue/<slug>.jsonl` in the same or immediately-following response. Queue SSOT helper: `.windsurf/scripts/_author_gate_queue.py`. Plan-time seeding via `AG_QUEUE_SEED:` markers (captured by `post_cascade_ag_queue_seed_capture.py`). Pre-hook surface: `pre_user_prompt_ag_queue_surface.py`. Audit: `post_cascade_ag_queue_drain_audit.py`. Pre-commit prose↔marker parity: `check_ag_queue_seed_markers.py`. Weekly drift: `check_ag_queue_drain_freshness.py`. Detail: `author-gate-queue-drain.md`. Bypass: `AG_QUEUE_DRAIN_BYPASS=1`.

36. **Plan–Notion registration mandatory.** Every new `.windsurf/plans/<slug>-<6hex>.md` MUST emit `PLAN_CREATED:` marker AND post a Plans DB row (Slug, Status, Exists On Disk, Plan File Path, Summary, AI Summary) before wave execution. `wave_execution_state.py start` blocks on unregistered plans. Cascade MUST NOT claim registration status without a live `API-query-data-source` call same-response. Helper: `_plan_registration.py`. Pre-commit T7u: `check_plan_registration_freshness.py`. Detail: `plan-registration-enforcement.md`. Bypass: `PLAN_REGISTRATION_BYPASS=1`.

## Quick Non-Negotiables (rule-number index)

PowerShell §0 · shell=True §0 · scope growth §18 · grep-vs-ADG §5/§22/§28 · completion-without-verify §19 · anti-pattern §6/§8 · progress bar §16 · `DEFERRED_SCOPE:` §24 · remote-MCP batch §25 · config schema §27 · interactive pagers §26 · `DECISION_CAPTURED:` §30 · refactor-class capture §6/§30 · retrieval budgets §34 · `AG_QUEUE_SEED:` / queue drain §35 · `PLAN_CREATED:` / Notion registration §36.

## Tier Classification

| Tier | Scope | ADG Requirement |
|------|-------|----------------|
| **T0 — Question** | No code changes | ADG cache optional |
| **T1 — Trivial** | ≤1 file, ≤20 lines | Scoped tests only |
| **T2 — Scoped** | 2–5 files, single layer | Query ADG blast radius |
| **T3 — Architectural** | >5 files or cross-layer | Full ADG protocol mandatory |

ADG graph is the **primary** analysis primitive. `grep_search` for dependency analysis is FORBIDDEN.

**ADG-First Retrieval-Tool Decision Tree** — full table moved to `.windsurf/skills/graph-analysis/tool_routing_decision_tree.md` (auto-loads via `graph-analysis` skill). Constitutional invariant: any query about imports / consumers / references / blast radius / layers / function-or-class names → ADG MCP, never grep. Literal text / TODOs / non-Python content → `grep_search` allowed.

**Degraded fallback**: Before grep for any graph query, call `adg_health`. Fallback only when health red AND response contains `DEGRADED_FALLBACK: reason=<...>`. Silent fallback = `severity: critical` in `adg_first_violations.jsonl`.

Enforcement chain: `graph-analysis` skill (auto-load) → `pre_prompt_classifier.py` step 0 (T2/T3) → this rule (always-on) → `post_cascade_adg_audit.py` (retroactive) → `artifacts/windsurf/adg_first_violations.jsonl`.

## Quick Gates

- Plan SSOT: `.windsurf/plans/<name>-<6hex>.md` — never `docs/reports/plans/` for plans
- All Python file I/O: `encoding="utf-8"`
- `grep_search` permitted only to confirm literals, never for dependency tracing

## Extended Doctrine (model_decision rules)

Full protocol details live in focused rules — loaded on demand, not always_on:
- `adg-repair-discipline.md` — ADG repair loop and fail-closed recovery
- `anti-pattern-author-gate.md` — anti-pattern Author-Gate approval gate
- `author-gate-enforcement.md` — full Author-Gate decision pipeline and option shapes
- `sequential-thinking-enforcement.md` — T2/T3 structured reasoning protocol
- `global_rules.md` — subprocess, exception, MCP SSOT policy details
- `adg-test-accelerator-enforcement.md` — ADG-driven test scope selection
- `memory-management.md` — memory graph maintenance, purge sync, health thresholds
- `adg-hotspot-enforcement.md` — mandatory hotspot report before any refactoring
- `adg-graph-layer-enforcement.md` — MVs + semantic edges + P-views are PRIMARY for refactoring decisions
- `deferred-scope-capture.md` — DEFERRED_SCOPE marker contract, auto-scoring, auto-post + session-start recovery
