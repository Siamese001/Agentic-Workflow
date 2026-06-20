---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-qna-golden-spine-restoration-a7c8d3.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-qna-golden-spine-restoration-a7c8d3.md'
source_sha256: db37fcf790025c5f61602f855d980f98d3cbaec8e9ba5536a9f8751533c16cc6
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-qna-golden-spine-restoration-a7c8d3
plan_type: refactor
# T3 architectural refactor: cross-layer, >50 files, governance pattern migration
dod_exempt: false
---

# apps_qna Golden-State Spine Restoration

Restore apps_qna to the same golden-state agentic_core spine pattern used for apps_rg, fully customized for Q&A live interview runtime and ChromaDB Interview Card retrieval.

---

## Context (SCQA)

**Situation**: apps_qna currently violates the core architectural invariant that apps_* should be declarative configuration only. It owns runtime authority files (`live_interview_runtime.py`, `exit_wiring.py`, `l0_router.py`, `l1_planner.py`, `c0_adapter.py`, `l2/` folder) that should live in `agentic_core`. The apps_rg golden pattern (plan apps-rg-runtime-wiring-completion-d4e8a1) proved the correct split: apps_* owns config/contracts, agentic_core owns runtime execution via pure-function layer bindings.

**Complication**: apps_qna uses "briefing" terminology throughout, which must be renamed to "Interview Cards" per architectural clarity. It also has local runtime implementations that bypass the core spine pipeline, creating parallel exit paths and potential X3 emission violations. The current structure prevents unified certification, L5 governance, and proper UWG write admission.

**Question**: How do we restore apps_qna to the golden-state pattern while preserving its Q&A domain specialization, ensuring it delegates all runtime authority to agentic_core layer bindings?

**Answer**: Perform a comprehensive refactor across 8 waves: (1) terminology rename briefing→Interview Cards, (2) build runtime_customization_package, (3) create U0/L1/L0/C0/PA/L2/Exit bindings in agentic_core, (4) remove apps_qna runtime authority files, (5) implement Chroma Interview Card retrieval, (6) wire semantic cache, (7) implement 00C runtime gates, (8) produce proof bundle with negative controls.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| apps_rg binding pattern (agentic_core/runtime/*) | Golden-state reference implementation | ✅ Verified |
| apps_qna current structure | Baseline for migration scope | ✅ Cataloged |
| ADG graph-layer evidence | Refactor impact analysis | ✅ Healthy (05102026_1319) |
| ADR-082 apps_* spine taxonomy | Governance pattern authority | ✅ Active |
| plan apps-rg-runtime-wiring-completion-d4e8a1 | Proven implementation pattern | ✅ Completed |

---

## ADG_HOTSPOT_REPORT

| Rank | Node | Archetype | Layer | Violations | Fan-In | Impact Score |
|------|------|-----------|-------|------------|--------|--------------|
| 1 | apps_qna/exit_wiring.py | ORCHESTRATOR | L6-violation | 4 | 3 | 8.0 |
| 2 | apps_qna/live_interview_runtime.py | ORCHESTRATOR | L6-violation | 5 | 2 | 7.5 |
| 3 | apps_qna/l0_router.py | STATE_NODE | L0-violation | 3 | 4 | 6.0 |
| 4 | apps_qna/l1_planner.py | STATE_NODE | L1-violation | 2 | 3 | 4.5 |
| 5 | apps_qna/l2/ | CENTRAL_DEPENDENCY | L2-violation | 4 | 5 | 6.0 |
| 6 | apps_qna/c0_adapter.py | SAFETY_GATEKEEPER | C0-violation | 3 | 2 | 4.5 |

Impact formula: violations × (1 + log10(1 + fan_in)) × multiplier
Layer multipliers: L0/L5 ×2.0, L3/L4 ×1.75, L1/L2 ×1.0, L6 ×0.75

---

## ADG_GRAPH_LAYER_EVIDENCE

**Materialized Views Consulted**:
- `mv_hotspot_centrality`: Confirmed apps_qna runtime files as structural hotspots
- `mv_graph_reverse_dependency_hotspots`: Identified 6 downstream consumers of exit_wiring.py
- `mv_dependency_cone_risk`: Cross-layer violation risk from apps_qna→agentic_core→L4_state

**Semantic Edges**:
- `apps_qna.exit_wiring → emits_side_effect → agentic_core.L4_state.uwg`
- `apps_qna.live_interview_runtime → controls_flow → apps_qna.l0_router`
- `apps_qna.l2.e3_exec → writes_to → agentic_core.L4_state.records`

**P-Views**:
- `v_p1_mislayered_infra`: apps_qna exit_wiring.py (L6 logic in app layer)
- `v_p1_zero_caller_utils`: apps_qna/briefing_validator.py (orphaned post-rename)
- `v_p2_duplicated`: apps_qna l0/l1/l2 vs agentic_core layer bindings

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 0 | Baseline audit | Verify ADG health, catalog current state, confirm apps_rg pattern | Pre-flight | ~5K 🔲 |
| Wave 1 | Terminology rename | briefing→Interview Cards across 15+ files | Terminology clean | ~15K 🔲 |
| Wave 2 | Runtime package | Build apps_qna runtime_customization_package.live_interview_answer.v1.json | Package valid | ~12K 🔲 |
| Wave 3 | Layer bindings | Create 7 agentic_core bindings (U0/L1/L0/C0/PA/L2/Exit) | Bindings compile | ~25K 🔲 |
| Wave 4 | Authority removal | Delete apps_qna runtime files (exit_wiring.py, l0_router.py, l1_planner.py, l2/, c0_adapter.py, live_interview_runtime.py) | No local runtime | ~10K 🔲 |
| Wave 5 | Chroma retrieval | Implement agentic_core/C0_context/apps_qna_interview_card_retriever.py with 7 collection support | Retrieval working | ~20K 🔲 |
| Wave 6 | Semantic cache | Wire R1B cache with strict-gated policy | Cache strict | ~10K 🔲 |
| Wave 7 | 00C gates | Implement stage-mapped runtime gates (G01-G29) | Gates emitting | ~15K 🔲 |
| Wave 8 | Proof bundle | E2E tests, negative controls, certification artifacts | All tests green | ~18K 🔲 |

**Total: ~130K tokens across 8 waves**

---

## Out Of Scope

- Real LLM inference logic (uses stub/echo for testing per apps_rg pattern)
- Production ChromaDB data migration (handled in separate ingestion plan)
- apps_qna build_time_compiler route changes (unchanged)
- apps_eval, apps_lic, apps_rfp, apps_exec changes (separate plans)
- OTel tracing enhancements (separate observability plan)
- L6 meta-learning algorithm improvements (future run only)

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Terminology inventory | Catalog all briefing references | PP-1: string search vs ADG | ~3K | 🔲 TODO |
| 1.2 | Rename implementation | 15 files: briefing→Interview Cards | PP-2: contract shape changes | ~12K | 🔲 TODO |
| 2.1 | Runtime package schema | Define 27-field customization package | PP-3: cross-layer refs | ~6K | 🔲 TODO |
| 2.2 | Package validation | Tests + receipt generation | PP-4: digest chain | ~6K | 🔲 TODO |
| 3.1 | U0 binding | agentic_core/runtime/entry/u0_apps_qna_binding.py | PP-5: ingress validation | ~4K | 🔲 TODO |
| 3.2 | L1 binding | agentic_core/L1_cognition/apps_qna_l1_binding.py | PP-6: planning hints | ~4K | 🔲 TODO |
| 3.3 | L0 binding | agentic_core/L0_routing/apps_qna_l0_binding.py | PP-7: route ordering | ~4K | 🔲 TODO |
| 3.4 | C0 binding | agentic_core/runtime/c0/apps_qna_c0_binding.py | PP-8: Chroma profile | ~5K | 🔲 TODO |
| 3.5 | PA binding | agentic_core/prompt_governance/apps_qna_pa_binding.py | PP-9: 8-slot order | ~4K | 🔲 TODO |
| 3.6 | L2 binding | agentic_core/L2_execution/apps_qna_l2_binding.py | PP-10: bounded packet | ~4K | 🔲 TODO |
| 3.7 | Exit binding | agentic_core/runtime/exit/apps_qna_exit_binding.py | PP-11: X3 singularity | ~4K | 🔲 TODO |
| 4.1 | Runtime file removal | Delete 6 runtime authority files | PP-12: import cleanup | ~5K | 🔲 TODO |
| 4.2 | __main__.py rewire | Delegate to core dispatch | PP-13: backwards compat | ~5K | 🔲 TODO |
| 5.1 | Retriever implementation | C0 Interview Card retriever | PP-14: 7 collections | ~12K | 🔲 TODO |
| 5.2 | Evidence contract | FinalInterviewCardEvidenceContract | PP-15: contract chain | ~8K | 🔲 TODO |
| 6.1 | Cache profile | semantic_cache_profile.live_interview_answer.v1.json | PP-16: strict gates | ~5K | 🔲 TODO |
| 6.2 | R1B wiring | L0 semantic cache lookup | PP-17: reuse constraints | ~5K | 🔲 TODO |
| 7.1 | Gate profile | runtime_gate_profile with 29 gate refs | PP-18: stage mapping | ~8K | 🔲 TODO |
| 7.2 | Gate implementations | 00C per-stage emitters | PP-19: GateVerdict shape | ~7K | 🔲 TODO |
| 8.1 | E2E spine tests | Full pipeline integration | PP-20: timing | ~10K | 🔲 TODO |
| 8.2 | Negative controls | Bypass prevention tests | PP-21: evil path coverage | ~8K | 🔲 TODO |

---

## Gap Register

**GAP-1: Runtime authority violation in apps_qna**
- apps_qna/exit_wiring.py emits X3 (should be in agentic_core)
- apps_qna/live_interview_runtime.py orchestrates full pipeline (should be core dispatch)
- Impact: Prevents unified certification, creates parallel governance path

**GAP-2: Terminology inconsistency**
- "briefing" used where "Interview Cards" is architecturally correct
- 47 references across 15 files requiring rename
- Impact: Domain confusion, onboarding friction

**GAP-3: Missing runtime_customization_package**
- No declarative package defining apps_qna runtime parameters
- Core cannot dispatch apps_qna without hardcoded exceptions
- Impact: Violates spine delegation pattern

**GAP-4: No agentic_core layer bindings**
- Missing: U0, L1, L0, C0, PA, L2, Exit bindings for apps_qna
- apps_qna has local implementations instead
- Impact: apps_qna cannot participate in unified spine certification

**GAP-5: Chroma Interview Card retrieval not implemented**
- C0 retrieves generic documents, not Interview Cards
- No support for 7 required collections
- Impact: Evidence quality degradation

**GAP-6: Semantic cache ungated**
- No strict policy for R1B reuse
- Missing reuse constraint enforcement
- Impact: Cache poisoning risk

---

## Definition of Done

| ID | Criterion | Verification |
|----|-----------|--------------|
| DoD-1 | All "briefing" renamed to "Interview Cards" | `grep -r "briefing" apps_qna/ --include="*.py" --include="*.yaml"` returns 0 matches |
| DoD-2 | runtime_customization_package exists and validates | `python -m tests._apps_contract.test_apps_qna_runtime_package` passes |
| DoD-3 | 7 layer bindings exist in agentic_core | All 7 files present, imports clean, no circular deps |
| DoD-4 | apps_qna runtime authority files removed | exit_wiring.py, l0_router.py, l1_planner.py, l2/, c0_adapter.py, live_interview_runtime.py deleted |
| DoD-5 | C0 Interview Card retriever implemented | `python -m tests._apps_contract.test_c0_interview_card_retrieval` passes |
| DoD-6 | Semantic cache strict-gated | R1B only with explicit profile enable, reuse constraints enforced |
| DoD-7 | 00C gates emit GateVerdicts | All 29 gates mapped to stages, consumed by Exit |
| DoD-8 | Exit emits exactly one X3 | `test_exit_x3_singularity` passes, no dual-X3 paths |
| DoD-9 | apps_qna __main__ delegates to core | `python -m apps_qna --help` works, delegates to AppIngressRunner |
| DoD-10 | Full E2E test passes | `pytest tests/_apps_contract/test_apps_qna_e2e_spine.py -v` green |
| DoD-11 | Negative control tests pass | Bypass prevention tests: no direct L4 write, no direct Chroma write, no separate Exit |
| DoD-12 | Proof bundle artifacts generated | 13 receipt files in artifacts/apps_qna/ |

---

## Execution Plan

### Phase 1.1 — Terminology Inventory
**Scope**: Catalog all briefing references across apps_qna

**Commands**:
```bash
# Find all briefing references
grep -r "briefing" apps_qna/ --include="*.py" --include="*.yaml" --include="*.json" --include="*.md" -l

# Count per file
grep -r "briefing" apps_qna/ --include="*.py" -c | sort -t: -k2 -nr
```

**Acceptance**: Complete inventory of 47 references across 15 files

### Phase 1.2 — Terminology Rename
**Scope**: Rename briefing→Interview Cards in all cataloged files

**Key files**:
- apps_qna/briefing_validator.py → apps_qna/interview_cards_validator.py
- apps_qna/types/evidence_contracts.py (UploadedBriefingEvidenceContract → UploadedInterviewCardsEvidenceContract)
- apps_qna/spine_manifest.yaml
- apps_qna/__main__.py (--briefing → --interview-cards)
- All internal variable names: briefing_* → interview_cards_*

**Acceptance**: Zero remaining briefing references, all tests updated

### Phase 2.1 — Runtime Package Schema
**Scope**: Define 27-field runtime customization package

**File**: apps_qna/config/domain_contract/runtime_customization_package.live_interview_answer.v1.json

**Required fields**:
- package_id, package_version, app_id = apps_qna
- task_class = live_interview_answer
- spine_profile_ref, route_profile_ref, retrieval_profile_ref
- interview_card_schema_ref, interview_card_ingestion_profile_ref
- chroma_retrieval_profile_ref, semantic_cache_profile_ref
- prompt_profile_ref, runtime_gate_profile_ref, exit_profile_ref
- judge_profile_ref, eval_rubric_ref, threshold_profile_ref
- grader_roster_ref, negative_controls_ref
- learning_profile_ref, meta_feedback_profile_ref
- capability_profile_ref, provider_profile_ref
- write_policy, required_runtime_gates, required_exit_gates
- conditional_exit_gates, l5_certification_profile_ref
- l6_learning_policy, package_digest

**Acceptance**: JSON schema validates, digest chain computed

### Phase 2.2 — Package Validation
**Scope**: Tests + receipt generation

**File**: tests/_apps_contract/test_apps_qna_runtime_package.py

**Tests**:
- Package loads and validates
- All 27 fields present
- Cross-references resolve
- Digest reproducible
- Receipt generation

**Acceptance**: 7 tests pass

### Phase 3.1 — U0 Binding
**Scope**: agentic_core/runtime/entry/u0_apps_qna_binding.py

**Function**: u0_validate_apps_qna(envelope: RequestEnvelope) -> ValidatedRequest

**Required**:
- Validate RequestEnvelope
- Check required fields: interview_slug, company, role
- Normalize uploaded_interview_cards path if provided
- Emit ValidatedRequest with reflection_receipt

**Acceptance**: Imports clean, pure function, no I/O beyond envelope

### Phase 3.2 — L1 Binding
**Scope**: agentic_core/L1_cognition/apps_qna_l1_binding.py

**Function**: l1_plan_apps_qna(validated: ValidatedRequest) -> L1PlanContract

**Required hints**:
- normalized_query, question_format, evaluation_dimension
- turn_state, active_card_id, used_card_ids
- target_company, target_role
- ambiguity_register, grounding_required_hint
- interview_card_required_hint
- uploaded_interview_cards_present_hint
- indexed_interview_cards_required_hint
- semantic_cache_allowed_hint

**Prohibited**: routing, retrieval, prompt assembly, execution

**Acceptance**: Emits L1PlanContract, no route selection

### Phase 3.3 — L0 Binding
**Scope**: agentic_core/L0_routing/apps_qna_l0_binding.py

**Function**: l0_route_apps_qna(l1_plan: L1PlanContract) -> RouteContract

**Route order**:
1. R1A exact cache (if enabled and hit)
2. R1B semantic cache (if enabled and valid hit)
3. R5 fallback (missing cards, invalid set)
4. R4_SINGLE_ACTION (default live answer)
5. R3R4_MANAGED_WORKFLOW (card pack build)

**Acceptance**: Exactly one RouteContract emitted, deterministic

### Phase 3.4 — C0 Binding
**Scope**: agentic_core/runtime/c0/apps_qna_c0_binding.py

**Function**: c0_retrieve_apps_qna(route: RouteContract, plan: L1PlanContract) -> FinalInterviewCardEvidenceContract

**Required**:
- Support 7 Chroma collections
- Handle uploaded_interview_cards validation
- Emit FinalInterviewCardEvidenceContract
- Set support_status: PASS, WEAK_WITH_CAVEATS, CONFLICTED, EMPTY, BLOCKED, UNKNOWN

**Prohibited**: answering, routing, prompt assembly, execution

**Acceptance**: Retrieval working, contract valid

### Phase 3.5 — PA Binding
**Scope**: agentic_core/prompt_governance/apps_qna_pa_binding.py

**Function**: pa_compose_apps_qna(plan, route, evidence, l5_refs, prompt_profile_ref, response_schema_ref) -> CompiledPromptArtifact

**Slot order**: S0, D0, I0, E0, C0, M0, U0, H0, R0

**Required**:
- Interview Cards as data, not instructions
- Company overlays cannot rewrite history
- User transcript is intent, not authority
- Output schema bound through R0

**Acceptance**: CompiledPromptArtifact with hash and replay manifest

### Phase 3.6 — L2 Binding
**Scope**: agentic_core/L2_execution/apps_qna_l2_binding.py

**Function**: l2_execute_apps_qn_a(l2_packet: L2ExecutionPacket) -> SealedL2Artifact

**E1 Prep**: Bind route, hashes, replay_key, provider lane
**E2 Valid**: Validate signature chain, L5 refs, runtime gates
**E3 Exec**: Single model invocation, spoken answer from Interview Card evidence only
**E4 Heal**: Schema repair, reformat, one bounded retry
**E5 Seal**: SealedL2Artifact with answer payload, card IDs, telemetry

**Prohibited**: opportunistic retrieval, Chroma writes, cache writes, L4 writes

**Acceptance**: SealedL2Artifact emitted

### Phase 3.7 — Exit Binding
**Scope**: agentic_core/runtime/exit/apps_qna_exit_binding.py

**Function**: exit_finalize_apps_qna(sealed: SealedL2Artifact, ...) -> ExitDispositionReceipt

**X1 checks**:
- X1A Today's Rules
- X1B Answered It
- X1C Safe to Leave
- X1D Answer Good
- X1E Trajectory OK
- X1F Story Adds Up
- X1G Replay Eligible
- X1H Observable
- X1I Consistency (if activated)
- X1J Write Eligibility

**apps_qna-specific checks**:
- correct question_format, turn_state handling
- no disqualified card used
- STAR present when required
- framework answer present when situational
- challenge uses tradeoffs_and_alternatives

**Allowed X3**: X3A_DENY_REROUTE, X3B_ESCALATE_HITL, X3C_COMMIT_REQUEST_TO_UWG, X3D_ALLOW_FINISH, X3E_SAFE_ABSTAIN

**Acceptance**: Exactly one X3 emitted, no dual paths

### Phase 4.1 — Runtime File Removal
**Scope**: Delete apps_qna runtime authority files

**Files to delete**:
- apps_qna/exit_wiring.py
- apps_qna/live_interview_runtime.py
- apps_qna/l0_router.py
- apps_qna/l1_planner.py
- apps_qna/c0_adapter.py
- apps_qna/l2/ (entire directory)

**Files to rename**:
- apps_qna/briefing_validator.py → apps_qna/interview_cards_validator.py

**Acceptance**: Zero runtime authority files remain in apps_qna

### Phase 4.2 — __main__.py Rewire
**Scope**: Delegate to core AppIngressRunner

**New structure**:
- Parse CLI args
- Build RequestEnvelope
- Delegate to agentic_core.runtime.entry.app_ingress_runner.AppIngressRunner
- No local pipeline orchestration

**Acceptance**: `python -m apps_qna --help` works, delegates correctly

### Phase 5.1 — Retriever Implementation
**Scope**: C0 Interview Card retriever

**File**: agentic_core/C0_context/apps_qna_interview_card_retriever.py

**7 collections**:
1. apps_qna_interview_card_retrieval_v1 (routing heads and chunks)
2. apps_qna_interview_card_children_v1 (drill-downs, credibility tests)
3. apps_qna_defense_clarifier_cards_v1 (challenge, pushback)
4. apps_qna_company_overlays_v1 (company fit)
5. apps_qna_role_overlays_v1 (role fit)
6. apps_qna_gap_pivot_cards_v1 (no verified experience)
7. apps_qna_semantic_cache_v1 (R1B only)

**Acceptance**: Retrieves from correct collection based on route context

### Phase 5.2 — Evidence Contract
**Scope**: FinalInterviewCardEvidenceContract

**File**: agentic_core/runtime/contracts/final_interview_card_evidence_contract.py

**Required fields**:
- route_contract_ref, retrieval_plan_ref, query_vec_ref
- chroma_collection_refs, dense_search_refs
- selected_card_refs, selected_overlay_refs
- rejected_card_refs, disqualifier_receipts
- support_status, support_score_profile
- citation_or_payload_lineage_map

**Acceptance**: Contract consumed by PA, digest chain valid

### Phase 6.1 — Cache Profile
**Scope**: Semantic cache profile

**File**: apps_qna/config/domain_contract/semantic_cache_profile.live_interview_answer.v1.json

**Reuse constraints**:
- same_company_required = true
- same_role_required = true
- same_question_format_required = true
- same_turn_state_required = true
- same_policy_hash_required = true
- same_blueprint_hash_required = true
- same_evidence_digest_required = true
- same_prompt_hash_required = true
- not expired

**Acceptance**: Profile validates, disabled by default

### Phase 6.2 — R1B Wiring
**Scope**: L0 semantic cache lookup

**Logic**: Only when profile explicitly enables AND all reuse constraints satisfied

**Acceptance**: Cache hit when valid, miss when constraints violated

### Phase 7.1 — Gate Profile
**Scope**: 00C runtime gate profile

**File**: apps_qna/config/domain_contract/runtime_gate_profile.live_interview_answer.v1.json

**29 gates mapped to stages**:
- U0: G01, G02, G03-lite, G04-lite, G17-lite
- L1: G03, G04, G05, G18
- L0: G07, G08, G10, G20
- C0: G08, G09, G13, G17, G23, G24
- PA: G10, G13, G17, G21, G23
- L3: G18, G19, G20, G25
- L2: G11, G12, G14, G15, G17, G19, G20, G21, G23, G24, G28
- Exit: G21, G22, G23, G24, G25, G26, G27, G28
- UWG: G27, G28
- L6: G28, G29

**Acceptance**: All 29 gates mapped

### Phase 7.2 — Gate Implementations
**Scope**: 00C per-stage emitters

**Logic**: Each stage emits GateVerdicts consumed by Exit

**Acceptance**: UNKNOWN is never PASS, NOT_APPLICABLE requires reason

### Phase 8.1 — E2E Spine Tests
**Scope**: Full pipeline integration

**File**: tests/_apps_contract/test_apps_qna_e2e_spine.py

**Tests**:
- End-to-end live_interview_answer
- End-to-end interview_card_pack_build
- Contract chain verification

**Acceptance**: All tests pass

### Phase 8.2 — Negative Controls
**Scope**: Bypass prevention tests

**Tests**:
- No apps_qna-specific Exit (test_no_separate_exit)
- No X3 emission from apps_qna (test_no_app_x3_emission)
- No direct L4 write (test_no_direct_l4_write)
- No direct Chroma write (test_no_direct_chroma_write)
- No direct semantic cache write (test_no_direct_cache_write)

**Acceptance**: All evil paths blocked

---

## Success Criteria

- [ ] All briefing terminology renamed to Interview Cards
- [ ] runtime_customization_package exists with 27 fields
- [ ] 7 layer bindings in agentic_core compile cleanly
- [ ] apps_qna runtime authority files removed
- [ ] C0 Interview Card retriever supports 7 collections
- [ ] Semantic cache strict-gated (disabled by default)
- [ ] 29 00C gates mapped and emitting GateVerdicts
- [ ] Exit emits exactly one X3
- [ ] __main__.py delegates to core AppIngressRunner
- [ ] E2E tests pass (pytest tests/_apps_contract/test_apps_qna_e2e_spine.py)
- [ ] Negative control tests pass (no bypass possible)
- [ ] 13 proof bundle artifacts generated

---

## Implementation Commands

```bash
# W0: Pre-flight verification
python tools/adg/adg_health.py
python ops_scripts/ci/check_app_domain_harness_parity.py --app apps_qna

# W1: Terminology rename
python tools/refactor/bulk_rename.py --from briefing --to interview_cards --path apps_qna/

# W2: Runtime package validation
python -m tests._apps_contract.test_apps_qna_runtime_package

# W3: Layer binding verification
python -c "from agentic_core.runtime.entry.u0_apps_qna_binding import u0_validate_apps_qna; print('U0 OK')"
python -c "from agentic_core.L1_cognition.apps_qna_l1_binding import l1_plan_apps_qna; print('L1 OK')"
python -c "from agentic_core.L0_routing.apps_qna_l0_binding import l0_route_apps_qna; print('L0 OK')"
python -c "from agentic_core.runtime.c0.apps_qna_c0_binding import c0_retrieve_apps_qna; print('C0 OK')"
python -c "from agentic_core.prompt_governance.apps_qna_pa_binding import pa_compose_apps_qna; print('PA OK')"
python -c "from agentic_core.L2_execution.apps_qna_l2_binding import l2_execute_apps_qna; print('L2 OK')"
python -c "from agentic_core.runtime.exit.apps_qna_exit_binding import exit_finalize_apps_qna; print('Exit OK')"

# W4: File removal verification
ls apps_qna/exit_wiring.py 2>&1 | grep "No such file"
ls apps_qna/live_interview_runtime.py 2>&1 | grep "No such file"
ls apps_qna/l0_router.py 2>&1 | grep "No such file"
ls apps_qna/l1_planner.py 2>&1 | grep "No such file"
ls apps_qna/c0_adapter.py 2>&1 | grep "No such file"
ls apps_qna/l2/ 2>&1 | grep "No such file"

# W5: C0 retriever smoke test
python -m tests._apps_contract.test_c0_interview_card_retrieval

# W6: Semantic cache test
python -m tests._apps_contract.test_semantic_cache_strict_gated

# W7: Gate test
python -m tests._apps_contract.test_runtime_gates_apps_qna

# W8: Full E2E and negative controls
pytest tests/_apps_contract/test_apps_qna_e2e_spine.py -v --tb=short
pytest tests/_apps_contract/test_apps_qna_negative_controls.py -v --tb=short

# Smoke run
python -m apps_qna --help
python -m apps_qna --interview test-slug --company "Test Corp" --role "Test Role" --dry-run
```

---

## Verification vs Deferral

| Component | Verify Now | Defer |
|-----------|------------|-------|
| Terminology rename | ✅ All files | ❌ |
| Runtime package | ✅ Schema + validation | ❌ |
| Layer bindings | ✅ 7 bindings compile | ❌ |
| Runtime file removal | ✅ Delete 6 files | ❌ |
| C0 retriever | ✅ Core retrieval | ❌ |
| Chroma collections | ✅ Schema | Populate with real data |
| Semantic cache | ✅ Strict gating | Performance tuning |
| 00C gates | ✅ 29 mapped | Implementation detail |
| Exit X3 | ✅ Singularity proof | ❌ |
| L6 learning | ✅ Future-run only | Algorithm improvements |
| UWG writes | ✅ Admission path | Production load test |
| E2E tests | ✅ Integration | Load testing |
| Negative controls | ✅ Bypass prevention | ❌ |
| Proof bundle | ✅ 13 artifacts | ❌ |

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Import cycles in layer bindings | Medium | High | Pure functions, no cross-imports between bindings |
| Backward compatibility break | Medium | High | Keep old CLI args, delegate to new path |
| Chroma collection schema mismatch | Low | Medium | Version in metadata, migration script ready |
| Test flakiness after refactor | Medium | Medium | Serial test execution, no xdist for spine tests |
| Runtime performance regression | Low | Medium | Benchmark before/after, optimize post-merge |

---

## References

- apps_rg golden pattern: `agentic_core/runtime/*apps_rg*` files
- Plan apps-rg-runtime-wiring-completion-d4e8a1 (Completed 2026-05-09)
- ADR-082: apps_* spine taxonomy
- docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md
- Constitutional §22: ADG graph-layer primary
- apps_qna current state: `live_interview_runtime.py`, `exit_wiring.py`, `l0_router.py`, `l1_planner.py`, `l2/`, `c0_adapter.py`

---

## Plan Metadata

- Created: 2026-05-11
- Author: Cascade
- Status: Not Started → In Progress (at Wave 1 start)
- Target completion: 8 waves, ~130K tokens
- Blockers: None
- Dependencies: None (apps_rg pattern proven)

PLAN_CREATED: plan=apps-qna-golden-spine-restoration-a7c8d3
