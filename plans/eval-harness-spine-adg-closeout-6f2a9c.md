---
plan_id: eval-harness-spine-adg-closeout-6f2a9c
plan_format: v2
plan_type: platform_core_change
touches_agentic_core: true
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: "TBD before W2 implementation"
dod_exempt: false
supersedes: []
---

# Eval Harness Spine ADG Closeout

Rectify the structural gaps between the proposed eval harness and the current Agentic-Workflow runtime spine, using ADG evidence as the wave-ordering authority.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-06-10

---

## Context (SCQA)

- **Situation** — The repo has meaningful eval assets: `tools/eval/run_capability_regression.py`, golden datasets, judge calibration workflows, X1D panel code, L5 exit evaluation, L6 flywheel promotion, boundary-fault tests, and runtime proof fixtures. The proposed harness defines four seams around the online spine: whole-spine replay, X1D judge calibration, L6 exhaust corpus growth, and X2 micro-evals.
- **Complication** — The latest available ADG SQLite snapshot (`artifacts/adg/adg_indexed_06082026_1212.sqlite`, snapshot `7d215be372b8db698594d811fda9d757c781ce05`, generated `2026-06-08T16:17:16Z`, dirty main) shows eval coverage gaps across every runtime layer, replay gaps on apps spine adapters and L6 flywheel, exit disposition coverage gaps on L5 exit eval, and determinism/provenance drift on the harness targets. The live ADG MCP transport was unavailable in Codex (`Transport closed`), so this plan is based on direct read-only SQLite fallback.
- **Question** — How do we turn the existing eval pieces into the proposed offline harness that promotes future changes without ever waiving current-run X2, X1D, X3, Exit, or UWG authority?
- **Answer** — Build the harness in dependency order: restore ADG/MCP freshness, define a canonical replay scenario contract, replay whole-spine fixtures through existing proof surfaces, harden X2/X1D/L6 seam suites, then bind promotion gates and Notion/CI evidence to the same receipt schema.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2, W1.3 | ADG freshness and gap inventory | ~18K | ADG snapshot can be regenerated or MCP restored locally | TODO | Fresh ADG health works; gap report names target files, nodes, and views |
| W2 | W2.1, W2.2, W2.3 | Whole-spine replay contract and runner | ~45K | Existing apps spine proof fixtures can be adapted without live providers | TODO | Pinned scenarios replay U0-to-L6 receipts; pass-rate gate uses candidate vs baseline |
| W3 | W3.1, W3.2, W3.3 | X2 micro-evals and X1D calibration trust | ~38K | Human-label corpus can be staged incrementally; fake/live judge lanes stay separate | TODO | X2 probes fail closed; stale/no-quorum X1D cannot clear; calibration threshold is consistent |
| W4 | W4.1, W4.2, W4.3 | L6 exhaust-to-corpus flywheel | ~30K | L6 exhaust packages are sealed and trace-bound before promotion | TODO | L6 stages triage records with review packets; capability graduation is deterministic |
| W5 | W5.1, W5.2, W5.3 | CI/UWG promotion binding and closeout | ~28K | Promotion gate can require artifacts without blocking unrelated changes | TODO | CI blocks missing harness evidence; UWG promotion cites regression receipt; docs/Notion synced |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Restore or regenerate ADG authority | TODO |
| W1.2 | Produce ADG-backed target matrix | TODO |
| W1.3 | Reconcile proposed harness seams to ADG views | TODO |
| W2.1 | Define replay scenario and receipt schemas | TODO |
| W2.2 | Implement whole-spine replay runner | TODO |
| W2.3 | Add baseline comparison and pass-rate evidence | TODO |
| W3.1 | Centralize X2 micro-eval fixture families | TODO |
| W3.2 | Harden X1D calibration/disqualification path | TODO |
| W3.3 | Bind judge snapshot IDs to every X1D score | TODO |
| W4.1 | Wire L6 exhaust ingestion to triage staging | TODO |
| W4.2 | Add human review packet and corpus graduation flow | TODO |
| W4.3 | Add adversarial and session-find corpus seeds | TODO |
| W5.1 | Update eval-harness CI triggers and gates | TODO |
| W5.2 | Add UWG/Notion evidence binding | TODO |
| W5.3 | Run verification, regenerate ADG, and close gaps | TODO |

---

## Out Of Scope

- Rewriting the online runtime spine in this plan.
- Allowing offline eval to override a current-run gate verdict.
- Replacing existing app-specific X1D/X2 validators with a single generic judge.
- Auto-promoting L6 findings directly into `data/eval/golden/` without review.
- Treating fake/mock provider receipts as live X1D proof.

---

## ADG Evidence Baseline

Source: `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_indexed_06082026_1212.sqlite`.

Snapshot metadata:
- `git_head_sha`: `7d215be372b8db698594d811fda9d757c781ce05`
- `git_branch`: `main`
- `git_dirty`: `1`
- `generated_at_utc`: `2026-06-08T16:17:16Z`

Important MCP caveat:
- `adg_health` and `adg_reopen_connections` failed in Codex with `Transport closed` during the original Codex audit.
- The ADG backend itself is healthy when invoked through the repo-local MCP handler path: mode `full`, SQLite healthy, Redis healthy, snapshot `06082026_1212`.
- The exposed Codex MCP transport regressed to `Transport closed` again on 2026-06-10 after a prior successful restart check.
- W1 must distinguish **backend health** from **Codex transport health** before implementation claims are made.

> **Codex transport recheck (2026-06-10).** `mcp__adg_sqlite.adg_health` and
> `mcp__adg_sqlite.adg_reopen_connections` both returned `Transport closed`.
> The repo-local ADG handler path remained healthy in `full` mode against snapshot
> `06082026_1212` with SQLite healthy, Redis healthy, and graph projection fresh.
> Local `adg_reopen_connections` returned `reopened=true, noop=true` because the
> active snapshot path and mtime were unchanged. There is no exposed Codex MCP-host
> restart tool in this session, so the actionable gap is host transport lifecycle
> supervision, not ADG backend or Redis cache health.

> **MCP verification update (2026-06-10, Claude Code).** `adg_health` is **healthy** and serving the
> SAME snapshot this plan cites (`06082026_1212`, 182,313 nodes / 1,072,457 edges, Redis healthy,
> graph projection fresh). Every MV named below EXISTS, and the following claims verified **exactly**
> against the live snapshot: eval-coverage 0.0% on every layer; all 7 `mv_runtime_spine_gaps` layer
> figures; the 3 `mv_trace_replay_eval_gaps` target files (`no_trace_replay_eval`); the
> `mv_replay_surface_gaps` mutation/replay counts (17/0, 16/0, 1/0); `exit_eval.py
> no_exit_disposition`; zero rows in `mv_gateway_bypass_paths` + `mv_live_future_mutation_conflicts`;
> drift flags on all 9 named files; `gold_set.jsonl` absent; `judge-calibration.yml` 0.6; narrow
> `eval-harness.yml` triggers; the GAP-1 runner premise (loads golden JSON, classifies stored labels,
> never executes the spine); and `executive_summary_x2` fan_in 299 / fan_out 36.
> **Two corrections were required** (see corrected Target node signals and GAP-3/GAP-9 notes):
> the five other node fan_in/fan_out figures were not reproducible on any counting basis, and the
> GAP-3 threshold mismatch is kappa-vs-agreement-rate, not a like-for-like number drift. Context
> added: `mv_determinism_provenance_drift` flags **5,344 files** repo-wide, so drift on the 9
> targets is background-level signal, not target-specific evidence.

Observed ADG gaps:
- `mv_eval_coverage_by_path`: 0.0 percent eval coverage for action nodes across L0, L1, L2, L3, L4, L5, L6, L_APP, L_PG, L_RUNTIME, L_SHARED, and L_TOOLS.
- `mv_runtime_spine_gaps`: L5 gap 304/533 modules, L6 gap 276/427, L2 gap 164/285, L3 gap 138/224, L1 gap 118/183, L0 gap 90/179, L4 gap 90/166.
- `mv_trace_replay_eval_gaps`: target files with no trace, replay link, or eval include `agentic_core/L6_observability/flywheel_promoter.py`, `apps_rg/__main__.py`, and `apps_shared/spine_emission/adapter.py`.
- `mv_replay_surface_gaps`: `apps_rg/__main__.py` has mutation_count 17 and replay_link_count 0; `apps_shared/spine_emission/adapter.py` has mutation_count 16 and replay_link_count 0; `flywheel_promoter.py` has mutation_count 1 and replay_link_count 0.
- `mv_exit_disposition_coverage`: `agentic_core/L5_safety/eval_spine/exit_eval.py` has `gap_type=no_exit_disposition`.
- `mv_determinism_provenance_drift`: drift flags appear on `tools/eval/run_capability_regression.py`, `apps_rg/runtime/validators/executive_summary_x2.py`, `apps_rg/runtime/judges/x1d_panel_harness.py`, `agentic_core/runtime/judges/panel/panel_runner.py`, `agentic_core/runtime/exit/x2_aggregator.py`, `apps_rg/__main__.py`, `apps_shared/spine_emission/adapter.py`, `agentic_core/L5_safety/eval_spine/exit_eval.py`, and `agentic_core/L6_observability/flywheel_promoter.py`.
- `mv_gateway_bypass_paths` and `mv_live_future_mutation_conflicts`: no rows in this snapshot for the sampled query, so the main risk is not provider bypass; it is missing replay/eval/disposition binding.

Target node signals (**corrected 2026-06-10** — the original Codex fan_in/fan_out figures for the
first five files were not reproducible against the snapshot on any counting basis (module-distinct,
module-total, file-aggregate, or `mv_high_fan_in_out_with_defects`); figures below are verified from
`mv_high_fan_in_out_with_defects` (hotspot view) with module distinct-neighbor degrees in parens.
Qualitative role descriptions stand; magnitude claims were overstated for `exit_eval` ("fan_out 130")
and `x1d_panel_harness` ("fan_out 152")):
- `tools/eval/run_capability_regression.py`: hotspot fan_in 0, fan_out 10 (module 5/27); current runner scores static golden labels rather than replaying the spine — **verified in code** (`_load_trials` + `_classify`).
- `agentic_core/L6_observability/flywheel_promoter.py`: hotspot fan_in 2, fan_out 10 (module 3/30); currently stages candidates only when called and `stage_to_disk=True`.
- `agentic_core/L5_safety/eval_spine/exit_eval.py`: hotspot fan_in 19, fan_out 33 (module 2/65); central exit surface with ADG exit disposition coverage gap (**gap row verified**).
- `agentic_core/runtime/judges/panel/panel_runner.py`: hotspot fan_in 2, fan_out 9 (module 1/25); generic X1D panel runner surface.
- `apps_rg/runtime/judges/x1d_panel_harness.py`: hotspot fan_in 13, fan_out 8 (module 4/48); app-specific bridge.
- `apps_rg/runtime/validators/executive_summary_x2.py`: high centrality X2 validator, fan_in 299 and fan_out 36 in hotspot view (**verified exact**).

---

## Gap Register

**GAP-1: Whole-spine replay is not the eval runner.**
- Current `tools/eval/run_capability_regression.py` loads golden JSON and classifies stored labels.
- Proposed harness requires pinned JD/briefing/scenario fixtures to execute the runtime spine and compare emitted receipts.
- Impact: promotion can be blocked or passed by static labels without proving U0-to-L6 behavior.

**GAP-2: Baseline comparison is documented but not structurally bound.**
- `evaluation-promotion-gate.md` requires baseline snapshots and regression detector verdicts.
- Current runner emits current pass-rate only.
- Impact: regressions can hide when absolute pass-rate remains above a threshold, and improvements cannot be attributed.

**GAP-3: X1D calibration trust is split across docs, workflow defaults, and runtime fields.**
- Cadence rule disqualifies below agreement 0.7, but `judge-calibration.yml` defaults to 0.6.
- **Refinement (2026-06-10 verification):** the two thresholds are not even the same statistic —
  the workflow's 0.6 is `MIN_KAPPA` (Cohen's κ, chance-corrected) while the cadence policy's 0.7 is
  `human_agreement_rate` (raw agreement). κ 0.6 and agreement 0.7 are not directly comparable
  (raw agreement is systematically higher than κ on imbalanced label sets). W3.2 must pick ONE
  statistic and convert/align both surfaces — not just bump 0.6 → 0.7.
- `data/judge_calibration/gold_set.jsonl` is absent in the checked worktree (**verified absent**); `data/eval/golden` has too few two-rater items for promotion-grade calibration.
- Impact: a judge can appear calibrated by CI while failing the proposed trust bar.

**GAP-4: X2 micro-evals are not a first-class suite.**
- Boundary-fault tests cover important hard-line behavior, but the proposed fact-checker probes are scattered or absent as a named suite.
- Required probes include decimal `99.99%` single-thought acceptance, two-sentence bullet rejection, self-check non-leakage, token truncation with zero merged bullets, and zero judge-row refresh.
- Impact: regressions in deterministic gates can be missed or rediscovered through E2E failures.

**GAP-5: L6 exhaust-to-corpus loop is optional and not end-to-end.**
- `flywheel_promoter.promote_candidate()` exists, but staging is opt-in and no required review packet/graduation pipeline is visible.
- Impact: session findings do not reliably become capability scenarios or graduate to regression.

**GAP-6: Replay/disposition evidence is missing on app spine adapters.**
- ADG reports replay gaps on `apps_rg/__main__.py` and `apps_shared/spine_emission/adapter.py`.
- Impact: the harness cannot prove that app-level mutations and spine emissions are replay-tied.

**GAP-7: Exit disposition coverage is not ADG-visible for L5 exit eval.**
- ADG flags `agentic_core/L5_safety/eval_spine/exit_eval.py` with `no_exit_disposition`.
- Impact: whole-spine replay cannot show the hard line that per-run verdicts remain owned by X2/X1D/X3/Exit.

**GAP-8: CI trigger surface is too narrow for spine promotion.**
- `eval-harness.yml` triggers on judge/eval files but not all runtime/app spine surfaces implicated by ADG.
- Impact: changes to `agentic_core/runtime/**`, L5/L6 spine code, or apps spine adapters can bypass the offline harness.

**GAP-9: ADG MCP availability is itself a planning blocker. — PARTIALLY RESOLVED (2026-06-10)**
- Codex saw closed ADG transport and the branch worktree lacks local ADG SQLite artifacts.
- **Update:** the ADG backend now returns healthy through the repo-local MCP handler path
  (mode=full, SQLite+Redis healthy, snapshot `06082026_1212`, 182,313 nodes / 1,072,457 edges,
  graph projection fresh). A Codex restart briefly exposed a healthy MCP process, but the callable
  `mcp__adg_sqlite.adg_health` surface later regressed to `Transport closed`.
- **Residual:** Codex transport stability. The backend and cache path are healthy; the exposed MCP
  transport still needs lifecycle supervision and restart proof before agents can rely on it as
  the primary ADG access surface.
- **Residual:** snapshot FRESHNESS. `06082026_1212` was generated 2026-06-08 from dirty main and
  predates substantial apps_rg changes (C0.2 evidence bootstrap, dense-filter fix, bullet-gate
  fixes, judge-refresh re-enable landed 06-09/06-10). W1.1's remaining work is regeneration, not
  restoration.
- Impact: future implementation waves cannot safely claim ADG-backed closure until both Codex
  transport stability and snapshot freshness are restored.

---

## Wave 1 - ADG Freshness and Gap Inventory

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED - read-only ADG/gap inventory and report generation.

**Phases**:
- **W1.1** - Restore or regenerate ADG authority | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** - Produce ADG-backed target matrix | ~7K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.3** - Reconcile proposed harness seams to ADG views | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- `adg_health` returns a live snapshot ID, SQLite path, node count, and edge count.
- Fresh ADG snapshot generated from the active branch or primary checkout, with dirty-state recorded.
- Target matrix maps each proposed harness seam to files, nodes, ADG views, gap rows, and tests.
- If MCP remains unavailable, a fallback report explicitly records direct-SQL provenance and blocker status.

---

## Wave 2 - Whole-Spine Replay Contract and Runner

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: B

**Authorization**: REQUIRED - touches platform core runtime/eval contracts and promotion evidence.

**Phases**:
- **W2.1** - Define replay scenario and receipt schemas | ~12K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** - Implement whole-spine replay runner | ~22K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.3** - Add baseline comparison and pass-rate evidence | ~11K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- New scenario schema pins fixture hashes, prompt/rubric/config versions, expected receipt set, expected disposition, replay seed, and baseline snapshot.
- Replay runner executes or simulates the full spine boundary contract without live provider dependence by default.
- Receipt output includes U0/L1/C0/PA/L2/X2/X1D/X3/Exit/UWG/L6 references where applicable.
- Regression evidence compares candidate vs baseline and fails on safety regressions regardless of aggregate pass-rate.

---

## Wave 3 - X2 Micro-Evals and X1D Calibration Trust

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** - Centralize X2 micro-eval fixture families | ~13K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** - Harden X1D calibration/disqualification path | ~14K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.3** - Bind judge snapshot IDs to every X1D score | ~11K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Named X2 micro-eval suite covers decimal metrics, sentence-count traps, self-check leakage, token truncation, empty judge rows, mock/unavailable paths, and UNKNOWN-not-PASS.
- `judge-calibration.yml` threshold matches policy or the policy is deliberately changed with evidence.
- Stale, over-budget, or under-agreement judges are disqualified before score aggregation.
- No quorum forces `escalate_hitl` and cannot produce a clear/pass disposition.
- Every X1D score in replay receipts carries judge ID, rubric version, provider mode, calibration snapshot, and transport provenance.

---

## Wave 4 - L6 Exhaust-to-Corpus Flywheel

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** - Wire L6 exhaust ingestion to triage staging | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.2** - Add human review packet and corpus graduation flow | ~12K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.3** - Add adversarial and session-find corpus seeds | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- L6 sealed exhaust packages can deterministically create triage scenario proposals.
- Triage records include source run, evidence refs, target dataset, reason codes, replay key, and review status.
- Human review is required before movement into `data/eval/golden/`.
- Capability-to-regression graduation uses sustained pass-rate history and writes a proposal rather than mutating taxonomy directly.
- Frozen scenarios cover the proposed examples: token truncation, judge-refresh off, decimal false positive, and zero merged bullets.

---

## Wave 5 - CI/UWG Promotion Binding and Closeout

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: E

**Phases**:
- **W5.1** - Update eval-harness CI triggers and gates | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.2** - Add UWG/Notion evidence binding | ~9K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.3** - Run verification, regenerate ADG, and close gaps | ~9K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- CI triggers include `agentic_core/runtime/**`, `agentic_core/L5_safety/eval_spine/**`, `agentic_core/L6_observability/**`, `apps_shared/spine_emission/**`, relevant `apps_rg/runtime/**`, `tools/eval/**`, and judge config/data.
- Promotion gate requires a whole-spine regression receipt for prompt/rubric/policy/config changes.
- UWG promotion request cites the regression receipt and baseline snapshot.
- Final ADG snapshot shows target gaps closed or explicitly deferred with reasons.
- Notion Plans row links the plan path and status; closeout updates status only after all waves are complete.

---

## Execution Details

### W1.1 - Restore or Regenerate ADG Authority
**Scope**: Make ADG queryable before implementation work.

**Commands**:
```bash
python -m tools.adg.mcp.server --help
python tools/generate/generate_full_adg.py --help
python -m tools.adg.validate_snapshot artifacts/adg/<latest>.sqlite
```

**Notes**:
- Prefer MCP `adg_health` once restored.
- If MCP remains down, use read-only SQLite with explicit snapshot metadata in every report.

### W1.2 - Produce ADG-Backed Target Matrix
**Scope**: Export target rows from ADG views into a report under `docs/reports/adg/`.

**Queries**:
```sql
SELECT * FROM mv_eval_coverage_by_path;
SELECT * FROM mv_runtime_spine_gaps;
SELECT * FROM mv_trace_replay_eval_gaps WHERE file IN (...target files...);
SELECT * FROM mv_replay_surface_gaps WHERE gap_flag = 1;
SELECT * FROM mv_exit_disposition_coverage WHERE gap_type != '';
SELECT * FROM mv_determinism_provenance_drift WHERE drift_flag = 1;
```

### W1.3 - Reconcile Proposed Harness Seams to ADG Views
**Scope**: Map the diagram's seams to concrete surfaces:
- [1] Whole-spine replay rig -> `tools/eval`, apps spine runners, runtime proof fixtures.
- [2] Judge calibration -> `tools/exit_eval/run_judge_calibration.py`, `agentic_core/evaluation/judges/calibration.py`, runtime panel runner.
- [3] L6 exhaust corpus -> `agentic_core/L6_observability/flywheel_promoter.py`, `data/eval/triage`, `data/eval/golden`.
- [4] X2 micro-evals -> app validators and `agentic_core/runtime/exit/x2_aggregator.py`.

### W2.1 - Define Replay Scenario and Receipt Schemas
**Scope**: Add schemas for scenario input and replay output; keep them app-agnostic and receipt-first.

**Required fields**:
- scenario_id
- fixture_hashes
- candidate_ref
- baseline_ref
- expected_spine_receipts
- expected_disposition
- judge_snapshot_requirements
- hard_line_assertions

### W2.2 - Implement Whole-Spine Replay Runner
**Scope**: Extend or wrap `tools/eval/run_capability_regression.py` with a replay mode that invokes spine proof packages rather than static label classification.

**Guardrails**:
- Default lane must be offline/fake-provider-safe.
- Fake lanes cannot clear live proof.
- UNKNOWN, mock, blocked, skipped, or unavailable cannot count as pass for runtime authority.

### W2.3 - Add Baseline Comparison and Pass-Rate Evidence
**Scope**: Persist candidate-vs-baseline reports with deltas and safety-regression vetoes.

**Evidence shape**:
- baseline_snapshot_id
- candidate_snapshot_id
- total_scenarios
- pass/warn/fail/unknown counts
- per-dimension deltas
- safety veto results
- regression_detector verdict

### W3.1 - Centralize X2 Micro-Eval Fixture Families
**Scope**: Build small deterministic fixtures per gate and app validator family.

**Initial fixture families**:
- decimal metric single-thought acceptance
- two-sentence bullet rejection
- self-check leakage rejection
- token truncation with zero merged bullets
- empty judge-row refresh
- UNKNOWN-not-PASS

### W3.2 - Harden X1D Calibration/Disqualification Path
**Scope**: Align policy and workflow thresholds, add stale judge and no-quorum negative controls.

### W3.3 - Bind Judge Snapshot IDs to Every X1D Score
**Scope**: Ensure replay receipts make score trust auditable.

### W4.1 - Wire L6 Exhaust Ingestion to Triage Staging
**Scope**: Make L6 exhaust packages produce deterministic triage records when candidate signals fire.

### W4.2 - Add Human Review Packet and Corpus Graduation Flow
**Scope**: Define review status and manual promotion path into `data/eval/golden/`.

### W4.3 - Add Adversarial and Session-Find Corpus Seeds
**Scope**: Seed known failure classes from recent session findings and boundary-fault matrix.

### W5.1 - Update Eval-Harness CI Triggers and Gates
**Scope**: Ensure spine-changing PRs cannot bypass eval harness.

### W5.2 - Add UWG/Notion Evidence Binding
**Scope**: Require promotion attempts to cite replay/regression receipts.

### W5.3 - Run Verification, Regenerate ADG, and Close Gaps
**Scope**: Prove closure through tests, ADG views, and plan/Notion status updates.

---

## Definition of Done

DoD-1: Fresh ADG proof exists.
- Evidence: `adg_health` returns a current snapshot or direct SQLite report records snapshot metadata and fallback reason.
- Status: TODO

DoD-2: Whole-spine replay runner exists and produces receipts.
- Evidence: `python tools/eval/run_capability_regression.py --suite regression --replay-spine --out artifacts/eval/spine_regression_run.json` exits 0 or 1 by scenario outcome, not harness error.
- Status: TODO

DoD-3: X2 micro-eval suite is green.
- Evidence: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/eval tests/unit/apps_rg -q` shows the new micro-eval selectors pass.
- Status: TODO

DoD-4: X1D calibration trust gate is enforced.
- Evidence: stale, under-agreement, over-unknown-budget, and no-quorum fixtures all produce `escalate_hitl` or blocked promotion, never clear/pass.
- Status: TODO

DoD-5: L6 corpus flywheel is review-gated.
- Evidence: sealed exhaust creates `data/eval/triage/<event_id>.json`; no direct write into `data/eval/golden/` occurs without review marker.
- Status: TODO

DoD-6: Promotion gate is bound to baseline comparison.
- Evidence: CI fails when a prompt/rubric/policy/config change lacks a whole-spine regression receipt with baseline comparison and safety veto fields.
- Status: TODO

DoD-7: ADG target gaps are closed or explicitly deferred.
- Evidence: fresh ADG query shows target rows removed from `mv_trace_replay_eval_gaps`, `mv_replay_surface_gaps`, and `mv_exit_disposition_coverage`, or a deferral report names owner and reason.
- Status: TODO

DoD-8: Plan registration and status are synchronized.
- Evidence: Notion Plans row exists with Status `Not Started`, `Exists On Disk=true`, and `Plan File Path=C:\Git\Agentic-Workflow-FRESH\plans\eval-harness-spine-adg-closeout-6f2a9c.md`.
- Status: TODO

---

## Verification vs Deferral

| Check | Required Before Completion | Deferrable? | Deferral Rule |
|---|---:|---:|---|
| ADG MCP health or documented direct-SQL fallback | Yes | No | Must be resolved or plan remains Waiting |
| Whole-spine replay receipt schema | Yes | No | Core of this plan |
| Live provider X1D proof | No | Yes | Live proof may remain manual if fake/offline lane is clearly non-authoritative |
| Human-labeled calibration corpus at full target size | No | Yes | Minimum seed can land first; full corpus tracked as backlog |
| CI trigger expansion | Yes | No | Required to prevent bypass |
| Notion registration | Yes | No | Required before wave execution |

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```text
DISCOVERED_SCOPE: plan=eval-harness-spine-adg-closeout-6f2a9c wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=eval-harness-spine-adg-closeout-6f2a9c decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=eval-harness-spine-adg-closeout-6f2a9c reason="<summary>" added="<waves/phases>" authorized="yes"
```

| Decision | When | Continues? |
|---|---|---|
| ACCEPTED | In-charter, absorbable | Yes, expanded scope |
| DEFERRED | Valid but time-gated | Yes, original scope |
| SPLIT_TO_NEW_PLAN | Too large | Yes, original scope |
| REJECTED | Gold-plating | Yes, original scope |

---

## Supersedes

| Predecessor slug | Reason |
|---|---|
| _None_ | Net-new plan for ADG-backed eval harness closeout |

_None - net-new plan._

---

## Marker Quick Reference

```text
PLAN_CREATED: slug=eval-harness-spine-adg-closeout-6f2a9c path=plans/eval-harness-spine-adg-closeout-6f2a9c.md status=Not Started
WAVE_START: plan=eval-harness-spine-adg-closeout-6f2a9c wave=<N>
WAVE_COMPLETE: plan=eval-harness-spine-adg-closeout-6f2a9c wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=eval-harness-spine-adg-closeout-6f2a9c phase=<W1.1>
PLAN_COMPLETE: plan=eval-harness-spine-adg-closeout-6f2a9c note="<final outcome>"
```
