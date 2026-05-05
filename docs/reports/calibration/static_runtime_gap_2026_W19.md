# Static↔Runtime ADG Gap Report

- **Generated:** 2026-05-05 09:54:09 UTC
- **Static snapshot:** `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_indexed_05052026_0523.sqlite`
- **Lookback:** 30 days
- **Static L5/L6 nodes scanned:** 200
- **Runtime observed layers:** L0_ROUTING, L4_STATE, L6_OBSERVABILITY
- **Orphan count:** 200
- **Observability coverage:** 0.0%

## Top Orphans (static-only, never observed at runtime)

| Layer | Fan-in | Node | File |
|---|---:|---|---|
| L5 | 49 | `ADG::Symbol::agentic_core.L5_safety.runtime_gates.types.Disposition` | `agentic_core/L5_safety/runtime_gates/types.py` |
| L5 | 40 | `ADG::Symbol::agentic_core.L5_safety.runtime_gates.types.GateDecision` | `agentic_core/L5_safety/runtime_gates/types.py` |
| L5 | 39 | `ADG::Symbol::agentic_core.L5_safety.runtime_gates.types.GateContext` | `agentic_core/L5_safety/runtime_gates/types.py` |
| L5 | 30 | `ADG::Symbol::agentic_core.L5_safety.runtime_gates.base.register_gate` | `agentic_core/L5_safety/runtime_gates/base.py` |
| L5 | 30 | `ADG::Symbol::agentic_core.L5_safety.runtime_gates.types.RegressionSignal` | `agentic_core/L5_safety/runtime_gates/types.py` |
| L5 | 26 | `ADG::Symbol::agentic_core.L5_safety.runtime_gates.types.DecisionAlias` | `agentic_core/L5_safety/runtime_gates/types.py` |
| L5 | 23 | `ADG::Symbol::agentic_core.L5_safety.exit_control.hitl_classes.HitlClass` | `agentic_core/L5_safety/exit_control/hitl_classes.py` |
| L5 | 17 | `ADG::Symbol::agentic_core.L5_safety.runtime_gates.evaluate` | `agentic_core/L5_safety/runtime_gates/__init__.py` |
| L5 | 16 | `ADG::Symbol::agentic_core.L5_safety.enforcement.ingress_envelope_check.IngressEnvelopeCheck` | `agentic_core/L5_safety/enforcement/ingress_envelope_check.py` |
| L5 | 14 | `ADG::Symbol::agentic_core.L5_safety.identity.guardrail_bank.GuardrailOutcome` | `agentic_core/L5_safety/identity/guardrail_bank.py` |
| L5 | 14 | `ADG::Symbol::agentic_core.L5_safety.reasoning.hierarchy_healer.HierarchyAgent` | `agentic_core/L5_safety/reasoning/hierarchy_healer.py` |
| L6 | 14 | `ADG::Symbol::agentic_core.L6_observability.utils.evaluation.async_eval_packet.get_async_eval_ingester` | `agentic_core/L6_observability/utils/evaluation/async_eval_packet.py` |
| L6 | 14 | `ADG::Symbol::agentic_core.L6_observability.utils.evaluation.async_eval_packet.get_shadow_eval_ingester` | `agentic_core/L6_observability/utils/evaluation/async_eval_packet.py` |
| L5 | 13 | `ADG::Symbol::agentic_core.L5_safety.identity.principal_verifier.VerificationResult` | `agentic_core/L5_safety/identity/principal_verifier.py` |
| L5 | 12 | `ADG::Symbol::agentic_core.L5_safety.adapters.human_approval_adapter.AdapterError` | `agentic_core/L5_safety/adapters/human_approval_adapter.py` |
| L5 | 12 | `ADG::Symbol::agentic_core.L5_safety.adapters.human_approval_adapter.ApprovalOutcomeKind` | `agentic_core/L5_safety/adapters/human_approval_adapter.py` |
| L5 | 11 | `ADG::Symbol::agentic_core.L5_safety.adapters.human_approval_adapter.ApprovalHandle` | `agentic_core/L5_safety/adapters/human_approval_adapter.py` |
| L5 | 11 | `ADG::Symbol::agentic_core.L5_safety.enforcement.archival_gatekeeper_gate.ArchivalGatekeeper` | `agentic_core/L5_safety/enforcement/archival_gatekeeper_gate.py` |
| L5 | 11 | `ADG::Symbol::agentic_core.L5_safety.identity.runtime_entry_sweep.RuntimeLaneDecisionWithSweep` | `agentic_core/L5_safety/identity/runtime_entry_sweep.py` |
| L5 | 11 | `ADG::Symbol::agentic_core.L5_safety.runtime_gates.GateContext` | `agentic_core/L5_safety/runtime_gates/__init__.py` |
| L5 | 11 | `ADG::Symbol::agentic_core.L5_safety.types.heal_request_types.HealResult` | `agentic_core/L5_safety/types/heal_request_types.py` |
| L6 | 11 | `ADG::Symbol::agentic_core.L6_observability.semconv.gen_ai.ATTR_OPERATION_NAME` | `agentic_core/L6_observability/semconv/gen_ai.py` |
| L5 | 10 | `ADG::Symbol::agentic_core.L5_safety.enforcement.ingress_envelope_check.ClarificationRequired` | `agentic_core/L5_safety/enforcement/ingress_envelope_check.py` |
| L5 | 10 | `ADG::Symbol::agentic_core.L5_safety.eval_spine.exit_eval.SealedArtifact` | `agentic_core/L5_safety/eval_spine/exit_eval.py` |
| L5 | 10 | `ADG::Symbol::agentic_core.L5_safety.reasoning.location_validator.LocationValidatorAgent` | `agentic_core/L5_safety/reasoning/location_validator.py` |

## Interpretation

Orphans are L5/L6 functions present in the static dependency graph but never linked to a REQ exemplar in the runtime ledger window. High-fan-in orphans are the highest-priority closure candidates: many static callers, but no runtime evidence the code path fires.