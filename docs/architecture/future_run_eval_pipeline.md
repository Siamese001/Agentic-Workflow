# Future-Run Evaluation Pipeline

Evaluation path for async future-run improvement proposals. No live-run mutation. No direct L4 write.

## Pipeline stages

```
SealedL2Artifact  +  CurrentRunEvaluationResult
         │                        │
         └──────────┬─────────────┘
                    ▼
         build_shadow_eval_packet()
         [async_eval_packet.py]
                    │
                    ▼
         ShadowPacketGrader.grade()
         [shadow_eval_grader.py]
                    │
                    ▼
         RcaAggregator.ingest() → clusters()
         [rca_aggregator.py]
                    │
                    ▼
         PromotionStager.stage()
         [promotion_stager.py]
                    │
                    ▼
         PromotionPacketizer.packetize_pending()
         [promotion_packet.py]  → approval_state=PENDING
                    │
                    ▼
         transition_approval_state(packet, APPROVED)
         [promotion_packet.py]  → approval_state=APPROVED
                    │
                    ▼
         L6ShadowEvalPipeline.approve_and_handoff()
         [shadow_eval_pipeline.py]
                    │
                    ├── dry_run=True  → HandoffRecord(committed=False)
                    │                   packet stays APPROVED
                    │
                    └── dry_run=False, committed=True
                            │
                            ▼
                   GovernedHandoffAgent.handoff()
                   [governed_handoff.py]
                            │
                            ├── PromotionTokenIssuer.issue_promotion_token()  [L2]
                            ├── PromotionAuthority.update_pointer_via_gateway() [L4 — sole write seam]
                            └── TelemetryBus.publish(PROMOTION_ROLLOUT)  [BUS T]
                            │
                            ▼
                   HandoffRecord(committed=True)
                            │
                            ▼
                   transition_approval_state(packet, COMMITTED)
                   approval_state=COMMITTED
```

## Module ownership

| Stage | Owner module | Run scope |
|---|---|---|
| Live current-run evaluation | `agentic_core/L5_safety/enforcement/exit_control_gate.py` | `CURRENT_RUN` |
| Async future-run evaluation | `agentic_core/L6_observability/utils/evaluation/shadow_eval_grader.py` | `FUTURE_RUN` |
| Approval state transitions | `agentic_core/L6_observability/utils/evaluation/promotion_packet.py` | `FUTURE_RUN` |
| Promotion staging | `agentic_core/L6_observability/utils/evaluation/promotion_stager.py` | `FUTURE_RUN` |
| Governed / UWG handoff | `agentic_core/L6_observability/utils/evaluation/governed_handoff.py` | `FUTURE_RUN` |
| Pipeline coordinator | `agentic_core/L6_observability/utils/evaluation/shadow_eval_pipeline.py` | `FUTURE_RUN` |

## Approval state lifecycle

```
PENDING ──► APPROVED ──► COMMITTED   (only after HandoffRecord.committed=True)
   │            │
   └──► REJECTED└──► REJECTED
```

Invalid transitions raise `ValueError` from `transition_approval_state()`.

## Public entrypoints

Five clean canonical entrypoints cover the full pipeline; all other methods are internal.

| Entrypoint | Module | Purpose |
|---|---|---|
| `ExitControlGate.evaluate_sealed(artifact)` | `L5_safety/enforcement/exit_control_gate.py` | Live current-run evaluation → `CurrentRunEvaluationResult` |
| `ExitControlGate.shape_outcome(result, artifact)` | same | Maps disposition to typed outcome payload |
| `build_shadow_eval_packet(artifact, eval_result)` | `L6_observability/utils/evaluation/async_eval_packet.py` | Crosses CURRENT_RUN → FUTURE_RUN boundary; scope-guarded |
| `L6ShadowEvalPipeline.run_shadow_packet_cycle(packets)` | `L6_observability/utils/evaluation/shadow_eval_pipeline.py` | Grades `ShadowEvalPacket`s → RCA clusters → promotion candidates |
| `L6ShadowEvalPipeline.approve_and_handoff(packet)` | same | APPROVED → governed UWG handoff → optional COMMITTED |

## Adopted runtime entrypoints

The following runtime entrypoints were **adopted** in the repo-wide pass to route through the canonical pipeline.  All governed app runners delegate to `GovernedAppRunner.run_governed_core()`, which in turn calls `evaluate_and_emit()`.

### Canonical choke point: `evaluate_and_emit()`

`evidence_eval_bridge.evaluate_and_emit()` (`L3_orchestration/reasoning/engines/evidence_eval_bridge.py`) is the **only authorized live evaluation + L6 shadow seam**.  All evidence-upgraded execution lanes must route through it.

After adoption it fires both ingestion paths:

1. **`AsyncEvalPacket` path** — `ingest_eval_packet()` → `AsyncEvalIngester` queue (pre-existing narrow BUS T join)
2. **`ShadowEvalPacket` path** (new) — `_build_sealed_l2_artifact()` → `_run_sealed_exit_gate()` → `build_shadow_eval_packet()` → `enqueue_shadow_eval_packet()` → `ShadowEvalIngester` queue → drainable by `L6ShadowEvalPipeline.run_shadow_packet_cycle()`

### Shadow ingestion queue

`ShadowEvalIngester` (`L6_observability/utils/evaluation/async_eval_packet.py`) is the thread-safe in-process queue for `ShadowEvalPacket`s.  Access via `get_shadow_eval_ingester()`.  Drain via `ShadowEvalIngester.drain()` before calling `run_shadow_packet_cycle()`.

### Adopted governed runners

All six apps have been verified to already delegate fully to `GovernedAppRunner`:

| Runner | File | Status |
|---|---|---|
| `GovernedResearchRun` | `apps_research/integrations/governed_research_run.py` | Delegates |
| `GovernedExecRun` | `apps_exec/integrations/governed_exec_run.py` | Delegates |
| `GovernedRfpRun` | `apps_rfp/integrations/governed_rfp_run.py` | Delegates |
| `GovernedLicRun` | `apps_lic/integrations/governed_lic_run.py` | Delegates |
| `GovernedRgRun` | `apps_rg/integrations/governed_rg_run.py` | Delegates |

### Intentionally out of scope

| Entrypoint | Reason |
|---|---|
| `EvalSpine.commit_optimization()` | Data structures + stage enum only; no live safety gate or user-visible response |
| `ExecutionAdapter.submit()` | Eval-lab internal tracker; not a user-visible response path |
| `EvalSpineAdapter.execute()` | Spine CID delegation; eval-lab internal; no direct eval artifact emission |

## Invariants

The following invariants are enforced in code (not just in tests or docs):

### Structural invariants (ClassVar)
- `SealedL2Artifact.run_scope == "CURRENT_RUN"` — live run output
- `CurrentRunEvaluationResult.run_scope == "CURRENT_RUN"` — gate output
- All `ExitDisposition` outcome payloads: `run_scope == "CURRENT_RUN"`
- `ShadowEvalPacket.run_scope == "FUTURE_RUN"` — async learning input
- `PromotionPacket.run_scope == "FUTURE_RUN"` — future-run promotion

### Code-level scope guards (runtime `ValueError`)
1. **`build_shadow_eval_packet()`** — raises if `artifact.run_scope != "CURRENT_RUN"` or `eval_result.run_scope != "CURRENT_RUN"`. This is the only legal CURRENT_RUN → FUTURE_RUN boundary crossing.
2. **`ShadowPacketGrader.grade()`** — raises if `packet.run_scope != "FUTURE_RUN"`.
3. **`L6ShadowEvalPipeline.run_shadow_packet_cycle()`** — raises if any packet in the input list has `run_scope != "FUTURE_RUN"`.
4. **`GovernedHandoffAgent.handoff()`** — raises if `packet.run_scope != "FUTURE_RUN"`.

### Approval state invariants
5. `COMMITTED` is only reachable when `HandoffRecord.committed is True`.
6. `HandoffRecord.committed` is only `True` when `GovernedHandoffAgent.handoff(dry_run=False, approved=True)` completes a successful `PromotionAuthority.update_pointer_via_gateway()` call.
7. `GovernedHandoffAgent.handoff(dry_run=False, approved=True)` blocks if `packet.approval_state != "APPROVED"` (returns `HandoffRecord(committed=False, error=...)`).
8. `transition_approval_state()` is pure (returns a new frozen packet); invalid transitions raise `ValueError`.

### No-mutation invariants
9. No `approve_and_handoff()` path writes directly to L4 — all writes go through `PromotionAuthority.update_pointer_via_gateway()` in `GovernedHandoffAgent`.
10. `CurrentRunEvaluationResult` is a frozen dataclass; the async slice cannot mutate it.
11. Shadow eval never influences current-run disposition — `build_shadow_eval_packet()` is only called after `evaluate_sealed()` has returned.
