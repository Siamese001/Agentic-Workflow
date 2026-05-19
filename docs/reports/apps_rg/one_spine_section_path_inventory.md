# One-spine section path inventory (Wave 1)

Generated: 2026-05-19T15:02:29.228918+00:00

## Summary

- **TWO_PATHS_FOUND:** True
- **CANONICAL_SPINE_TARGET:** U0 → L1 → L0 → C0 → PA → L2 → Exit → UWG → L4 → L6

## Path A — Section CLI (`python -m apps_rg --section <lane>`)

- Entry: `apps_rg/__main__.py`
- Dispatch: `apps_rg/runtime/orchestration/canonical_dispatch.py::run_canonical_apps_rg_from_cli_primitives`
- Exemplar: `apps_rg/runtime/sections/executive_summary_lane.py`
- Observed chain: CLI → canonical_dispatch.section_branch → proof_pool_resolver → section_graph_binding_shim → section_PA → section_L2 → section_X2 → section_X1D → section_X3 → section_L6_shadow

## Path B — Integrated R4 spine (no `--section`)

- Dispatch: `canonical_dispatch → run_integrated_r4_deterministic_pipeline`
- C0/PA: `agentic_core/runtime/entry/apps_rg_dispatch.py::run_ag2_retrieval_and_prompt (ValidatedRequest → c0_retrieve_apps_rg → pa_compose_apps_rg)`

## Contract bypass matrix

| Contract | Section emits canonical | Substitute | R4 emits |
|----------|-------------------------|------------|----------|
| ValidatedRequest | False | CLI args + runtime_payload.json (unvalidated spine contract) | True |
| L1PlanContract | False | none | True |
| RouteContract | False | none | True |
| FinalEvidenceContract | False | final_evidence_contract_snapshot.json (FEC-shaped snapshot only; fec_shape_only) | True |
| PromptEnvelope | False | compiled_prompt_artifact.json (section-local, not spine PromptEnvelope) | True |
| CompiledPromptArtifact | False | compiled_prompt_artifact.json (section CPA shape) | True |
| L2ExecutionPacket | False | l2_output.json + provider_* (section-local) | True |
| SealedL2Artifact | False | none | True |
| ExitDispositionReceipt | False | x3_disposition.json (section X3 aggregate, not spine Exit receipt) | True |
| RuntimeExhaustBundle | False | runtime_exhaust_bundle.json (lane-local refs bundle) | True |

## Misnamed C0 artifacts

- **apps_rg/runtime/c03_graphrag_bound.py**: `C0.3 GraphRAG binding` → `section_graph_binding_shim (C0.3-compatible receipt only)` (changed_now=metadata_fields_added) — Static ledger neighbor expansion is not agentic_core graph traverse
- **final_evidence_contract_snapshot.json**: `final_evidence_contract_snapshot` → `section_graph_binding_fec_snapshot.json` (changed_now=False) — Filename kept for compat; doc now marks fec_shape_only
- **apps_rg/runtime/dispatch/input_authority_prompt_block.py**: `C0.3 GraphRAG-bound` → `section graph binding (C0.3-shim)` (changed_now=True) — Prompt INPUT_AUTHORITY must not imply full C0.3
- **apps_rg/runtime/validators/validate_exec_summary_graph_only_generation.py**: `C0.3 GraphRAG live proof` → `section graph binding live proof` (changed_now=docstring) — Validator checks lane graph pool, not spine C0
- **runtime_exhaust_bundle.json**: `runtime_exhaust_bundle` → `section_runtime_exhaust_bundle (spine alias documented in proof bundle)` (changed_now=spine_classification metadata in proof bundle builder) — Same basename as spine contract but lane-local schema

## Explicit non-claims

- no claim of full canonical C0.2 dense retrieval unless Chroma/BGE dense path ran
- no claim of full canonical C0.3 graph traverse unless RouteContract + ACL-bound traverse ran
- no claim of canonical C0.5 FinalEvidenceContract unless spine FEC was emitted and consumed by spine PA
- no claim of durable write unless UWG commit path executed
- section runtime_exhaust_bundle.json is lane-local exhaust refs, not spine RuntimeExhaustBundle

## Open gaps

- Broad tests/_apps_contract suite needs bounded follow-up triage: full run aborted ~22 minutes at ~48% with no final summary and many F markers (non-dispositive)
- Route section lanes through U0 package validation → ValidatedRequest before proof pool
- Emit spine RouteContract + call agentic_core c0_retrieve_apps_rg for grounded lanes
- Replace section_graph_binding_shim with C0 output or wrap shim as explicit C0.3 sub-step under route
- Consume spine FinalEvidenceContract in section PA (or merge section PA into spine PA)
- Emit spine ExitDispositionReceipt + SealedL2Artifact; map section X3 to Exit only as read-only mirror
- Optional UWG/L4 only when product requests durable write
