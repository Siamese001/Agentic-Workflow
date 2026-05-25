# Exit Eval & Control — Code Execution Plan

**Plan ID:** `exit-eval-spine-code-fb2c19`
**Parent plan:** `.windsurf/plans/exit-eval-spine-gap-ce683b.md` (doc phase — EXECUTED)
**Scope:** Follow-up code work for ADR-036 … ADR-042 listed as "Open Items" in each ADR, collected here as one T3 execution plan with bounded micro-waves.
**Status:** EXECUTED (67/67 unit tests pass; CI gate smoke-validated end-to-end)
**Tier:** T3 (cross-layer: L5, L6, L2 trace emitter, UWG contract surface, CI)

## Constraints (from plan `-ce683b` §6)

Code is added only. Explicit non-touch list:
- `ADR-023-runtime-hitl-exit-control.md` content (referenced only)
- UWG internals (only the `uwg_commit_ref` contract surface is populated)
- Judge rubric weights / model swaps

## Package layout (new subpackage)

All new code lives under:

```
agentic_core/L5_safety/eval_spine/
```

L5 is cross-cutting per constitutional rules — `eval_spine` depends on
`config/` (schemas + rubric YAMLs) and stdlib only. No L0/L1/L2/L3 imports.

Flywheel promoter lives under `agentic_core/L6_observability/`.

## Wave Summary

| Wave | Focus | Micro-waves | Est. LOC | Status |
|---|---|---|---|---|
| **C1** | Schema alignment + config scaffolds | C1.1–C1.5 | ~300 | ✅ done |
| **C2** | Pure-utility modules | C2.1–C2.5 | ~650 | ✅ done |
| **C3** | Composite dataclasses + kill-switch | C3.1–C3.4 | ~550 | ✅ done |
| **C4** | Orchestrator + flywheel | C4.1–C4.2 | ~400 | ✅ done |
| **C5** | Unit tests | C5.1–C5.3 | ~900 | ✅ done |
| **C6** | CI gate | C6.1 | ~150 | ✅ done |

## Micro-wave Detail

### C1 — Schema alignment + config (no module deps)

| Micro | Artifact | Purpose |
|---|---|---|
| C1.1 | `config/schemas/escalation_packet.schema.json` (edit) | Align `hitl_class` enum with the existing `HitlClass` SSOT in `agentic_core/L5_safety/exit_control/hitl_classes.py` — avoid drift. |
| C1.2 | `config/contracts/README.md` (new) | Registry scaffold for output-contract kinds (ADR-039 §2.1). |
| C1.3 | `config/runtime_budget_policy.yaml` (new) | Tenant ceilings + per-route defaults (ADR-038 §2.2). |
| C1.4 | `config/schemas/kill_switch_audit.schema.json` (new) | ADR-042 §2.4 ledger row schema. |
| C1.5 | `config/schemas/judge_calibration_ledger.schema.json` (new) | `data/judge_calibration/` row schema (rule `judge-calibration-cadence.md`). |

### C2 — Pure-utility modules

| Micro | Module | Contract |
|---|---|---|
| C2.1 | `tool_call_canonicalizer.py` | `canonicalize_tool_call(tool, args) -> {"tool": str, "args_hash": str}` — JCS-style normalized JSON + sha256; strips volatile fields (`timestamp`, `request_id`, `trace_id`). |
| C2.2 | `trajectory_metrics.py` | Six Vertex metrics over lists of canonical records. Pure functions. |
| C2.3 | `budget_envelope.py` | `BudgetEnvelope` dataclass + `check_fit(consumed, envelope) -> BudgetFit`. |
| C2.4 | `claim_extractor.py` | Code-based deterministic extractor; sentence-level segmentation + support classification (`context`/`tool_output`/`parametric`/`unsupported`). |
| C2.5 | `output_contract_validator.py` | Dispatch on `kind` → validator (JSON-Schema / markdown-sections / tool_result_envelope / text_constraints / none). |

### C3 — Composite dataclasses

| Micro | Module | Notes |
|---|---|---|
| C3.1 | `exit_decision.py` | `ExitDecision` dataclass + `to_dict`/`from_dict` + JSON-Schema validation via `jsonschema` if available, else structural fallback. |
| C3.2 | `escalation_packet.py` | `EscalationPacket` dataclass + `from_exit_decision` factory. |
| C3.3 | `trace_grader.py` | Rubric loader + `grade(sealed_artifact, trace_spans, budget, contract) -> GraderOutput`. LLM-scored dims are stubs that return `Unknown` by default; deterministic signals (tool_selection where ledger comparable, safety_policy_adherence via policy-hit flags) compute real scores. Framework so an LLM backend can plug in later without schema changes. |
| C3.4 | `kill_switch.py` | In-memory store + `activate(scope, reason, ttl)` / `hit(request_context) -> Optional[KillSwitchHit]` / `release(scope)` + audit-ledger emit. |

### C4 — Orchestrator + flywheel

| Micro | Module | Notes |
|---|---|---|
| C4.1 | `exit_eval.py` | Top-level `evaluate_exit(sealed_artifact, envelope, contract, policy) -> ExitDecision`. Composes trace_grader + trajectory_metrics + budget_envelope.check_fit + output_contract_validator + kill_switch.hit → produces typed ExitDecision and (optionally) EscalationPacket. |
| C4.2 | `agentic_core/L6_observability/flywheel_promoter.py` | `promote_candidate(eval_event) -> Optional[TriageRecord]`. Reads candidate signals (ADR-040 §2.1), routes to target dataset (§2.2), writes to `data/eval/triage/`. |

### C5 — Tests

| Micro | Test path | Coverage |
|---|---|---|
| C5.1 | `tests/unit/agentic_core/L5_safety/eval_spine/test_pure_utilities.py` | canonicalizer, trajectory_metrics, budget_envelope, claim_extractor, output_contract_validator |
| C5.2 | `tests/unit/agentic_core/L5_safety/eval_spine/test_composites.py` | exit_decision schema roundtrip, escalation_packet factory, kill_switch activate/hit/release, trace_grader framework |
| C5.3 | `tests/unit/agentic_core/L5_safety/eval_spine/test_exit_eval_orchestrator.py` | evaluate_exit end-to-end, flywheel_promoter candidate detection |

### C6 — CI gate

| Micro | Script | Purpose |
|---|---|---|
| C6.1 | `ops_scripts/ci/check_exit_decision_schema.py` | Validates that any emitted ExitDecision JSON (found under `artifacts/eval_spine/`) conforms to `config/schemas/exit_decision.schema.json`. Fail-open when no artifacts present (no false reds in clean repo). |

## Success Criteria

- All new modules importable with zero side effects.
- Unit tests green (`pytest tests/unit/agentic_core/L5_safety/eval_spine/`).
- CI gate runs and passes on clean repo.
- ADG regeneration does not add P0/P1 violations attributable to the new subpackage.
- No changes under the non-touch list (ADR-023, UWG internals, judge weights).

## Non-goals

- LLM-judge backends for the 5 rubric dims (framework only; stubs return `Unknown`).
- Wiring `evaluate_exit` into the live §5 path — that is a separate T3 plan with SVP review.
- Calibration runs / population of `data/judge_calibration/`.
- Triage UI / retention automation.
- OTel semconv alignment for budget attributes.
