---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-qna-grounded-spine-refactor-f5a2c9.md'
original_relative_path: 'apps-qna-grounded-spine-refactor-f5a2c9.md'
source_sha256: 68246a9d4c3dd1a2ea8338ef809538aea2ec788c18b54f155022dd74d6d6e234
recovered_status: SURVIVED_IN_CURRENT
last_commit: '315fd11926d'
last_commit_date: '2026-05-06 06:26:53 -0400'
created_date: '2026-05-04'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-qna-grounded-spine-refactor-f5a2c9
plan_type: refactor
---

# apps_qna Grounded Spine Refactor

> **SUPERSEDED by**: `apps-qna-grounded-spine-refactor-v2-d7e3a1.md` (Notion: 35627693-f55c-8169-bc80-fd9cd5a2590c)
> 
> This plan contained errors: parallel C0 implementation, fake C0 contract for briefing, invented route enum, ambiguous prompt assembly status, missing W0 thin-slice, UWG/L4 language confusion.
> 
> Use the revised plan (v2) for implementation.

Transform apps_qna from static template compiler to grounded two-tier live interview runtime pack compiler riding the agentic_core spine with C0 grounding, deterministic L2 execution, and proper Exit evaluation.

---

## Context (SCQA)

**Situation** — apps_qna currently operates as a `build_time_compiler` route with `c0_required: false`, producing static 18-card packs via deterministic Jinja2 template rendering. The app claims no runtime LLM calls, no C0 retrieval, and no spine routing at build time. The spine provides only intake validation (`ValidatedRequest`) and UWG-routed writes. The current architecture treats ChatGPT as the external runtime, with apps_qna merely preparing context packs for paste.

**Complication** — The current architecture contradicts the requirement for interviewer-personalized, company-grounded live interview packs. It cannot retrieve interviewer background, validate company claims against sources, or enforce two-tier progressive disclosure routing. It produces generic cards when interviewer-specific cards are required, lacks q-prefix live-mode control enforcement, and has no egress verification to block fake precision or unsupported claims. The semantic cache is advisory-only but not enforced, and L2 writes directly to local filesystem without clear Exit disposition.

**Question** — How do we refactor apps_qna to become a grounded, two-tier live interview runtime pack compiler that correctly rides the agentic_core spine with C0 grounding when no sealed briefing exists, deterministic L2 E1-E5 execution, proper Exit X3 disposition, and L6 post-run evaluation?

**Answer** — A multi-wave refactor introducing: (1) C0-required route model with uploaded briefing bypass; (2) two-tier card architecture (Tier 1 always-on + Tier 2 specialist); (3) deterministic router with single primary route selection; (4) E1-E5 L2 execution mapping; (5) egress verifier blocking unsupported claims; (6) proper Exit disposition; (7) digest-safe R1A exact cache and advisory-only R1B semantic cache; (8) comprehensive test coverage for grounding, routing, live-mode, and egress requirements.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `apps_qna/spine_manifest.yaml` | current route declaration | ✅ |
| `apps_qna/__main__.py` | entrypoint and cert mode | ✅ |
| `apps_qna/builder/card_pack_builder.py` | L2 build implementation | ✅ |
| `apps_qna/integrations/spine_handoff.py` | ValidatedRequest wrapper | ✅ |
| `apps_qna/router/*.py` | routing primitives | ✅ |
| `agentic_core/L0_routing/intake/validated_request.py` | U0/L1 contracts | ✅ |
| `agentic_core/L0_routing/doctrine/route_types.py` | canonical route families | 🔲 |
| `agentic_core/L1_cognition/planning/l1_plan_contract.py` | L1 contract shape | 🔲 |
| `agentic_core/L2_execution/execution_forms.py` | L2 E1-E5 mapping | 🔲 |
| `agentic_core/L3_orchestration/exit_eval/` | Exit X3 disposition | 🔲 |
| ADG SQLite | structural dependencies | 🔲 |

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| W1 | Route model + spine contracts | spine_manifest.yaml, route_registry, __main__.py spine wiring | A | ~45K 🟢 |
| W2 | C0 integration + evidence contracts | C0 client, FEC producer, briefing validation | B | ~38K 🟢 |
| W3 | Two-tier card architecture | Tier 1/2 card specs, router, manifest schema | C | ~52K 🟢 |
| W4 | L2 E1-E5 execution mapping | builder refactor, heal logic, seal logic | D | ~48K 🟢 |
| W5 | Exit + egress verifier | Exit disposition, egress verifier card, blocking rules | E | ~35K 🟢 |
| W6 | Cache strategy + tests | R1A/R1B/R5 implementation, test coverage | F | ~42K 🟢 |
| W7 | Documentation + acceptance | README, RUNBOOK, TECHNICAL_SPEC, spine flow docs | G | ~28K 🟢 |

**Total: ~288K tokens across 7 waves, all GREEN**

---

## Out Of Scope

- Real LLM judge implementations (stubs only, per apps-eval-harness-deferred-e4a1b7)
- Production C0 retrieval backend (assume C0 interface exists, mock for tests)
- Multi-interviewer parallel C0 calls (defer to future orchestration plan)
- ChatGPT 5.5 Thinking API integration (external runtime remains unchanged)
- UWG/L4 durable commit for pack indexing (local filesystem default, UWG optional)
- L6 eval implementation (shadow evaluation skeleton only)
- Archive of old static-only behavior (maintain backward compatibility for non-interview builds)
- Rename public API surfaces unless required for spine correctness
- Broad refactoring of unrelated apps_* modules

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Spine route model redesign | spine_manifest.yaml, route_registry.yaml, cert_route_registry.yaml | GAP-1: current build_time_compiler route denies C0 | ~8K | 🔲 TODO |
| 1.2 | U0/L1/L0 contract wiring | __main__.py, spine_handoff.py, new u0_intake.py, l1_planner.py | GAP-2: missing L1PlanContract emission | ~12K | 🔲 TODO |
| 1.3 | Route selection implementation | l0_router.py, route_contract.py | GAP-3: no deterministic route selection | ~10K | 🔲 TODO |
| 1.4 | Wave 1 verification | tests/test_w1_route_model.py | GAP-4: no route model tests | ~15K | 🔲 TODO |
| 2.1 | C0 client integration | c0_client.py, c0_evidence_contract.py | GAP-5: no C0 grounding capability | ~12K | 🔲 TODO |
| 2.2 | Uploaded briefing validation | briefing_validator.py, briefing_contract.py | GAP-6: no sealed briefing bypass | ~8K | 🔲 TODO |
| 2.3 | FEC producer update | cert/fec_producer.py | GAP-7: FEC doesn't reflect C0 vs briefing | ~6K | 🔲 TODO |
| 2.4 | Wave 2 verification | tests/test_w2_c0_integration.py | | ~12K | 🔲 TODO |
| 3.1 | Tier 1 always-on card spec | card_specs/tier_1.py, templates/tier_1/*.md.j2 | GAP-8: flat card architecture | ~15K | 🔲 TODO |
| 3.2 | Tier 2 specialist card spec | card_specs/tier_2.py, templates/tier_2/*.md.j2 | GAP-9: no specialist triggers | ~18K | 🔲 TODO |
| 3.3 | Two-tier router implementation | two_tier_router.py, route_precedence.py | GAP-10: no primary route enforcement | ~14K | 🔲 TODO |
| 3.4 | CardPackManifest schema update | types/manifest_types.py | GAP-11: manifest lacks tier info | ~5K | 🔲 TODO |
| 3.5 | Wave 3 verification | tests/test_w3_two_tier_routing.py | | ~15K | 🔲 TODO |
| 4.1 | E1 Prep implementation | l2/e1_prep.py | GAP-12: no E1-E5 mapping | ~8K | 🔲 TODO |
| 4.2 | E2 Valid implementation | l2/e2_valid.py | GAP-13: weak validation | ~10K | 🔲 TODO |
| 4.3 | E3 Exec implementation | l2/e3_exec.py, builder refactor | GAP-14: no deterministic exec stages | ~12K | 🔲 TODO |
| 4.4 | E4 Heal implementation | l2/e4_heal.py | GAP-15: no healing boundaries | ~8K | 🔲 TODO |
| 4.5 | E5 Seal implementation | l2/e5_seal.py | GAP-16: no seal contract | ~10K | 🔲 TODO |
| 4.6 | Wave 4 verification | tests/test_w4_l2_execution.py | | ~15K | 🔲 TODO |
| 5.1 | Exit X3 disposition wiring | exit_eval_wiring.py, x3_disposition.py | GAP-17: no Exit disposition | ~10K | 🔲 TODO |
| 5.2 | Egress verifier card | templates/tier_1/00a_egress_verifier.md.j2 | GAP-18: no egress verification | ~8K | 🔲 TODO |
| 5.3 | Blocking rules implementation | egress/blocking_rules.py | GAP-19: no fake precision blocking | ~10K | 🔲 TODO |
| 5.4 | Wave 5 verification | tests/test_w5_exit_egress.py | | ~12K | 🔲 TODO |
| 6.1 | R1A exact cache | cache/r1a_exact.py | GAP-20: no digest-safe cache | ~10K | 🔲 TODO |
| 6.2 | R1B semantic cache | cache/r1b_semantic.py | GAP-21: semantic cache not advisory | ~8K | 🔲 TODO |
| 6.3 | R5 fallback | cache/r5_fallback.py | GAP-22: no degraded fallback | ~6K | 🔲 TODO |
| 6.4 | Comprehensive test suite | tests/test_*.py updates | GAP-23: insufficient coverage | ~28K | 🔲 TODO |
| 6.5 | Blend360/Steven fixture | tests/fixtures/blend360_steven_fixture.py | | ~8K | 🔲 TODO |
| 7.1 | README update | README.md | GAP-24: outdated docs | ~8K | 🔲 TODO |
| 7.2 | RUNBOOK spine flow | RUNBOOK.md spine section | GAP-25: no spine flow docs | ~6K | 🔲 TODO |
| 7.3 | TECHNICAL_SPEC update | TECHNICAL_SPEC.md | GAP-26: spec outdated | ~8K | 🔲 TODO |
| 7.4 | ASCII spine flow diagram | docs/spine_flow.md | GAP-27: no visual spine flow | ~6K | 🔲 TODO |
| 7.5 | Acceptance verification | final acceptance check | | ~12K | 🔲 TODO |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1: Current route denies C0 grounding**
- `spine_manifest.yaml` declares `build_time_compiler` with `c0_required: false`
- This contradicts requirement for interviewer/company grounding
- Impact: Cannot retrieve interviewer evidence, validate company claims

**GAP-2: Missing L1PlanContract emission**
- Current `spine_handoff.py` only emits `ValidatedRequest`
- No L1 planning stage that declares C0 requirements
- Impact: No spine-correct plan-before-route discipline

**GAP-3: No deterministic route selection**
- Current routing is implicit via template selection
- No explicit `RouteContract` with `route_family`, `route_id`, `execution_form`
- Impact: Cannot enforce R3_PLUS_R4_GROUNDED_SINGLE_ACTION vs R4_SINGLE_ACTION distinction

**GAP-4: No route model tests**
- Existing tests verify template rendering, not spine routing
- Missing coverage for route selection, C0 requirements, Exit disposition
- Impact: Cannot verify spine correctness

**GAP-5: No C0 grounding capability**
- No C0 client integration in apps_qna
- Cannot retrieve interviewer background, company context
- Impact: Cannot produce grounded packs for live interviews

**GAP-6: No sealed briefing bypass**
- No validation for uploaded briefing packets
- No path to bypass C0 when briefing passes sufficiency checks
- Impact: Cannot support pre-researched briefing workflows

**GAP-7: FEC doesn't reflect C0 vs briefing**
- Current `fec_producer.py` returns `grounded: false`, empty `retrieval_sources`
- Doesn't distinguish C0-retrieved vs uploaded-briefing evidence
- Impact: Exit evaluation cannot assess evidence provenance

**GAP-8: Flat card architecture**
- Current 18-card flat pack loads all cards
- No Tier 1/Tier 2 distinction
- Impact: Context bloat, overfire of specialist cards

**GAP-9: No specialist triggers**
- Specialist cards lack explicit trigger rules
- No deterministic routing based on q-prefix intent
- Impact: Cannot enforce progressive disclosure

**GAP-10: No primary route enforcement**
- No mechanism to select exactly one primary specialist route
- Support card rules not implemented
- Impact: Multiple routes fire, overfire occurs

**GAP-11: Manifest lacks tier info**
- `CardPackManifest` doesn't track Tier 1 vs Tier 2 cards
- No `primary_route_candidate`, `support_card_candidate` flags
- Impact: Cannot verify two-tier architecture

**GAP-12: No E1-E5 mapping**
- Current `card_pack_builder.py` doesn't map to canonical L2 stages
- No explicit Prep, Valid, Exec, Heal, Seal phases
- Impact: Not spine-correct L2 execution

**GAP-13: Weak validation**
- Validation exists but not mapped to E2 Valid stage
- No evidence sufficiency checks
- Impact: May build with weak/missing evidence

**GAP-14: No deterministic exec stages**
- Build is monolithic, not staged
- No clear boundaries between prep, validation, execution
- Impact: Cannot audit or heal at stage boundaries

**GAP-15: No healing boundaries**
- No E4 Heal stage with clear repair permissions
- Risk of inventing facts during healing
- Impact: May violate evidence integrity

**GAP-16: No seal contract**
- Manifest is written but not as sealed L2 artifact
- No clear handoff to Exit
- Impact: Exit cannot verify sealed state

**GAP-17: No Exit disposition**
- Current flow lacks Exit X1/X2/X3 stage
- No `ALLOW_FINISH`, `SAFE_ABSTAIN`, `REROUTE`, `ESCALATE_HITL` disposition
- Impact: No runtime control or human escalation path

**GAP-18: No egress verification**
- No card blocking fake precision, unsupported claims
- No verification of internal label absence
- Impact: Quality escapes, internal leaks

**GAP-19: No fake precision blocking**
- No enforcement of measurement categories vs exact numbers
- No blocking of invented metrics
- Impact: Unsupported claims in output

**GAP-20: No digest-safe cache**
- No R1A exact cache implementation
- Risk of stale pack reuse
- Impact: Wrong interviewer pack returned

**GAP-21: Semantic cache not advisory**
- R1B semantic cache behavior undefined
- Risk of silent wrong-pack return
- Impact: Interviewer mismatch

**GAP-22: No degraded fallback**
- No R5 fallback for emergency scenarios
- No degraded pack path
- Impact: No graceful degradation

**GAP-23: Insufficient coverage**
- Current tests don't cover grounding, routing, live-mode, egress
- Missing Blend360/Steven fixture
- Impact: Cannot verify refactor correctness

**GAP-24: Outdated docs**
- `README.md` describes static template compiler
- Doesn't reflect grounded runtime pack compiler target
- Impact: Misleading documentation

**GAP-25: No spine flow docs**
- No ASCII diagram showing U0->L1->L0->C0->L2->Exit flow
- No explanation of spine ownership
- Impact: Hard to understand architecture

**GAP-26: Spec outdated**
- `TECHNICAL_SPEC.md` describes old architecture
- No two-tier routing, egress verifier, C0 integration
- Impact: Implementation guide is wrong

**GAP-27: No visual spine flow**
- No standalone `spine_flow.md` with ASCII diagram
- No end-to-end ownership explanation
- Impact: Onboarding difficulty

---

## Execution Plan

### Phase 1.1 — Spine Route Model Redesign
**Scope**: Replace `build_time_compiler` with `R3_PLUS_R4_GROUNDED_SINGLE_ACTION` and `R4_SINGLE_ACTION` routes, update registries

**Files**:
- `apps_qna/spine_manifest.yaml` — new route declarations
- `apps_qna/config/route_registry.yaml` — route definitions
- `apps_qna/config/cert_route_registry.yaml` — cert route updates
- `apps_qna/config/domain_contract/` — new contract YAMLs

**Changes**:
1. Update `spine_manifest.yaml` with two route types:
   - `R3_PLUS_R4_GROUNDED_SINGLE_ACTION` — normal grounded build
   - `R4_SINGLE_ACTION` — uploaded briefing bypass
2. Define `route_id: apps_qna.live_interview_runtime_pack_v1`
3. Define `route_id: apps_qna.live_interview_runtime_pack_from_uploaded_brief_v1`
4. Set `c0_required: true` for grounded route
5. Set `c0_required: false` for briefing route
6. Set `execution_form: SINGLE_STEP` for both
7. Set `l3_required: false` for both
8. Update contract requirements per route

**Acceptance**:
- `spine_manifest.yaml` validates against schema
- Both routes declare correct spine ownership
- `c0_required` reflects evidence requirements

### Phase 1.2 — U0/L1/L0 Contract Wiring
**Scope**: Implement U0 intake, L1 planning, L0 routing with proper contracts

**Files**:
- `apps_qna/u0_intake.py` — new U0 implementation
- `apps_qna/l1_planner.py` — new L1 implementation
- `apps_qna/l0_router.py` — new L0 implementation
- `apps_qna/__main__.py` — wire to spine
- `apps_qna/types/spine_contracts.py` — contract types

**Changes**:
1. Create `u0_intake.py` with `ValidatedRequest` emission:
   - CLI/input envelope validation
   - Interview slug, company, role, interviewer capture
   - Optional briefing packet handling
   - Request ID, trace root stamping
2. Create `l1_planner.py` with `L1PlanContract` emission:
   - Task interpretation as live pack build
   - C0 requirement declaration
   - Briefing sufficiency requirements
   - Route recommendation (not selection)
3. Create `l0_router.py` with `RouteContract` emission:
   - Deterministic route selection
   - Cache decision (R1A/R1B/R5)
   - Route family, execution form, side effect class
4. Update `__main__.py` to wire U0->L1->L0 before C0/L2
5. Create `types/spine_contracts.py` for contract dataclasses

**Acceptance**:
- U0 emits `ValidatedRequest` with all required fields
- L1 emits `L1PlanContract` with C0 requirement declared
- L0 emits exactly one `RouteContract`
- Contracts validate against canonical shapes

### Phase 1.3 — Route Selection Implementation
**Scope**: Implement cache decision logic and route selection

**Files**:
- `apps_qna/l0_router.py` — route selection logic
- `apps_qna/cache/decision.py` — cache decision module
- `apps_qna/briefing/validator.py` — briefing validation

**Changes**:
1. Implement cache decision in L0:
   - Check R1A exact cache (full digest match)
   - Check R1B semantic cache (advisory only)
   - Determine R5 fallback eligibility
2. Implement briefing validation:
   - Hash validation
   - Staleness check
   - Sufficiency verification
3. Route selection logic:
   - If briefing passes → `R4_SINGLE_ACTION`
   - If briefing fails/missing and C0 enabled → `R3_PLUS_R4_GROUNDED_SINGLE_ACTION`
   - If briefing fails and C0 disabled → Exit disposition

**Acceptance**:
- Cache decision considers all material digests
- Briefing validation rejects stale/invalid packets
- Route selection is deterministic and logged

### Phase 1.4 — Wave 1 Verification
**Scope**: Add tests for route model

**Files**:
- `tests/test_w1_route_model.py` — new test file
- `tests/fixtures/routes.py` — route fixtures

**Acceptance**:
- Tests cover both route types
- Tests verify C0 requirement per route
- Tests verify cache decision logic
- All Wave 1 tests pass

### Phase 2.1 — C0 Client Integration
**Scope**: Implement C0 grounding client

**Files**:
- `apps_qna/c0_client.py` — C0 client implementation
- `apps_qna/types/c0_contracts.py` — C0 contract types
- `apps_qna/c0/shaper.py` — evidence shaping
- `apps_qna/c0/verifier.py` — evidence verification

**Changes**:
1. Create `c0_client.py`:
   - Interviewer/company/role evidence retrieval
   - Source register construction
   - Freshness report
   - Contradiction detection
2. Implement evidence requirements:
   - Public profile or credible bio
   - Role/company relevance
   - Public writing/speaking material
   - Explicit "no public material found" statement
3. Create `FinalEvidenceContract` with:
   - `evidence_status`: PASS|WEAK|WEAK_WITH_CAVEATS|CONFLICTED|EMPTY|BLOCKED
   - `source_refs`, `source_authority`, `freshness`
   - `support_score`, `unsupported_gaps`
   - `allowed_personalization_hooks`, `prohibited_personalization_hooks`
   - `per_interviewer_coverage`
4. Fail-soft on C0 errors with `evidence_status: BLOCKED`

**Acceptance**:
- C0 client retrieves interviewer evidence
- Evidence contract includes all required fields
- Weak evidence is flagged, not hidden
- C0 errors result in BLOCKED status

### Phase 2.2 — Uploaded Briefing Validation
**Scope**: Implement sealed briefing packet validation

**Files**:
- `apps_qna/briefing/validator.py` — briefing validation
- `apps_qna/briefing/contract.py` — briefing contract
- `apps_qna/briefing/loader.py` — briefing loader

**Changes**:
1. Create briefing validation:
   - Hash verification (SHA-256)
   - Schema validation
   - Staleness check (timestamp vs max_age)
   - Sufficiency validation:
     - Interviewer coverage
     - Company context presence
     - Source register presence
2. Create `BriefingContract`:
   - `briefing_hash`, `created_at`, `max_age`
   - `interviewer_coverage[]`
   - `source_register_ref`
   - `evidence_sufficiency`: SUFFICIENT|STALE|INCOMPLETE|MISMATCH
3. Briefing bypass decision:
   - SUFFICIENT → bypass C0
   - Other → require C0 or Exit

**Acceptance**:
- Briefing validation rejects stale packets
- Sufficiency checks verify interviewer coverage
- Bypass decision is explicit and logged

### Phase 2.3 — FEC Producer Update
**Scope**: Update FEC producer to reflect C0 vs briefing provenance

**Files**:
- `apps_qna/cert/fec_producer.py` — update FEC shape

**Changes**:
1. Update `produce_fec()` to include:
   - `grounded: true` when C0 or briefing provides evidence
   - `retrieval_sources`: C0 sources or briefing sources
   - `evidence_sufficiency`: `grounded` | `uploaded_briefing` | `template`
   - `briefing_ref` when briefing used
   - `c0_ref` when C0 used
2. Distinguish evidence provenance in FEC

**Acceptance**:
- FEC reflects C0-grounded vs briefing-grounded vs template-only
- `retrieval_sources` populated correctly
- `evidence_sufficiency` accurate

### Phase 2.4 — Wave 2 Verification
**Scope**: Add tests for C0 and briefing integration

**Files**:
- `tests/test_w2_c0_integration.py` — C0 tests
- `tests/test_w2_briefing.py` — briefing tests
- `tests/fixtures/c0_responses.py` — C0 fixtures
- `tests/fixtures/briefings.py` — briefing fixtures

**Acceptance**:
- C0 retrieval tests pass
- Briefing validation tests pass
- FEC producer tests verify provenance
- Mock C0 client for tests

### Phase 3.1 — Tier 1 Always-On Card Spec
**Scope**: Define and implement Tier 1 always-on cards

**Files**:
- `apps_qna/card_specs/tier_1.py` — Tier 1 specifications
- `apps_qna/templates/tier_1/00_start_here_runtime_root.md.j2` — new template
- `apps_qna/templates/tier_1/00a_source_set_and_egress_verifier.md.j2` — new template
- `apps_qna/templates/tier_1/01_card_selection_manifest.md.j2` — new template
- `apps_qna/templates/tier_1/03_interviewer_lens_and_company_bridge.md.j2` — updated

**Changes**:
1. Create Tier 1 card specifications:
   - `00_START_HERE_RUNTIME_ROOT.md` — live mode gate, q-prefix behavior
   - `00A_SOURCE_SET_AND_EGRESS_VERIFIER.md` — egress verification
   - `01_CARD_SELECTION_MANIFEST.md` — deterministic routing
   - `03_INTERVIEWER_LENS_AND_COMPANY_BRIDGE.md` — relevance bridge
2. Each card has:
   - Frontmatter with `card_id`, `tier: 1`, `always_on: true`
   - Trigger description
   - Answer shape specification
   - Readout realism rules
3. Update existing templates to Tier 1 semantics

**Acceptance**:
- Tier 1 cards have correct frontmatter
- Always-on semantics defined
- Templates render correctly

### Phase 3.2 — Tier 2 Specialist Card Spec
**Scope**: Define and implement Tier 2 specialist cards with triggers

**Files**:
- `apps_qna/card_specs/tier_2.py` — Tier 2 specifications
- `apps_qna/templates/tier_2/` — specialist templates directory
- Individual specialist card templates:
  - `star_proof.md.j2`
  - `star_failure_learning.md.j2`
  - `rag_context.md.j2`
  - `governance_hitl.md.j2`
  - `tools_mcp_gateway.md.j2`
  - `agentic_architecture.md.j2`
  - `ds_to_platform.md.j2`
  - `platform_productization.md.j2`
  - `client_advisory_roi.md.j2`
  - `role_scope_mandate.md.j2`
  - `exec_translation_fit.md.j2`
  - `cross_exam_depth.md.j2`

**Changes**:
1. Create Tier 2 card specifications:
   - Each card has `card_id`, `tier: 2`, `always_on: false`
   - Explicit trigger rules
   - Hard gates (when NOT to fire)
   - Primary route candidate flag
   - Support card candidate flag
2. Define route precedence:
   - Failure/learning beats all
   - Proof beats concept
   - Role scope beats generic fit
   - RAG beats generic architecture when relevant
   - Governance beats tools when risk appears
3. Cards include:
   - Purpose
   - Trigger rules
   - Hard gates
   - Answer shape
   - Failure patterns
   - Minimal examples
   - Readout realism rules

**Acceptance**:
- All 12 specialist cards defined
- Trigger rules specific enough to prevent overfire
- Route precedence documented

### Phase 3.3 — Two-Tier Router Implementation
**Scope**: Implement deterministic router with single primary route selection

**Files**:
- `apps_qna/router/two_tier_router.py` — main router
- `apps_qna/router/route_precedence.py` — precedence rules
- `apps_qna/router/intent_classifier.py` — intent classification
- `apps_qna/router/card_selector.py` — card selection logic

**Changes**:
1. Create `two_tier_router.py`:
   - Consumes C0 evidence or briefing evidence
   - Classifies intent from q-prefix prompt
   - Applies route precedence rules
   - Selects exactly one primary specialist route
   - Selects support cards per budget rules
   - Emits `CardSelectionManifest`
2. Implement route precedence (per §7 requirements)
3. Card budget enforcement:
   - Concept: Tier 1 + 1 specialist
   - STAR: Tier 1 + STAR + optional support
   - Failure STAR: Tier 1 + STAR + recovery + optional support
   - Cross-exam: recovery + current specialist

**Acceptance**:
- Router selects exactly one primary route
- Support cards follow budget rules
- Route precedence enforced
- Card overfire detected and blocked

### Phase 3.4 — CardPackManifest Schema Update
**Scope**: Update manifest to track tier information

**Files**:
- `apps_qna/types/manifest_types.py` — updated manifest types
- `apps_qna/types/card_entry.py` — card entry type

**Changes**:
1. Update `CardPackManifest`:
   - Add `tier_1_cards[]`, `tier_2_cards[]`
   - Add `passive_overlay_card` ref
   - Add `router_card` ref
   - Add `egress_verifier_card` ref
   - Add `card_budget_report_ref`
   - Add `unsupported_claim_blocklist_ref`
2. Update card entries:
   - Add `tier`, `always_on`, `passive_context`
   - Add `primary_route_candidate`, `support_card_candidate`
   - Add `route_tags[]`, `trigger_description`
   - Add `source_evidence_refs[]`

**Acceptance**:
- Manifest includes all tier-related fields
- Card entries have complete metadata
- Schema validates

### Phase 3.5 — Wave 3 Verification
**Scope**: Add tests for two-tier routing

**Files**:
- `tests/test_w3_two_tier_routing.py` — routing tests
- `tests/fixtures/routes.py` — route fixtures

**Acceptance**:
- Tier 1 always-on cards loaded
- Specialist cards not always-on
- Exactly one primary route selected
- Card budget enforced
- Overfire detected

### Phase 4.1 — E1 Prep Implementation
**Scope**: Implement E1 Prep stage

**Files**:
- `apps_qna/l2/e1_prep.py` — E1 implementation

**Changes**:
1. Create `e1_prep.py`:
   - Freeze interview config
   - Freeze template registry refs
   - Freeze C0 evidence or briefing refs
   - Freeze source register refs
   - Bind `policy_hash`, `blueprint_hash`, `replay_key`, `route_id`, `template_version`
   - Compute input digest
   - Create build workspace
2. Emit E1 completion marker

**Acceptance**:
- All refs frozen at E1
- Input digest computed
- Build workspace created
- E1 marker emitted

### Phase 4.2 — E2 Valid Implementation
**Scope**: Implement E2 Valid stage

**Files**:
- `apps_qna/l2/e2_valid.py` — E2 implementation

**Changes**:
1. Create `e2_valid.py`:
   - Validate interview YAML/schema
   - Validate company, role, interviewer set
   - Validate C0 evidence sufficiency OR uploaded briefing sufficiency
   - Validate no unsupported personalization hooks
   - Validate template availability
   - Validate route manifest coverage
   - Validate target overlay length budget
   - Validate no old card collision
   - Validate card count and specialist triggers
   - Validate no generic fallback when interviewer-specific required
2. On validation failure → sealed error packet → Exit disposition

**Acceptance**:
- All validation checks implemented
- Evidence sufficiency verified
- Validation failures emit sealed packet
- E2 marker emitted on success

### Phase 4.3 — E3 Exec Implementation
**Scope**: Implement E3 Exec stage

**Files**:
- `apps_qna/l2/e3_exec.py` — E3 implementation
- `apps_qna/builder/tiered_builder.py` — tiered builder

**Changes**:
1. Create `e3_exec.py`:
   - Render Tier 1 always-on cards
   - Render Tier 2 specialist cards (via router selection)
   - Render target overlay (from C0 or briefing)
   - Render card selection manifest
   - Render routing evals
   - Stage output under `reports/qna/<slug>/`
2. Refactor builder to tiered execution:
   - Separate Tier 1 and Tier 2 render passes
   - Router-driven specialist selection
   - Overlay generation from evidence

**Acceptance**:
- Tier 1 cards rendered first
- Specialist cards selected by router
- Overlay generated from evidence
- Output staged correctly
- E3 marker emitted

### Phase 4.4 — E4 Heal Implementation
**Scope**: Implement E4 Heal stage with repair boundaries

**Files**:
- `apps_qna/l2/e4_heal.py` — E4 implementation

**Changes**:
1. Create `e4_heal.py`:
   - Same-authority local repairs only:
     - Formatting repair
     - File naming repair
     - Manifest field completion from sealed data
     - Deterministic template fallback
   - DISALLOWED repairs:
     - Inventing missing interviewer facts
     - Inferring unsupported interests
     - Calling LLM
     - Web research outside C0
     - Changing route after L0
     - Writing L4 directly
2. Repair attempt logging
3. Heal failure handling

**Acceptance**:
- Only allowed repairs performed
- Disallowed repairs rejected
- Heal attempts logged
- E4 marker emitted

### Phase 4.5 — E5 Seal Implementation
**Scope**: Implement E5 Seal stage

**Files**:
- `apps_qna/l2/e5_seal.py` — E5 implementation

**Changes**:
1. Create `e5_seal.py`:
   - Emit `CardPackManifest`
   - Emit per-card hashes
   - Emit source/evidence register
   - Emit routing table
   - Emit card budget report
   - Emit no-claim list
   - Emit build ledger event
   - Emit sealed L2 artifact for Exit
2. Compute manifest hash
3. Create HMAC sig if signing enabled

**Acceptance**:
- All seal artifacts emitted
- Manifest includes all fields
- Sealed artifact ready for Exit
- E5 marker emitted

### Phase 4.6 — Wave 4 Verification
**Scope**: Add tests for L2 E1-E5 execution

**Files**:
- `tests/test_w4_l2_execution.py` — L2 execution tests

**Acceptance**:
- E1 Prep tests pass
- E2 Valid tests pass
- E3 Exec tests pass
- E4 Heal boundary tests pass
- E5 Seal tests pass
- Full E1-E5 pipeline tests pass

### Phase 5.1 — Exit X3 Disposition Wiring
**Scope**: Implement Exit evaluation and X3 disposition

**Files**:
- `apps_qna/exit_eval_wiring.py` — Exit wiring
- `apps_qna/exit/x3_disposition.py` — X3 disposition
- `apps_qna/__main__.py` — Exit integration

**Changes**:
1. Create Exit wiring:
   - Consume sealed L2 artifact
   - Run checkout validation
   - Emit exactly one X3 disposition
2. X3 dispositions:
   - `ALLOW_FINISH` — normal completion
   - `SAFE_ABSTAIN` — fix inputs and retry
   - `REROUTE` — retry with different parameters
   - `ESCALATE_HITL` — human review required
   - `SAFE_FALLBACK` — degraded pack
3. Integration with `apps_shared.cert.maybe_invoke_exit_eval`
4. Update `__main__.py` to call Exit after L2

**Acceptance**:
- Exit consumes sealed artifact
- Exactly one X3 disposition emitted
- Disposition appropriate to outcome
- Integration with cert hook works

### Phase 5.2 — Egress Verifier Card
**Scope**: Implement egress verification card

**Files**:
- `apps_qna/templates/tier_1/00a_source_set_and_egress_verifier.md.j2` — egress verifier template

**Changes**:
1. Create egress verifier card:
   - Blocks non-q prompt generating live answer
   - Blocks internal card names or route labels
   - Blocks multiple primary routes firing
   - Blocks STAR missing when proof requested
   - Blocks STAR for pure concept question
   - Blocks failure story without owned mistake
   - Blocks technical answer starting with vendors
   - Blocks company bridge in pure technical answer
   - Blocks unsupported company claims
   - Blocks invented metrics
   - Blocks consulting brochure language
2. Include metric language guidance:
   - Use measurement categories when exact numbers unavailable
   - workflow, quality, risk, adoption, operating, commercial categories

**Acceptance**:
- Egress verifier card renders
- Blocking rules documented
- Metric language guidance included

### Phase 5.3 — Blocking Rules Implementation
**Scope**: Implement egress blocking rules

**Files**:
- `apps_qna/egress/blocking_rules.py` — blocking rules
- `apps_qna/egress/fake_precision_detector.py` — fake precision detection
- `apps_qna/egress/internal_label_detector.py` — internal label detection

**Changes**:
1. Create blocking rules:
   - Detect forbidden phrases ("I would say", "use this version", etc.)
   - Detect internal labels (C0, L0, L1, L2, L3, L4, L5, L6, U0, R3, R4, R5)
   - Detect card names in output
   - Detect route labels in output
   - Detect fake precision (exact numbers without evidence)
   - Detect unsupported company claims
2. Create rule evaluation:
   - Each rule returns BLOCK|WARN|PASS
   - Aggregate into egress verdict

**Acceptance**:
- All blocking rules implemented
- Forbidden phrases detected
- Internal labels detected
- Fake precision detected
- Egress verdict produced

### Phase 5.4 — Wave 5 Verification
**Scope**: Add tests for Exit and egress

**Files**:
- `tests/test_w5_exit_egress.py` — Exit and egress tests

**Acceptance**:
- Exit disposition tests pass
- Egress blocking tests pass
- Fake precision detection tests pass
- Internal label blocking tests pass

### Phase 6.1 — R1A Exact Cache
**Scope**: Implement R1A exact cache

**Files**:
- `apps_qna/cache/r1a_exact.py` — exact cache
- `apps_qna/cache/digest.py` — digest computation

**Changes**:
1. Create R1A exact cache:
   - Key: SHA-256 of material digest bundle
   - Material digests:
     - interview YAML hash
     - company/role/interviewer identity set
     - template registry version
     - C0 evidence snapshot hash OR briefing hash
     - source register hash
     - policy_hash, blueprint_hash
     - output schema version
     - target runtime profile
     - paste budget mode
2. Auto-return only on full match
3. Miss on any material change

**Acceptance**:
- Cache key includes all material digests
- Full match required for return
- Miss on interviewer change
- Miss on evidence change

### Phase 6.2 — R1B Semantic Cache
**Scope**: Implement R1B semantic cache (advisory only)

**Files**:
- `apps_qna/cache/r1b_semantic.py` — semantic cache

**Changes**:
1. Create R1B semantic cache:
   - Advisory-only behavior
   - Never silently return similar pack
   - Allowed: "similar prior pack exists", candidate discovery
   - Allowed: manual reuse suggestion, explicit reuse flag
   - Forbidden: silent terminal return
   - Forbidden: reusing wrong interviewer panel
   - Forbidden: reusing stale company overlay
2. Compatibility proof required for reuse

**Acceptance**:
- Semantic cache is advisory only
- No silent returns
- Reuse requires explicit flag
- Compatibility verified

### Phase 6.3 — R5 Fallback
**Scope**: Implement R5 fallback

**Files**:
- `apps_qna/cache/r5_fallback.py` — fallback implementation

**Changes**:
1. Create R5 fallback:
   - Emergency degraded pack generation
   - Clearly marked as degraded
   - No interviewer personalization claims
   - Minimal card set (Tier 1 only)
   - Passes Exit as `SAFE_FALLBACK` or `MARK_DEGRADED`
   - No hiding of missing C0 evidence

**Acceptance**:
- Degraded pack generated
- Marked as degraded
- No personalization claims
- Correct Exit disposition

### Phase 6.4 — Comprehensive Test Suite
**Scope**: Add comprehensive tests

**Files**:
- `tests/test_grounding.py` — grounding tests
- `tests/test_routing.py` — routing tests
- `tests/test_live_mode.py` — live mode tests
- `tests/test_egress.py` — egress tests
- `tests/test_cache.py` — cache tests
- Update existing tests

**Test Coverage**:
1. Grounding:
   - Missing briefing + C0 disabled → SAFE_ABSTAIN/REROUTE
   - Uploaded briefing stale → C0 required
   - Briefing hash mismatch → reject
   - Unsupported interest → blocked
   - No public writing → explicit caveat
   - C0 weak → weak_with_caveats/reroute
2. Two-tier routing:
   - Tier 1 always-on present
   - Specialist not always-on
   - Exactly one primary route
   - Support card budget rules
   - Technical prompt → no company bridge
   - Proof prompt → STAR selected
   - Failure prompt → root cause included
3. Live mode:
   - non-q → ingest-only
   - q → answer generated
   - diagnostics bypass properly
   - forbidden phrases blocked
4. Egress:
   - No fake precision
   - No unsupported claims
   - No internal labels
   - No vendor-first technical answer
5. Cache:
   - R1A exact on full digest
   - R1A miss on interviewer change
   - R1B advisory only
   - R5 fallback marks degraded

**Acceptance**:
- All test categories pass
- Coverage >90% for new code
- Zero regressions in existing tests

### Phase 6.5 — Blend360/Steven Fixture
**Scope**: Create regression fixture

**Files**:
- `tests/fixtures/blend360_steven_fixture.py` — fixture
- `tests/fixtures/data/blend360_steven/` — fixture data

**Changes**:
1. Create Blend360/Steven fixture:
   - Interview YAML
   - Expected C0 evidence
   - Expected briefing (optional)
   - Expected card pack structure
   - Verification assertions
2. Fixture proves:
   - 00_START_HERE_RUNTIME_ROOT style
   - 00A_SOURCE_SET_AND_EGRESS_VERIFIER style
   - 01_CARD_SELECTION_MANIFEST style
   - Target overlay style
   - Specialist route examples
   - Routing eval edge cases

**Acceptance**:
- Fixture validates target architecture
- Tests pass with fixture
- Fixture doesn't hardcode app to Blend

### Phase 7.1 — README Update
**Scope**: Update README for new architecture

**Files**:
- `apps_qna/README.md` — updated

**Changes**:
1. Update description:
   - Grounded two-tier live runtime pack compiler
   - C0 required unless sealed briefing passes
   - Deterministic L2 render
   - Exit sealed output
   - No generic packs for interviewer-specific runtime
2. Remove outdated static compiler language
3. Add two-tier explanation
4. Add C0/briefing explanation

**Acceptance**:
- README reflects target architecture
- No outdated static compiler claims
- Two-tier architecture explained
- C0/briefing flow explained

### Phase 7.2 — RUNBOOK Spine Flow
**Scope**: Add spine flow section to RUNBOOK

**Files**:
- `apps_qna/RUNBOOK.md` — spine flow section

**Changes**:
1. Add ASCII flow diagram:
   ```
   USER
     |
     v
   U0 Intake
     |
     v
   L1 Plan
     |
     v
   L0 Route
     |\
     | \ exact cache terminal return if full digest match
     |
     v
   C0 Grounding unless uploaded briefing passes
     |
     v
   Card Context Assembly
     |
     v
   L2 E1 Prep -> E2 Valid -> E3 Exec -> E4 Heal -> E5 Seal
     |
     v
   Exit X1/X2/X3
     |
     v
   reports/qna/<slug> sealed pack
     |
     v
   L6 post-run evaluation only
   ```
2. Explain each stage ownership
3. Explain C0 requirement
4. Explain semantic cache advisory
5. Explain two-tier routing
6. Explain always-on vs specialist

**Acceptance**:
- ASCII diagram present
- Stage ownership clear
- Architecture explained

### Phase 7.3 — TECHNICAL_SPEC Update
**Scope**: Update technical specification

**Files**:
- `apps_qna/TECHNICAL_SPEC.md` — updated

**Changes**:
1. Update types:
   - Spine contracts (ValidatedRequest, L1PlanContract, RouteContract)
   - C0 contracts (FinalEvidenceContract)
   - Briefing contracts (BriefingContract)
   - Tiered card types
   - Updated CardPackManifest
2. Update builder contract:
   - E1-E5 stages
   - Tier 1/2 rendering
   - Router integration
3. Update linter contract:
   - Egress verification
   - Two-tier validation
   - Routing validation

**Acceptance**:
- Spec reflects target architecture
- All new types documented
- Contracts specified

### Phase 7.4 — ASCII Spine Flow Diagram
**Scope**: Create standalone spine flow document

**Files**:
- `apps_qna/docs/spine_flow.md` — new document

**Changes**:
1. Create comprehensive ASCII diagram:
   - Full U0->L1->L0->C0->L2->Exit flow
   - Cache decision points
   - C0 vs briefing paths
   - Error paths
   - L6 shadow
2. Explain ownership at each stage
3. Explain data flow
4. Explain error handling

**Acceptance**:
- Complete ASCII flow
- All paths covered
- Ownership clear

### Phase 7.5 — Acceptance Verification
**Scope**: Final acceptance check

**Files**:
- `tests/test_acceptance.py` — acceptance tests

**Verification**:
1. apps_qna no longer claims C0 grounding is false for normal builds
2. apps_qna supports uploaded sealed briefing validation
3. apps_qna routes to C0 when briefing missing/stale/weak/invalid
4. apps_qna produces two-tier live runtime pack
5. Tier 1 and Tier 2 semantics explicit
6. Router enforces exactly one primary specialist route
7. Egress verifier blocks unsupported claims
8. L2 build maps to E1-E5
9. Exit emits exactly one X3 disposition
10. R1A exact cache is digest-safe
11. R1B semantic cache is advisory only
12. No direct L2 to L4 durable write
13. Tests cover all requirements
14. Blend360/Steven fixture passes
15. Docs are spine-correct

**Acceptance**:
- All 15 acceptance criteria pass
- No regressions
- Plan complete

---

## Rules

- Zero-loss: Preserve all valid existing behavior that fits target architecture
- No broad unrelated refactors
- No public surface renames unless required for spine correctness
- No missing runtime evidence invented
- No tests silently skipped
- Best implementation-grade decisions; document ambiguity in short notes
- C0 required unless sealed briefing passes
- Two-tier pack: Tier 1 always-on, Tier 2 specialist
- Exactly one primary route
- L2 E1-E5 execution
- Exit X3 disposition
- No direct L4 write
- R1B semantic cache advisory only

---

## Success Criteria

- [ ] C0 grounding integrated with proper contracts
- [ ] Uploaded briefing validation implemented
- [ ] Two-tier card architecture operational
- [ ] Deterministic router enforces single primary route
- [ ] L2 maps to E1-E5 stages
- [ ] Exit emits correct X3 disposition
- [ ] Egress verifier blocks fake precision and unsupported claims
- [ ] R1A exact cache digest-safe
- [ ] R1B semantic cache advisory-only
- [ ] Comprehensive test coverage (>90%)
- [ ] Blend360/Steven fixture passes
- [ ] Documentation reflects spine-correct architecture
- [ ] No regressions in existing tests
- [ ] Acceptance criteria (§17) all pass

---

## Implementation Commands

```bash
# Verify plan
python ops_scripts/ci/check_plan_registration_freshness.py

# Run tests during implementation
python -m pytest tests/_apps_contract/test_w*.py -v

# Final verification
python -m pytest tests/ -v --tb=short

# ADG regeneration after structural changes
python tools/generate_full_adg.py
python tools/adg/adg_redis_ingest.py --force
```

---

## Rollback Strategy

If things go wrong:
1. Revert to pre-refactor git branch
2. Restore `spine_manifest.yaml` to `build_time_compiler`
3. Restore `__main__.py` to static build path
4. Remove new U0/L1/L0/C0/L2/Exit modules
5. Keep fixture tests as regression baseline for future attempt

---

## Acceptance Criteria (Detailed)

| Metric | Target | Verification |
|---|---|---|
| C0 integration | C0 client exists, FEC reflects provenance | `apps_qna/c0_client.py` exists, FEC has `grounded: true` |
| Briefing validation | Validator rejects stale/invalid | `test_w2_briefing.py` passes |
| Two-tier architecture | Tier 1/2 cards, manifest tracks tiers | `test_w3_two_tier_routing.py` passes |
| Single primary route | Router enforces exactly one | `test_routing.py` assertions |
| E1-E5 mapping | L2 stages explicit | `test_w4_l2_execution.py` passes |
| Exit disposition | X3 emitted correctly | `test_w5_exit_egress.py` passes |
| Egress verification | Fake precision blocked | `test_egress.py` passes |
| Cache safety | R1A digest-safe, R1B advisory | `test_cache.py` passes |
| Test coverage | >90% new code | pytest --cov-report |
| Fixture pass | Blend360/Steven example works | `tests/fixtures/blend360_steven_fixture.py` passes |
| Docs accuracy | README/RUNBOOK/SPEC updated | Manual review |
| No regressions | All existing tests pass | `pytest tests/ -v` |

## Cascade Alignment Checks

- Plan follows structured-reasoning discipline (SR_INTAKE → SR_PLAN → SR_APPROVAL → SR_EXECUTE)
- All new Python files routed to canonical SSOT folders per §31
- ADG graph-layer evidence will be collected before implementation (§22)
- Author-Gate queue seeded for ambiguous decisions (§35)
- Deferred scope captured per §24
- MCP serialization honored for Notion write (§25)
