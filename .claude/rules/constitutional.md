
<!-- Converted from `.claude/rules/constitutional.md`. Original Cursor trigger: `always_on`. -->

> See `CLAUDE.md` for shared retrieval / enforcement guidance.

# Constitutional Floor

> ⛔ Applies every task, every tier, every session. No exceptions.

## Hard Constraints

0. **Subprocess timeout required.** `subprocess.run(argv, shell=False, timeout=30)`. PowerShell is permitted (primary Windows shell); the legacy Windsurf-era PowerShell ban is lifted. (Slot §14 retained for stable numbering.)
1. **No test skipping.** No `pytest.mark.skip`, no `xfail` without `strict=True`.
2. **No editing while exploring.** All five repair gates must pass before any edit.
3. **No agent deletion without authorization.** AGENT-DELETION-AUTHORIZED marker, 90-day deprecation, zero references.
4. **CI enforces all of this.** `python ops_scripts/ci/run_contract_gates.py`
5. **ADG before T2/T3 work.** Ingest `artifacts/adg/adg_indexed_<ts>.sqlite` before any query/edit. Regenerate: `python tools/generate_full_adg.py`.
6. **Author-Gate for ambiguous decisions.** Use the native `AskUserQuestion` tool when ≥2 plausible approaches have different blast radius and no unambiguous directive; mark the recommended option. W1 supersession (ADR-093) retired the packet/marker/ledger pipeline. See `CLAUDE.md` § Author-Gate.
7. **RCA auto-closure.** Execute corrective actions immediately. Never leave RCA unresolved.
8. **Guardian exemptions require Author-Gate.** `# guardian: allow-<type> -- <specific justification>`. Generic words forbidden. Gate: `guardian_exemption_gate.py`.
9. **SVP Engineering persona for T3 architecture.** Operational simplicity, dependency hygiene, archival over deletion, ADRs, zero-regression.
10. **Zero-loss refactor.** After removing boilerplate, check for hollow files. Gate: `zero_loss_refactor_verifier.py`.
11. **Terminal process lifecycle.** All `run_command`/subprocess must terminate. Gate: `check_terminal_cleanup.py`.
12. **No imports from `archives/` in production.** Gate: `check_no_archives_imports.py`.
13. **ADG SQLite SSOT green light before T2/T3.** The ADG SQLite snapshot (`artifacts/adg/adg_indexed_*.sqlite`) is the SSOT: no readable canonical snapshot ⇒ **BLOCKED**. Redis is a non-authoritative hot cache (`adg_redis_ingest.py --check`) — cold/absent ⇒ advisory warning only, **never blocks** (a Redis hit may not substitute for an unavailable SSOT; see `adg-canonical-invariants.md` §1). Gate: `pre_user_prompt_adg_ssot_gate.py`, dispatched from `before_submit_prompt.py`. Bypass: `ADG_SSOT_GATE_BYPASS=1`. (Detail: plan `adg-redis-hotcache-enforcement-b9f4c2`.)
14. **Subprocess timeout required** — reserved alias of §0, kept for stable numbering (sibling rules `query-progress-bar.md` and `python-dash-c-quote-hazard.md` cite "§14"; do not renumber to dedupe). See §0.
15. **Precise exception handling.** Catch specific types. Bare `except:` and `except Exception` without guardian comment FORBIDDEN.
16. **Query progress bar mandatory.** Operations >5s, loops >10 lines, heavy-named functions (`scan_*`/`build_*`/`query_*`) >12 lines. Gate: `check_query_progress_bar.py`. See `query-progress-bar.md`.
17. **Memory lifecycle (native file memory).** Recall project memory at session start and write back significant decisions/patterns. SSOT is native file memory (`memory/MEMORY.md` + per-fact files); the knowledge-graph MCP is optional for genuine graph queries. W3 supersession (ADR-095) retired the mandatory `mem_recall_session_start` first-call ritual and the purge/staleness gates.

### Process Discipline (§18–§21)

18. **No hidden scope expansion.** State scope growth in the working packet; keep changes bounded.
19. **Mode separation mandatory.** `analyze` (no edits) / `plan` (no edits) / `edit` / `verify`. Don't blur.
20. **Fact grading mandatory.** Classify claims as **DIRECTLY OBSERVED** / **DERIVED** / **UNRESOLVED**. Don't present unresolved as fact.
21. **Zero-loss overwrite discipline.** When overwriting rule/skill/workflow: preserve constraints + script-relied references; remove redundancy; don't silently delete operational intent.

22. **ADG graph layer is primary for refactoring.** MVs (`mv_*`), semantic edges (`flows_to`/`emits_side_effect`/`resolves_callsite`/`controls_flow`/`reads_from`/`writes_to`), P-views (`v_p0_*`..`v_p3_*`) MUST drive T2/T3 plans — not raw `edges`/`violations`. Plans missing `## ADG_GRAPH_LAYER_EVIDENCE` invalid. Gate: `check_graph_layer_evidence.py`. See `adg-analysis-procedures.md` §3.
23. **ADG canonical invariants.** SQLite=truth, Redis=hot projection, MCP=read-only gateway. ADG wins vs text-search/intuition. Hotspot rows MUST classify by archetype (`CENTRAL_DEPENDENCY`/`ORCHESTRATOR`/`STATE_NODE`/`SAFETY_GATEKEEPER`) + cross-ref 5 Surfaces (Execution/Write/Security/State/Observability). Layer multipliers: L0/L5 ×2.0, L3/L4 ×1.75, L1/L2 ×1.0, L6 ×0.75. Static ADG (`adg_sqlite`) ≠ Runtime ADG (`otel_mcp`). Detail: `adg-canonical-invariants.md`.
24. **Deferred-scope capture — native spawn_task (W4 claude-native-supersession-9d3f7a, ADR-096).** Out-of-scope work surfaces via the native `spawn_task` background-task chip (one click → its own session/worktree), not a `DEFERRED_SCOPE:`/`NEXT_STEP:` marker → hook → Notion pipeline. Notion remains an optional durable backlog via explicit user action. Slot retained for stable numbering.
25. *(Reserved — no rule occupies §25. Slot intentionally vacant; numbering held stable because `§`-citations are load-bearing across rules. Do not renumber to close the gap.)*
26. **No interactive pagers in `run_command`.** `more`/`less`/`most`/`more.com` (pipe or bare) FORBIDDEN — Claude Code can't send keystrokes; pagers hang the turn. Pattern: redirect to file (`> out.txt`) + `read_file`. Long-running: `Blocking=false` + `WaitMsBeforeAsync`. Gate: `pre_run_gate.py`.
27. **Config schema purity.** `.claude/settings.json` (only `command`+`working_directory`+`show_output`) and `.mcp.json` (only `command`+`args`+`env`+`disabled`) MUST contain ONLY official-schema fields. Unknown keys silently disable subsystem. Gate: `check_cursor_config_schema.py`.
28. **SQLite-direct fallback supersedes grep for dependency analysis.** Hierarchy: (1) `adg_sqlite` MCP → (2) direct `sqlite3` of latest `artifacts/adg/adg_indexed_<ts>.sqlite` → (3) grep ONLY if BOTH fail AND `DEGRADED_FALLBACK: reason=<mcp_err>+<sqlite_err>` emitted. MCP unavailability is NEVER an excuse for grep — only for SQLite. Audit: `post_agent_adg_audit.py`. Bypass: `ADG_SQLITE_FALLBACK_BYPASS=1`.
29. **Closed-loop router evidence mandatory.** All 10 routers (L0/bandit, L0/r5, L1/c0, L2/cascade, L3/shape, L3/reroute, L4/uwg, L5/hitl, L6/promo, L6/regret) MUST emit `ROUTER_DECISION:` + `emit_ledger_event` same code path. `L6/promo` promote: Wilson≥0.60, z≥1.96, uplift>0, n≥30. `L6/regret`: non-empty `by_layer_json`. Detail: `closed-loop-router-enforcement.md`. Audit: `post_agent_router_decision_audit.py`. Bypass: `ROUTER_ENFORCEMENT_BYPASS=1`.
30. **Author-Gate capture health — RETIRED** (ADR-093; native `AskUserQuestion` supersedes the `DECISION_CAPTURED:` ledger pipeline). Slot retained for stable numbering.
31. **SSOT folder routing for new files.** `check_*`/`*_gate.py` → `ops_scripts/ci/`; calibration/binder/poller → `ops_scripts/calibration/`; `purge_*`/`cleanup_*` → `ops_scripts/maintenance/`; `pre_*`/`post_*` hooks → `.claude/governance/scripts/`; else → `tools/<domain>/`. Pre-existing files exempt. Detail: `ssot-folder-enforcement.md`. Hook: `pre_write_gate.py`. Bypass: `SSOT_FOLDER_BYPASS=1`.
32. **Fort Knox certification integrity — RETIRED (2026-06-14).** The bottom-up requirements-certification arm (`RTC-REQ-*` → `compile_requirement_signoff.py` → Merkle/signature) is decommissioned; its integrity principle (claims emerge from a compiler, no green theater) lives in §37 + `002-pass-blocked-proof-contract`. Runtime teardown (`agentic_core/L7_auditability/**`, `tools/cert/**`) deferred — tracked in git history / ADR. Slot retained for stable numbering.
33. **Two-tier compliance (Anthropic).** The real always-on surface (root `CLAUDE.md` + ALL `.claude/rules/*.md`, which the native loader injects every session) MUST sum ≤86,016 bytes (84 KiB) — re-baselined from the legacy 51,200 (set for the retired 4-file `.mdc` design) by plan `always-on-rule-surface-cut-c7f3a1`. Procedural detail → skills; invariants → rules (thin pointer stubs); deterministic enforcement → hooks. Gate: `check_always_on_token_budget.py` (T7r — now measures + enforces the real surface). Bypass: `ALWAYS_ON_BUDGET_BYPASS=1`.
34. **Per-turn retrieval budgets.** `grep_search`+`code_search` ≤3/response (audit: `post_agent_grep_budget_audit.py`, bypass `GREP_BUDGET_BYPASS=1`). File reads (native `read_file`/`read_notebook`/`read_url_content` + MCP `read_text_file`/`read_file`/`read_multiple_files`) ≤10/response (audit: `post_agent_read_budget_audit.py`, bypass `READ_BUDGET_BYPASS=1`). Token-burn telemetry: `post_agent_token_telemetry.py` → `artifacts/governance/turn_budget.jsonl`; weekly: `ops_scripts/calibration/token_burn_weekly_report.py`. Detail: `scope-containment.md`.
35. **Author-Gate queue drain — RETIRED** (ADR-093; superseded by native `AskUserQuestion` at the point of decision). Slot retained for stable numbering.
36. **Plan–Notion registration — RETIRED (notion-wave-enforcement-removal).** The plan→Notion registration pipeline never functioned and is removed. **Plans are disk-only.** The only plan gates are the disk-side format lints (`check_plan_format_compliance`, `check_plan_wave_summary_top`, `check_plan_definition_of_done`) + `plan-location.md`. Slot retained for stable numbering.
37. **RCA mandatory on runtime failure.** Any repo-work response that sets `STATUS: FAIL` or surfaces a runtime-failure signal (`X3_BLOCK`, traceback, non-zero exit, pytest `N failed`, `PRE_RUN_BLOCKED`, `BLOCKED_*`/`MISSING_GRAPH_PATH`) MUST carry an `RCA:` block — symptom · root_cause (graded §20) · evidence · fix_or_next (§7) · recurrence_guard. A green/PASS status over a body failure-signal is forbidden (an exit code or X3 label alone is not a runtime outcome). **On refactoring turns (T2/T3 code changes) the response MUST use the Outcome frame on EVERY turn (pass or fail) — Did it run? + verdict source + provenance · What worked · Failure · Next (the PASS/FAIL verdict is the `STATUS:` line; the frame proves it, it does not re-vote); omitting it is `missing_refactor_outcome`. On a failure the frame MUST carry the deep Layered RCA: Immediate symptom → Failing layer (isolated from the surfacing layer) → Why-chain (apply "but why?" and dig until the true root, even across many levels; ≥2 descent levels) → Root cause (DISTINCT from the symptom) → Evidence → Confidence. Stopping at a symptom, a single-hop cause, or root==symptom is `shallow_rca`.** Detail: `001-runtime-seam-execution.md` § Runtime failure ⇒ RCA mandatory. Audit: `post_agent_runtime_rca_audit.py` → `artifacts/governance/runtime_rca_violations.jsonl` (kinds `missing_refactor_outcome`/`missing_rca`/`incomplete_rca`/`status_signal_mismatch`/`shallow_rca`). Bypass: `RUNTIME_RCA_AUDIT_BYPASS=1`.

## Tier Classification

| Tier | Scope | ADG Requirement |
|------|-------|----------------|
| **T0 — Question** | No code changes | ADG cache optional |
| **T1 — Trivial** | ≤1 file, ≤20 lines | Scoped tests only |
| **T2 — Scoped** | 2–5 files, single layer | Query ADG blast radius |
| **T3 — Architectural** | >5 files or cross-layer | Full ADG protocol mandatory |

ADG graph is the **primary** analysis primitive. `grep_search` for dependency analysis FORBIDDEN. Decision tree: `.claude/skills/graph-analysis/tool_routing_decision_tree.md` (auto-load via `graph-analysis` skill). Any query about imports / consumers / references / blast radius / layers / function-or-class names → ADG MCP, never grep. Literal text / TODOs / non-Python content → `grep_search` allowed.

**Degraded fallback** (§28): before grep for any graph query, call `adg_health`. Fallback only when health red AND response contains `DEGRADED_FALLBACK: reason=<...>`. Silent fallback = `severity: critical` in `adg_first_violations.jsonl`. Enforcement chain: `graph-analysis` skill (auto-load) → `pre_prompt_classifier.py` step 0 → this rule → `post_agent_adg_audit.py`.

## Quick Gates

- Plan SSOT: `plans/<name>-<6hex>.md` (legacy `.claude/plans/` still valid) — never `docs/reports/plans/` for plans
- Python file I/O: `encoding="utf-8"`
- `grep_search` permitted only to confirm literals, never for dependency tracing

## Extended Doctrine (model_decision rules — load on demand)

`adg-analysis-procedures.md` · `adg-canonical-invariants.md` · `plan-first-enforcement.md` · `memory-management.md`

> Deprecated ADG/Author-Gate/deferred-scope/notion-plan stubs and the Notion plan-status/wave/registration rules were removed (never functioned; plans are disk-only). Signal lives at canonical targets (constitutional §6/§24/§36, `plan-location.md`); full map: `docs/reports/governance/retired-rules-index.md`.
