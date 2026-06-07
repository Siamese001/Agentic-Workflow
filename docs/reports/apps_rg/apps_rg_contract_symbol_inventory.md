# apps_rg Contract Symbol Inventory

Generated: 2026-06-07

Scope: first safe slice of `apps_rg` lean-core binding. This report inventories actual contract symbols and current `apps_rg` import sites only. It does not create a facade and does not invent missing imports.

## Summary

apps_rg currently imports several canonical dataclasses from `agentic_core.runtime.contracts`, but it also contains migration debt through concrete `agentic_core.L0_routing`, `agentic_core.L2_execution`, `agentic_core.runtime.entry*`, and `agentic_core.runtime.judges` imports. The safe next step is a contract facade only after this inventory is reviewed.

No placeholder aliases are approved. In particular, do not equate:

- `RejectedRequest` with `ValidatedRequest`
- `SealedSectionArtifact` with `SealedL2Artifact`
- `ExitReviewPacket` with a plain `dict`

## Symbol Inventory

| Symbol | Verified Import Path | Current apps_rg Import Sites | Contract-Only or Concrete Runtime | Safe Future Facade Re-export? | Missing / Ambiguous | Recommended Migration Action |
|---|---|---|---|---|---|---|
| `ValidatedRequest` | `agentic_core.runtime.contracts.apps_rg_ingress_payload.ValidatedRequest` | `apps_rg/runtime/bindings/briefing_u0_signals.py`; `apps_rg/runtime/bindings/c0_binding.py`; `apps_rg/runtime/bindings/l1_binding.py`; `apps_rg/runtime/bindings/pa_binding.py`; `apps_rg/runtime/spine/governed_pa_compose.py`; `apps_rg/runtime/spine/spine_contract_loaders.py` | Contract-only import path | Yes | None | Re-export later from an apps_rg contract facade after facade creation is approved. |
| `RejectedRequest` | Not found as a spine contract. Related concrete notice: `agentic_core.L0_routing.intake.validated_request.RejectedRequestNotice` | `apps_rg/runtime/bindings/u0_rejection.py` imports `RejectedRequestNotice` from concrete L0 routing | Concrete runtime implementation | No | Missing canonical `RejectedRequest` contract | Do not alias. Inventory current rejection needs and request/define a real spine rejection contract or app-local migration protocol. |
| `L1PlanContract` | `agentic_core.runtime.contracts.l1_plan_contract.L1PlanContract` | `apps_rg/runtime/bindings/l0_binding.py`; `apps_rg/runtime/bindings/l0_route_evidence.py`; `apps_rg/runtime/bindings/l1_binding.py`; `apps_rg/runtime/bindings/pa_binding.py`; `apps_rg/runtime/spine/governed_pa_compose.py`; `apps_rg/runtime/spine/spine_contract_loaders.py` | Contract-only import path, except `governed_pa_compose.py` also imports an orchestration plan from concrete L0 routing | Yes for runtime contract path only | Concrete orchestration alias remains migration debt | Re-export canonical runtime contract later; burn down concrete orchestration alias through import-boundary ratchet. |
| `RouteContract` | `agentic_core.runtime.contracts.route_contract.RouteContract` | `apps_rg/runtime/bindings/l0_binding.py`; `apps_rg/runtime/bindings/l0_l3_otel_spans.py`; `apps_rg/runtime/bindings/l0_route_evidence.py`; `apps_rg/runtime/bindings/l2_binding_adapter.py`; `apps_rg/runtime/bindings/l3_binding.py`; `apps_rg/runtime/bindings/pa_binding.py`; `apps_rg/runtime/spine/governed_pa_compose.py`; `apps_rg/runtime/spine/spine_contract_loaders.py` | Contract-only import path, except `governed_pa_compose.py` also imports concrete L0 routing route classes | Yes for runtime contract path only | Duplicate concrete route contract usage is ambiguous | Re-export canonical runtime contract later; migrate concrete route adapters behind ports. |
| `GraphTraversePolicy` | `agentic_core.runtime.contracts.route_contract.GraphTraversePolicy` | `apps_rg/runtime/bindings/l0_binding.py` | Contract-only import path | Yes | None | Preserve. Do not weaken graph traverse policy. |
| `FinalEvidenceContract` | `agentic_core.runtime.contracts.final_evidence_contract.FinalEvidenceContract` | `apps_rg/runtime/bindings/l2_binding_adapter.py`; `apps_rg/runtime/bindings/l3_binding.py`; `apps_rg/runtime/bindings/pa_binding.py`; `apps_rg/runtime/spine/governed_l2_exit_compose.py`; several runtime C0/exit files reference it by annotation or construction | Contract-only import path, except `governed_pa_compose.py` imports a concrete L0 retrieval final contract | Yes for runtime contract path only | Concrete L0 retrieval final contract remains migration debt | Re-export canonical runtime contract later; isolate concrete retrieval adapter usage. |
| `CompiledPromptArtifact` | `agentic_core.runtime.contracts.compiled_prompt_artifact.CompiledPromptArtifact` | `apps_rg/runtime/bindings/l2_binding_adapter.py`; `apps_rg/runtime/bindings/l3_binding.py`; `apps_rg/runtime/spine/governed_l2_exit_compose.py` | Contract-only import path | Yes | apps_rg also has `apps_rg.prompt_assembly.contracts.CompiledPromptArtifact` | Reconcile app-local prompt artifact vs spine artifact before facade re-export. |
| `L3ToL2StepContract` | `agentic_core.runtime.contracts.l3_to_l2_step_contract.L3ToL2StepContract` | No direct apps_rg import found in this inventory | Contract-only import path | Yes, if later needed | Currently unused by apps_rg | Do not re-export until an apps_rg use exists. |
| `SealedL2Artifact` | `agentic_core.runtime.contracts.sealed_l2_artifact.SealedL2Artifact` | `apps_rg/runtime/bindings/exit_binding.py`; `apps_rg/runtime/bindings/l2_binding_adapter.py`; `apps_rg/runtime/bindings/l2_envelope_adapter.py`; `apps_rg/runtime/spine/governed_l2_exit_compose.py` | Contract-only import path | Yes | No canonical `SealedSectionArtifact` found | Re-export `SealedL2Artifact` later if needed; do not alias section artifacts to it. |
| `ExitReviewPacket` | Not found | No apps_rg import found | Missing | No | Missing canonical exit review packet | Define a spine exit contract or app-local migration `TypedDict` only after owner decision. |
| `ExitDispositionReceipt` | Not found | No apps_rg import found | Missing | No | `agentic_core.runtime.contracts.x3_disposition.X3Disposition` exists but is not the same name | Do not alias. Inventory exit receipt fields and request/define a canonical receipt if needed. |
| `RuntimeExhaustBundle` | Not found as a class. String reference exists in `agentic_core/runtime/contracts/future_run_promotion.py` field `source_runtime_exhaust_bundle_ref` | No apps_rg import found | Missing / reference-only | No | No canonical bundle class found | Treat as missing; use runtime exhaust refs only until a real contract exists. |
| `CommitRequest` | Not found as a spine contract class in searched paths | No apps_rg import found | Missing | No | L1 comments mention gate posture reusing CommitRequest shape, but no class was found | Do not alias to `dict`. Request/define a canonical commit contract only if implementation needs it. |

## Facade Readiness

Symbols that appear safe to re-export later, after facade approval:

- `ValidatedRequest`
- `L1PlanContract`
- `RouteContract`
- `GraphTraversePolicy`
- `FinalEvidenceContract`
- `CompiledPromptArtifact`, after app-local artifact ambiguity is resolved
- `L3ToL2StepContract`, only if apps_rg starts using it
- `SealedL2Artifact`

Symbols not safe to re-export:

- `RejectedRequest`
- `ExitReviewPacket`
- `ExitDispositionReceipt`
- `RuntimeExhaustBundle`
- `CommitRequest`

## Migration Notes

- Contract-only imports are not automatically the final dependency surface; they should converge through a future apps_rg contract facade.
- Concrete runtime imports are tracked by `docs/reports/apps_rg/apps_rg_forbidden_core_import_baseline.json`.
- Missing symbols require explicit owner decisions before implementation.
