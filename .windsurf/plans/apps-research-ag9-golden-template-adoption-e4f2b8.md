---
plan_id: apps-research-ag9-golden-template-adoption-e4f2b8
plan_type: refactor
---

# AG-9 apps_research Golden Template Adoption with Prompt Authority Hardening

Preservation-first plan that wires apps_research onto the shared agentic_core spine using apps_rg as the sole accepted golden baseline (AG-6/AG-7). apps_lic is regression-only and must not be used as an implementation template for apps_research. Full prompt authority inventory, classification, and hardening included. All current apps_research functionality is inventoried, mapped, and proven by tests with zero silent drops.

---

## Context (SCQA)

- **Situation** — apps_rg (AG-6/AG-7) has an accepted golden-path runtime chain on the agentic_core spine (U0→L1→L0→C0→PA→L3 if required→L2→Exit→X1/X3) and is the sole golden baseline for AG-9. apps_research is a grounded company-brief generation app with its own prompt assembly layer (`research_pa_compiler.py`), hop orchestration pipeline, Tavily-based web retrieval, ChromaDB-backed C0 retrieval, and a rich internal engine stack. A partial `ResearchIngressPayload` contract already exists in `agentic_core/runtime/contracts/research_ingress_payload.py` but is not yet wired to the runtime.
- **Complication** — apps_research must ride the same spine but cannot be wired blindly from the apps_rg template. Its current functionality (company brief generation, hop orchestration, Tavily retrieval, depth profiling, FEC v1.1, L4 durable write path, OTEL tracing, multi-section output) must be fully inventoried and preserved. The existing prompt assembly layer (`research_pa_compiler.py`, `prompt_registry.yaml`, `prompt_bom.yaml`, template files) introduces a secondary prompt authority surface that must be classified, mapped, and hardened so PA is the sole assembly authority. Silent drops are not acceptable. Reachability alone is not restoration.
- **Question** — How do we wire apps_research onto the agentic_core spine such that every current capability is preserved, all prompt surfaces are classified and hardened, a custom U0 payload is wired, downstream stages consume only allowed fields, and the whole chain is proven by tests and CI gates?
- **Answer** — A preservation-first multi-wave plan following the apps_rg golden baseline: discover (W0–W1.8), define custom U0 payload (W2), implement U0 reflection (W3), wire L1/L0/C0/PA/L3/L2/Exit/X1/X3 with apps_research-specific consumption (W4–W7), close prompt authority hardening (W5.5), prove with E2E golden-path tests and CI gate (W8–W9), and emit all acceptance artifacts (W10–W11).

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `artifacts/apps_rg_template/` | **Sole golden baseline** — spine shape, binding patterns | 🔲 |
| `artifacts/apps_rg/ag8_prompt_authority_inventory.json` | Golden baseline — prompt authority inventory shape | 🔲 |
| `artifacts/apps_rg/ag8_prompt_authority_classification.json` | Golden baseline — prompt classification schema | 🔲 |
| `artifacts/apps_rg/ag8_prompt_stage_consumption_matrix.json` | Golden baseline — stage consumption matrix shape | 🔲 |
| `artifacts/apps_rg/ag8_prompt_no_bypass_map.json` | Golden baseline — no-bypass proof shape | 🔲 |
| `artifacts/apps_rg/ag8_prompt_contract_mapping.json` | Golden baseline — prompt contract mapping shape | 🔲 |
| `artifacts/apps_rg/ag8_prompt_authority_report.md` | Golden baseline — PA report format | 🔲 |
| `artifacts/apps_rg/ag8_prompt_acceptance_evidence.json` | Golden baseline — acceptance evidence shape | 🔲 |
| `apps_research/` — all source files | Discovery of current functionality | 🔲 |
| `apps_research/prompt_assembly/` | Prompt authority inventory | 🔲 |
| `agentic_core/runtime/contracts/research_ingress_payload.py` | Existing partial payload contract | 🔲 |
| `tests/_apps_contract/test_ag6_apps_rg_golden_path.py` | Baseline gate (golden baseline regression) | 🔲 |
| `tests/_apps_contract/test_ag8_apps_lic_golden_path.py` | Baseline gate (regression compatibility check only — not AG-9 design authority) | 🔲 |
| `ops_scripts/ci/check_apps_rg_golden_path_runtime.py` | Baseline gate | 🔲 |
| `ops_scripts/ci/check_apps_lic_golden_path_runtime.py` | Baseline gate (regression guard only — not AG-9 design authority) | 🔲 |
| `ops_scripts/ci/check_exit_x1_evaluator_wiring.py` | Baseline gate | 🔲 |
| `ops_scripts/ci/check_evidence_contract_carriers.py` | Baseline gate | 🔲 |

---

## Hard Laws

- **apps_research only.** Do not modify apps_rg, apps_lic, apps_qna, or any other apps_* except for shared import compatibility.
- **No parallel runtime.** Do not create or restore a parallel apps_research runtime outside agentic_core.
- **Do not weaken apps_rg AG-6/AG-7 receipts.** Do not weaken apps_lic AG-8 receipts (regression guard).
- **apps_rg is the sole golden baseline.** Do not use apps_lic as a template source, target delta baseline, or implementation model for apps_research.
- **No embeddings.** Do not generate embeddings or mutate ChromaDB.
- **No R1B semantic cache.** Do not wire R1B semantic cache.
- **No direct L4 writes.** Do not add direct L4 writes outside the existing UWG-gated L4 path.
- **No bypass.** Do not bypass U0, L1, L0, C0, PA, L3 if required, L2, Exit, X1, or X3.
- **UNKNOWN is never PASS.** All unknown prompt surfaces must be resolved before acceptance.
- **NOT_APPLICABLE requires reason.** Every NOT_APPLICABLE field in the preservation matrix requires a documented reason.
- **PA is sole prompt assembly authority.** No stage below PA may assemble or mutate prompt content without PA receipt.
- **Legacy prompt authority surfaces must be classified.** `research_pa_compiler.py`, `prompt_registry.yaml`, `prompt_bom.yaml`, and all template files must be classified as TASK_DATA, EVIDENCE_DATA, or PA_OWNED before acceptance.
- **Separation of task data (U0) and evidence data (C0) in PA.** PA must not conflate them.
- **Retrieved/generated evidence is data only** unless cleared by the proper stage.
- **X3 must consume structured X1/X2 evidence.**
- **Any durable mutation must be routed Exit → UWG → L4** (preserve existing UWG-gated path).

---

## Wave Structure

| Wave | Focus | Scope | Status |
|------|-------|-------|--------|
| W0 | Baseline verification | 6 gates, stop on any failure | 🔲 |
| W1 | apps_research discovery | Full codebase inspection + 2 JSON artifacts | 🔲 |
| W1.5 | Functionality preservation matrix | 1 JSON artifact, every capability mapped | 🔲 |
| W1.8 | Prompt authority inventory | 1 JSON artifact, every prompt surface classified | 🔲 |
| W2 | Custom apps_research U0 payload definition | 2 JSON artifacts | 🔲 |
| W3 | apps_research U0 reflection implementation | New/hardened U0 adapter + tests | 🔲 |
| W4 | L1/L0 consumption wiring | L1 binding + L0 binding + tests | 🔲 |
| W5 | C0/PA wiring | C0 evidence + PA governed assembly + tests | 🔲 |
| W5.5 | Prompt authority hardening closure | Resolve all PA risks, enforce separation | 🔲 |
| W6 | L3 if required + L2 | L3 conditional + L2 sealed artifact + tests | 🔲 |
| W7 | Exit/X1/X3 wiring | ExitReviewPacket + X1 + X3Disposition + tests | 🔲 |
| W8 | E2E golden-path tests | `test_ag9_apps_research_golden_path.py` | 🔲 |
| W9 | CI gate | `check_apps_research_golden_path_runtime.py` registered | 🔲 |
| W10 | Prompt authority CI gate | `check_apps_research_prompt_authority.py` registered | 🔲 |
| W11 | Output artifacts | All artifacts under `artifacts/apps_research/` | 🔲 |

---

## Out Of Scope

- Any modification to apps_rg, apps_lic, apps_qna, apps_rfp, apps_exec, apps_underwriting_ai, apps_eval, apps_architect, apps_repo_brief.
- Creating or restoring a parallel apps_research runtime outside agentic_core.
- Weakening or modifying any apps_rg AG-6/AG-7 receipts or tests.
- Weakening or modifying apps_lic AG-8 receipts or tests (they are regression guards, not AG-9 design authority).
- Using apps_lic as a template source, delta baseline, or implementation model for any AG-9 wave.
- Embedding generation or ChromaDB collection rebuilds.
- R1B semantic cache wiring.
- Full L3 DAG (conditional participation only).
- Real LLM-judge Spearman calibration (stubs acceptable for AG-9).
- Production-log mining or holdout corpus.
- Rewriting the hop orchestration pipeline (wire existing `ResearchHopOrchestrator` as inner pipeline, do not replace).

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0 | Baseline verification | 6 CI gates | Must pass before any edits | ~2K | 🔲 |
| W1 | apps_research discovery | All `apps_research/` source | Identifying all touchpoints | ~10K | 🔲 |
| W1.5 | Preservation matrix | `artifacts/apps_research/` | Mapping every capability | ~6K | 🔲 |
| W1.8 | Prompt authority inventory | `apps_research/prompt_assembly/` + all prompt surfaces | Classifying every prompt surface | ~6K | 🔲 |
| W2 | U0 payload definition | `agentic_core/runtime/contracts/` | Extend existing ResearchIngressPayload | ~5K | 🔲 |
| W3 | U0 reflection impl | `agentic_core/runtime/entry/` | Deterministic digests, zero drops | ~8K | 🔲 |
| W4 | L1/L0 wiring | `agentic_core/L1_cognition/`, `agentic_core/L0_routing/` | app_payload consumption, no legacy reads | ~8K | 🔲 |
| W5 | C0/PA wiring | `agentic_core/runtime/c0/`, `agentic_core/prompt_governance/` | Evidence governance, data-only slots | ~8K | 🔲 |
| W5.5 | PA hardening closure | `agentic_core/prompt_governance/` | Resolve all prompt authority risks | ~6K | 🔲 |
| W6 | L3+L2 wiring | `agentic_core/L3_orchestration/`, `agentic_core/L2_execution/` | Conditional L3, sealed artifact | ~8K | 🔲 |
| W7 | Exit/X1/X3 | `agentic_core/runtime/exit/` + eval | X1 checkout, X3 disposition | ~8K | 🔲 |
| W8 | E2E tests | `tests/_apps_contract/` | ~100+ tests, zero regressions | ~10K | 🔲 |
| W9 | Runtime CI gate | `ops_scripts/ci/` | checks, registered in run_contract_gates.py | ~6K | 🔲 |
| W10 | PA CI gate | `ops_scripts/ci/` | prompt authority checks | ~5K | 🔲 |
| W11 | Output artifacts | `artifacts/apps_research/` | all acceptance artifacts | ~4K | 🔲 |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Execution Plan

### W0 — Baseline Verification

**Scope**: Run all baseline gates before any code changes. Stop and report on any failure.

**Commands**:
```bash
# Golden baseline gates (apps_rg)
python -m pytest tests/_apps_contract/test_ag6_apps_rg_golden_path.py -v
python ops_scripts/ci/check_apps_rg_golden_path_runtime.py --fail-closed
python ops_scripts/ci/check_exit_x1_evaluator_wiring.py --fail-closed
python ops_scripts/ci/check_evidence_contract_carriers.py
# Regression compatibility guards (apps_lic — not AG-9 design authority)
python -m pytest tests/_apps_contract/test_ag8_apps_lic_golden_path.py -v
python ops_scripts/ci/check_apps_lic_golden_path_runtime.py --fail-closed
```

**Acceptance**: All 6 exit 0. Any failure → stop, report, do not proceed. apps_lic failures that are caused by unrelated repo drift must be reported separately and do not gate AG-9 design decisions.

---

### W1 — apps_research Discovery

**Scope**: Read-only inspection of entire apps_research codebase. No edits.

Identify:
- Entrypoints / CLI / dispatch path (`__main__.py`, `integrations/governed_research_run.py`)
- Current payload shape (`ResearchRequest`, `ResearchIngressPayload`)
- Current modes / commands / flags / depth profiles
- Current prompt surfaces (all files in `prompt_assembly/`, `templates/`, `prompt_registry.yaml`, `prompt_bom.yaml`)
- Current policy/rubric refs
- Current tools/actions/business logic (hop orchestration, Tavily, ChromaDB, company brief engine)
- Current generated outputs and artifact structure
- Current side effects (L4 durable write via UWG, OTEL telemetry)
- Current L1/L0/C0/PA/L3/L2/Exit touchpoints
- Direct `envelope.payload` reads after U0
- Direct L4 writes vs UWG-gated writes
- App-local runtime bypasses
- ChromaDB query calls (read vs mutation)
- FEC v1.1 context path (`research_depth_profile`, `fec_run_context`)
- Inner hop pipeline stages (`ResearchHopOrchestrator`)
- Existing spine alignment artifacts from `SPINE_ALIGNMENT_REPORT.md`

**Produce**:
- `artifacts/apps_research/ag9_apps_research_discovery.json`
- `artifacts/apps_research/ag9_no_bypass_map.json`

**Acceptance**: Both JSON artifacts written, zero edits to any source file.

---

### W1.5 — Functionality Preservation Matrix

**Scope**: Before any runtime wiring, build the capability preservation matrix.

Every current apps_research capability must have a row with fields:
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

**Produce**: `artifacts/apps_research/ag9_apps_research_functionality_preservation_matrix.json`

**Acceptance**: All capabilities have status ≠ MISSING, artifact written.

---

### W1.8 — Prompt Authority Inventory

**Scope**: Full inventory and classification of all prompt surfaces in apps_research.

Surfaces to classify:
- All files in `apps_research/prompt_assembly/` — `research_pa_compiler.py`, `prompt_registry.yaml`, `prompt_bom.yaml`
- All template files in `apps_research/prompt_assembly/templates/`
- Any prompt assembly logic in `apps_research/engines/`, `apps_research/reasoning/`, `apps_research/services/`
- Any prompt injection in `apps_research/integrations/`
- `apps_research/config/` prompt-adjacent configs

For every prompt surface, classify as:
- `PA_OWNED` — assembled and governed exclusively by PA stage; no other stage may modify
- `TASK_DATA` — task description provided at U0; flows through as data; PA reads but does not promote to instructions
- `EVIDENCE_DATA` — retrieved/generated evidence; flows through C0 as data only; PA may reference but not promote
- `LEGACY_BRIDGE` — historical bridged surface; must be labeled as data, not authority
- `UNKNOWN` — unresolved; UNKNOWN is never PASS

For every classified surface, produce a row:
- `surface_id`
- `file_path`
- `surface_type` (assembly_call / template_load / yaml_config / registry_lookup)
- `classification` (PA_OWNED / TASK_DATA / EVIDENCE_DATA / LEGACY_BRIDGE / UNKNOWN)
- `authority_rule` (how this surface is consumed under the hardened PA)
- `consumption_stage` (which spine stage owns it)
- `risk_if_misclassified`
- `resolution` (how risk is resolved)

**Rules**:
- No `UNKNOWN` classification at acceptance.
- `research_pa_compiler.py` must be classified in its entirety — every public method mapped.
- PA must be identified as the sole stage that assembles prompts.
- C0 must not assemble prompts.
- L1 and L0 must not assemble prompts.

**Produce**: `artifacts/apps_research/ag9_prompt_authority_inventory.json`

**Acceptance**: Artifact written, zero `UNKNOWN` rows, every surface classified.

---

### W2 — Custom apps_research U0 Payload Definition

**Scope**: Extend and harden the existing `ResearchIngressPayload` contract for full U0 wiring.

Fields to define/extend in `agentic_core/runtime/contracts/research_ingress_payload.py`:
- `app_id` = `apps_research`
- `request_type` (company_brief / process_research / analysis / custom)
- `research_topic` (primary topic for the research request)
- `target_company` (company name — maps to current `ResearchTarget.company_name`)
- `target_role` (role title — maps to current `ResearchTarget.role_title`)
- `depth_profile` (quick / standard / deep — maps to current `ResearchDepth`)
- `evidence_sources` (tavily / manual_brief / company_website / linkedin / glassdoor)
- `manual_brief_text` (optional user-provided brief)
- `manual_brief_digest` (sha256 of manual brief if provided)
- `required_output_sections` (advisory list of output sections)
- `grounding_required` (bool — whether C0 retrieval is required)
- `action_required` (bool — whether L4 durable write is required)
- `workflow_required` (bool — whether L3 managed workflow is required)
- `side_effect_class` (none / l4_write / otel_only)
- `HITL_posture` (none / advisory / required)
- `UWG_posture` (none / required)
- `evidence_requirement` (grounded / best_effort / stub_ok)
- `citation_requirement` (required / advisory / none)
- `output_format` (json / markdown / structured)
- `replay_refs` (optional list of prior run refs for replay)
- `audit_refs` (optional list of audit trail refs)
- `profile_pack_digest` (sha256 of profile pack YAML)
- `request_id` (unique request ID — carry forward from existing contract)
- `timestamp_utc` (ISO timestamp)
- `parent_trace_id` (optional parent trace ID for correlation)

Map into: `ValidatedRequest.app_payload`

**U0 Rules**:
- U0 may normalize and label.
- U0 must not perform apps_research business logic.
- U0 must not route.
- U0 must not retrieve.
- U0 must not assemble prompts.
- U0 must not write L4.
- `silently_dropped` must be zero.
- `unknown_mappings` must be zero unless rejected/blocked.

**Produce**:
- `artifacts/apps_research/ag9_apps_research_payload_schema.json`
- `artifacts/apps_research/ag9_apps_research_payload_mapping_matrix.json`

**Acceptance**: Both artifacts written, all fields mapped, zero `unknown_mappings`.

---

### W3 — apps_research U0 Reflection Implementation

**Scope**: Create `agentic_core/runtime/entry/u0_apps_research_binding.py`.

**Required**:
- Accepts custom apps_research ingress payload (`ResearchIngressPayload`)
- Emits `ValidatedRequest`
- Populates `ValidatedRequest.app_payload` with all research-specific fields
- Emits apps_research reflection receipt
- Zero `silently_dropped`
- Zero `unknown_mappings`
- Deterministic `input_payload_digest`
- Deterministic `validated_request_digest`
- Preserves legacy `ResearchRequest` fields only as labeled data (not authority)
- No business logic in U0
- No prompt assembly in U0

**Tests**:
- Valid fixture accepted
- Malformed payload rejected
- Reflection receipt exists
- `app_payload` exists before L1
- Same input produces same digests
- Unknown mappings fail or are explicitly blocked
- `target_company` and `research_topic` survive into `app_payload`
- `depth_profile` maps into `app_payload`

**Acceptance**: All U0 tests pass, reflection receipt in artifact.

---

### W4 — L1/L0 Consumption Wiring

**Scope**: Create `agentic_core/L1_cognition/apps_research_l1_binding.py` and `agentic_core/L0_routing/apps_research_l0_binding.py`.

**L1**:
- Consumes `ValidatedRequest.app_payload` only
- No legacy `envelope.payload` reads
- Emits `L1PlanContract`
- Populates `task_spec`, `query_spec`, `support_expectation`, `output_expectation`
- Derives sub-query decomposition hints (advisory, not binding) from `research_topic` and `depth_profile`
- Route hints advisory only
- No prompt assembly

**L0**:
- Consumes `L1PlanContract`
- Reads the apps_research route profile (create if missing)
- Emits exactly one deterministic `RouteContract`
- Derives `route_family`, `execution_form`, `grounding_required`, `action_required`, `side_effect_class`, `cache_eligibility`, HITL posture
- If `workflow_required`, `execution_form` must be `MANAGED_WORKFLOW`
- Does not retrieve, execute, assemble prompts, or write L4

**Tests**:
- L1 consumes `app_payload`
- L0 route changes when grounding/action/workflow requirements change
- Same input produces same `RouteContract`
- L0 does not retrieve, execute, assemble prompts, or write L4
- `depth_profile` = DEEP routes differently than QUICK

**Acceptance**: L1/L0 tests pass, no legacy payload reads.

---

### W5 — C0/PA Wiring

**Scope**: Create `agentic_core/runtime/c0/apps_research_c0_binding.py` and `agentic_core/prompt_governance/apps_research_pa_binding.py`.

**C0**:
- Consumes `RouteContract` and `ValidatedRequest.app_payload` where needed
- Calls existing `HybridSearchEngine.search()` (real retrieval) when `grounding_required`
- Calls `EvidenceShaper.shape()` for evidence normalization
- Emits `FinalEvidenceContract`
- Populates `EvidenceItem` fields from shaped evidence bundle
- Includes `support_status`, `citation_map`, `source_lineage_map`, `evidence_strata` where available
- Includes research-specific evidence fields: `research_topic`, `depth_profile`, `hop_checkpoints`, `snippet_count`
- Unavailable dense/vector fields → `NOT_APPLICABLE` with reason
- No answering, no prompt assembly, no execution
- Does not call Tavily directly (Tavily is called by inner hop pipeline, not C0 binding)

**PA**:
- Consumes governed contracts only (`ValidatedRequest.app_payload`, `FinalEvidenceContract`, `RouteContract`)
- Invokes `research_pa_compiler.py` only as a **classified PA_OWNED** sub-component, not independently
- Emits `CompiledPromptArtifact`
- Preserves apps_research evidence as data only (EVIDENCE_DATA slot)
- Task data from `app_payload` flows into TASK_DATA slot
- Preserves `slot_lineage_map`, `component_hash_map`, `prompt_hash`, replay manifest
- No direct legacy payload reads
- No promotion of C0 evidence into instruction authority

**Tests**:
- C0 emits `FinalEvidenceContract`
- `EvidenceItem.allowed_prompt_slot` = `C0_EVIDENCE_DATA_ONLY`
- PA `slot_lineage_map` includes apps_research evidence lineage
- PA does not promote C0 evidence into instructions
- C0 degrades gracefully when ChromaDB absent (zero real chunks → slim evidence)
- `research_pa_compiler.py` only invoked under PA governance

**Acceptance**: C0/PA tests pass, evidence governance enforced.

---

### W5.5 — Prompt Authority Hardening Closure

**Scope**: Resolve all prompt authority risks surfaced in W1.8.

**For each LEGACY_BRIDGE surface**:
- Wrap in a data-only carrier (no promotion to instructions)
- Add `authority_classification = LEGACY_BRIDGE` annotation
- Confirm PA binding only reads it as data

**For each PA_OWNED surface**:
- Confirm only PA binding invokes it
- Add import guard or assertion in PA binding: `assert_invoked_only_under_pa()`
- Confirm no L1/L0/C0 or L2 path calls it directly

**For each TASK_DATA surface**:
- Confirm it flows from U0 `app_payload` only
- Confirm it reaches PA as typed field, not free-form string injection

**For each EVIDENCE_DATA surface**:
- Confirm it flows from C0 `FinalEvidenceContract` only
- Confirm PA reads it via `allowed_prompt_slot` = `C0_EVIDENCE_DATA_ONLY`

**Produce**:
- `artifacts/apps_research/ag9_prompt_authority_hardening_report.json`

**Tests**:
- TASK_DATA slot cannot receive C0 evidence
- EVIDENCE_DATA slot cannot receive U0 task data
- PA is the only stage that calls `research_pa_compiler.py`
- No L0/L1/C0/L2 import of `research_pa_compiler`

**Acceptance**: All hardening tests pass, zero UNKNOWN surfaces remain, artifact written.

---

### W6 — L3 if Required + L2

**Scope**: Create `agentic_core/L2_execution/apps_research_l2_binding.py` and conditional L3 wiring.

**L3** (if `workflow_required`):
- L0 routes to L3 with `execution_form = MANAGED_WORKFLOW`
- L3 emits `L3ToL2StepContract`
- Preserves `workflow_id`, `node_id`, capability token, sandbox envelope, allowed execution lane
- Does not reroute, retrieve, execute, or write L4

**L2**:
- Consumes `RouteContract` / `L3ToL2StepContract` / `CompiledPromptArtifact` as applicable
- Executes one bounded packet (invokes inner hop pipeline via `ResearchHopOrchestrator`)
- Emits `SealedL2Artifact`
- Preserves `evidence_refs`, `prompt_refs`, `tool_call_refs`, `model_call_refs`, `provider_receipts`, `otel_span_refs`, `replay_manifest`, `audit_manifest_ref`
- Attaches `GovernedE2ERunRecord` fields to sealed artifact
- L4 durable write via existing UWG path only — never directly from L2
- Emits `proposed_state_diff` only (no durable commit)

**Tests**:
- L3 participates when `MANAGED_WORKFLOW`
- L2 receives bounded packet
- L2 preserves refs including hop checkpoint refs
- L2 does not write L4 directly
- Inner hop pipeline (`ResearchHopOrchestrator`) invoked under L2 governance

**Acceptance**: L3/L2 tests pass, sealed artifact refs intact.

---

### W7 — Exit/X1/X3 Wiring

**Scope**: Create `agentic_core/runtime/exit/apps_research_exit_binding.py`.

**Exit must**:
- Build `ExitReviewPacket` from `SealedL2Artifact` and `GovernedE2ERunRecord`
- Populate from `fec_run_context` (FEC v1.1 fields)
- Produce `X1CheckoutResult`
- Aggregate into X2
- Emit exactly one `X3Disposition`
- Route L4 durable write proposal through UWG gate (preserve existing `research_brief_uwg_writer` path)

**Exit tests**:
- X3 cannot emit without `X1CheckoutResult`
- Material FAIL blocks `ALLOW_FINISH`
- Material UNKNOWN cannot pass
- Scalar `eval_score` is not authoritative
- Missing evidence on grounded path fails or safe-abstains
- `proposed_state_diff` cannot bypass X1J/UWG eligibility
- FEC v1.1 fields preserved in ExitReviewPacket

**Acceptance**: All Exit/X1/X3 tests pass, X3 never emits without X1.

---

### W8 — E2E Golden-Path Tests

**Scope**: Create `tests/_apps_contract/test_ag9_apps_research_golden_path.py` with ≥21 required tests.

| # | Test |
|---|------|
| 1 | Runtime imports available |
| 2 | Custom apps_research ingress payload valid |
| 3 | Functionality preservation matrix has no MISSING rows |
| 4 | U0 produces `ValidatedRequest` |
| 5 | U0 reflection receipt exists |
| 6 | `ValidatedRequest.app_payload` populated |
| 7 | L1 consumes `app_payload` |
| 8 | L0 produces deterministic `RouteContract` |
| 9 | L3 participates if `MANAGED_WORKFLOW` |
| 10 | C0 produces `FinalEvidenceContract` when grounding is required |
| 11 | PA consumes evidence as data only |
| 12 | PA invokes `research_pa_compiler.py` only under PA governance |
| 13 | L2 preserves refs including hop checkpoint refs |
| 14 | Exit produces X3 with `X1CheckoutResult` |
| 15 | No legacy `envelope.payload` downstream |
| 16 | No direct L4 write (outside UWG path) |
| 17 | No ChromaDB mutation |
| 18 | No embedding generation |
| 19 | UNKNOWN never PASS |
| 20 | NOT_APPLICABLE requires reason |
| 21 | Prompt authority inventory has zero UNKNOWN surfaces |
| 22 | TASK_DATA and EVIDENCE_DATA slots are separate in PA |

**Acceptance**: All ≥21 tests pass, zero regressions in existing suite.

---

### W9 — Runtime CI Gate

**Scope**: Create `ops_scripts/ci/check_apps_research_golden_path_runtime.py`.

**Gate must fail if**:
- apps_research can enter L1 without U0 reflection receipt
- Custom apps_research payload is not mapped into `ValidatedRequest.app_payload`
- Functionality preservation matrix has MISSING rows
- L1 ignores `app_payload`
- L0 ignores `app_payload`-derived projections
- L3 is bypassed when `workflow_required`
- C0 emits thin/default-only evidence when grounding is required
- PA reads legacy payload directly
- PA promotes evidence into instruction authority
- `research_pa_compiler.py` is invoked outside PA
- L2 drops refs
- L2 writes L4 directly (outside UWG)
- Exit emits X3 without `X1CheckoutResult`
- Scalar `eval_score` is authoritative
- UNKNOWN is treated as PASS
- ChromaDB is mutated
- Embeddings are generated

**Acceptance**: Gate registered in `run_contract_gates.py`, exits 0 on green path.

---

### W10 — Prompt Authority CI Gate

**Scope**: Create `ops_scripts/ci/check_apps_research_prompt_authority.py`.

**Gate must fail if**:
- `apps_research/prompt_assembly/research_pa_compiler.py` is imported outside `agentic_core/prompt_governance/apps_research_pa_binding.py`
- Any L0/L1/C0/L2/Exit binding imports prompt assembly modules directly
- Prompt authority inventory has `UNKNOWN` rows
- TASK_DATA and EVIDENCE_DATA slots are conflated in PA binding
- `prompt_registry.yaml` or `prompt_bom.yaml` are read outside PA binding

**Acceptance**: Gate registered in `run_contract_gates.py`, exits 0 on green path.

---

### W11 — Output Artifacts

**Scope**: Produce all acceptance artifacts under `artifacts/apps_research/`.

| Artifact | Description |
|---|---|
| `ag9_apps_research_golden_path_report.md` | Human-readable summary of AG-9 acceptance |
| `ag9_contract_chain_receipt.json` | Per-stage contract chain proof |
| `ag9_evidence_population_matrix.json` | Evidence fields populated vs NOT_APPLICABLE |
| `ag9_no_bypass_map.json` | Proof of no stage bypasses |
| `ag9_acceptance_evidence.json` | Final acceptance evidence bundle |
| `ag9_template_delta_from_apps_rg.json` | Delta from apps_rg golden baseline template (apps_lic excluded) |
| `ag9_apps_research_payload_schema.json` | Custom U0 payload schema |
| `ag9_apps_research_payload_mapping_matrix.json` | Field mapping matrix |
| `ag9_apps_research_functionality_preservation_matrix.json` | Capability preservation rows |
| `ag9_prompt_authority_inventory.json` | Full prompt surface inventory and classification |
| `ag9_prompt_authority_hardening_report.json` | PA hardening closure evidence |

**Acceptance**: All 11 artifacts present, `ag9_acceptance_evidence.json` shows AG-9 invariant MET.

---

## Final Response Must Include

- Files changed
- Tests added
- Commands run
- Custom apps_research payload fields
- Functionality preservation summary
- Whether apps_research uses `SINGLE_STEP` or `MANAGED_WORKFLOW`
- Prompt authority classification counts (PA_OWNED / TASK_DATA / EVIDENCE_DATA / LEGACY_BRIDGE)
- Contract chain proof
- Evidence fields populated count
- Remaining `NOT_APPLICABLE` fields and reasons
- Whether X3 consumed `X1CheckoutResult` via shared `build_x3_packet`
- Whether any ChromaDB mutation occurred
- Whether any embeddings were generated
- **Explicit statement whether AG-9 invariant is MET**

---

## Definition of Done

| # | Criterion | Verification command / evidence | Status |
|---|---|---|---|
| DoD-1 | apps_research rides the full agentic_core spine (U0→L1→L0→C0→PA→L3?→L2→Exit→X1/X3) with all current functionality preserved or explicitly deferred | `artifacts/apps_research/ag9_acceptance_evidence.json` shows `ag9_invariant_met: true` | 🔲 |
| DoD-2 | Functionality preservation matrix has zero MISSING rows | `cat artifacts/apps_research/ag9_apps_research_functionality_preservation_matrix.json \| python -c "import json,sys; rows=json.load(sys.stdin); assert not any(r['status']=='MISSING' for r in rows)"` | 🔲 |
| DoD-3 | Prompt authority inventory has zero UNKNOWN surfaces | `cat artifacts/apps_research/ag9_prompt_authority_inventory.json \| python -c "import json,sys; rows=json.load(sys.stdin); assert not any(r.get('classification')=='UNKNOWN' for r in rows)"` | 🔲 |
| DoD-4 | ≥21 E2E golden-path tests pass, zero regressions | `pytest tests/_apps_contract/test_ag9_apps_research_golden_path.py -v` | 🔲 |
| DoD-5 | Both CI gates green | `python ops_scripts/ci/check_apps_research_golden_path_runtime.py` and `python ops_scripts/ci/check_apps_research_prompt_authority.py` both exit 0 | 🔲 |
| DoD-6 | All 11 output artifacts present, memory writeback done | All files exist under `artifacts/apps_research/`, memory entity updated | 🔲 |

**Verification-vs-Deferral table**:

| Item | Why deferred | Tracked in |
|---|---|---|
| Real LLM inference for company brief synthesis | Out of AG-9 scope; stubs acceptable for spine proof | Future plan |
| Holdout corpus / Spearman calibration | Requires labeled data; not a spine concern | Future plan |
| Full L3 DAG | Only conditional L3 participation required for AG-9 | Future plan |
| R1B semantic cache wiring | Hard-law excluded from AG-9 | Future plan |
| Tavily live retrieval in C0 binding | Tavily is called by inner hop pipeline; C0 binding reads shaped evidence only | Existing inner pipeline |

---

## Rollback Strategy

1. W0 gates protect against regressions — do not proceed if any fail.
2. apps_research bindings are isolated in `agentic_core/<layer>/apps_research_*_binding.py` — removal does not touch shared code.
3. If any stage breaks existing apps_rg tests, revert the offending binding file.
4. If apps_lic regression guards fail due to the AG-9 changes, treat as a regression bug and revert; apps_lic tests are not AG-9 design checkpoints.
5. `git stash` is safe at any wave boundary (no migrations, no schema changes, no new L4 writes).

---

## Acceptance Invariant

AG-9 is complete only when apps_research has **one proven golden-path runtime chain** using the accepted apps_rg golden baseline, with:
- Current apps_research functionality preserved or explicitly deferred
- All apps_research prompt surfaces inventoried, classified, and stage-consumption-mapped
- A custom apps_research payload into U0
- U0 reflection receipt
- `app_payload` consumption at L1/L0/C0/PA
- Deterministic route from L0
- C0/PA governed evidence handling (existing `HybridSearchEngine` + `EvidenceShaper` path)
- PA is sole prompt assembly authority (`research_pa_compiler.py` governed by PA binding only)
- Prompt authority hardening: no prompt authority bypass
- All prompt surfaces classified with zero UNKNOWN
- L3 included if `workflow_required`
- L2 sealed artifact with ref preservation (inner hop pipeline under L2 governance)
- Exit/X1/X3 structured evaluation through shared `build_x3_packet`
- No legacy `envelope.payload` bypass
- No prompt authority bypass
- No direct L4 write (UWG-gated path preserved)
- No ChromaDB mutation
- No embedding generation
