# Evaluation Pipeline — Release Acceptance Report

> Status: **ACCEPTED** · Date: 2026-04-13  
> Run: `python ops_scripts/ci/run_eval_pipeline_acceptance.py`

---

## Canonical Owners

| Owner | Module | Role |
|---|---|---|
| `ExitControlGate` | `L5_safety/enforcement/exit_control_gate.py` | Live current-run evaluation + disposition |
| `evidence_eval_bridge.evaluate_and_emit()` | `L3_orchestration/reasoning/engines/evidence_eval_bridge.py` | Sole canonical choke point: live gate → async + shadow ingestion |
| `AsyncEvalIngester` | `L6_observability/utils/evaluation/async_eval_packet.py` | Future-run async packet queue |
| `ShadowEvalIngester` | same | Future-run shadow packet queue |
| `build_shadow_eval_packet()` | same | CURRENT_RUN → FUTURE_RUN scope crossing |
| `L6ShadowEvalPipeline` | `L6_observability/utils/evaluation/shadow_eval_pipeline.py` | Async grading + promotion staging |
| `GovernedHandoffAgent` | `L6_observability/utils/evaluation/governed_handoff.py` | Sole durable-write seam (UWG) |
| `GovernedAppRunner` | `apps_shared/integrations/governed_app_runner.py` | Base runner orchestrating full live + shadow path |

---

## Adopted Entrypoints

All five governed app runners delegate to `GovernedAppRunner`, which calls `evaluate_and_emit()`:

| Runner | File |
|---|---|
| `GovernedResearchRun` | `apps_research/integrations/governed_research_run.py` |
| `GovernedExecRun` | `apps_exec/integrations/governed_exec_run.py` |
| `GovernedRfpRun` | `apps_rfp/integrations/governed_rfp_run.py` |
| `GovernedLicRun` | `apps_lic/integrations/governed_lic_run.py` |
| `GovernedRgRun` | `apps_rg/integrations/governed_rg_run.py` |

`evaluate_and_emit()` fires both ingestion paths in sequence:

1. `ingest_eval_packet()` → `AsyncEvalIngester` (pre-existing BUS T join)
2. `_build_sealed_l2_artifact()` → `_run_sealed_exit_gate()` → `build_shadow_eval_packet()` → `enqueue_shadow_eval_packet()` → `ShadowEvalIngester`

---

## Deferred / Fenced Paths

The following paths are **intentionally outside the canonical evaluation pipeline**.
Each carries an `EVAL-PIPELINE SCOPE: NON_CANONICAL_EVAL_LAB` marker in its module docstring.

| Module | Path | Why Out of Scope |
|---|---|---|
| `agentic_core/runtime/engine/eval_spine.py` | `EvalSpine.commit_optimization()` | In-memory OptimizationProposal state mutation only; no L5 exit gate, no durable write, no UWG |
| `apps_eval/integrations/execution_adapter.py` | `ExecutionAdapter.submit()` | Eval-lab internal in-memory execution log; no canonical pipeline coupling |
| `apps_eval/spine/eval_spine_adapter.py` | `EvalSpineAdapter.execute()` | Spine CID delegation (BaseSpineAdapter); no eval artifact emission |

**Rule:** Do not add canonical pipeline wiring to these modules. If a future feature requires them to emit eval artifacts, route through `evaluate_and_emit()` via a new governed caller.

---

## Queue / Backpressure Behavior

Both ingesters (`AsyncEvalIngester`, `ShadowEvalIngester`) are thread-safe, non-blocking, in-process queues (`maxsize=5000`).

| Behavior | Implementation |
|---|---|
| Successful enqueue | `_enqueue_count += 1`, returns `True` |
| Queue full (drop) | `_drop_count += 1`, returns `False`, emits `WARNING` log |
| Drain | `_drain_count += 1` per item consumed |
| Health snapshot | `.status()` → `{qsize, maxsize, saturation_pct, enqueue_count, drop_count, drain_count}` |

**Silent drops are now observable**: both `ingest_eval_packet()` and `enqueue_shadow_eval_packet()` emit a `WARNING` log on any drop.

**Saturation threshold:** at `saturation_pct >= 80%` (4000/5000 items), the pipeline is approaching capacity. No automatic back-pressure is applied — drain is the only relief path.

---

## Test Suites and Pass Status

| Suite | File | Tests | Status |
|---|---|---|---|
| Live pipeline integration | `test_pipeline_integration.py` | 7 | ✅ PASS |
| Async future-run slice | `test_async_future_run_slice.py` | 34 | ✅ PASS |
| Promotion / handoff | `test_promotion_approval_slice.py` | 62 | ✅ PASS |
| Adoption smoke | `test_eval_bridge_adoption.py` | 18 | ✅ PASS |
| Queue health / backpressure | `test_queue_health.py` | 14 | ✅ PASS |
| **Total** | | **135** | ✅ **PASS** |

All test files carry `pytestmark = pytest.mark.eval_pipeline`.

Run the suite:
```
python ops_scripts/ci/run_eval_pipeline_acceptance.py
# or directly:
python -m pytest tests/unit/agentic_core/L6_observability/utils/evaluation/test_pipeline_integration.py \
  tests/unit/agentic_core/L6_observability/utils/evaluation/test_async_future_run_slice.py \
  tests/unit/agentic_core/L6_observability/utils/evaluation/test_promotion_approval_slice.py \
  tests/unit/agentic_core/L6_observability/utils/evaluation/test_queue_health.py \
  tests/unit/agentic_core/L3_orchestration/reasoning/engines/test_eval_bridge_adoption.py \
  --tb=short -q
```

---

## Known Unrelated Failures (Excluded from Acceptance)

These 3 tests fail on `main` and are unrelated to the canonical evaluation pipeline:

| Test | Module | Reason |
|---|---|---|
| `test_statistics_tracking` | `LearningSignalEnricher` | `enrich_signal()` returns `None` — pre-existing bug |
| `test_low_quality_filtering` | same | same |
| `test_trend_analysis_degrading` | same | same |

Do not include `test_learning_signal_enrichment.py` in the `eval_pipeline` marker suite.

---

## Architecture Invariants Preserved

1. **Current-run / future-run separation** — `SealedL2Artifact.run_scope == "CURRENT_RUN"`; `ShadowEvalPacket.run_scope == "FUTURE_RUN"`; crossing guarded by `build_shadow_eval_packet()` scope check.
2. **Singular live disposition** — `ExitControlGate.evaluate_sealed()` is the only live gate call per request.
3. **Async evaluation is future-run only** — both ingesters are FUTURE_RUN; no live-run mutation path.
4. **Durable writes behind governed handoff only** — `GovernedHandoffAgent.handoff()` is the sole durable-write seam; all others are read-only or in-memory.
5. **Deferred paths do not masquerade as canonical** — `NON_CANONICAL_EVAL_LAB` marker in all three fenced modules.
6. **Queue drops observable** — `WARNING` log + `drop_count` counter; not silently discarded.

---

# Operational Runbook

## How to Validate the Live Path

```bash
# Run live gate + exit control integration tests
python -m pytest tests/unit/agentic_core/L6_observability/utils/evaluation/test_pipeline_integration.py -v
```

Expected: All 7 tests pass. If failures: check `ExitControlGate.evaluate_sealed()` in
`L5_safety/enforcement/exit_control_gate.py` and `SealedL2Artifact` construction in
`L2_execution/types/sealed_l2_artifact.py`.

## How to Validate the Async Path

```bash
python -m pytest tests/unit/agentic_core/L6_observability/utils/evaluation/test_async_future_run_slice.py -v
```

Expected: All tests pass. If failures: check `build_shadow_eval_packet()` scope guards and
`ShadowPacketGrader` in `L6_observability/utils/evaluation/shadow_eval_grader.py`.

## How to Validate the Promotion / Handoff Path

```bash
python -m pytest tests/unit/agentic_core/L6_observability/utils/evaluation/test_promotion_approval_slice.py -v
```

Expected: All tests pass. If failures: check `transition_approval_state()` in
`L6_observability/utils/evaluation/promotion_packet.py` and
`GovernedHandoffAgent.handoff()` in `L6_observability/utils/evaluation/governed_handoff.py`.

## What Queue Saturation Means

- **`saturation_pct < 50%`** — normal operation.
- **`saturation_pct 50–80%`** — elevated load; acceptable but monitor.
- **`saturation_pct > 80%`** — approaching capacity; drain soon or drops will occur.
- **`drop_count > 0`** — packets were silently discarded (WARNING logged).
  - Drops are non-fatal (no live-run impact).
  - Shadow evaluation data is lost for dropped packets.
  - Relief: call `ShadowEvalIngester.drain()` / `AsyncEvalIngester.drain()` more frequently,
    or reduce request rate.

Inspect live queue health:
```python
from agentic_core.L6_observability.utils.evaluation.async_eval_packet import (
    get_async_eval_ingester, get_shadow_eval_ingester
)
print(get_async_eval_ingester().status())
print(get_shadow_eval_ingester().status())
```

## What Blocked Handoff Means

`GovernedHandoffAgent.handoff(dry_run=False, approved=True)` returns `HandoffRecord(committed=False, error=...)`
when:
1. `packet.approval_state != "APPROVED"` — call `transition_approval_state(packet, "APPROVED")` first.
2. `PromotionAuthority.update_pointer_via_gateway()` fails — check UWG connectivity and L4 write permissions.

`HandoffRecord.committed == True` is the only evidence that a durable write occurred.

## Where to Look First When the Pipeline Appears Broken

| Symptom | First Look |
|---|---|
| No async packets in queue | `AsyncEvalIngester.status()["drop_count"]` — if > 0, queue was full |
| No shadow packets in queue | `ShadowEvalIngester.status()["drop_count"]` — same |
| Live disposition not firing | `ExitControlGate.evaluate_sealed()` in `exit_control_gate.py` |
| Shadow grading not promoting | `ShadowPacketGrader._PROPOSE_MIN_FAILURES` threshold in `shadow_eval_grader.py` |
| Handoff returning `committed=False` | `HandoffRecord.error` field; check `governed_handoff.py` |
| `evaluate_and_emit()` not called | Check `GovernedAppRunner.run_governed_core()` wiring in `governed_app_runner.py` |
| `l6_ingested` probe is `False` | `get_async_eval_ingester().qsize() or get_shadow_eval_ingester().qsize()` — both queues empty |
