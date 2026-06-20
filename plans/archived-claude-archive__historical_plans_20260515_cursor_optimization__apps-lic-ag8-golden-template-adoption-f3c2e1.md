---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-lic-ag8-golden-template-adoption-f3c2e1.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-lic-ag8-golden-template-adoption-f3c2e1.md'
source_sha256: 9ab859a60e7d2aca9b11b56abea3cd492d26ec93b04e313faf866cc31f05ae24
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-lic-ag8-golden-template-adoption-f3c2e1
plan_type: refactor
---

# AG-8 apps_lic Golden Template Adoption

Preservation-first plan that wires apps_lic onto the shared agentic_core spine using apps_rg as the Level 5 golden reference, with all current apps_lic functionality inventoried, mapped, and proven by tests with no silent drops.

---

## Context (SCQA)

- **Situation** — apps_rg has an accepted AG-6/AG-7 golden-path runtime chain on the agentic_core spine (U0→L1→L0→C0→PA→L3 if required→L2→Exit→X1/X3). The extracted template lives at `artifacts/apps_rg_template/`. apps_lic is a grounded license/contract analysis app with its own payload shape, prompts, policy/rubric refs, and business logic.
- **Complication** — apps_lic must ride the same spine but cannot be wired blindly from the apps_rg template. Its current functionality (license text analysis, contract review, policy comparison, jurisdiction handling, risk-tier routing, citation requirements) must be fully inventoried and preserved; silent drops are not acceptable. Reachability alone is not restoration.
- **Question** — How do we wire apps_lic onto the agentic_core spine such that every current apps_lic capability is preserved, mapped into a custom U0 payload, consumed by downstream stages, and proven by tests?
- **Answer** — A preservation-first 10-wave plan: discover existing apps_lic behavior (W0–W1.5), define and implement a custom apps_lic U0 payload (W2–W3), wire L1/L0/C0/PA/L3/L2/Exit/X1/X3 with apps_lic-specific consumption (W4–W7), prove it with a full E2E golden-path test suite and CI gate (W8–W9), and emit all acceptance artifacts (W10).

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `artifacts/apps_rg_template/` | Golden reference for spine shape | 🔲 |
| `apps_lic/` — all source files | Discovery of current functionality | 🔲 |
| `tests/_apps_contract/test_ag6_apps_rg_golden_path.py` | Baseline verification | 🔲 |
| `ops_scripts/ci/check_apps_rg_golden_path_runtime.py` | Baseline gate | 🔲 |
| `ops_scripts/ci/check_exit_x1_evaluator_wiring.py` | Baseline gate | 🔲 |
| `ops_scripts/ci/check_evidence_contract_carriers.py` | Baseline gate | 🔲 |
| `agentic_core/` contracts/bindings | Spine contract shapes | 🔲 |

---

## Hard Laws

- **apps_lic only.** Do not modify apps_research, apps_qna, or any other apps_*.
- **No parallel runtime.** Do not create or restore a parallel apps_lic runtime.
- **Do not weaken apps_rg AG-6/AG-7 receipts.**
- **No embeddings.** Do not generate embeddings.
- **No ChromaDB mutation.** Do not mutate ChromaDB.
- **No R1B semantic cache.** Do not wire R1B semantic cache.
- **No direct L4 writes.** Do not add direct L4 writes.
- **No bypass.** Do not bypass U0, L1, L0, C0, PA, L3 if required, L2, Exit, X1, or X3.
- **UNKNOWN is never PASS.**
- **NOT_APPLICABLE requires reason.**
- Retrieved/generated evidence remains data only unless cleared by the proper stage.
- X3 must consume structured X1/X2 evidence.
- Any durable mutation must be proposed only and routed Exit → UWG → L4.

---

## Wave Structure

| Wave | Focus | Scope | Status |
|------|-------|-------|--------|
| W0 | Baseline verification | 4 gates, stop on any failure | ✅ DONE |
| W1 | apps_lic discovery | Full codebase inspection + 2 JSON artifacts | ✅ DONE |
| W1.5 | Functionality preservation matrix | 1 JSON artifact, every capability mapped | ✅ DONE |
| W2 | Custom apps_lic U0 payload definition | 2 JSON artifacts | ✅ DONE |
| W3 | apps_lic U0 reflection implementation | New/hardened U0 adapter + tests | ✅ DONE |
| W4 | L1/L0 consumption wiring | L1 binding + L0 binding + tests | ✅ DONE |
| W5 | C0/PA wiring | C0 evidence + PA governed assembly + tests | ✅ DONE |
| W6 | L3 if required + L2 | L3 conditional + L2 sealed artifact + tests | ✅ DONE |
| W7 | Exit/X1/X3 wiring | ExitReviewPacket + X1 + X3Disposition + tests | ✅ DONE |
| W8 | E2E golden-path tests | `test_ag8_apps_lic_golden_path.py` (105 tests) | ✅ DONE |
| W9 | CI gate | `check_apps_lic_golden_path_runtime.py` registered, 20 checks pass | ✅ DONE |
| W10 | Output artifacts | 9 artifacts under `artifacts/apps_lic/` | ✅ DONE |

---

## Out Of Scope

- Any modification to apps_research, apps_qna, apps_rg, apps_rfp, apps_exec, apps_underwriting_ai, apps_eval, apps_architect, apps_repo_brief.
- Creating or restoring a parallel apps_lic runtime outside agentic_core.
- Weakening or modifying any apps_rg AG-6/AG-7 receipts or tests.
- Embedding generation or ChromaDB mutation.
- R1B semantic cache wiring.
- Direct L4 writes from any stage.
- Full L3 DAG (conditional participation only if `workflow_required`).
- Real LLM-judge Spearman calibration (stubs acceptable for AG-8).
- Production-log mining or holdout corpus.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0 | Baseline verification | 4 CI gates | Must pass before any edits | ~2K | ✅ DONE |
| W1 | apps_lic discovery | All `apps_lic/` source | Identifying all touchpoints | ~8K | ✅ DONE |
| W1.5 | Preservation matrix | `artifacts/apps_lic/` | Mapping every capability | ~6K | ✅ DONE |
| W2 | U0 payload definition | `artifacts/apps_lic/` | License/contract field enumeration | ~5K | ✅ DONE |
| W3 | U0 reflection impl | `apps_lic/` U0 adapter | Deterministic digests, zero drops | ~8K | ✅ DONE |
| W4 | L1/L0 wiring | `agentic_core/L1_cognition/`, `agentic_core/L0_routing/` | app_payload consumption, no legacy reads | ~8K | ✅ DONE |
| W5 | C0/PA wiring | `agentic_core/` C0 + PA | Evidence governance, data-only slots | ~8K | ✅ DONE |
| W6 | L3+L2 wiring | `agentic_core/L3_orchestration/`, `agentic_core/L2_execution/` | Conditional L3, sealed artifact | ~8K | ✅ DONE |
| W7 | Exit/X1/X3 | `agentic_core/` exit + eval | X1 checkout, X3 disposition | ~8K | ✅ DONE |
| W8 | E2E tests | `tests/_apps_contract/` | 105 tests, zero regressions | ~10K | ✅ DONE |
| W9 | CI gate | `ops_scripts/ci/` | 20 checks, registered in run_contract_gates.py | ~6K | ✅ DONE |
| W10 | Output artifacts | `artifacts/apps_lic/` | 9 artifacts, all complete | ~4K | ✅ DONE |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Execution Plan

### W0 — Baseline Verification

**Scope**: Run all 4 baseline gates before any code changes. Stop and report on any failure.

**Commands**:
```bash
python -m pytest tests/_apps_contract/test_ag6_apps_rg_golden_path.py -v
python ops_scripts/ci/check_apps_rg_golden_path_runtime.py --fail-closed
python ops_scripts/ci/check_exit_x1_evaluator_wiring.py --fail-closed
python ops_scripts/ci/check_evidence_contract_carriers.py
```

**Acceptance**: All 4 exit 0. Any failure → stop, report, do not proceed.

---

### W1 — apps_lic Discovery

**Scope**: Read-only inspection of entire apps_lic codebase. No edits.

Identify:
- Entrypoints / CLI / dispatch path
- Current payload shape
- Current modes / commands / flags
- Current prompts/templates
- Current policy/rubric refs
- Current tools/actions/business logic
- Current generated outputs
- Current side effects
- Current L4/state interactions
- Current tests/smoke flows
- Current L1/L0/C0/PA/L3/L2/Exit touchpoints
- Direct `envelope.payload` reads after U0
- Direct L4 writes
- App-local runtime bypasses
- ChromaDB or embedding calls
- Managed workflow usage

**Produce**:
- `artifacts/apps_lic/ag8_apps_lic_discovery.json`
- `artifacts/apps_lic/ag8_no_bypass_map.json`

**Acceptance**: Both JSON artifacts written, zero edit to any source file.

---

### W1.5 — Functionality Preservation Matrix

**Scope**: Before any runtime wiring, build the capability preservation matrix.

Every current apps_lic capability must have a row with fields:
- `capability_id`
- `current_behavior`
- `current_entrypoint`
- `current_inputs`
- `current_outputs`
- `current_side_effects`
- `current_prompts_or_templates`
- `current_tools_or_engines`
- `current_policy_or_rubric_refs`
- `current_tests`
- `target_u0_payload_fields`
- `target_app_payload_fields`
- `target_l1_fields`
- `target_l0_route_fields`
- `target_c0_evidence_fields`
- `target_pa_prompt_slots`
- `target_l3_fields_if_workflow`
- `target_l2_execution_fields`
- `target_exit_x1_fields`
- `preservation_test`
- `status`: `PRESERVED` | `PARTIAL` | `MISSING` | `DEFERRED_WITH_REASON`
- `evidence_paths`

**Rules**:
- No `MISSING` capabilities allowed at acceptance.
- `PARTIAL` requires explicit follow-up plan.
- `DEFERRED_WITH_REASON` requires reason, owner, and future AG.
- No capability may silently disappear because apps_lic now rides agentic_core.

**Produce**: `artifacts/apps_lic/ag8_apps_lic_functionality_preservation_matrix.json`

**Acceptance**: All capabilities have status ≠ MISSING, artifact written.

---

### W2 — Custom apps_lic U0 Payload Definition

**Scope**: Define the apps_lic-specific ingress payload shape.

Minimum fields to inspect and map:
- `app_id` = `apps_lic`
- `request_type`
- `analysis_objective`
- `license_text` or `license_ref`
- `contract_text` or `contract_ref`
- `policy_text` or `policy_ref`
- `source_document_type`
- `target_question`
- `jurisdiction` / `governing_context` if applicable
- `party_context` if applicable
- `risk_tier`
- `required_output_format`
- `evidence_requirement`
- `citation_requirement`
- `grounding_required`
- `action_required`
- `workflow_required`
- `side_effect_class`
- `HITL` posture
- `UWG` / durable-write posture
- `policy_refs`
- `rubric_refs`
- `replay_refs`
- `audit_refs`

Map into: `ValidatedRequest.app_payload`

**U0 Rules**:
- U0 may normalize and label.
- U0 must not perform apps_lic business logic.
- U0 must not route.
- U0 must not retrieve.
- U0 must not execute.
- U0 must not write L4.
- `silently_dropped` must be zero.
- `unknown_mappings` must be zero unless rejected/blocked.

**Produce**:
- `artifacts/apps_lic/ag8_apps_lic_payload_schema.json`
- `artifacts/apps_lic/ag8_apps_lic_payload_mapping_matrix.json`

**Acceptance**: Both artifacts written, all fields mapped, zero `unknown_mappings`.

---

### W3 — apps_lic U0 Reflection Implementation

**Scope**: Create or harden apps_lic U0 adapter.

**Required**:
- Accepts custom apps_lic ingress payload
- Emits `ValidatedRequest`
- Populates `ValidatedRequest.app_payload`
- Emits apps_lic reflection receipt
- Zero `silently_dropped`
- Zero `unknown_mappings`
- Deterministic `input_payload_digest`
- Deterministic `validated_request_digest`
- Preserves legacy ingress only as labeled data
- No business logic in U0

**Tests**:
- Valid fixture accepted
- Malformed payload rejected
- Reflection receipt exists
- `app_payload` exists before L1
- Same input produces same digests
- Unknown mappings fail or are explicitly blocked

**Acceptance**: All U0 tests pass, reflection receipt in artifact.

---

### W4 — L1/L0 Consumption Wiring

**Scope**: Wire L1 and L0 to consume apps_lic-specific contracts.

**L1**:
- Consumes `ValidatedRequest.app_payload` only
- No legacy `envelope.payload` reads
- Emits `L1PlanContract`
- Populates `task_spec`, `query_spec`, `support_expectation`, `output_expectation`, policy refs, route hints
- Route hints advisory only

**L0**:
- Consumes `L1PlanContract`
- Emits exactly one deterministic `RouteContract`
- Derives `route_family`, `execution_form`, `grounding_required`, `action_required`, `side_effect_class`, `cache_eligibility`, HITL posture
- If `workflow_required`, `execution_form` must be `MANAGED_WORKFLOW`
- Does not retrieve, execute, assemble prompts, or write L4

**Tests**:
- L1 consumes `app_payload`
- L0 route changes when action/grounding/workflow requirements change
- Same input produces same `RouteContract`
- L0 does not retrieve, execute, assemble prompts, or write L4

**Acceptance**: L1/L0 tests pass, no legacy payload reads.

---

### W5 — C0/PA Wiring

**Scope**: Wire C0 and PA for apps_lic evidence governance.

**C0**:
- Consumes `RouteContract` and `ValidatedRequest.app_payload` where needed
- Emits `FinalEvidenceContract` when grounding is required
- Populates `EvidenceItem` fields using best available apps_lic evidence
- Includes `support_status`, `citation_map`, `source_lineage_map`, `evidence_strata`, `contradiction_report` where available
- Unavailable dense/vector fields become `NOT_APPLICABLE` with reason
- No answering, no prompt assembly, no execution

**PA**:
- Consumes governed contracts only
- Emits `CompiledPromptArtifact`
- Preserves apps_lic evidence as data only
- Preserves `slot_lineage_map`, `component_hash_map`, `prompt_hash`, replay manifest
- No direct legacy payload reads

**Tests**:
- C0 emits `FinalEvidenceContract`
- `EvidenceItem.allowed_prompt_slot` = `C0_EVIDENCE_DATA_ONLY`
- PA `slot_lineage_map` includes apps_lic evidence lineage
- PA does not promote lower-authority content into instructions

**Acceptance**: C0/PA tests pass, evidence governance enforced.

---

### W6 — L3 if Required + L2

**Scope**: Wire L3 conditionally and L2 for bounded execution.

**L3** (if `workflow_required`):
- L0 routes to L3
- L3 emits `L3ToL2StepContract`
- Preserves `workflow_id`, `node_id`, dependency refs, checkpoint refs, capability token, sandbox envelope, allowed execution lane
- L3 may sequence and merge sealed step artifacts
- L3 must not reroute, retrieve, execute, or write L4

**L2**:
- Consumes `RouteContract` / `L3ToL2StepContract` / `PromptEnvelope` as applicable
- Executes one bounded packet
- Emits `SealedL2Artifact`
- Preserves `evidence_refs`, `prompt_refs`, `tool_call_refs`, `model_call_refs`, `provider_receipts`, `otel_span_refs`, `replay_manifest`, `audit_manifest_ref`
- May emit `proposed_state_diff` only
- No durable commit

**Tests**:
- L3 participates when `MANAGED_WORKFLOW`
- L2 receives bounded packet
- L2 preserves refs
- L2 does not write L4

**Acceptance**: L3/L2 tests pass, sealed artifact refs intact.

---

### W7 — Exit/X1/X3 Wiring

**Scope**: Wire Exit, X1 checkout, and X3 disposition for apps_lic.

**Exit must**:
- Build `ExitReviewPacket`
- Produce `X1CheckoutResult`
- Aggregate into X2
- Emit exactly one `X3Disposition`

**Tests**:
- X3 cannot emit without `X1CheckoutResult`
- Material FAIL blocks `ALLOW_FINISH`
- Material UNKNOWN cannot pass
- Scalar `eval_score` is not authoritative
- Missing evidence on grounded path fails or safe-abstains
- `proposed_state_diff` cannot bypass X1J/UWG eligibility

**Acceptance**: All Exit/X1/X3 tests pass, X3 never emits without X1.

---

### W8 — E2E Golden-Path Tests

**Scope**: Create `tests/_apps_contract/test_ag8_apps_lic_golden_path.py` with 19 required tests.

| # | Test |
|---|------|
| 1 | Runtime imports available |
| 2 | Custom apps_lic ingress payload valid |
| 3 | Functionality preservation matrix has no MISSING rows |
| 4 | U0 produces `ValidatedRequest` |
| 5 | U0 reflection receipt exists |
| 6 | `ValidatedRequest.app_payload` populated |
| 7 | L1 consumes `app_payload` |
| 8 | L0 produces deterministic `RouteContract` |
| 9 | L3 participates if `MANAGED_WORKFLOW` |
| 10 | C0 produces `FinalEvidenceContract` when grounding is required |
| 11 | PA consumes evidence as data only |
| 12 | L2 preserves refs |
| 13 | Exit produces X3 with `X1CheckoutResult` |
| 14 | No legacy `envelope.payload` downstream |
| 15 | No direct L4 write |
| 16 | No ChromaDB mutation |
| 17 | No embedding generation |
| 18 | UNKNOWN never PASS |
| 19 | NOT_APPLICABLE requires reason |

**Acceptance**: All 19 tests pass, zero regressions in existing suite.

---

### W9 — CI Gate

**Scope**: Create `ops_scripts/ci/check_apps_lic_golden_path_runtime.py`.

**Gate must fail if**:
- apps_lic can enter L1 without U0 reflection receipt
- Custom apps_lic payload is not mapped into `ValidatedRequest.app_payload`
- Functionality preservation matrix has MISSING rows
- L1 ignores `app_payload`
- L0 ignores `app_payload`-derived projections
- L3 is bypassed when `workflow_required`
- C0 emits thin/default-only evidence when grounding is required
- PA reads legacy payload
- PA promotes evidence into instruction authority
- L2 drops refs
- L2 writes L4 directly
- Exit emits X3 without `X1CheckoutResult`
- Scalar `eval_score` is authoritative
- UNKNOWN is treated as PASS
- ChromaDB is mutated
- Embeddings are generated

**Acceptance**: Gate registered in `run_contract_gates.py`, exits 0 on green path.

---

### W10 — Output Artifacts

**Scope**: Produce all acceptance artifacts under `artifacts/apps_lic/`.

| Artifact | Description |
|---|---|
| `ag8_apps_lic_golden_path_report.md` | Human-readable summary of AG-8 acceptance |
| `ag8_contract_chain_receipt.json` | Per-stage contract chain proof |
| `ag8_evidence_population_matrix.json` | Evidence fields populated vs NOT_APPLICABLE |
| `ag8_no_bypass_map.json` | Proof of no stage bypasses |
| `ag8_acceptance_evidence.json` | Final acceptance evidence bundle |
| `ag8_template_delta_from_apps_rg.json` | Delta from apps_rg template |
| `ag8_apps_lic_payload_schema.json` | Custom U0 payload schema |
| `ag8_apps_lic_payload_mapping_matrix.json` | Field mapping matrix |
| `ag8_apps_lic_functionality_preservation_matrix.json` | Capability preservation rows |

**Acceptance**: All 9 artifacts present, `ag8_acceptance_evidence.json` shows AG-8 invariant MET.

---

## Final Response Must Include

- Files changed
- Tests added
- Commands run
- Custom apps_lic payload fields
- Functionality preservation summary
- Whether apps_lic uses `SINGLE_STEP` or `MANAGED_WORKFLOW`
- Contract chain proof
- Evidence fields populated count
- Remaining `NOT_APPLICABLE` fields and reasons
- Whether X3 consumed `X1CheckoutResult`
- Whether any ChromaDB mutation occurred
- Whether any embeddings were generated
- **Explicit statement whether AG-8 invariant is MET**

---

## Definition of Done

| # | Criterion | Verification command / evidence | Status |
|---|---|---|---|
| DoD-1 | apps_lic rides the full agentic_core spine (U0→L1→L0→C0→PA→L3?→L2→Exit→X1/X3) with all current functionality preserved or explicitly deferred | `artifacts/apps_lic/ag8_acceptance_evidence.json` shows `ag8_invariant_met: true` | ✅ |
| DoD-2 | Functionality preservation matrix has zero MISSING rows | `cat artifacts/apps_lic/ag8_apps_lic_functionality_preservation_matrix.json \| python -c "import json,sys; rows=json.load(sys.stdin); assert not any(r['status']=='MISSING' for r in rows)"` | ✅ |
| DoD-3 | 105 E2E golden-path tests pass, zero regressions | `pytest tests/_apps_contract/test_ag8_apps_lic_golden_path.py -v` shows 105 pass, 0 fail | ✅ |
| DoD-4 | CI gate green | `python ops_scripts/ci/check_apps_lic_golden_path_runtime.py` exits 0 on green path | ✅ |
| DoD-5 | All 9 output artifacts present, memory writeback done | All files exist under `artifacts/apps_lic/`, memory entity updated | ✅ |

**Verification-vs-Deferral table**:

| Item | Why deferred | Tracked in |
|---|---|---|
| Real LLM inference over license text | Out of AG-8 scope; stubs acceptable for spine proof | Future plan |
| Holdout corpus / Spearman calibration | Requires labeled data; not a spine concern | Future plan |
| Full L3 DAG | Only conditional L3 participation required for AG-8 | Future plan |
| R1B semantic cache wiring | Hard-law excluded from AG-8 | Future plan |

---

## Rollback Strategy

1. W0 gates protect against regressions — do not proceed if any fail.
2. apps_lic bindings are isolated in `agentic_core/<layer>/apps_lic_*_binding.py` — removal does not touch shared code.
3. If any stage breaks existing apps_rg tests, revert the offending binding file.
4. `git stash` is safe at any wave boundary (no migrations, no schema changes, no L4 writes).

---

## Acceptance Invariant

AG-8 is complete only when apps_lic has **one proven golden-path runtime chain** using the apps_rg template, with:
- Current apps_lic functionality preserved or explicitly deferred
- A custom apps_lic payload into U0
- U0 reflection receipt
- `app_payload` consumption at L1/L0/C0/PA
- Deterministic route from L0
- C0/PA governed evidence handling
- L3 included if `workflow_required`
- L2 sealed artifact with ref preservation
- Exit/X1/X3 structured evaluation
- No legacy `envelope.payload` bypass
- No direct L4 write
- No ChromaDB mutation
- No embedding generation
