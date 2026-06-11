---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-repo-brief-plan3-zero-loss-overwrite.md'
original_relative_path: 'apps-repo-brief-plan3-zero-loss-overwrite.md'
source_sha256: 18b23cc6e3fcfb132be954ab0768d85d21f890a18dac44e2568b547e31778f99
recovered_status: SURVIVED_IN_CURRENT
last_commit: '315fd11926d'
last_commit_date: '2026-05-06 06:26:53 -0400'
created_date: '2026-05-04'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_exec → apps_repo_brief Plan 3: Hardened Zero-Loss Canonical Spine Refactor

> **Status:** Not Started · **Tier:** T3 · **Slug:** `apps-repo-brief-plan3-zero-loss-overwrite`  
> **Authority:** Merges Plan 1 (`apps-exec-to-repo-brief-rename-d3f8a2.md`) + Plan 2 (`apps_research` canonical spine standard)  
> **Output:** Single SSOT plan; no implementation until reviewed

---

## 1. Executive Summary

**Primary Product:** `apps_repo_brief` translates a technical repo into evidence-backed executive briefs for a target audience (recruiter / cto / svp_eng / board / head_of_ai). It does **not** perform runtime execution, own C0 retrieval, own Prompt Assembly, own L2 execution, own Exit, write L4, or mutate current-run learning.

**Current Defects (from Plan 1, preserved):**
1. **Misnaming** — `apps_exec` implies runtime execution; actual function is repo→brief translation.
2. **Pre-C0 HOP pipeline** — `ExecOrchestrator` runs `INGEST → EXTRACT → ASSEMBLE → GATE → EMIT` before any C0 call, violating the canonical spine.
3. **Post-L2 authoritative FEC anti-pattern** — `cert/fec_producer.py` mints `FinalEvidenceContract` after L2; authoritative FEC must come from C0 before PA/L2.
4. **Contradictory route declarations** — `spine_manifest.yaml` claims R3 grounded with C0; `cert_route_registry.yaml` claims template-only/no-C0.
5. **Narrow cross-app coupling** — only `apps_eval` has lazy-import runtime coupling (3 scenarios, allowlisted, SKIP-on-failure); siblings have doc-only references.
6. **Blast-radius hotspot** — `apps_exec.types.exec_types` has 8+ consumers; requires type re-export strategy through migration.

**Target Architecture:** Canonical spine `U0 → L1 → L0 → C0 → PA → L2 → Exit → L6` with zero app-level work before C0. C0 owns authoritative `FinalEvidenceContract.v1`; PA owns `CompiledPromptArtifact` with real templates (no placeholders); L2 owns bounded synthesis with E1-E5 receipts; Exit owns exactly one X3; L6 owns only future-run learning; UWG owns all durable writes.

**Migration Strategy:** 6-wave phased rollout (W0 Discovery → W1 Parallel Package → W2 Canonical Route + Prompt Assembly Scaffold → W3 C0/PA Spine Restructure → W4 L2/Exit/Negative Controls → W5 Shim Sunset). Compatibility shim retained until zero-hard-refs gate passes.

---

## 2. Current `apps_exec` Function (Plan 1 Defects Preserved)

| Surface | Current State | Defect |
|---------|--------------|--------|
| **Naming** | `apps_exec` | Implies runtime execution; actual product is repo→brief translation |
| **Spine claim** | `spine_manifest.yaml` declares `R3_grounded_read` with C0 over `exec_docs` | Contradicts `cert_route_registry.yaml` "template-driven (no C0)" |
| **HOP pipeline** | `ExecOrchestrator` 5 HOPs: `INGEST → EXTRACT → ASSEMBLE → GATE → EMIT` | **Pre-C0 work** — app owns ingestion, extraction, assembly, style gate before canonical layers |
| **Cert route** | `apps_exec.execution_v1`, `invoke_exit_eval=true`, `execution_form=SINGLE_STEP` | Self-describes as template-only; no C0 requirement enforced |
| **Product route** | `apps_exec.single_step_v1` (legacy second route in `route_registry.yaml`) | Route duplication — two SSOTs for same capability |
| **FEC producer** | `apps_exec/cert/fec_producer.py` post-L2 | **Authoritative-FEC anti-pattern** — mints contract after L2 instead of C0 before PA |
| **Style gate** | `StyleGateValidator` as HOP 4 pre-C0 | App owns final release authority before C0/PA/L2/Exit |
| **Module count** | 59 | Cross-cutting imports: 36; shim: `_optional_agentic_core.py` |
| **Blast hotspot** | `apps_exec.types.exec_types` | 8 service-test consumers + scenario_runner; highest rename risk |

---

## 3. Proposed `apps_repo_brief` Function (Zero-Loss Merge)

### 3.1 Product Definition
```yaml
app_name: apps_repo_brief
capability: apps_repo_brief.generate_executive_brief_v1
route_id: apps_repo_brief.executive_brief_v1
route_family: R3_SIMPLE_GROUNDED_READ
execution_form: SINGLE_STEP
c0_required: true
pa_required: true
l3_required: false
durable_write_allowed: false
commit_request_allowed: false
```

### 3.2 Canonical Spine Path
```
U0 Intake
  → L1 Plan
  → L0 Route Decision
  → R1A Exact Cache ([RET] → Exit)
  → R1B Semantic Cache ([RET] → Exit)
  → R5 Pre-route Fallback ([RET] → Exit)
  → R3_SIMPLE_GROUNDED_READ
  → apps_repo_brief normalization adapter ONLY
  → C0 Context Engine (authoritative FinalEvidenceContract.v1)
  → PA Prompt Assembly (CompiledPromptArtifact with real templates)
  → L2 Execute E1-E5
  → apps_repo_brief cert projection adapter ONLY
  → Exit v6 / exactly one X3
  → L6 Shadow Evaluation (after-runtime only)
  → UWG / L4 (durable writes only through UWG)
```

**Hard rules:**
- SIMPLE ≠ ungrounded; SIMPLE ≠ skip C0; GROUNDED means C0 is **mandatory**
- Direct `apps_repo_brief` does **not** use static app DAG, Hop terminology, or L3 by default
- L3 only for: multi-audience batch, snapshot comparison, board pack+appendix+talk track, `apps_research` external context, staged HITL loop

### 3.3 Responsibility Split (Adapted from Plan 2)

| Layer | Owner | Responsibilities |
|-------|-------|------------------|
| **apps_repo_brief** | App | Audience personas, board/CTO/SVP/recruiter/head_of_ai schemas, exec brief templates, audience rubrics, style policy, artifact naming, normalization adapter, app-specific validation helpers, cert projection adapter, run-summary adapter |
| **C0** | Core | Retrieval planning, repo evidence discovery, source hydration, dense/sparse/metadata/graph/code-symbol/proof/prior-artifact retrieval, claim-support map, section-level evidence coverage, contradiction detection, freshness/ACL checks, **authoritative `FinalEvidenceContract.v1`** |
| **PA** | Core | Prompt packet construction, PromptBOM, prompt registry, real template bodies, slot composition, evidence fencing, schema binding, citation instructions, signed `CompiledPromptArtifact` |
| **L2** | Core | Bounded synthesis/render, provider/model invocation through governed gateway only, same-authority local repair, artifact sealing, E1-E5 receipts |
| **Exit** | Core | Final current-run disposition, board-readiness evaluation, groundedness/citation integrity, **exactly one X3** |
| **L6** | Core | Completed-run evaluation, future-run learning proposals **only**, no current-run mutation |
| **L4/UWG** | Core | Durable retrieval surfaces (`repo_brief_docs`), cache state, policy/registry state, approved future-run memory, **durable writes only through UWG** |

---

## 4. Inbound Dependency Map (Plan 1 Preserved + Plan 2 Hardening)

### 4.1 Hard Runtime Coupling
**Only `apps_eval` has runtime coupling:**
- `apps_eval/engines/scenario_runner.py` L568-636 — 3 scenarios (`recruiter_brief`, `cto_brief`, `dry_run`) lazy-import `apps_exec.reasoning.ExecOrchestrator` + `apps_exec.types.exec_types`
- **Mitigation:** ImportError → `("SKIP", _SKIP_SCORE, "apps_exec not available")`
- **Allowlist:** `config/cross_app_import_allowlist.yaml` sanctions `apps_eval → apps_exec` coupling

### 4.2 Soft References (String Literals)
```
agentic_core/L0_routing/config/path_constants.py          → APPS_EXEC_DIR, APPS_EXEC_SUBFOLDER_MAP, 4 allowlist tuples
agentic_core/L2_execution/types/agent_taxonomy_registry.py  → 7 literal matches
agentic_core/L5_safety/config/structure_blueprint/ssot.py   → 5 literal matches
apps_shared/spine_emission/context.py                       → app-name allowlist (6 matches)
apps_shared/proof/scenarios.py                            → scenario fixtures (8 matches)
config/cross_app_import_allowlist.yaml                    → apps_eval→apps_exec entry
docs/wave_g/G1b_apps_inventory/app_inventory.yaml           → APP-EXEC row (16 matches)
tools/eval/retrieval_benchmark.py                         → scenario IDs (20 matches)
```

### 4.3 Doc-Only References (Zero Coupling)
- `apps_rg/spine_manifest.yaml` — pattern attribution comment
- `apps_rfp/spine_manifest.yaml` — HITL-posture comparison + pattern attribution
- `apps_research/SVP_ENGINEERING_REVIEW.md` — "rigor of apps_eval, apps_lic, apps_exec, ..."
- `apps_underwriting_ai/spine_manifest.yaml` — pattern attribution
- `apps_rfp/config/reasoning_toggles_config.py` — "Aligned with apps_exec ... pattern"

### 4.4 Cross-App Dependency Matrix (Hardened)

| app | dep_type | evidence_file | current_reference | migration_action | risk |
|-----|----------|---------------|-------------------|------------------|------|
| **apps_eval** | calls directly (lazy+SKIP) | `scenario_runner.py` L568-636 | `from apps_exec.reasoning.ExecOrchestrator import ExecOrchestrator` ×3 | Add parallel `apps_repo_brief` scenarios W1; flip primary W4; shim until zero-refs gate | **Medium** |
| apps_research | doc only | `SVP_ENGINEERING_REVIEW.md` | "rigor of ... apps_exec ..." | Comment update W2 | Low |
| apps_rg | doc only | `spine_manifest.yaml` L16 | pattern attribution | Comment update W2 | Low |
| apps_lic | doc only | (rg/rfp HITL-posture refs) | "weaker than apps_lic and apps_exec" | Comment update W2 | Low |
| apps_rfp | doc only | `spine_manifest.yaml` L16/65/99, `reasoning_toggles_config.py` L4 | pattern + HITL comparisons | Comment update W2 | Low |
| apps_qna | none | — | none | none | None |
| apps_underwriting_ai | doc only | `spine_manifest.yaml` L14 | pattern attribution | Comment update W2 | Low |
| apps_shared | shared substrate | `proof/scenarios.py` (8), `spine_emission/context.py` (6) | allowlist literals + scenario IDs | Add `apps_repo_brief` allowlist W1; retain `apps_exec` until W5 | **Medium** |

**Zero of 7 sibling `apps_*` have Python-import coupling.** Only `apps_eval` has allowlisted lazy-import with SKIP fallback.

---

## 5. Outbound Dependency Map (Plan 1 Preserved)

**36 cross-cutting + substrate imports from `agentic_core`:**
- `L2_execution.types.local_first_disposition`, `L2_execution.types.vllm_gateway_adapter_types`
- `L3_orchestration.inference.qwen_vllm` (optional, graceful degrade)
- `L4_state.config.vllm_routing_predicates`
- `adg.applications.execute_ssot_integration`, `adg.runtime.behavioral_index`
- `mixins.embedding_mixin`, `mixins.semantic_cache_mixin`
- `runtime.contracts.lifecycle_trace_contract` (all `_emit_*` lineage)
- R3 contract chain: `L0_routing.{intake.validated_request, c0_retrieval.{route_contract,plan,final_contract}}`, `L1_cognition.types.plan_contract_types`, `L2_execution.reasoning.compiled_artifact`, `L5_safety.eval_spine.exit_eval`, `L3_orchestration.exit_eval.v6.types`

**`apps_shared` substrate:**
- `integrations.governed_app_runner.GovernedAppRunner`
- `spine.base_spine_adapter.BaseSpineAdapter`
- `cert.{maybe_invoke_exit_eval, rubric_output_mapper}`
- `spine_emission.governed_run`

**Zero outbound `apps_*` imports.**

---

## 6. Registry and Route Impact (Plan 1 Preserved + Plan 2 Hardening)

| File | Current | Migration Action | Wave |
|------|---------|----------------|------|
| `apps_exec/spine_manifest.yaml` | R3_grounded_read, contradicts cert_route | Migrate to `apps_repo_brief/spine_manifest.yaml`; old path → deprecation stub | W2 |
| `apps_exec/config/route_registry.yaml` | `apps_exec.single_step_v1` (legacy) + `apps_exec.execution_v1` | **Collapse to ONE canonical** `apps_repo_brief.executive_brief_v1`; deprecated aliases W2–W4 | W2 |
| `apps_exec/config/cert_route_registry.yaml` | Contradictory "template-only" description | Resolve to C0-required; migrate to `apps_repo_brief/` | W2 |
| `agentic_core/L0_routing/config/path_constants.py` | `APPS_EXEC_*` | Add `APPS_REPO_BRIEF_*` W1; remove `APPS_EXEC_*` W5 | W1, W5 |
| `agentic_core/L2_execution/types/agent_taxonomy_registry.py` | apps_exec rows | Dual-entry W1; retire W5 | W1, W5 |
| `agentic_core/L5_safety/config/structure_blueprint/ssot.py` | apps_exec allowlist | Dual-entry W1; retire W5 | W1, W5 |
| `apps_shared/spine_emission/context.py` | app-name allowlist | Add `apps_repo_brief` W1; remove `apps_exec` W5 | W1, W5 |
| `config/cross_app_import_allowlist.yaml` | apps_eval→apps_exec | Add apps_eval→apps_repo_brief W1; remove legacy W5 | W1, W5 |
| `docs/wave_g/G1b_apps_inventory/app_inventory.yaml` | APP-EXEC row | Add APP-REPO-BRIEF W1; retire APP-EXEC W5 | W1, W5 |
| `tools/eval/retrieval_benchmark.py` | apps_exec scenario IDs | Parallel `apps_repo_brief` IDs W1; retire legacy W5 | W1, W5 |

---

## 7. C0 Requirements (Plan 2 Adapted to Repo Brief)

### 7.1 Retrieval Surface
**Rename:** `exec_docs` → `repo_brief_docs`  
**Nature:** L4 durable retrieval surface (not live runtime directory scan)  
**Coverage:**
- Architecture, reference, governance, runtime-gates, L5 docs
- C0/PA/L2/Exit/L4/L6 doctrine docs
- Runtime proof, E2E acceptance, replay proof, no-bypass proof, OTEL span proof, ADG proof docs
- Code references, route/capability/app registries, tests, cert receipts
- ADRs, DDRs, known limitations

### 7.2 C0 Retrieval Lanes (7 lanes)
1. **BM25/exact-phrase** — policy names, layer names, route IDs, file paths, class names, test names, hash fields, exact claims
2. **Dense semantic** — concept discovery, exec narrative support, governance language
3. **Metadata** — source_type, audience relevance, recency, policy_hash, blueprint_hash, repo_snapshot_id, source authority
4. **Graph** — docs↔code↔tests↔proof linkage; L5↔Runtime Gates↔Exit↔UWG relationships
5. **Code symbol** — implementation-backed claims, entrypoint validation, registry evidence
6. **Proof lane** — tests, cert receipts, replay proof, OTEL spans, negative controls
7. **Prior artifact** — prior board/CTO briefs, claim maps, evidence maps (hints only unless snapshot-perfect)

### 7.3 Evidence Rules
- Dense hits alone **cannot** support high-stakes governance claims
- Exact names/IDs/paths/labels/symbols/dates require sparse/BM25 or metadata support
- Every important claim traces to `claim_support_map`
- Board governance claims require **section-level evidence coverage**
- Mean combined score alone is **forbidden** as support standard

### 7.4 C0 Depth Profiles (Repo-Brief Specific)

```yaml
REPO_BRIEF_LIGHT:
  final_sources_min: 3
  final_sources_target: 5
  citation_anchors_min: 5
  output_equivalent: 1-2 pages

REPO_BRIEF_STANDARD:
  final_sources_min: 8
  final_sources_target: 12
  citation_anchors_min: 12
  output_equivalent: 3-5 pages

REPO_BRIEF_DEEP:
  final_sources_min: 18
  final_sources_target: 25
  final_sources_max: 35
  raw_candidates_min: 80
  raw_candidates_target: 150
  raw_candidates_max: 250
  citation_anchors_min: 30
  citation_anchors_target: 45
  output_equivalent: 8-15 pages

REPO_BRIEF_BOARD_DOSSIER:
  final_sources_min: 35
  final_sources_target: 50
  final_sources_max: 60
  citation_anchors_min: 60
  output_equivalent: 15+ pages
```

**Defaults:**
- board → REPO_BRIEF_DEEP (unless user requests dossier)
- cto → STANDARD or DEEP depending on emphasis
- svp_eng → STANDARD
- recruiter/hiring exec → STANDARD
- head_of_ai → DEEP

### 7.5 Adaptive Coverage Matrix

**Coverage family catalog:**
- executive_thesis, governance_model, runtime_controls, architecture_boundaries
- evidence_of_operating_discipline, risk_and_gap_posture, implementation_proof
- observability_and_replay, delivery_and_operating_model
- board_asks_or_decision_points, recruiter_positioning
- cto_technical_implications, svp_engineering_implications, head_of_ai_implications

**BriefingCoverageMatrix schema:**
```yaml
briefing_profile_id
artifact_type
user_intent
target_audience
emphasis_areas
repo_snapshot_id
selected_coverage_sections[]:
  - section_id
  - coverage_family
  - selection_reason
  - required_for_this_brief
  - coverage_status
  - source_count
  - citation_anchor_count
  - source_type_requirements
  - strongest_sources
  - gaps
  - caveats
  - omit_if_unsupported
```

### 7.6 C0 Required Outputs for REPO_BRIEF_DEEP
1. **FinalEvidenceContract.v1** (authoritative)
2. **BriefingCoverageMatrix** (adaptive sections)
3. **SourcePortfolioSummary** (counts by source type, diversity, freshness)
4. **ClaimEvidenceMap** (per-claim support status)
5. **ContradictionMatrix** (unresolved conflicts)
6. **FreshnessReport** (source recency, staleness caveats)
7. **SectionGapReport** (missing coverage, omit-if-unsupported flags)
8. **SynthesisGuidanceForPA** (how to handle gaps/caveats/contradictions)

### 7.7 Contradiction Policy
Detect conflicts on:
- Route identity, capability identity, layer ownership
- C0 vs PA vs L2 responsibility, Exit vs FEC ownership
- L4/UWG write ownership, L6 current-run mutation prohibition
- Cache compatibility, persona schema, artifact naming
- Repo snapshot identity, route vs cert registry contradiction
- `apps_exec` legacy vs `apps_repo_brief` canonical references

### 7.8 Board Gates at C0

**PASS if:**
- Required section coverage ≥ 85%
- Total final sources ≥ 18 (DEEP floor)
- Citation anchors ≥ 30
- governance_model PASS
- runtime_controls PASS
- risk_and_gap_posture PASS or WEAK_WITH_CAVEATS with explicit caveat
- No unresolved critical contradiction
- ≥1 authoritative governance/source anchor exists
- Source diversity appropriate
- Proof/test evidence exists for implementation claims

**WEAK_WITH_CAVEATS if:**
- Coverage 60-84%, sources 10-17, some caveats required
- Non-critical contradictions unresolved
- Some claims partially fresh
- Risks/gaps partial but explicit

**FAIL / DEGRADE if:**
- Coverage < 60%, sources < 10
- No authoritative governance anchor
- Critical contradiction unresolved
- template_only requested as full board brief
- Citation anchors < 12

**Fallback behavior:**
- PASS → FinalEvidenceContract to PA
- WEAK_WITH_CAVEATS → FEC to PA with caveats + synthesis restrictions
- WEAK → one bounded C0 refinement pass
- CONFLICTED → contradiction report + human_review/reroute for board
- EMPTY → SAFE_FALLBACK scaffold or SAFE_ABSTAIN to Exit
- BLOCKED → SAFE_ABSTAIN or human_review to Exit
- **template_only → scaffold only, never full board brief**

---

## 8. Final Evidence Contract v1 (Plan 1 Target Hardened)

**Create:** `agentic_core/L0_routing/c0_retrieval/repo_brief_final_contract.py`

```yaml
final_evidence_contract:
  contract_type: apps_repo_brief.FinalEvidenceContract.v1

  identity:
    request_id, run_id, trace_id
    route_id: apps_repo_brief.executive_brief_v1
    audience, emphasis_areas
    repo_snapshot_id, policy_hash, blueprint_hash, replay_key

  retrieval:
    source_collection: repo_brief_docs
    retrieval_surface_id, retrieval_plan_hash, lanes_used
    raw_count, hydrated_count, shaped_count, excluded_count

  status:
    evidence_status: PASS | WEAK | WEAK_WITH_CAVEATS | CONFLICTED | EMPTY | BLOCKED
    recommended_disposition: proceed | proceed_with_caveat | fallback_R5 | abstain | reroute | human_review
    grounded: true | false
    template_only: true | false

  section_coverage:
    executive_thesis, governance_model, runtime_controls
    architecture_boundaries, operating_discipline
    risks_and_gaps, board_asks

  claim_support_map:
    - claim_id, claim_text
      claim_type: governance_control | architecture_boundary | runtime_proof | operating_model | risk_gap | board_decision | implementation_claim
      support_status: PASS | WEAK | UNSUPPORTED | CONTRADICTED
      direct_support_refs, implementation_support_refs, proof_support_refs
      contradiction_refs, gap_notes

  verified_evidence:
    must_use, supporting, background, contradicts, excluded

  reports:
    freshness_report, acl_report, contradiction_report, gap_report
    lineage_manifest, prompt_budget_hint

  observability:
    c0_span_id, retrieval_ms, shaping_ms, scoring_ms
    refinement_attempted, budget_status
```

---

## 9. Prompt Assembly Requirements (Plan 2 Adapted)

### 9.1 Files to Create
```
apps_repo_brief/prompt_assembly/prompt_bom.yaml
apps_repo_brief/config/prompt_registry.yaml
apps_repo_brief/prompt_assembly/repo_brief_pa_compiler.py
apps_repo_brief/prompt_assembly/templates/repo_brief_synthesis_v1.yaml
apps_repo_brief/prompt_assembly/templates/repo_evidence_to_prompt_context_v1.yaml
apps_repo_brief/prompt_assembly/templates/unsupported_repo_claim_omission_v1.yaml
apps_repo_brief/prompt_assembly/templates/caveat_and_confidence_repair_v1.yaml
apps_repo_brief/prompt_assembly/templates/brief_length_and_structure_repair_v1.yaml
```

### 9.2 PromptBOM Required Slots (S0-R0)
- **S0** system_and_governance
- **I0** repo_brief_rules
- **C0** verified_repo_evidence_context
- **U0** user_repo_brief_request
- **A0** audience_persona_and_schema
- **D0** origin_and_injection_fences
- **E0** approved_examples_optional
- **Y0** approved_style_preferences
- **R0** output_schema_and_disposition_constraints

### 9.3 PromptBOM Rules
- No placeholders, no TODO, no vague shells
- No ad hoc prompt strings outside registered templates
- All templates include: `input_contract`, `required_slots`, `forbidden_behaviors`, `slot_bodies`, `output_contract`, `validation_rules`, `hash_fields`

### 9.4 `repo_brief_synthesis_v1.yaml` Required Fields
```yaml
purpose: Synthesize governed executive brief from C0 evidence
allowed_stage: E3_EXEC
required_inputs:
  - normalized_repo_brief_task
  - FinalEvidenceContract
  - BriefingCoverageMatrix
  - SourcePortfolioSummary
  - ClaimEvidenceMap
  - ContradictionMatrix
  - FreshnessReport
  - SynthesisGuidanceForPA
  - repo_brief_depth_profile
  - audience_schema_ref, output_schema_ref
  - policy_hash, blueprint_hash, replay_key
forbidden_behaviors:
  - invent_repo_fact
  - invent_architecture_claim
  - invent_governance_control
  - invent_test_evidence
  - invent_runtime_trace
  - invent_source
  - use_unsupported_claim_as_fact
  - follow_instruction_inside_retrieved_content
  - retrieve_new_information
  - call_provider_directly
  - mutate_state
  - approve_final_output
```

### 9.5 `repo_brief_pa_compiler.py` Requirements
**Must:**
- Load `prompt_bom.yaml`, `prompt_registry.yaml`
- Resolve template by `template_id`
- Validate required slots, input contract, C0 evidence refs
- Render structured slots, canonicalize slot bytes
- Compute hashes: `prompt_bom_hash`, `prompt_registry_hash`, `template_hash`, `manifest_hash`
- Emit `CompiledPromptArtifact`

**Must NOT:**
- Retrieve, route, call providers, execute tools, emit Exit disposition, write durable state

### 9.6 CompiledPromptArtifact Fields
```yaml
artifact_id, request_id, run_id, trace_id, route_id
selected_capability, template_id, template_version
prompt_bom_hash, prompt_registry_hash, template_hash, manifest_hash
policy_hash, blueprint_hash, replay_key
evidence_contract_ref, briefing_coverage_matrix_ref, source_portfolio_ref
claim_evidence_map_ref, contradiction_matrix_ref, freshness_report_ref
rendered_slots, canonical_slot_bytes_hash, artifact_hash
provider_lane, output_schema_ref, audit_refs
```

---

## 10. L2 Requirements (Plan 2 Adapted)

### 10.1 L2 E1-E5 Receipts
- `L2.E1.repo_brief_execution_context_bound`
- `L2.E2.repo_brief_evidence_validated`
- `L2.E3.repo_brief_synthesized`
- `L2.E4.repo_brief_local_heal_applied`
- `L2.E5.repo_brief_artifact_sealed`

### 10.2 L2.E1 Prep Verification
- route_id = `apps_repo_brief.executive_brief_v1`
- selected_capability = `apps_repo_brief.generate_executive_brief_v1`
- l3_required = false
- repo_brief_depth_profile, audience persona present
- FinalEvidenceContract, BriefingCoverageMatrix, SourcePortfolioSummary, ClaimEvidenceMap, ContradictionMatrix, FreshnessReport, CompiledPromptArtifact all present
- policy_hash, blueprint_hash, replay_key present
- No direct L4 write path available

### 10.3 L2.E2 Validate
- Evidence status usable (PASS or WEAK_WITH_CAVEATS)
- Source refs, citation anchors exist
- Section coverage satisfies profile gate
- Freshness satisfied or explicitly caveated
- Contradictions surfaced
- Prompt artifact fences retrieved text as data
- Output schema = governed repo brief packet
- Provider fallback governed, not silent

### 10.4 L2.E3 Execute
- Synthesize governed repo brief packet
- Use **only** C0-approved evidence
- Adapt to target audience, cite factual claims
- Label weak/caveated claims, preserve contradiction/gap notes
- No new retrieval, no durable write

### 10.5 L2.E4 Heal Allowed
- Remove unsupported claim, add caveat
- Repair citation formatting, align claim to cited evidence
- Trim over-budget output, repair missing section if evidence exists
- Rerun synthesis against **same** evidence contract if retry budget allows

### 10.6 L2.E4 Heal Forbidden
- Retrieve new evidence, change route
- Silently switch provider
- Upgrade weak evidence to strong
- Invent citations, write L4, ask HITL directly

### 10.7 L2.E5 Seal
Include: sealed artifact, candidate packet, depth profile, target audience, all C0/PA refs, source refs/citations, support score, freshness status, contradiction flags, unresolved gaps, model/provider receipt, repair ledger, replay/trace refs, terminal class.

---

## 11. Cert Projection Adapter (Plan 1 Reframe Hardened)

**Old:** `apps_exec/cert/fec_producer.py` as authoritative post-L2 FEC producer  
**New:** `apps_repo_brief/cert/cert_projection_adapter.py`

**May attach/project:**
- repo_brief_depth_profile, evidence coverage, selected section coverage
- SourcePortfolioSummary, ClaimEvidenceMap, ContradictionMatrix
- FreshnessReport, SectionGapReport, citation coverage
- Unsupported-claim checks, audience/briefing schema checks
- ExitReviewPacket fields, **C0 FinalEvidenceContract ref** (not replacement)

**Must NOT:**
- Create authoritative FEC after L2
- Final approve, decide X3, write L4, promote learning

---

## 12. Exit v6 Requirements (Plan 2 Adapted)

### 12.1 Exit Receives
- `[RET]` exact cache (R1A), semantic cache (R1B), pre-route fallback (R5)
- Sealed degraded/failure from C0, prompt failure from PA, execution failure from L2
- Sealed repo brief artifact from successful `apps_repo_brief`

### 12.2 Exit Checks
- Policy/authority, task completion, groundedness, citation integrity
- Support score, selected section coverage, source portfolio quality
- Gaps/contradictions, freshness, schema, audience fit, board-readiness
- Safety/egress, replay/observability

### 12.3 Exit Emits Exactly One X3
- `ALLOW_FINISH`
- `SAFE_ABSTAIN`
- `SAFE_FALLBACK`
- `REROUTE`
- `ESCALATE_HITL`
- `COMMIT_REQUEST`
- `DENY / BLOCK_COMMIT`

**Must NOT:** retrieve, execute tools, write L4 directly, allow L6 to rescue current run.

---

## 13. L6 and UWG/L4 (Plan 2 Adapted)

- **L6 runs only after Exit**
- **L6 learns only for future runs** (no current-run mutation)

**Possible approved future-run state:**
- Exact/semantic cache entries, approved examples, repo brief rubrics/thresholds
- Retrieval/source manifests, prompt/schema improvements, provider-routing lessons
- C0 depth-profile tuning, source-authority weights, selected coverage policies

**UWG is the ONLY durable write path.**
**L4 stores only approved future-run state.**

---

## 14. Cache Requirements (Plan 1 Preserved + Hardened)

**Create:** `apps_repo_brief/config/cache_compat.yaml`

### 14.1 R1A Exact Cache
May terminal-return prior artifact **only if ALL** match:
```
normalized_request_hash, audience, emphasis_areas_hash
repo_snapshot_id, retrieval_surface_id, policy_hash, blueprint_hash
persona_schema_version, rubric_version, source_freshness_window
```

### 14.2 R1B Semantic Cache
- **MUST NOT** terminal-return board briefs unless strict-compat exact
- May return prior evidence maps/artifact refs as **hints to C0/PA only**
- Board defaults to **no terminal semantic return** unless snapshot-perfect

---

## 15. Entrypoint Purity Requirements (Plan 2 Adapted)

### 15.1 Target Entrypoint
**`apps_repo_brief/__main__.py` must:**
- Parse CLI args only
- Build raw request envelope only
- Call canonical `agentic_core` runner with `app_name="apps_repo_brief"`
- **Fail closed** if runner/capability unavailable
- **Never** fallback to `apps_exec` legacy runner
- Never instantiate repo brief engines, never call C0/PA/L2 directly
- Never call provider SDKs, never call L4, never import sibling apps

### 15.2 Shim Entrypoint (Transition)
**`apps_exec/__main__.py` during W1–W4 must:**
- Emit deprecation warning
- Delegate **only** to `apps_repo_brief` canonical runner path
- Not preserve old off-spine behavior
- Fail closed if `apps_repo_brief` path unavailable

### 15.3 Governance Tests to Create/Update
```
tests/governance/test_apps_repo_brief_entrypoint_purity.py
tests/governance/test_apps_repo_brief_recipe_resolution.py
tests/governance/test_apps_repo_brief_no_legacy_runner.py
tests/governance/test_apps_repo_brief_provider_boundary.py
tests/governance/test_apps_repo_brief_l4_write_boundary.py
```

**20 Required Tests:**
1. `test_apps_repo_brief_main_is_pure_shim`
2. `test_apps_repo_brief_main_does_not_import_repo_brief_engines`
3. `test_apps_repo_brief_main_does_not_import_c0_adapters`
4. `test_apps_repo_brief_main_does_not_import_pa_compiler`
5. `test_apps_repo_brief_main_does_not_import_l2_adapters`
6. `test_apps_repo_brief_main_does_not_import_provider_sdks`
7. `test_apps_repo_brief_main_does_not_import_l4_write_surfaces`
8. `test_apps_repo_brief_main_contains_no_l2_callable_construction`
9. `test_apps_repo_brief_main_contains_no_inline_synthesis_closure`
10. `test_apps_repo_brief_no_legacy_runner_feature_flag`
11. `test_apps_repo_brief_legacy_apps_exec_runner_not_reachable_from_main`
12. `test_apps_repo_brief_core_runner_resolves_executive_brief_capability`
13. `test_apps_repo_brief_route_registry_selects_r3_simple_grounded_read`
14. `test_apps_repo_brief_r3_requires_c0`
15. `test_apps_repo_brief_direct_path_uses_no_l3`
16. `test_apps_repo_brief_recipe_resolution_failure_fails_closed_through_exit`
17. `test_apps_repo_brief_no_generic_brief_when_recipe_missing`
18. `test_apps_repo_brief_no_direct_l4_writes`
19. `test_apps_repo_brief_provider_calls_only_through_governed_gateway`
20. `test_apps_repo_brief_exit_emits_x3_but_does_not_write_l4`

---

## 16. Recipe and Capability Resolution (Plan 2 Adapted)

### 16.1 Files to Create/Update
```
apps_repo_brief/integrations/repo_brief_capability_registry.py
apps_repo_brief/integrations/repo_brief_l2_step_adapters.py
apps_repo_brief/integrations/repo_brief_c0_adapter.py
apps_repo_brief/integrations/repo_brief_exit_cert_projection.py
```

### 16.2 Required Exports
- `register_repo_brief_capability()`
- `resolve_repo_brief_capability(app_name, route_id)`
- `register_repo_brief_l2_steps()`
- `get_repo_brief_step_adapter(step_name)`

### 16.3 Selected Route
```yaml
route_id: apps_repo_brief.executive_brief_v1
execution_form: SINGLE_STEP
l3_required: false
selected_capability: apps_repo_brief.generate_executive_brief_v1
```

---

## 17. Tests and Negative Controls (Merged Plan 1 + Plan 2)

### 17.1 Prompt Assembly Tests (24 tests)
1. `test_apps_repo_brief_prompt_bom_exists_and_has_required_slots`
2. `test_apps_repo_brief_prompt_registry_registers_required_templates`
3. `test_apps_repo_brief_pa_compiler_compiles_prompt_artifact`
4. `test_apps_repo_brief_pa_compiler_does_not_retrieve_execute_or_call_provider`
5. `test_apps_repo_brief_l2_synthesis_requires_compiled_prompt_artifact`
6. `test_apps_repo_brief_provider_gateway_requires_compiled_prompt_artifact`
7. `test_apps_repo_brief_repair_steps_require_repair_prompt_artifacts`
8. `test_apps_repo_brief_prompt_artifact_contains_evidence_contract_refs`
9. `test_apps_repo_brief_missing_prompt_template_fails_closed_through_exit`
10. `test_apps_repo_brief_prompt_registry_hash_bound_to_replay_key`
11. `test_apps_repo_brief_no_ad_hoc_prompt_strings_in_l2_adapters`
12. `test_apps_repo_brief_no_ad_hoc_prompt_strings_in_engines`
13. `test_apps_repo_brief_prompt_artifact_manifest_hash_matches_evidence_contract`
14. `test_apps_repo_brief_prompt_templates_are_data_boundary_safe`
15. `test_apps_repo_brief_prompt_templates_are_not_placeholders`
16. `test_apps_repo_brief_template_contains_required_slot_sections`
17. `test_apps_repo_brief_repair_templates_contain_forbidden_behavior_blocks`
18. `test_apps_repo_brief_templates_reference_claim_evidence_map_and_caveat_policy`
19. `test_apps_repo_brief_templates_reference_output_schema`
20. `test_apps_repo_brief_templates_preserve_origin_boundary_language`
21. `test_apps_repo_brief_template_files_include_concrete_instruction_text`
22. `test_apps_repo_brief_template_files_include_input_contracts_and_validation_rules`
23. `test_apps_repo_brief_template_files_include_hash_fields`
24. `test_apps_repo_brief_evidence_to_prompt_context_template_blocks_weak_to_fresh_promotion`

### 17.2 C0 and Spine Tests (20 tests)
25. `test_apps_repo_brief_direct_path_uses_no_l3`
26. `test_apps_repo_brief_direct_path_uses_no_static_dag_terms`
27. `test_apps_repo_brief_l0_checks_exact_cache_before_r3`
28. `test_apps_repo_brief_l0_checks_semantic_cache_before_r3`
29. `test_apps_repo_brief_r5_returns_to_exit_before_c0_pa_l2`
30. `test_apps_repo_brief_r3_requires_c0_evidence_contract`
31. `test_apps_repo_brief_deep_enforces_source_floor`
32. `test_apps_repo_brief_deep_enforces_citation_anchor_floor`
33. `test_apps_repo_brief_c0_uses_adaptive_selected_coverage_sections`
34. `test_apps_repo_brief_c0_does_not_use_fixed_board_template`
35. `test_apps_repo_brief_c0_failure_goes_to_exit_as_sealed_packet`
36. `test_apps_repo_brief_fec_includes_briefing_grade_evidence`
37. `test_apps_repo_brief_exit_emits_exactly_one_x3`
38. `test_apps_repo_brief_no_pre_c0_retrieval`
39. `test_apps_repo_brief_no_pre_c0_assembly`
40. `test_apps_repo_brief_authoritative_fec_at_c0`
41. `test_apps_repo_brief_template_only_no_full_board`
42. `test_apps_repo_brief_semantic_cache_strict_compat`
43. `test_apps_repo_brief_style_violations_l2_repair_then_exit_gate`
44. `test_no_apps_exec_python_imports_outside_shim` (P4 gate)

### 17.3 Negative Controls (Must Fail Closed)

| Control | Failure Mode |
|---------|--------------|
| Missing RouteContract | Exit SAFE_ABSTAIN |
| R3 selected with no C0 evidence | Exit BLOCK_COMMIT |
| grounding_required true but FEC missing | Exit BLOCK_COMMIT |
| REPO_BRIEF_DEEP with <10 sources proceeds as PASS | Exit BLOCK_COMMIT |
| REPO_BRIEF_DEEP with no auth governance anchor proceeds as PASS | Exit BLOCK_COMMIT |
| Critical contradiction unresolved proceeds as PASS | Exit ESCALATE_HITL or BLOCK_COMMIT |
| Current claim uses stale source without caveat | Exit requires explicit caveat or BLOCK |
| Implementation claim lacks code/registry/test/proof support | Exit BLOCK_COMMIT |
| Governance claim lacks governance/runtime gate support | Exit BLOCK_COMMIT |
| Runtime proof claim lacks test/OTEL/ADG/replay evidence | Exit BLOCK_COMMIT |
| C0 uses fixed board template regardless of audience/intent | Exit BLOCK_COMMIT |
| Direct apps_repo_brief attempts L3 | Exit BLOCK_COMMIT |
| Direct apps_repo_brief calls itself a static DAG | Exit BLOCK_COMMIT |
| PA retrieves evidence | Exit BLOCK_COMMIT |
| L2 retrieves new evidence outside C0 contract | Exit BLOCK_COMMIT |
| L2 writes L4 directly | Exit BLOCK_COMMIT |
| apps_repo_brief silently switches provider | Exit BLOCK_COMMIT |
| Model output changes route/policy/registry/capability | Exit BLOCK_COMMIT |
| Untrusted retrieved text treated as instruction | Exit BLOCK_COMMIT |
| ExitReviewPacket missing support score or evidence refs | Exit BLOCK_COMMIT |
| L6 attempts current-run mutation | UWG blocks (sanity check) |
| Durable state written without UWG receipt | Exit BLOCK_COMMIT |
| template_only produces full board brief | Exit BLOCK_COMMIT |
| Semantic cache terminal-returns board brief without strict compat | Exit BLOCK_COMMIT |
| Post-L2 cert projection adapter creates authoritative FEC | Exit BLOCK_COMMIT |
| apps_exec legacy runner reachable from apps_repo_brief main | Exit BLOCK_COMMIT |
| apps_exec hard import remains outside shim after P4 | P4 gate blocks sunset |

---

## 18. Wave Structure (Merged and Deduplicated)

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|----------------|
| **W0** | P0.1–P0.6 | Discovery & Plan-Only Verification | ~8k | No implementation yet | Not Started | Dependency scan confirms Plan 1 findings; ADG refreshed; zero new hard refs discovered |
| **W1** | P1.1–P1.12 | Parallel Package + Entrypoint Purity | ~20k | W0 green; additive only | Not Started | `apps_repo_brief/` live; `__main__.py` pure shim; 20 entrypoint governance tests pass; `apps_eval` green |
| **W2** | P2.1–P2.12 | Canonical Route + Prompt Assembly Scaffold | ~24k | W1 green; AG-route-consolidation resolved | Not Started | One canonical route; deprecated aliases live; prompt templates real (no placeholders); cache compat schema; dual OTEL |
| **W3** | P3.1–P3.14 | C0/PA Spine Restructure | ~36k | W2 green; AG-prompt-template + AG-C0-depth resolved | Not Started | Pre-C0 work moved to proper layers; authoritative C0 FEC.v1; PA emits CompiledPromptArtifact; 44 governance tests green |
| **W4** | P4.1–P4.10 | L2/Exit/Negative Controls | ~18k | W3 green; AG-style-gate + AG-FEC-reframe resolved | Not Started | L2 E1-E5 receipts; cert projection adapter (not authoritative FEC); Exit exactly one X3; negative controls fail closed |
| **W5** | P5.1–P5.8 | Shim Sunset & Cleanup | ~12k | W4 green ≥4 weekly cycles; zero-hard-refs gate passes | Not Started | P4 gate passes; `apps_exec/` archived; single OTEL attribute; CI green |

---

## 19. Phase-Level Summary (Hardened)

| Phase | Title | Scope (files/lines) | Pain Points | Est. Tokens | Status |
|-------|-------|---------------------|-------------|-------------|--------|
| **W0** | | | | | |
| P0.1 | Re-run dependency scan | full-repo grep/AST/ADG | may find new coupling vs Plan 1 | 1.5k | Not Started |
| P0.2 | Refresh ADG snapshot | `tools/generate_full_adg.py` | verify apps_exec node IDs current | 1k | Not Started |
| P0.3 | Confirm apps_eval coupling | `scenario_runner.py` L568-636 | verify SKIP-fallback still present | 0.5k | Not Started |
| P0.4 | Confirm route contradictions | `spine_manifest.yaml` vs `cert_route_registry.yaml` | document exact contradiction text | 0.5k | Not Started |
| P0.5 | Confirm current HOP ownership | `ExecOrchestrator.py` line-by-line | map each HOP to current layer | 2k | Not Started |
| P0.6 | Confirm prompt string locations | grep for ad hoc prompt strings | quarantine list for W2 | 2.5k | Not Started |
| **W1** | | | | | |
| P1.1 | Package skeleton | `apps_repo_brief/__init__.py`, dirs | none | 1k | Not Started |
| P1.2 | Reasoning re-export shim | `apps_repo_brief/reasoning/__init__.py` | name collision avoidance | 1k | Not Started |
| P1.3 | spine_manifest.yaml | `apps_repo_brief/spine_manifest.yaml` | resolve C0 contradiction (defer to W2) | 1.5k | Not Started |
| P1.4 | Route registries | `apps_repo_brief/config/{route,cert_route}_registry.yaml` | dual-route consolidation deferred | 2k | Not Started |
| P1.5 | path_constants additive | `agentic_core/L0_routing/config/path_constants.py` | APPS_REPO_BRIEF_* only | 1.5k | Not Started |
| P1.6 | taxonomy + ssot additive | `agent_taxonomy_registry.py`, `structure_blueprint/ssot.py` | dual-entry | 1.5k | Not Started |
| P1.7 | apps_shared allowlists | `spine_emission/context.py`, `cross_app_import_allowlist.yaml` | additive | 1k | Not Started |
| P1.8 | app_inventory row | `docs/wave_g/G1b_apps_inventory/app_inventory.yaml` | APP-REPO-BRIEF additive | 1k | Not Started |
| P1.9 | Eval scenario parallels | `scenario_runner.py`, `proof/scenarios.py`, `retrieval_benchmark.py` | both scenario sets coexist | 3k | Not Started |
| P1.10 | Mirror unit tests | `tests/unit/apps_repo_brief/**` | mechanical mirror | 5k | Not Started |
| P1.11 | Entrypoint purity tests | `tests/governance/test_apps_repo_brief_*.py` (20 tests) | enforce pure shim | 3k | Not Started |
| P1.12 | W1 integration test | full W1 scope | ensure no regression | 1k | Not Started |
| **W2** | | | | | |
| P2.1 | AG: route consolidation | decision | Author-Gate | 0.5k | Not Started |
| P2.2 | Route registry migration | route + cert_route registries | dual-alias deprecation | 2.5k | Not Started |
| P2.3 | Resolve C0 contradiction | cert_route_registry alignment | remove "template-only" text | 0.5k | Not Started |
| P2.4 | Artifact rename | output paths, orchestrator, run-summary | string literals sweep | 2.5k | Not Started |
| P2.5 | Routing target rename | `exec_brief_assembly`→`repo_brief_assembly` | sweep | 1k | Not Started |
| P2.6 | OTEL dual-span | span emitter | dual window | 1k | Not Started |
| P2.7 | Sibling doc updates | sibling `apps_*` comments | sweep | 2k | Not Started |
| P2.8 | Cache compat schema | `apps_repo_brief/config/cache_compat.yaml` + test | strict-compat | 2k | Not Started |
| P2.9 | PromptBOM creation | `apps_repo_brief/prompt_assembly/prompt_bom.yaml` | S0-R0 slots | 2k | Not Started |
| P2.10 | Prompt registry creation | `apps_repo_brief/config/prompt_registry.yaml` | real template refs | 1.5k | Not Started |
| P2.11 | Real template bodies | 6 template YAML files under `templates/` | no placeholders | 4k | Not Started |
| P2.12 | PA compiler scaffold | `apps_repo_brief/prompt_assembly/repo_brief_pa_compiler.py` | skeleton, full impl W3 | 2k | Not Started |
| **W3** | | | | | |
| P3.1 | AG: C0 depth thresholds | decision | Author-Gate | 0.5k | Not Started |
| P3.2 | AG: prompt template completeness | decision | Author-Gate | 0.5k | Not Started |
| P3.3 | IngestionEngine retirement | remove live-scan; UWG seeder for repo_brief_docs | high blast | 5k | Not Started |
| P3.4 | C0 claim extraction | move `CapabilityExtractionEngine` logic to C0 | logic relocation | 4k | Not Started |
| P3.5 | BriefAssemblyEngine split | PA (prompt) + L2 (render) | layer refactor | 5k | Not Started |
| P3.6 | StyleGate hybrid | L2 repair + Exit gate | AG-decision-driven | 3k | Not Started |
| P3.7 | Authoritative FEC.v1 | `agentic_core/L0_routing/c0_retrieval/repo_brief_final_contract.py` | new contract | 4k | Not Started |
| P3.8 | PA compiler full | `repo_brief_pa_compiler.py` full implementation | CompiledPromptArtifact | 3k | Not Started |
| P3.9 | C0 depth profiles | REPO_BRIEF_{LIGHT,STANDARD,DEEP,BOARD_DOSSIER} | thresholds | 2k | Not Started |
| P3.10 | C0 coverage matrix | BriefingCoverageMatrix schema + selection logic | adaptive sections | 3k | Not Started |
| P3.11 | Source portfolio, claim map, contradiction matrix | new C0 outputs | evidence quality | 4k | Not Started |
| P3.12 | C0 board gates | section coverage, hard-blocks | board-specific | 3k | Not Started |
| P3.13 | Cache strict compat enforcement | runtime check | hard gate | 2k | Not Started |
| P3.14 | W3 contract tests | 44 governance tests | ≥44 new test cases | 5k | Not Started |
| **W4** | | | | | |
| P4.1 | AG: style-gate hybrid placement | decision | Author-Gate | 0.5k | Not Started |
| P4.2 | AG: FEC reframe strategy | decision | Author-Gate | 0.5k | Not Started |
| P4.3 | StyleGate L2 repair | `L2.E4` implementation | same-authority | 2k | Not Started |
| P4.4 | StyleGate Exit gate | Exit check for persistent violations | hard gate | 2k | Not Started |
| P4.5 | Cert projection adapter | `apps_repo_brief/cert/cert_projection_adapter.py` | reframe, not authoritative | 3k | Not Started |
| P4.6 | L2 E1-E5 receipts | receipt definitions + runtime emission | E1-E5 | 2.5k | Not Started |
| P4.7 | Exit v6 checks | board-readiness, citation integrity | X3 logic | 2k | Not Started |
| P4.8 | Negative controls | 25 negative control tests | fail-closed | 3k | Not Started |
| P4.9 | apps_eval dual-scenario verification | both old+new scenarios green | eval harness | 1.5k | Not Started |
| P4.10 | W4 integration | full W4 scope | acceptance | 1k | Not Started |
| **W5** | | | | | |
| P5.1 | AG: shim sunset date | decision | Author-Gate | 0.5k | Not Started |
| P5.2 | Zero-hard-refs gate | `test_no_apps_exec_python_imports_outside_shim` | grep+AST | 1k | Not Started |
| P5.3 | path_constants cleanup | remove `APPS_EXEC_*` | dead-code | 1k | Not Started |
| P5.4 | Registry/inventory cleanup | retire apps_exec rows | dead-code | 1.5k | Not Started |
| P5.5 | Scenario cleanup | remove apps_exec scenarios | removal | 1k | Not Started |
| P5.6 | Archive package | `archives/apps_exec_<ts>/` | git mv | 1k | Not Started |
| P5.7 | Drop dual-OTEL | single span attribute | cleanup | 1k | Not Started |
| P5.8 | Final acceptance | run full acceptance report template | YES/NO | 1k | Not Started |

---

## 20. Acceptance Criteria (Merged Checklist)

Plan 3 is **complete** only when all of the following are true:

### 20.1 Plan Completeness
- [x] Full dependency impact report (Plan 1 preserved)
- [x] Full canonical spine target (Plan 2 adapted)
- [x] Rename strategy with phased compatibility shim
- [x] Entrypoint purity requirements with 20 governance tests
- [x] Core-owned route/capability resolution
- [x] C0 authoritative FEC before PA/L2
- [x] `repo_brief_docs` L4 retrieval surface
- [x] Adaptive coverage matrix
- [x] Claim evidence map
- [x] Contradiction matrix
- [x] Freshness report
- [x] Source portfolio summary
- [x] Synthesis guidance for PA
- [x] PromptBOM (S0-R0 slots)
- [x] Prompt registry
- [x] Real prompt template bodies (6 templates)
- [x] No ad hoc prompt string tests
- [x] CompiledPromptArtifact requirement
- [x] L2 E1-E5 receipts
- [x] Cert projection adapter reframe (not authoritative FEC)
- [x] Exit v6 exactly one X3
- [x] L6 after-runtime only
- [x] UWG as only durable write path
- [x] Cache strict compatibility
- [x] Board `template_only` blocked from full brief
- [x] Semantic cache board terminal return blocked unless strict compat
- [x] 44 tests to add/update (24 PA + 20 spine/C0)
- [x] 25 negative controls
- [x] P4 zero hard import gate
- [x] ADG hotspot and graph-layer evidence
- [x] Final acceptance report template

### 20.2 Implementation Acceptance (Post-Implementation)
- [ ] `apps_repo_brief` aligned to canonical spine
- [ ] `apps_repo_brief` aligned to Prompt Assembly standard
- [ ] `apps_repo_brief` aligned to C0 briefing-grade repo retrieval standard
- [ ] Zero off-spine bypasses
- [ ] Zero pre-C0 retrieval/assembly
- [ ] Authoritative FEC at C0
- [ ] No template-only full board brief
- [ ] No semantic cache stale board return
- [ ] No ad hoc prompt strings
- [ ] No placeholder templates
- [ ] No provider call without CompiledPromptArtifact
- [ ] No L6 current-run mutation
- [ ] No durable write outside UWG
- [ ] `apps_eval` green throughout
- [ ] P4 gate: zero `import apps_exec` outside shim

---

## 21. Final Acceptance Report Template

```markdown
## apps_repo_brief Acceptance Report

### Files Changed
- List all modified files with line counts

### Files Created
- List all new files with purpose

### Tests Added
- List 44 governance tests with pass/fail status

### Commands to Run
```bash
python -m pytest tests/governance/test_apps_repo_brief_*.py -v
python -m pytest tests/_apps_contract/test_repo_brief_*.py -v
python ops_scripts/ci/check_app_domain_harness_parity.py
python tools/analysis/apps_spine_coverage.py --app=apps_repo_brief
```

### Static Proof Expected
- Entrypoint imports only agentic_core runner
- No direct C0/PA/L2/L4/Exit/L6 imports in __main__
- Prompt templates exist with input_contract, forbidden_behaviors, hash_fields
- C0 depth profiles defined with source/citation floors
- Route registry has ONE canonical route
- cache_compat.yaml with strict compatibility schema

### Runtime Proof Expected
- 20 entrypoint governance tests pass
- 24 PA tests pass
- 20 C0/spine tests pass
- 25 negative controls fail closed
- apps_eval scenarios green (both old and new during transition)
- OTEL spans show correct layer sequence

### ADG Proof Expected
- `apps_repo_brief/__main__.py` node has zero inbound import edges (pure shim)
- `apps_repo_brief/reasoning/` has no direct `IngestionEngine` calls
- C0 layer shows `FinalEvidenceContract.v1` emission edge
- PA layer shows `CompiledPromptArtifact` emission edge
- No L4 write edges from apps_repo_brief layer

### Passing Evidence
- <attach test output>
- <attach ADG blast radius report>
- <attach spine coverage scanner output>

### Failing Evidence (if any)
- <list any failures with RCA>

### Remaining Gaps
- <list any deferred scope with DEFERRED_SCOPE markers>

### Final YES/NO
**"Is apps_repo_brief aligned to the canonical agentic_core spine, Prompt Assembly standard, and C0 briefing-grade repo retrieval standard?"**

Allowed answers:
- **YES** — static and runtime proof both pass
- **NO, static incomplete** — runtime path exists but static scanner visibility incomplete
- **NO, runtime incomplete** — static proof passes but runtime proof incomplete
- **NO, off-spine bypasses remain** — apps_repo_brief has off-spine paths
- **NO, PA standard incomplete** — templates are placeholders or ad hoc strings remain
- **NO, C0 standard incomplete** — depth profiles missing or pre-C0 work remains
- **NO, dependency migration incomplete** — hard apps_exec imports remain outside shim
- **NO, insufficient evidence** — cannot prove alignment

**Decision:** YES / NO (circle one)
**Date:** ___________
**Reviewer:** ___________
```

---

## 22. Non-Goals (Explicit Exclusion List)

Plan 3 explicitly excludes:
- No broad unrelated refactors outside rename + spine repair scope
- No blind rename without dependency report (already done in Plan 1, verified in W0)
- No premature `apps_exec` deletion before zero-hard-refs gate (W5 only)
- No C0 prose generation (C0 produces evidence contracts only)
- No PA retrieval (PA consumes C0 evidence only)
- No L2 direct L4 writes (all durable writes through UWG)
- No Exit direct L4 writes
- No L6 current-run mutation (L6 is after-runtime only)
- No app HOPs bypassing canonical spine (pre-C0 work removed in W3)
- No `template_only` full board brief (blocked at C0)
- No semantic cache stale board brief terminal return (blocked at L0)
- No provider call without `CompiledPromptArtifact` (blocked at L2)
- No ad hoc prompt strings (all templates registry-defined)
- No placeholder templates (all templates have concrete instruction text)

---

## 23. Author-Gate Queue (Merged & Expanded)

```
AG_QUEUE_SEED: plan=apps-repo-brief-plan3-zero-loss-overwrite id=ag-route-consolidation depends_on= title=Route consolidation (single_step_v1 vs execution_v1 collapse)
AG_QUEUE_SEED: plan=apps-repo-brief-plan3-zero-loss-overwrite id=ag-prompt-template-standard depends_on=ag-route-consolidation title=Prompt template completeness (concrete text vs placeholders)
AG_QUEUE_SEED: plan=apps-repo-brief-plan3-zero-loss-overwrite id=ag-c0-depth-profile-thresholds depends_on=ag-route-consolidation title=C0 depth profile thresholds (source floors, citation floors)
AG_QUEUE_SEED: plan=apps-repo-brief-plan3-zero-loss-overwrite id=ag-style-gate-placement depends_on=ag-prompt-template-standard title=StyleGate placement (L2 same-authority vs Exit hard gate vs hybrid)
AG_QUEUE_SEED: plan=apps-repo-brief-plan3-zero-loss-overwrite id=ag-fec-reframe depends_on=ag-c0-depth-profile-thresholds title=Authoritative-FEC reframe (C0 owns; post-L2 becomes projection adapter)
AG_QUEUE_SEED: plan=apps-repo-brief-plan3-zero-loss-overwrite id=ag-l4-surface-seed depends_on=ag-fec-reframe title=repo_brief_docs L4 surface seeding strategy and fallback policy
AG_QUEUE_SEED: plan=apps-repo-brief-plan3-zero-loss-overwrite id=ag-cache-terminal-policy depends_on=ag-c0-depth-profile-thresholds title=Semantic cache terminal-return policy for board briefs
AG_QUEUE_SEED: plan=apps-repo-brief-plan3-zero-loss-overwrite id=ag-apps-eval-dual-scenario-window depends_on=ag-route-consolidation title=apps_eval dual-scenario maintenance window (when to flip primary)
AG_QUEUE_SEED: plan=apps-repo-brief-plan3-zero-loss-overwrite id=ag-shim-sunset-date depends_on=ag-fec-reframe,ag-style-gate-placement title=apps_exec shim sunset date and gating criteria
AG_QUEUE_SEED: plan=apps-repo-brief-plan3-zero-loss-overwrite id=ag-doc-comment-batch depends_on= title=Doc-comment update batching (per-file vs single bulk pass)
```

---

## 24. ADG Hotspot Report (Plan 1 Preserved)

| Node | Layer | Fan-In | Blast 2-hop | Archetype | Surface | Impact |
|------|-------|--------|-------------|-----------|---------|--------|
| `apps_exec/__main__.py` (id 2635) | L_APP | 0 | 0 | ENTRYPOINT | Execution, Obs | Entrypoint; rename safe |
| `apps_exec.reasoning.ExecOrchestrator` | L_APP | 1 (eval lazy) | bounded by allowlist | ORCHESTRATOR | Execution | SKIP-fallback isolates blast |
| `apps_exec.cert.fec_producer` | L_APP | `apps_shared/cert` consumers | bounded | STATE_NODE (FEC writer) | State, Obs | **W3 hotspot — reframe to projection** |
| `apps_exec.types.exec_types` | L_APP | 8 service tests + scenario_runner | bounded | CENTRAL_DEPENDENCY | Execution | **Highest blast — W1 type re-export required** |
| `apps_exec.spine.exec_spine_adapter` | L_APP | 1 governance test | minimal | ENTRYPOINT | Execution | Clean rename W1 |

**Mitigation:** W1 adds `apps_repo_brief.types.repo_brief_types` re-exporting same names; W2 flips primary; W5 retires legacy.

---

## 25. ADG Graph-Layer Evidence (Constitutional §22)

**Materialized views:**
- `mv_hotspot_centrality` — `apps_exec/__main__.py` near-zero degree (entrypoint terminal)
- `mv_graph_reverse_dependency_hotspots` — top reverse-deps cluster on types module + FEC producer + Orchestrator; drives W1 type-shim
- `mv_graph_chokepoint_bridges` — `apps_shared.integrations.governed_app_runner.GovernedAppRunner` is chokepoint to `agentic_core`; substrate must NOT change, only subclass

**Semantic edges:**
- `flows_to`: `ExecBriefRequest → ExecOrchestrator.run → IngestionEngine → ...` (current pre-C0 flow; W3 collapses to U0/L1)
- `emits_side_effect`: `IngestionEngine` filesystem-read from L_APP (W3: L4 retrieval surface)
- `controls_flow`: `cert_route_registry.invoke_exit_eval=true` controls `_maybe_run_exit_hook`

**P-views:**
- `v_p1_*` (mis-layered) — `apps_exec.engines.{ingestion,capability_extraction,brief_assembly}_engine` as W3 relocation candidates
- `v_p3_*` (isolated experimental) — `apps_exec.engines.hop_*` shims for W1 retirement

---

## 26. AI Summary

- **Target:** Rename `apps_exec` → `apps_repo_brief` + repair canonical spine (U0→L6) + adapt Plan 2 Prompt Assembly/C0 standards
- **Closes:** Naming defect · Pre-C0 HOP pipeline · Post-L2 authoritative FEC anti-pattern · Contradictory route declarations · Template-only board brief risk
- **New files:** `apps_repo_brief/` parallel package (W1), `agentic_core/L0_routing/c0_retrieval/repo_brief_final_contract.py` (W3), `apps_repo_brief/cert/cert_projection_adapter.py` (W4), `apps_repo_brief/prompt_assembly/*` (6 templates, registry, compiler) (W2–W3), `apps_repo_brief/config/cache_compat.yaml` (W2), 44 governance tests (W1–W4), P4 gate test (W5)
- **Edits:** `agentic_core/L0_routing/config/path_constants.py`, `agent_taxonomy_registry.py`, `structure_blueprint/ssot.py`, `apps_shared/spine_emission/context.py`, `scenario_runner.py`, sibling `apps_*` doc comments
- **Pattern:** Merges Plan 1 dependency rigor with Plan 2 spine/prompt/C0 hardening. 6 waves, ~118k tokens, 10 Author-Gate decisions
- **Non-goals:** Broad refactors · blind rename · premature deletion · C0 prose · PA retrieval · L2/Exit L4 writes · L6 mutation · bypasses
- **Success:** Zero cross-app Python breaks · L0 canonical route · R3_SIMPLE_GROUNDED_READ default · C0 mandatory · PA mandatory · L3 off by default · template_only blocked from full board · strict-compat cache · authoritative FEC at C0 · 44 governance tests green · P4 zero-hard-refs gate passes

**PLAN_CREATED:** `.windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md`  
**NEXT:** Notion registration (Plans DB) per §36 before W0 begins.
</thinking>

The user wants a "Plan 3" that merges:
1. Plan 1 (apps-exec-to-repo-brief-rename-d3f8a2.md) — the dependency impact report I just authored
2. Plan 2 — "the detailed apps_research canonical spine, C0, Prompt Assembly, L2, Exit, L6/UWG, and negative-control plan" (which was provided as an example in the user's previous message showing the apps_research clean terminology)

The deliverable is a hardened, deduplicated, zero-loss overwrite plan saved to:
`.windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md`

Key requirements:
- Preserve all valid content from Plan 1 (the 10 defects, dependency matrix, phased migration, etc.)
- Adapt the strongest mechanics from Plan 2 (apps_research spine standard) to apps_repo_brief
- Remove duplication, resolve contradictions
- Create one final SSOT plan
- Do NOT implement — just write the plan file

This is a T3 task (complex multi-file planning). Per AGENTS.md I should use structured reasoning, but the user explicitly said "First deliverable: Only create the Plan 3 markdown file. Do not start implementation until Plan 3 is reviewed and approved."

Given the scope (~200 sections from the prompt), I'll author the comprehensive plan file directly.
