---
plan_id: routing-decision-process-enhancement-9c7e4d
plan_type: infra
---

# Routing Decision Process — Cross-Layer Enhancement

Implement the ~48 enhancement opportunities surfaced across the 10 routing decision points (L0/L1/C0/PA/L2/L3/L5/Exit/UWG/L6) plus 7 cross-cutting concerns, in a wave-based approach. Foundation waves (W1–W3) ship in this session; specialized waves (W4–W13) are auto-captured as deferred scope for sequenced execution.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.windsurf/rules/constitutional.md` §22, §24 | ADG graph-layer + DEFERRED_SCOPE marker contracts | ✅ |
| `agentic_core/L0_routing/reasoning/path_router.py:89-578` | Existing 5-route dispatch (R1A/R1B/R3/R4/R5) | ✅ |
| `agentic_core/L0_routing/config/routing_calibration.py:1-234` | YAML-backed threshold SSOT loader | ✅ |
| `agentic_core/L6_observability/routing_calibration_metrics.py:1-234` | Existing OTEL fail-soft counter surface | ✅ |
| `agentic_core/L6_observability/routing_decision_events_schema.py:1-113` | ADR-025 §3 relational projection (per-layer extension target) | ✅ |
| `tools/routing/calibrate_thresholds.py:1-272` | Brier + Platt offline calibration tool | ✅ |
| `agentic_core/L0_routing/reasoning/meta_learning_integration.py:1-839` | MAML + Continual learner framework | ✅ |
| `docs/reference/03_L0_Routing/03_L0_Route_Decision_Switching_L3 v15.md` | RouteContract schema + 19 runtime gates | ✅ |
| `docs/reference/05_Exit_Evaluation_&_Control/Evaluation_Runtime_Gates.md` | Exit Eval gate inventory | ✅ |
| ADG snapshot `adg_indexed_04252026_0843.sqlite` (Redis HOT) | Fan-in / hotspot evidence | ✅ |

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| W1 | Unified `decision_events` SQLite schema with per-layer partition + 100% test coverage | New schema module + tests | A — schema + ensure-fn + 1st insert path | ~6k 🟢 |
| W2 | `outcome_success` backfill API + Exit Eval hook stub + tests | New backfill module + tests | B — API + lag metric + Exit hook | ~5k 🟢 |
| W3 | Provenance stamp helper (`decision_layer + policy_hash + snapshot_id + calibration_version + judge_version`) + tests | New provenance module + integration in PathRouter telemetry | C — stamp helper + integration test | ~5k 🟢 |
| W4 | Per-namespace bandit framework | New `bandit_router.py` + Thompson + per-namespace YAML wiring | D | ~12k 🟡 DEFERRED |
| W5 | R5 reason-code calibration | Per-trigger Brier + auto-demote bad triggers | E | ~8k 🟡 DEFERRED |
| W6 | C0 retrieval-mode bandit | Mode bandit + adaptive-k + citation coverage | F | ~14k 🟡 DEFERRED |
| W7 | L3 workflow shape calibration | Per-task-class loop iter + fan-out admission + oscillation amplitude | G | ~11k 🟡 DEFERRED |
| W8 | L2 R-CASC cost-aware escalation | Expected-utility cascade + provider fingerprint gate + Brier-by-provider | H | ~10k 🟡 DEFERRED |
| W9 | L5 HITL false-positive + adversarial probe | FP metric + nightly red-team suite + toxicity attribution audit | I | ~12k 🟡 DEFERRED |
| W10 | Exit Eval reroute ceiling + judge disagreement | Reroute counter + ensemble disagreement + replay-cert SLO | J | ~9k 🟡 DEFERRED |
| W11 | UWG write-class severity matrix | Reversibility classes + invalidation-coverage gate + alias atomicity proof | K | ~10k 🟡 DEFERRED |
| W12 | L6 promotion gates | Wilson-CI gate + auto-rollback canary + counterfactual shadow eval | L | ~13k 🟡 DEFERRED |
| W13 | Cross-layer regret accounting | End-to-end counterfactual replay + per-decision regret table | M | ~15k 🟡 DEFERRED |

**Foundation in this session (W1+W2+W3): ~16k tokens, GREEN.**
**Specialized backlog (W4–W13): ~114k tokens across 10 follow-up sessions, captured via DEFERRED_SCOPE markers at session-end.**

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.1 | Unified `decision_events` schema module | `agentic_core/L6_observability/decision_events_schema.py` (new) | Today only L0 has a relational projection (`routing_decision_events`); L1/C0/PA/L2/L3/L5/Exit/UWG/L6 decisions are unrecorded | ~3k | 🔲 TODO |
| W1.2 | Schema unit tests | `tests/unit/agentic_core/L6_observability/test_decision_events_schema.py` (new) | Schema must be idempotent + concurrent-safe + handle partial provenance | ~2k | 🔲 TODO |
| W1.3 | Migration shim from `routing_decision_events` | Same module — `migrate_from_routing_decision_events()` helper | Must preserve back-compat with ADR-025 §3 | ~1k | 🔲 TODO |
| W2.1 | Outcome backfill API | `agentic_core/L6_observability/decision_outcome_backfill.py` (new) | `outcome_success` is currently nullable in `routing_decision_events` — every learner downstream is starved | ~2k | 🔲 TODO |
| W2.2 | Backfill lag metric | Same module — `decision.outcome.backfill_lag_seconds` Counter | Need observability that backfill is happening within SLO | ~1k | 🔲 TODO |
| W2.3 | Backfill API tests | `tests/unit/agentic_core/L6_observability/test_decision_outcome_backfill.py` (new) | Need: 1st write, 2nd write idempotent, lag emission, missing-row error | ~2k | 🔲 TODO |
| W3.1 | Provenance stamp helper | `agentic_core/L6_observability/decision_provenance.py` (new) | All decisions must carry provenance for blameless rollback | ~2k | 🔲 TODO |
| W3.2 | Provenance integration in `PathRouter` | Edit `agentic_core/L0_routing/reasoning/path_router.py` — add provenance dict to telemetry | Wires the new helper into the existing routing telemetry path | ~1k | 🔲 TODO |
| W3.3 | Provenance tests | `tests/unit/agentic_core/L6_observability/test_decision_provenance.py` (new) | Determinism: same inputs → same stamp; partial fields tolerated | ~2k | 🔲 TODO |

---

## Gap Register

**GAP-1: Single-layer telemetry myopia.**
Only L0 routing decisions land in a relational table (`routing_decision_events`). All other decision layers (L1 plan-gen, C0 retrieval-mode, PA authority-order, L3 workflow-shape, L2 tier-cascade, L5 HITL/guardrail, Exit allow/deny/reroute, UWG commit, L6 promotion) emit OTEL spans only — no SQL-queryable join surface. Every learner that needs cross-layer evidence is forced to scan jsonl files.

**GAP-2: `outcome_success` nullable.**
`routing_decision_events.outcome_success INTEGER` accepts NULL. In practice, ~all rows are NULL because there is no enforced backfill from Exit Eval. This starves the meta-learner replay buffer, the Brier calibrator, and the auto-rollback signal. Fix: mandatory backfill within N seconds of Exit, plus a `decision.outcome.backfill_lag` metric.

**GAP-3: Missing decision provenance.**
A decision row carries `policy_hash` but not `snapshot_id`, `calibration_version`, or `judge_version`. Blameless rollback cannot identify which calibration/judge release produced a regression. Fix: provenance stamp helper that joins all five identifiers into one schema.

**GAP-4 .. GAP-48**: Catalogued in the Wave 4–13 phase summaries above; auto-captured as DEFERRED_SCOPE markers at session end.

---

## Execution Plan

### Phase W1.1 — Unified `decision_events` schema module
**Scope**: Create `agentic_core/L6_observability/decision_events_schema.py` with DDL for a generic `decision_events` table that supersedes `routing_decision_events` while remaining back-compat via a view.

**Acceptance**:
- `ensure_schema(conn)` is idempotent
- Inserting an L0 row, L1 row, and C0 row each succeed
- `decision_layer` column accepts: `L0_routing`, `L1_reasoning`, `C0_retrieval`, `PA_assembly`, `L2_execution`, `L3_orchestration`, `L5_safety`, `Exit_eval`, `UWG`, `L6_promotion`
- All five provenance fields present with NOT NULL except `outcome_success` (nullable until backfill)

### Phase W1.2 — Schema tests
**Scope**: Pytest module exercising idempotency, schema migration, partial-provenance tolerance, concurrent insert safety (under `:memory:` SQLite).

**Acceptance**: 100% coverage of the new module; all tests pass under `pytest -xvs`.

### Phase W1.3 — Migration shim
**Scope**: `migrate_from_routing_decision_events(conn)` copies all rows into the new table with `decision_layer='L0_routing'`. Old table retained as deprecated.

**Acceptance**: Round-trip test — N rows in → N rows out with stable digest.

### Phase W2.1 — Outcome backfill API
**Scope**: `agentic_core/L6_observability/decision_outcome_backfill.py` exposes `backfill_outcome(decision_id, outcome_success, latency_ms_total, error_code=None)`. Idempotent. Emits the lag metric.

**Acceptance**: Backfill on a missing row raises `DecisionRowMissingError`. Backfill on a row twice with same values is a no-op. Lag metric increments.

### Phase W2.2 — Backfill lag metric
**Scope**: New OTEL counter `routing.decision.outcome.backfill_lag_seconds` (Histogram). Buckets: 1, 5, 10, 30, 60, 300, 1800.

**Acceptance**: Histogram populated with one observation per backfill call.

### Phase W2.3 — Backfill API tests
**Scope**: Tests cover: first backfill, double backfill no-op, missing-row error, lag histogram emission, conflict on outcome mismatch.

**Acceptance**: 5+ tests, all green.

### Phase W3.1 — Provenance stamp helper
**Scope**: `agentic_core/L6_observability/decision_provenance.py` exposes `DecisionProvenance` dataclass (5 fields) + `current_provenance(layer)` factory that pulls live `policy_hash`, `snapshot_id`, `calibration_version`, `judge_version` from process-state. Falls back to "unknown" sentinels on missing.

**Acceptance**: Same inputs → same `provenance_digest` (sha256 of canonical JSON). Partial fields use sentinels, never raise.

### Phase W3.2 — `PathRouter` integration
**Scope**: Edit `agentic_core/L0_routing/reasoning/path_router.py` `select_path` to call `current_provenance("L0_routing")` and attach to `RoutingTelemetryContext` extras dict (additive — no breaking signature change).

**Acceptance**: Existing 5 callers of `route_with_confidence` unchanged. New telemetry rows carry provenance.

### Phase W3.3 — Provenance tests
**Scope**: Determinism, sentinel handling, integration with PathRouter.

**Acceptance**: 4+ tests, all green.

---

## Rules

- No PowerShell. `subprocess.run(argv, shell=False, timeout=30)`.
- No edits before this plan is saved.
- Foundation waves (W1–W3) ship in this session; remaining waves emit `DEFERRED_SCOPE:` markers per constitutional §24.
- Every new module includes a docstring referencing this plan's `plan_id`.
- Every test file mirrors source path under `tests/unit/`.
- All exception handlers use specific types (no `except Exception`).
- All loops > 10 lines use `ProgressReporter` from `tools/progress_display.py`.
- ADG SQLite snapshot must remain green; no new SC/AP violations introduced.

---

## Success Criteria

- [ ] Plan saved at `.windsurf/plans/routing-decision-process-enhancement-9c7e4d.md`
- [ ] W1: `decision_events_schema.py` exists with idempotent DDL + tests passing
- [ ] W2: `decision_outcome_backfill.py` exists with API + tests passing
- [ ] W3: `decision_provenance.py` exists + PathRouter integration + tests passing
- [ ] All foundation tests green: `pytest tests/unit/agentic_core/L6_observability/`
- [ ] Plan committed and pushed to `origin/main`
- [ ] DEFERRED_SCOPE markers emitted for W4–W13 (auto-captured to Notion via post-hook)

---

## Implementation Commands

```bash
# Sanity check ADG green
python tools/adg/adg_redis_ingest.py --check

# After W1–W3 ship
python -m pytest tests/unit/agentic_core/L6_observability/test_decision_events_schema.py -xvs
python -m pytest tests/unit/agentic_core/L6_observability/test_decision_outcome_backfill.py -xvs
python -m pytest tests/unit/agentic_core/L6_observability/test_decision_provenance.py -xvs

# Verify PathRouter still green
python -m pytest tests/unit/agentic_core/L0_routing/ -xvs -k "path_router"

# Commit + sync
git add .windsurf/plans/routing-decision-process-enhancement-9c7e4d.md \
        agentic_core/L6_observability/decision_events_schema.py \
        agentic_core/L6_observability/decision_outcome_backfill.py \
        agentic_core/L6_observability/decision_provenance.py \
        tests/unit/agentic_core/L6_observability/test_decision_events_schema.py \
        tests/unit/agentic_core/L6_observability/test_decision_outcome_backfill.py \
        tests/unit/agentic_core/L6_observability/test_decision_provenance.py
git commit -m "routing-enhancement W1-W3: unified decision_events + outcome backfill + provenance"
git push origin main
```

---

## Rollback Strategy

1. New tables / modules are additive — `git revert <commit>` is safe.
2. `routing_decision_events` (legacy) is preserved unmodified; the migration shim is opt-in.
3. PathRouter integration is via additive `extras` dict — removing the integration restores prior signature.

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| W1 schema test count | ≥ 6 | `pytest tests/unit/agentic_core/L6_observability/test_decision_events_schema.py --collect-only` |
| W2 backfill test count | ≥ 5 | `pytest tests/unit/agentic_core/L6_observability/test_decision_outcome_backfill.py --collect-only` |
| W3 provenance test count | ≥ 4 | `pytest tests/unit/agentic_core/L6_observability/test_decision_provenance.py --collect-only` |
| All foundation tests green | 100% | `pytest tests/unit/agentic_core/L6_observability/ -q` exit 0 |
| Commit pushed | yes | `git log -n 1 origin/main --oneline` includes commit subject |

