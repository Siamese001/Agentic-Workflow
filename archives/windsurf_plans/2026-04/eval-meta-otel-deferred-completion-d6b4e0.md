# Eval / Meta-Learning / OTel — Deferred Scope Completion Plan

**Status**: Done (all 5 waves shipped in commits `11ee7a8644` W-D1, `a3cca1afea` W-D2, `9d7ea4f6c4` W-D3+W-D4+W-D5, `5b5fd17442` residual/out-of-scope closure — SSOT-delegating telemetry shim + services/reasoning `__init__` exports + ADR-028 resolution; review doc: `docs/reports/plans/eval-meta-otel-deferred-completion.md`)
**Parent plan**: `.windsurf/plans/eval-meta-otel-gap-review-ef4a20.md`
**Parent review**: `docs/reports/plans/eval-meta-otel-gap-review.md`
**Predecessor commits**: `9468dcb3ec` (W1–W4 initial), `5c99fa635d` (μW-1/2/3)
**ADG baseline**: `artifacts/adg/adg_indexed_04222026_2021.sqlite`
**Tier**: T2 (scoped, ~8 files, single-concern: OTel + bus wiring + one pipeline fix)

---

## 1. Goal

Close every item flagged `DEFERRED_SCOPE:` in the parent review so that:

1. The remaining eval engine (`evaluation_retrieval_engine`) publishes to the canonical bus with OTel tracing.
2. All bus consumers and drift/replay modules in `system_learning/` emit OTel spans on the real tracer (not the 21-line stub).
3. The ADG pipeline actually populates materialized views (`mv_*`) and P-views (`v_p*`) in the snapshot, unblocking the constitutional §22 graph-layer-evidence gate for every T2/T3 plan repo-wide.
4. The `L_APP → L_SL` guardian exemption is audited (not just applied) — either kept with a documented ADR, or routed through a dedicated ops/infra layer.

## 2. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| **W-D1** | D1.1 | Wire `evaluation_retrieval_engine` — `analyze_trends`, `detect_regression_signals`, `generate_baseline_comparison` | 4,500 | Parent μW publisher pattern reused verbatim | Todo | 3 new publisher kinds, 3 roundtrip tests, zero regressions |
| **W-D2** | D2.1, D2.2 | Wire 7 L_SL/L6 tracer sites | 9,000 | `opentelemetry.trace.get_tracer()` import stable per parent W4 | Todo | `apps_eval/L_SL/L6 → opentelemetry` edges grow by ≥5 in new ADG snapshot |
| **W-D3** | D3.1, D3.2 | Diagnose + fix ADG MV/P-view overlay | 12,000 | MV builder source lives in `tools/generate_full_adg.py` or a downstream helper | Todo | `sqlite_master` on a fresh snapshot lists ≥10 `mv_*` and ≥4 `v_p*` views; `check_graph_layer_evidence.py` accepts a plan citing them |
| **W-D4** | D4.1 | Authority-boundary disposition: keep guardian exemption or relocate shim | 3,500 | Author-Gate triggered if W-D4.1 chooses relocation | Todo | Either (a) ADR documenting the eval→SL publisher boundary, or (b) shim relocated and p0 gates green without exemption |
| **W-D5** | D5.1 | Final review doc + close the parent plan | 2,000 | All W-D1..W-D4 success criteria met | Todo | `docs/reports/plans/eval-meta-otel-deferred-completion.md` written; parent plan marked Done |

**Total est.**: 31,000 tokens. 🟡 (yellow — manageable inside a single session if W-D3 isn't deeper than expected).

---

## 3. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| **D1.1** | Retrieval engine wiring | `@c:/Git/Agentic-Workflow/apps_eval/engines/evaluation_retrieval_engine.py` + `@c:/Git/Agentic-Workflow/apps_eval/integrations/meta_bus_publisher.py` (add 3 KIND constants) + new test file | 3 distinct result types → 3 payload shapes; pre-existing `_emit_*` shim calls retained | 4,500 | Todo |
| **D2.1** | L_SL bus consumers tracer wiring | `@c:/Git/Agentic-Workflow/system_learning/engines/bus_consumer.py`, `@c:/Git/Agentic-Workflow/system_learning/runtime_hitl_consumer.py`, `@c:/Git/Agentic-Workflow/system_learning/meta_learning/meta_learning_bus.py` | Each module currently has its own tracer abstraction or none; must unify on `opentelemetry.trace.get_tracer()` | 5,000 | Todo |
| **D2.2** | L_SL drift/replay tracer wiring | `@c:/Git/Agentic-Workflow/system_learning/engines/shadow_drift_analyzer.py`, `prompt_drift_detector.py`, `meta_learning_replay_binding.py`, `@c:/Git/Agentic-Workflow/agentic_core/L6_observability/utils/engines/meta_learning_bridge.py` | `meta_learning_bridge` is an L6 utility — may already use the real tracer; verify first | 4,000 | Todo |
| **D3.1** | MV/P-view overlay diagnosis | `@c:/Git/Agentic-Workflow/tools/generate_full_adg.py` + any helper in `tools/adg/` | Two ADG regens in prior session produced 0 `mv_*` / 0 `v_p*`; root cause unknown (possibly p0_runner early-exit skipping MV build) | 7,000 | Todo |
| **D3.2** | MV/P-view overlay fix + gate re-enable | `@c:/Git/Agentic-Workflow/tools/generate_full_adg.py` + possibly `@c:/Git/Agentic-Workflow/ops_scripts/ci/check_graph_layer_evidence.py` | Fix may reveal further brittleness in MV definitions | 5,000 | Todo |
| **D4.1** | Authority-boundary decision (Author-Gate) | Either new ADR at `@c:/Git/Agentic-Workflow/docs/architecture/adr/ADR-NNN-eval-sl-publisher-boundary.md` OR shim relocation to `@c:/Git/Agentic-Workflow/infrastructure/` | Requires scored ask_user_question because both options are materially distinct | 3,500 | Todo |
| **D5.1** | Final review + parent closure | `@c:/Git/Agentic-Workflow/docs/reports/plans/eval-meta-otel-deferred-completion.md` + edit to parent plan status | None | 2,000 | Todo |

---

## 4. Gap Register (known unknowns)

| # | Gap | Mitigation |
|---|-----|-----------|
| G1 | D3.1 root cause is speculative — we don't yet know why MVs aren't populating | First action is a read-only audit of `generate_full_adg.py`'s gate-vs-MV ordering; no edits until cause is proven |
| G2 | D2.1/D2.2 modules may already have bespoke OTel adapters that shouldn't be overwritten | Pre-edit: grep each for existing `get_tracer` / `Tracer` / `span` usage; if present, upgrade in place rather than replace |
| G3 | D4.1 is a genuine Author-Gate: keep exemption vs. relocate | Run the Author-Gate protocol (score + filter at 0.72 + dominance check + `ask_user_question`) when D4.1 is reached |
| G4 | Pre-existing unrelated `ImportError: MetricCollectorService` in `test_apps_eval_integration.py` | Do NOT touch in this plan; flag for a separate T1 in the verification doc |

---

## 5. Success Criteria (aggregate)

1. New ADG snapshot shows:
   - `apps_eval → opentelemetry` edges: 5 → **≥8** (retrieval engine adds ≥3)
   - `system_learning → opentelemetry` edges: baseline → **+≥5**
   - `sqlite_master` on the snapshot: **≥10 `mv_*` views and ≥4 `v_p*` views** populated
2. Full eval roundtrip test count: 10 → **≥13** (3 new for retrieval engine)
3. `python tools/generate_full_adg.py` either:
   - exits 0, OR
   - exits non-zero **only** on violations that existed BEFORE this plan (no new p0 blocks introduced by D4.1's chosen path)
4. `check_graph_layer_evidence.py` accepts a new plan citing ≥3 `mv_*` views + semantic edges + ≥1 `v_p*` view
5. Zero test regressions across `tests/integration/apps_eval/` and `tests/unit/agentic_core/L6_observability/`
6. Parent plan `eval-meta-otel-gap-review-ef4a20.md` marked Done; every `DEFERRED_SCOPE:` marker in its review has a matching Wave/Phase row in Notion flipped to Done

---

## 6. Execution Rules

- **Order**: W-D1 → W-D2 (parallel D2.1 / D2.2) → W-D3 (sequential: D3.1 audit MUST finish before D3.2 edits) → W-D4 (Author-Gate) → W-D5.
- **Commit cadence**: one commit per wave, with pre-commit gates green. ADG regen after each wave to keep snapshots aligned.
- **Rollback checkpoint**: before W-D3.2 (the pipeline edit), tag the tree so a failed MV fix doesn't strand the repo.
- **Testing**: new tests land with their wave — no "tests later."
- **No silent scope growth**: if a module in D2 turns out to need refactoring beyond tracer wiring, capture a fresh `DEFERRED_SCOPE:` marker and stop; don't expand in-flight.

---

## 7. Out of Scope (explicit)

- Replacing the `apps_eval._telemetry` no-op shim repo-wide — still requires its own plan (interacts with `lifecycle_trace_contract` SSOT).
- Fixing the pre-existing `MetricCollectorService` ImportError in `test_apps_eval_integration.py`.
- The 933-LoC `system_learning/engines/meta_learning_bus.py` learning pipeline — orthogonal to the 286-LoC queue that this plan targets.
- Runtime HITL (ADR-023 / L5 exit-control) — different concern despite shared terminology.
