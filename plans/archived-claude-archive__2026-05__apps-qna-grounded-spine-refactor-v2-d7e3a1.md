---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-qna-grounded-spine-refactor-v2-d7e3a1.md'
original_relative_path: '_archive\\2026-05\\apps-qna-grounded-spine-refactor-v2-d7e3a1.md'
source_sha256: 1c6365ad0335ac67fa239bdf1f7fceeb7b070329c4a001bab1299b41198c1f66
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-qna-grounded-spine-refactor-v2-d7e3a1
plan_type: refactor
---

# apps_qna Grounded Two-Tier Spine Refactor Plan v2

Transform apps_qna from static template compiler to grounded two-tier live interview runtime pack compiler riding the agentic_core spine correctly—without duplicating agentic_core inside apps_qna.

---

## Executive Summary

This plan refactors apps_qna to become a spine-correct grounded pack compiler that:
1. Calls **canonical agentic_core C0** through a thin adapter (no parallel C0 implementation)
2. Distinguishes **C0 FinalEvidenceContract** from **UploadedBriefingEvidenceContract**
3. Uses **canonical R4_SINGLE_ACTION route** (not invented composite routes)
4. Implements **W0 thin-slice proof** before full waves
5. Makes **prompt assembly status explicit** (no ambiguous `conditional`)
6. Treats **reports/qna output as local sealed artifact** (not UWG/L4)
7. Preserves **progressive-disclosure two-tier architecture**
8. Uses **Blend360/Steven as fixture only** (not hardcoded path)

---

## What Changed from f5a2c9

| Aspect | Previous Plan (f5a2c9) | Revised Plan (d7e3a1) |
|--------|------------------------|----------------------|
| **C0 Ownership** | Proposed `c0_client.py`, `c0/shaper.py`, `c0/verifier.py` inside apps_qna | Thin `c0_adapter.py` only; calls canonical C0; no parallel implementation |
| **Evidence Contracts** | Single contract type; briefing "faked" as C0 | Two distinct contracts: `FinalEvidenceContract` (C0) vs `UploadedBriefingEvidenceContract` (app-owned) |
| **Route Expression** | Invented `R3_PLUS_R4_GROUNDED_SINGLE_ACTION` | Uses canonical `R4_SINGLE_ACTION` with `grounding_required: true/false` flags |
| **Prompt Assembly** | `pa_required: conditional` (ambiguous) | Explicit: `core_prompt_assembly_required: false`, `domain_card_context_assembly_required: true` |
| **W0 Proof** | Jumped directly to 7 waves | Mandatory W0 thin-slice proof before W1-W7 |
| **UWG/L4 Language** | "UWG Write", "UWG-sealed manifest" for local output | Local filesystem output; UWG/L4 only for future optional durable commit path |
| **Production C0** | "Assume C0 interface exists, mock for tests" | Thin adapter calls canonical C0; fail-closed if unavailable; mock only in tests |
| **Evidence Integrity** | Risk of inventing facts in healing | Explicit: C0 shapes evidence; apps_qna never invents; healing repairs formatting only |

---

## Updated Target Architecture

```
USER (CLI: python -m apps_qna --interview <slug> [--briefing <path>])
 |
 v
U0 Intake ────────────────────────────────────────────────────────────►
 |   • CLI envelope validation                                         |
 |   • Capture: slug, company, role, interviewers[], briefing path      |
 |   • Emit: ValidatedRequest (request_id, trace_root, input hashes)    |
 |   • No reasoning, no retrieval, no routing                           |
 v                                                                     |
L1 Interpret / Plan ───────────────────────────────────────────────────►
 |   • Consume: ValidatedRequest                                        |
 |   • Build: task_spec, query_spec                                     |
 |   • Declare: C0 required vs briefing sufficient                      |
 |   • Emit: L1PlanContract                                             |
 |   • Does not retrieve, route, execute, or write                      |
 v                                                                     |
L0 Route Decision ─────────────────────────────────────────────────────►
 |   • Consume: L1PlanContract                                          |
 |   • Check: R1A exact cache (full digest match) ──► [RET] Exit         |
 |   • Select: exactly one RouteContract                                |
 |   • Route family: R4_SINGLE_ACTION (canonical enum)                |
 |   • Does not retrieve, execute, write, or approve                    |
 v                                                                     |
C0 Context Engine (via thin adapter) ──────────────────────────────────►
 |   • Canonical agentic_core C0 (not apps_qna implementation)          |
 |   • Required if no briefing OR briefing fails validation            |
 |   • Emits: canonical FinalEvidenceContract                           |
 |   • Production unavailable → fail-closed (SAFE_ABSTAIN)             |
 |   • Mock C0 for tests only                                           |
 v                                                                     |
Briefing Bypass Path ──────────────────────────────────────────────────►
 |   • Validate uploaded sealed briefing packet                         |
 |   • Hash verification, staleness check, sufficiency validation        |
 |   • On pass → emit UploadedBriefingEvidenceContract                 |
 |   • On fail → route to C0 OR Exit with disposition                   |
 v                                                                     |
Domain Card Context Assembly ──────────────────────────────────────────►
 |   • NOT canonical Prompt Assembly (no model execution)               |
 |   • Shapes: C0 evidence OR briefing evidence → card-render inputs   |
 |   • Prepares: bounded context for Jinja2 templates                   |
 |   • Does not call LLM, does not compile prompts                    |
 v                                                                     |
L2 E1-E5 Deterministic Build ──────────────────────────────────────────►
 |   E1 Prep ──────► freeze refs, bind policy_hash, create workspace   |
 |   E2 Valid ─────► validate schema, evidence sufficiency, routes   |
 |   E3 Exec ──────► render Tier 1 always-on, Tier 2 via router      |
 |   E4 Heal ──────► formatting repair only (NO fact invention)      |
 |   E5 Seal ──────► CardPackManifest, hashes, source register       |
 |   Does not write L4 directly                                        |
 v                                                                     |
Exit X1/X2/X3 ─────────────────────────────────────────────────────────►
 |   • Checkout sealed L2 artifact                                     |
 |   • Emit exactly one X3 disposition:                                |
 |     - ALLOW_FINISH (normal completion)                                |
 |     - SAFE_ABSTAIN (fix inputs and retry)                          |
 |     - REROUTE (retry with different parameters)                    |
 |     - ESCALATE_HITL (human review)                                 |
 |     - SAFE_FALLBACK (degraded pack, marked)                        |
 v                                                                     |
reports/qna/<slug>/ sealed local artifact ─────────────────────────────►
 |   • Tier 1 cards (always-on runtime control)                         |
 |   • Tier 2 cards (specialist, router-selected)                    |
 |   • CardPackManifest with evidence refs, tiering, hashes          |
 |   • Source register, no-claim list                                 |
 |   • NOT UWG/L4 durable write (default)                               |
 v                                                                     |
L6 Post-Run Evaluation (shadow only) ──────────────────────────────────►
 |   • Reads runtime exhaust                                           |
 |   • Evaluates: routing quality, evidence sufficiency, overfire      |
 |   • Does not mutate current run, does not write L4                  |
```

---

## Updated Spine Ownership Table

| Stage | Canonical Owner | apps_qna Responsibility | Forbidden in apps_qna |
|-------|-----------------|------------------------|----------------------|
| **U0** | `agentic_core.L0_routing.intake` | Wrap CLI args → `ValidatedRequest`; emit request_id, trace | No reasoning, no routing, no C0 call |
| **L1** | `agentic_core.L1_cognition.planning` | Emit `L1PlanContract` declaring C0 vs briefing needs | No retrieval, no execution |
| **L0** | `agentic_core.L0_routing.reasoning` | Emit `RouteContract` (R4_SINGLE_ACTION); cache decision | No C0 call, no execution |
| **C0** | `agentic_core.L0_routing.c0_retrieval` | **Thin adapter only**: shape request, call canonical C0, return `FinalEvidenceContract` | No C0 implementation, no graph traversal, no evidence scoring, no fact invention |
| **Briefing** | `apps_qna` (app-owned) | Validate, emit `UploadedBriefingEvidenceContract` | No C0 contract impersonation |
| **Domain Assembly** | `apps_qna` (app-owned) | Shape evidence → card context (NOT canonical PA) | No provider/model prompt compilation |
| **L2** | `apps_qna` (app-owned) | E1-E5 deterministic build; seal artifacts | No direct L4 write, no C0 call, no route change |
| **Exit** | `agentic_core.L3_orchestration.exit_eval` | Wire L2 artifact → Exit; emit X3 disposition | No L2 mutation, no direct L4 write |
| **UWG/L4** | `agentic_core.L4_state.uwg` | **Not used for default local output** | No default UWG write for reports/qna |
| **L6** | `agentic_core.L6_observability` | Shadow eval skeleton only | No current-run mutation |

---

## W0 Thin-Slice Proof Plan

W0 validates the smallest runnable spine-correct target before full waves.

### W0 Scope

| Component | Files | Acceptance |
|-----------|-------|------------|
| U0 | `u0_intake.py` | Emits `ValidatedRequest` with request_id, trace_root |
| L1 | `l1_planner.py` | Emits `L1PlanContract` declaring C0 required OR briefing sufficient |
| L0 | `l0_router.py` | Emits exactly one `RouteContract` (R4_SINGLE_ACTION) |
| Briefing | `briefing_validator.py` | Validates and emits `UploadedBriefingEvidenceContract` |
| C0 Adapter | `c0_adapter.py` (thin) | Calls mock canonical C0, returns `FinalEvidenceContract` |
| L2 E1-E3 | `l2/e1_prep.py`, `e2_valid.py`, `e3_exec.py` | Renders two-tier pack (Tier 1 + Tier 2 via router) |
| Exit | `exit_wiring.py` | Emits exactly one X3 disposition |
| Manifest | Updated `CardPackManifest` | Includes evidence refs, tiering, card hashes |
| Tests | `tests/test_w0_thin_slice.py` | Proves spine correctness without breaking existing build |

### W0 Files to Inspect Before Edits

```
apps_qna/
├── __main__.py                    # Entrypoint to wrap
├── spine_manifest.yaml            # Route declaration to update
├── builder/card_pack_builder.py   # L2 build to refactor
├── types/qna_types.py             # Types to extend
├── config/route_registry.yaml     # Route registry to update
├── integrations/spine_handoff.py  # ValidatedRequest wrapper

tests/
├── conftest.py                    # Fixtures to add

canonical references/
├── agentic_core/L0_routing/types/route_contract_v15.py
├── agentic_core/L3_orchestration/types/c0_evidence_contract_types.py
```

### W0 Files to Create

```
apps_qna/
├── u0_intake.py                   # U0: CLI → ValidatedRequest
├── l1_planner.py                  # L1: PlanContract emission
├── l0_router.py                   # L0: RouteContract emission
├── c0_adapter.py                  # Thin adapter to canonical C0
├── briefing_validator.py          # Briefing validation
├── types/spine_contracts.py       # ValidatedRequest, L1PlanContract, RouteContract
├── types/briefing_contracts.py    # UploadedBriefingEvidenceContract
├── l2/
│   ├── e1_prep.py               # E1: freeze, bind hashes
│   ├── e2_valid.py                # E2: validation stage
│   └── e3_exec.py                 # E3: render execution
├── router/two_tier_router.py      # Two-tier card selection
├── exit_wiring.py                 # Exit integration
├── templates/tier_1/
│   ├── 00_start_here_runtime_root.md.j2
│   ├── 00a_source_set_and_egress_verifier.md.j2
│   ├── 01_card_selection_manifest.md.j2
│   └── 03_interviewer_lens_and_company_bridge.md.j2
tests/
├── test_w0_thin_slice.py          # W0 acceptance tests
├── fixtures/mock_c0.py            # Mock canonical C0
└── fixtures/briefing_fixture.py   # Valid briefing fixture
```

### W0 Files to Modify

```
apps_qna/
├── __main__.py                    # Wire U0→L1→L0→C0/Briefing→L2→Exit
├── spine_manifest.yaml            # R4_SINGLE_ACTION routes
├── types/qna_types.py             # Add CardPackManifest fields
├── builder/card_pack_builder.py   # Integrate E1-E3 calls
└── integrations/spine_handoff.py   # Keep for legacy path (backward compat)
```

### W0 Acceptance Tests

```python
# tests/test_w0_thin_slice.py

def test_u0_emits_validated_request():
    """U0 emits ValidatedRequest with required fields."""

def test_l1_emits_plan_contract():
    """L1 emits L1PlanContract declaring C0 requirement."""

def test_l0_emits_single_route_contract():
    """L0 emits exactly one RouteContract (R4_SINGLE_ACTION)."""

def test_uploaded_briefing_bypasses_c0():
    """Valid briefing emits UploadedBriefingEvidenceContract, bypasses C0."""

def test_mock_c0_returns_final_evidence_contract():
    """C0 adapter returns canonical FinalEvidenceContract."""

def test_l2_renders_two_tier_pack():
    """E3 renders Tier 1 always-on + Tier 2 via router."""

def test_exit_emits_x3_disposition():
    """Exit emits exactly one X3 disposition."""

def test_manifest_has_evidence_refs():
    """CardPackManifest includes evidence refs, tiering, hashes."""

def test_no_direct_l2_to_l4_write():
    """L2 writes to local workspace only, not L4."""

def test_existing_static_build_not_broken():
    """Legacy static build path still works (backward compat)."""
```

### W0 Commands

```bash
# Run W0 tests
python -m pytest tests/test_w0_thin_slice.py -v

# Verify spine contracts
python -c "from apps_qna.types.spine_contracts import ValidatedRequest, L1PlanContract, RouteContract; print('Contracts OK')"

# Verify C0 adapter calls mock
python -c "from apps_qna.c0_adapter import call_canonical_c0; from tests.fixtures.mock_c0 import MockC0; print('Adapter OK')"

# Build with W0 components (smoke test)
python -m apps_qna --interview test-w0 --company TestCo --dry-run --w0-mode

# Verify existing build still works
python -m apps_qna --interview legacy-test --company LegacyCo --dry-run
```

### W0 Rollback Notes

If W0 fails:
1. Restore `__main__.py` to pre-W0 state
2. Remove W0-created files (u0_intake.py, l1_planner.py, etc.)
3. Keep `spine_handoff.py` as fallback
4. Revert `spine_manifest.yaml` to `build_time_compiler`
5. Archive W0 learnings for next attempt

---

## Revised Wave Structure After W0

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| W0 | Thin-slice spine proof | U0→L1→L0→C0/Briefing→L2→Exit | A | ~35K 🟢 |
| W1 | Route model + spine contracts | spine_manifest, registries, contract types | B | ~32K 🟢 |
| W2 | C0 adapter + briefing validation | c0_adapter, briefing_validator, evidence contracts | C | ~28K 🟢 |
| W3 | Two-tier card architecture | Tier 1/2 specs, router, templates | D | ~45K 🟢 |
| W4 | L2 E4-E5 + egress | E4 heal, E5 seal, egress verifier | E | ~38K 🟢 |
| W5 | Cache strategy + full tests | R1A/R1B/R5, comprehensive test suite | F | ~42K 🟢 |
| W6 | Documentation + acceptance | README, RUNBOOK, TECHNICAL_SPEC, spine flow | G | ~25K 🟢 |

**Total: ~245K tokens across 7 waves (W0-W6), all GREEN**

---

## Detailed Phase Plan

### W0.1 — U0 Intake Implementation
**Files**: `u0_intake.py`, `types/spine_contracts.py`
**Scope**: CLI envelope → ValidatedRequest
**Acceptance**: U0 emits ValidatedRequest with request_id, trace_root, input hashes

### W0.2 — L1 Plan Implementation
**Files**: `l1_planner.py`, `types/spine_contracts.py`
**Scope**: ValidatedRequest → L1PlanContract (C0 required OR briefing sufficient)
**Acceptance**: L1PlanContract declares evidence requirements, emits without retrieval

### W0.3 — L0 Route Implementation
**Files**: `l0_router.py`, `types/spine_contracts.py`
**Scope**: L1PlanContract → RouteContract (R4_SINGLE_ACTION)
**Acceptance**: Exactly one RouteContract, canonical route enum, cache decision

### W0.4 — C0 Thin Adapter
**Files**: `c0_adapter.py`, `tests/fixtures/mock_c0.py`
**Scope**: Shape request → canonical C0 → FinalEvidenceContract
**Acceptance**: Adapter calls mock C0, returns canonical contract; production fail-closed

### W0.5 — Briefing Validation
**Files**: `briefing_validator.py`, `types/briefing_contracts.py`
**Scope**: Validate uploaded briefing → UploadedBriefingEvidenceContract
**Acceptance**: Hash check, staleness, sufficiency; distinct from C0 contract

### W0.6 — L2 E1-E3 Execution
**Files**: `l2/e1_prep.py`, `e2_valid.py`, `e3_exec.py`, `router/two_tier_router.py`
**Scope**: E1 freeze → E2 validate → E3 render two-tier pack
**Acceptance**: Tier 1 always-on + Tier 2 via router; no L4 write

### W0.7 — Exit Wiring
**Files**: `exit_wiring.py`
**Scope**: Sealed L2 artifact → Exit → X3 disposition
**Acceptance**: Exactly one X3 disposition emitted

### W0.8 — W0 Acceptance Tests
**Files**: `tests/test_w0_thin_slice.py`
**Scope**: Prove spine correctness
**Acceptance**: All 10 W0 acceptance tests pass

### W1.1 — Route Model Update
**Files**: `spine_manifest.yaml`, `config/route_registry.yaml`
**Scope**: R4_SINGLE_ACTION routes with grounding flags
**Acceptance**: Canonical route enum, no invented composites

### W1.2 — Contract Type Finalization
**Files**: `types/spine_contracts.py`
**Scope**: Finalize ValidatedRequest, L1PlanContract, RouteContract
**Acceptance**: Contracts match canonical shapes, validation passes

### W1.3 — Spine Manifest Registration
**Files**: `spine_manifest.yaml`, `config/cert_route_registry.yaml`
**Scope**: Register apps_qna routes in spine
**Acceptance**: Routes validated against schema, CI passes

### W1.4 — W1 Verification
**Files**: `tests/test_w1_route_model.py`
**Scope**: Route model tests
**Acceptance**: Tests pass, zero regressions

### W2.1 — C0 Adapter Hardening
**Files**: `c0_adapter.py`
**Scope**: Production fail-closed, error handling
**Acceptance**: Canonical C0 unavailable → SAFE_ABSTAIN disposition

### W2.2 — Briefing Contract Hardening
**Files**: `briefing_validator.py`, `types/briefing_contracts.py`
**Scope**: Edge cases, hash mismatch, staleness
**Acceptance**: All briefing failures handled correctly

### W2.3 — Evidence Contract Distinction
**Files**: `types/evidence_contracts.py`, `exit_wiring.py`
**Scope**: C0 FinalEvidenceContract vs UploadedBriefingEvidenceContract
**Acceptance**: Exit normalizes both for sufficiency checks; contracts never conflated

### W2.4 — W2 Verification
**Files**: `tests/test_w2_evidence_integration.py`
**Scope**: C0 and briefing path tests
**Acceptance**: All evidence path tests pass

### W3.1 — Tier 1 Card Templates
**Files**: `templates/tier_1/*.md.j2` (4 cards)
**Scope**: 00_START_HERE, 00A_EGRESS_VERIFIER, 01_ROUTING_MANIFEST, 03_LENS_BRIDGE
**Acceptance**: Tier 1 cards render, frontmatter correct

### W3.2 — Tier 2 Specialist Specs
**Files**: `card_specs/tier_2.py`, `templates/tier_2/*.md.j2` (12 specialists)
**Scope**: STAR, RAG, governance, tools, architecture, etc.
**Acceptance**: Specialist cards have narrow triggers, no overfire

### W3.3 — Two-Tier Router
**Files**: `router/two_tier_router.py`, `router/route_precedence.py`
**Scope**: Exactly one primary route, support card budget
**Acceptance**: Route precedence enforced, card budget followed

### W3.4 — CardPackManifest Schema
**Files**: `types/qna_types.py`
**Scope**: Tier info, evidence refs, hashes, source register
**Acceptance**: Manifest includes all required fields

### W3.5 — W3 Verification
**Files**: `tests/test_w3_two_tier.py`
**Scope**: Tier 1/2 routing tests
**Acceptance**: Tier 1 always loads, Tier 2 loads by trigger only

### W4.1 — E4 Heal Boundaries
**Files**: `l2/e4_heal.py`
**Scope**: Formatting repair only; NO fact invention
**Acceptance**: Healing repairs formatting; facts frozen at E3

### W4.2 — E5 Seal Implementation
**Files**: `l2/e5_seal.py`
**Scope**: Sealed artifact, manifest, hashes
**Acceptance**: Sealed artifact for Exit handoff

### W4.3 — Egress Verifier Card
**Files**: `templates/tier_1/00a_source_set_and_egress_verifier.md.j2`
**Scope**: Blocks fake precision, unsupported claims, internal labels
**Acceptance**: Verifier card renders with blocking rules

### W4.4 — Egress Blocking Rules
**Files**: `egress/blocking_rules.py`
**Scope**: Detect forbidden phrases, internal labels, fake precision
**Acceptance**: All blocking rules implemented

### W4.5 — W4 Verification
**Files**: `tests/test_w4_exit_egress.py`
**Scope**: E4-E5, egress tests
**Acceptance**: Healing boundaries, egress blocking tests pass

### W5.1 — R1A Exact Cache
**Files**: `cache/r1a_exact.py`
**Scope**: Digest-safe cache with all material hashes
**Acceptance**: Full digest match required; miss on any change

### W5.2 — R1B Semantic Cache
**Files**: `cache/r1b_semantic.py`
**Scope**: Advisory-only semantic cache
**Acceptance**: Never silent return; explicit reuse flag required

### W5.3 — R5 Fallback
**Files**: `cache/r5_fallback.py`
**Scope**: Degraded pack for emergency
**Acceptance**: Marked degraded, no personalization claims

### W5.4 — Comprehensive Test Suite
**Files**: `tests/test_*.py`
**Scope**: Grounding, routing, live-mode, egress, cache
**Acceptance**: >90% coverage, zero regressions

### W5.5 — Blend360/Steven Fixture
**Files**: `tests/fixtures/blend360_steven_fixture.py`
**Scope**: Regression fixture (not hardcoded app path)
**Acceptance**: Fixture validates target architecture

### W6.1 — README Update
**Files**: `README.md`
**Scope**: Grounded pack compiler description
**Acceptance**: Docs reflect target architecture

### W6.2 — RUNBOOK Spine Flow
**Files**: `RUNBOOK.md`
**Scope**: ASCII spine flow, stage ownership
**Acceptance**: Clear U0→L1→L0→C0/Briefing→L2→Exit diagram

### W6.3 — TECHNICAL_SPEC Update
**Files**: `TECHNICAL_SPEC.md`
**Scope**: Contracts, E1-E5, two-tier routing
**Acceptance**: Spec matches implementation

### W6.4 — ASCII Spine Flow Document
**Files**: `docs/spine_flow.md`
**Scope**: Standalone visual flow
**Acceptance**: Complete ASCII diagram, all paths covered

### W6.5 — Final Acceptance Verification
**Files**: `tests/test_acceptance.py`
**Scope**: All 15 acceptance criteria
**Acceptance**: All criteria pass

---

## Updated Gap Register

**GAP-1: Parallel C0 implementation risk** (from f5a2c9 GAP-5)
- Previous: Proposed full C0 inside apps_qna
- Revised: Thin adapter only; no parallel C0
- Resolution: W0.4, W2.1 implement adapter pattern

**GAP-2: Evidence contract conflation** (from f5a2c9 GAP-7)
- Previous: Briefing "faked" as C0 contract
- Revised: UploadedBriefingEvidenceContract distinct from FinalEvidenceContract
- Resolution: W0.5, W2.3 implement contract distinction

**GAP-3: Invented route enum** (from f5a2c9 GAP-3)
- Previous: R3_PLUS_R4_GROUNDED_SINGLE_ACTION
- Revised: Canonical R4_SINGLE_ACTION with grounding flags
- Resolution: W0.3, W1.1 use canonical enum

**GAP-4: Ambiguous prompt assembly** (new)
- Issue: `pa_required: conditional` too vague
- Resolution: Explicit `core_prompt_assembly_required: false`, `domain_card_context_assembly_required: true`

**GAP-5: No thin-slice proof** (from f5a2c9 structure)
- Previous: Jumped to 7 waves
- Revised: Mandatory W0 before W1-W6
- Resolution: W0 phases 0.1-0.8

**GAP-6: UWG/L4 language confusion** (from f5a2c9)
- Previous: "UWG Write" for local output
- Revised: Local filesystem only; UWG/L4 for optional future durable commit
- Resolution: Remove UWG language from default path

**GAP-7: Flat card architecture** (from f5a2c9 GAP-8)
- No change: Still two-tier required
- Resolution: W3.1-W3.5 implement Tier 1/2

**GAP-8: Missing spine tests** (from f5a2c9 GAP-4)
- No change: Still need comprehensive coverage
- Resolution: W0.8, W5.4 implement test suite

---

## Contract Inventory

### 1. ValidatedRequest (U0 → L1)
**Canonical**: `agentic_core.L0_routing.intake.validated_request.ValidatedRequest`
**apps_qna role**: Wrap CLI input → ValidatedRequest
**Fields**: request_id, trace_root, session_id, ingress_time_unix, source_channel, principal_type, auth_verdict, schema_verdict, normalized_payload_hash, etc.

### 2. L1PlanContract (L1 → L0)
**Canonical**: Defined in `agentic_core.L1_cognition.planning.contracts`
**apps_qna role**: Emit declaring C0 vs briefing requirements
**Fields**: plan_id, task_spec, query_spec, c0_required: bool, briefing_sufficient: bool, evidence_requirements[], plan_rationale

### 3. RouteContract (L0 → C0/Briefing/L2)
**Canonical**: `agentic_core.L0_routing.types.route_contract_v15.RouteContractV15`
**apps_qna role**: Emit exactly one (R4_SINGLE_ACTION)
**Fields**: route_id (RouteIdV15), execution_form (ExecutionFormV15), cache_policy, grounding_required: bool, c0_required: bool, uploaded_briefing_required: bool, side_effect_class

### 4. C0 FinalEvidenceContract (C0 → L2)
**Canonical**: `agentic_core.L3_orchestration.types.c0_evidence_contract_types.C0EvidenceContract`
**apps_qna role**: Consume via thin adapter; never fabricate
**Fields**: retrieval_id, request_id, coverage_score, abstain_hint, cited_spans[], evidence_hmac, claim_confidences[]

### 5. UploadedBriefingEvidenceContract (Briefing → L2)
**App-owned**: `apps_qna.types.briefing_contracts.UploadedBriefingEvidenceContract`
**Purpose**: Distinct from C0 contract for briefing bypass path
**Fields**: briefing_hash, created_at, max_age, interviewer_coverage[], source_register_ref, evidence_sufficiency: SUFFICIENT|STALE|INCOMPLETE|MISMATCH

### 6. DomainCardContextAssembly (C0/Briefing → L2)
**App-owned**: `apps_qna.types.assembly_types.DomainCardContextAssembly`
**Purpose**: Shapes evidence → card render inputs (NOT canonical PA)
**Fields**: evidence_source: c0|briefing, interviewer_context{}, company_context{}, role_context{}, personalization_hooks[], no_claim_list[]

### 7. L2 Stage Receipts E1-E5 (Internal)
**App-owned**: Stage markers
- E1PrepReceipt: frozen_refs, policy_hash, blueprint_hash, input_digest
- E2ValidReceipt: validation_passed: bool, errors[]
- E3ExecReceipt: rendered_cards[], tier_1_cards[], tier_2_cards[]
- E4HealReceipt: repairs_made[], facts_invented: false (enforced)
- E5SealReceipt: manifest_hash, sealed_artifact_path

### 8. CardPackManifest (L2 → Exit)
**App-owned**: `apps_qna.types.qna_types.CardPackManifest` (extended)
**Fields**: pack_id, slug, company, role, interviewer_names[], route_id, route_family, execution_form, c0_required, c0_invoked, uploaded_briefing_used, evidence_contract_ref, source_register_ref, cards[], tier_1_cards[], tier_2_cards[], card_hashes, manifest_hash, created_at

### 9. Exit X3 Disposition Receipt (Exit → User/L6)
**Canonical**: `agentic_core.L3_orchestration.exit_eval` disposition types
**apps_qna role**: Wire L2 artifact → Exit; emit one disposition
**Values**: ALLOW_FINISH, SAFE_ABSTAIN, REROUTE, ESCALATE_HITL, SAFE_FALLBACK

---

## Route Model

### Canonical Route Family

Apps_qna uses canonical `RouteIdV15.R4_SINGLE_ACTION` from `agentic_core.L0_routing.types.route_contract_v15`.

### Apps_qna Route Definitions

**Route 1: Live Interview Runtime Pack (Grounded)**
```yaml
route_family: R4_SINGLE_ACTION  # canonical enum
route_id: apps_qna.live_interview_runtime_pack_v1
execution_form: SINGLE_STEP   # canonical enum
side_effect_class: FILESYSTEM_SANDBOX_WRITE

# Evidence requirements
grounding_required: true
c0_required: true
uploaded_briefing_required: false

# Prompt assembly (explicit)
core_prompt_assembly_required: false      # No model/provider call
domain_card_context_assembly_required: true  # App shapes evidence for cards
```

**Route 2: Live Interview Runtime Pack (Briefing Bypass)**
```yaml
route_family: R4_SINGLE_ACTION  # canonical enum
route_id: apps_qna.live_interview_runtime_pack_from_uploaded_brief_v1
execution_form: SINGLE_STEP   # canonical enum
side_effect_class: FILESYSTEM_SANDBOX_WRITE

# Evidence requirements
grounding_required: false
c0_required: false
uploaded_briefing_required: true

# Prompt assembly (explicit)
core_prompt_assembly_required: false
domain_card_context_assembly_required: true
```

### Route Selection Logic

1. L1PlanContract declares: `c0_required: true` OR `briefing_sufficient: true`
2. L0 Router checks uploaded briefing validity:
   - Valid briefing exists → Route 2 (briefing bypass)
   - No briefing OR briefing invalid → Route 1 (requires C0)
3. If Route 1 and C0 unavailable → Exit SAFE_ABSTAIN (fail-closed)

---

## C0 Adapter Boundaries

### C0-Owned Responsibilities (Canonical agentic_core)
- Retrieval graph traversal
- Evidence shaping and scoring
- FinalEvidenceContract production
- Source register management
- Freshness assessment
- Claim confidence computation
- Contradiction detection

### apps_qna Adapter Responsibilities
**File**: `apps_qna.c0_adapter`
- Shape app-specific C0 request from interview parameters
- Call canonical C0 retrieval endpoint
- Return canonical FinalEvidenceContract unchanged
- Handle C0 errors (fail-closed → SAFE_ABSTAIN)
- No evidence transformation, no fact invention

### Test-Only Mock Responsibilities
**File**: `tests.fixtures.mock_c0`
- Provide mock C0 responses for tests
- Simulate PASS, WEAK, EMPTY, BLOCKED evidence states
- NOT used in production

### Production Fail-Closed
- If canonical C0 unavailable → Exit SAFE_ABSTAIN
- No degraded operation with invented evidence
- Clear error message: "C0 grounding required but unavailable"

---

## Briefing Bypass Path

### UploadedBriefingEvidenceContract

**Purpose**: Distinct contract type for validated briefing packets (not C0 impersonation)

**Validation Steps**:
1. Hash verification (SHA-256 of briefing content)
2. Staleness check (created_at vs max_age)
3. Schema validation (briefing structure)
4. Sufficiency validation:
   - Interviewer coverage matches request
   - Company context present
   - Source register present

**Evidence States**:
- `SUFFICIENT` → Proceed to L2 (bypass C0)
- `STALE` → Route to C0 OR Exit REROUTE
- `INCOMPLETE` → Route to C0 OR Exit SAFE_ABSTAIN
- `MISMATCH` → Exit SAFE_ABSTAIN (fix briefing)

### Exit Normalization

Exit may normalize both contract types for apps_qna evidence sufficiency checks:
- C0 FinalEvidenceContract → evidence_status, coverage_score, cited_spans
- UploadedBriefingEvidenceContract → evidence_sufficiency, interviewer_coverage

But contracts remain distinct types; never conflate provenance.

---

## Two-Tier Card Architecture

### Tier 1: Always-On Runtime Cards

Loaded for every interview (compact control layer):

| Card | Purpose | Key Content |
|------|---------|-------------|
| 00_START_HERE_RUNTIME_ROOT.md | Live mode gate | q-prefix rules, readout rules, no internal labels |
| 00A_SOURCE_SET_AND_EGRESS_VERIFIER.md | Final checks | Fake precision blocking, unsupported claim blocking |
| 01_CARD_SELECTION_MANIFEST.md | Deterministic routing | Route precedence, primary route selection |
| 03_INTERVIEWER_LENS_AND_COMPANY_BRIDGE.md | Relevance bridge | Interviewer context, company style (passive) |

### Tier 2: Specialist Cards

Loaded only when router triggers (progressive disclosure):

| Route ID | Specialist Card | Trigger |
|----------|-----------------|---------|
| STAR_PROOF | star_proof.md | Proof, example, prior work requested |
| STAR_FAILURE_LEARNING | star_failure_learning.md | Failure story requested |
| RAG_CONTEXT | rag_context.md | Evidence, retrieval, hallucination, citation |
| GOVERNANCE_HITL | governance_hitl.md | Risk, authority, approval, policy |
| TOOLS_MCP_GATEWAY | tools_mcp_gateway.md | Tools, stack, gateway, routing explicit |
| AGENTIC_ARCHITECTURE | agentic_architecture.md | Architecture, workflow, orchestration |
| DS_TO_PLATFORM | ds_to_platform.md | DS modernization, MLOps, platform |
| PLATFORM_PRODUCTIZATION | platform_productization.md | Reusable IP, margin, accelerators |
| CLIENT_ADVISORY_ROI | client_advisory_roi.md | Advisory, ROI, client value |
| ROLE_SCOPE_MANDATE | role_scope_mandate.md | Role fit, mandate, scope |
| EXEC_TRANSLATION_FIT | exec_translation_fit.md | Executive, translation, fit |
| CROSS_EXAM_DEPTH | cross_exam_depth.md | Recovery, depth, challenge response |

### Router Rules

1. Exactly one primary specialist route per q-prompt
2. Support cards attach only when required
3. Ambiguity resolved by route precedence (not loading more cards)
4. Card budget:
   - Concept: Tier 1 + 1 specialist
   - STAR: Tier 1 + STAR + optional support
   - Failure: Tier 1 + STAR + recovery + optional support
   - Cross-exam: recovery + current specialist

---

## Cache Strategy

### R1A Exact Cache (Digest-Safe)

**Key**: SHA-256 of material digest bundle:
- interview YAML hash
- company/role/interviewer identity set
- template registry version
- C0 evidence snapshot hash OR briefing hash
- source register hash
- policy_hash, blueprint_hash
- output schema version
- target runtime profile
- paste budget mode

**Behavior**:
- Auto-return ONLY on full digest match
- Miss on ANY material change
- No silent stale returns

### R1B Semantic Cache (Advisory Only)

**Behavior**:
- NEVER silent terminal return
- Allowed: "similar prior pack exists", candidate discovery
- Allowed: manual reuse suggestion, explicit reuse flag
- Forbidden: reusing wrong interviewer panel, stale company overlay
- Compatibility proof required for any reuse

### R5 Fallback (Degraded)

**Behavior**:
- Emergency degraded pack only
- Clearly marked as degraded
- No interviewer personalization claims
- Minimal Tier 1 cards only
- Exit disposition: SAFE_FALLBACK

---

## Local Artifact vs UWG/L4 Boundary

### Default: Local Filesystem Output

```
reports/qna/<interview-slug>/
├── 00_START_HERE_RUNTIME_ROOT.md
├── 00A_SOURCE_SET_AND_EGRESS_VERIFIER.md
├── 01_CARD_SELECTION_MANIFEST.md
├── 03_INTERVIEWER_LENS_AND_COMPANY_BRIDGE.md
├── [Tier 2 specialist cards]
├── pack_manifest.json
└── source_register.json
```

**Properties**:
- Sealed local build artifact
- NOT UWG/L4 durable state
- L2 writes directly to workspace (not L4)
- Manifest is local sealed artifact, not UWG commit

### Optional Future: UWG/L4 Durable Commit

If durable pack indexing/reuse required:
```
Exit emits COMMIT_REQUEST
  ↓
UWG commits to L4
  ↓
L4 stores cache/memory/retrieval records
```

**Not part of W0-W6 default implementation.**

---

## Test Plan

### W0 Acceptance Tests (Mandatory First)

1. `test_u0_emits_validated_request`
2. `test_l1_emits_plan_contract`
3. `test_l0_emits_single_route_contract`
4. `test_uploaded_briefing_bypasses_c0`
5. `test_mock_c0_returns_final_evidence_contract`
6. `test_l2_renders_two_tier_pack`
7. `test_exit_emits_x3_disposition`
8. `test_manifest_has_evidence_refs`
9. `test_no_direct_l2_to_l4_write`
10. `test_existing_static_build_not_broken`

### Comprehensive Test Coverage

| Category | Test File | Coverage Target |
|----------|-----------|-----------------|
| Grounding | `test_grounding.py` | C0 paths, briefing paths, weak evidence |
| Routing | `test_routing.py` | Tier 1/2, single primary route, overfire |
| Live Mode | `test_live_mode.py` | q-prefix, ingest-only, forbidden phrases |
| Egress | `test_egress.py` | Fake precision, unsupported claims, labels |
| Cache | `test_cache.py` | R1A exact, R1B advisory, R5 degraded |
| Spine | `test_spine_correctness.py` | U0→L1→L0→C0→L2→Exit flow |
| Regression | `test_regression.py` | Blend360/Steven fixture |

### Coverage Target

- New code: >90%
- Modified code: maintain or improve
- Zero regressions in existing tests

---

## Acceptance Criteria

1. **C0 Integration**: Thin adapter calls canonical C0; no parallel implementation
2. **Evidence Contracts**: `FinalEvidenceContract` (C0) vs `UploadedBriefingEvidenceContract` (briefing) distinct
3. **Route Model**: Uses canonical `R4_SINGLE_ACTION`; no invented composites
4. **Prompt Assembly**: Explicit `core_prompt_assembly_required: false`, `domain_card_context_assembly_required: true`
5. **W0 Proof**: Thin-slice proof passes before full waves
6. **Local Output**: `reports/qna` is local sealed artifact; no UWG/L4 default
7. **Two-Tier**: Tier 1 always-on + Tier 2 specialist with progressive disclosure
8. **Single Route**: Router enforces exactly one primary specialist route
9. **Egress Verification**: Blocks fake precision, unsupported claims, internal labels
10. **Cache**: R1A digest-safe; R1B advisory-only
11. **No L2→L4 Write**: L2 writes local only; UWG/L4 optional future
12. **Fail-Closed**: Production C0 unavailable → SAFE_ABSTAIN
13. **Blend360 Fixture**: Regression fixture validates architecture
14. **Tests**: >90% coverage, zero regressions
15. **Docs**: README, RUNBOOK, TECHNICAL_SPEC reflect spine-correct architecture

---

## Implementation Commands

```bash
# Verify W0 before starting
python ops_scripts/ci/check_plan_registration_freshness.py --refresh

# W0: Run thin-slice tests
python -m pytest tests/test_w0_thin_slice.py -v

# W1-W6: Run wave tests
python -m pytest tests/test_w1_route_model.py -v
python -m pytest tests/test_w2_evidence_integration.py -v
python -m pytest tests/test_w3_two_tier.py -v
python -m pytest tests/test_w4_exit_egress.py -v
python -m pytest tests/test_w5_cache.py -v

# Full test suite
python -m pytest tests/ -v --tb=short

# Coverage report
python -m pytest tests/ --cov=apps_qna --cov-report=term-missing

# ADG regeneration after structural changes
python tools/generate_full_adg.py

# Final acceptance
python -m pytest tests/test_acceptance.py -v
```

---

## Rollback Strategy

If W0 fails:
1. Revert `__main__.py` to pre-W0 state
2. Remove W0-created files (keep list in version control)
3. Restore `spine_handoff.py` as fallback
4. Revert `spine_manifest.yaml` to `build_time_compiler`
5. Archive learnings for next attempt

If W1-W6 fail at any wave:
1. Do not proceed to next wave
2. Fix current wave or revert to last passing wave
3. Update plan with lessons learned
4. Re-run acceptance tests before continuing

Emergency full rollback:
1. `git checkout pre-refactor-branch`
2. Verify existing tests pass
3. Document what failed for future attempt

---

## Open Questions / Ambiguity Log

**Q1: Canonical C0 endpoint location**
- Current: `agentic_core.L0_routing.c0_retrieval` has C0 components
- Assumption: `c0_retrieval.dispatcher` or similar is the canonical entry point
- Risk: If canonical C0 doesn't exist, adapter cannot call it
- Mitigation: Mock for W0; fail-closed if C0 unavailable in production

**Q2: L1PlanContract canonical shape**
- Assumption: Similar to existing planning contracts in `agentic_core.L1_cognition.planning`
- Risk: If no canonical L1 contract exists, apps_qna defines app-specific shape
- Mitigation: Check `contracts.py` in L1_cognition; adapt to existing patterns

**Q3: Exit X3 disposition wiring**
- Assumption: `apps_shared.cert.maybe_invoke_exit_eval` is the integration point
- Risk: Exit wiring may need additional contracts
- Mitigation: W0.7 focuses on Exit wiring; adapt to existing exit_eval patterns

**Q4: Two-tier router complexity**
- Risk: 12 specialist routes with precedence may be complex
- Mitigation: Start with 4-6 essential routes in W0; expand in W3
- Fallback: Simpler routing if full precedence too complex

**Q5: Backward compatibility**
- Question: Should old static build path be deprecated or maintained?
- Current plan: Maintain for non-interview builds
- Risk: Dual paths increase maintenance
- Mitigation: Clear separation; static path uses old code, grounded path uses new spine

**Q6: Blend360/Steven fixture privacy**
- Question: Is Blend360/Steven data appropriate for repo fixture?
- Assumption: Use as pattern/example, not proprietary data
- Mitigation: Use fictionalized/abstracted version; no real company secrets

---

## Plan Hardening Addendum

### 1. Contract Reuse

**Rule**: Do not duplicate canonical spine contracts inside apps_qna.

**Implementation**:
- Import canonical `ValidatedRequest` from `agentic_core.L0_routing.intake.validated_request`
- Import canonical `L1PlanContract` from `agentic_core.L1_cognition.planning.contracts`
- Import canonical `RouteContract` (v15) from `agentic_core.L0_routing.types.route_contract_v15`
- Import canonical `C0EvidenceContract` from `agentic_core.L3_orchestration.types.c0_evidence_contract_types`
- Import canonical Exit disposition types from `agentic_core.L3_orchestration.exit_eval`

**apps_qna/types permissible content**:
- App-local adapters (e.g., `BriefingToC0Adapter` for normalization)
- Compatibility wrappers for version bridging
- Type aliases for convenience
- `UploadedBriefingEvidenceContract` (app-owned, distinct from C0 contract)
- `DomainCardContextAssembly` (app-specific, not canonical PA)

**Forbidden in apps_qna/types**:
- Full contract redefinitions of canonical spine contracts
- Duplicated dataclass fields that shadow canonical contracts
- Modified validation logic that diverges from canonical

### 2. Route Enum Inspection

**Rule**: Before coding route constants, inspect the canonical agentic_core route-family and route-id enums.

**Inspection Steps** (before W0.3 implementation):
```python
# Verify canonical enum membership
from agentic_core.L0_routing.types.route_contract_v15 import RouteIdV15, ExecutionFormV15

# Check if R4_SINGLE_ACTION is a valid RouteIdV15 member
assert RouteIdV15.R4_SINGLE_ACTION  # May raise AttributeError if not present

# If R4_SINGLE_ACTION not in RouteIdV15:
#   - Use the closest canonical single-action route family
#   - Document the mapping in comments
#   - Do not invent new RouteIdV15 members

# ExecutionFormV15 membership check
assert ExecutionFormV15.SINGLE_STEP
```

**apps_qna route_id**:
- `apps_qna.live_interview_runtime_pack_v1` (grounded path)
- `apps_qna.live_interview_runtime_pack_from_uploaded_brief_v1` (briefing bypass)

**These are route_id strings, not RouteIdV15 enum members.**
The `route_family` field uses the canonical enum; the `route_id` field is app-specific string.

### 3. C0 Fail-Closed Path

**Rule**: If canonical C0 is unavailable, `c0_adapter` must not emit fabricated evidence.

**Implementation**:

```python
# c0_adapter.py - fail-closed pattern

def call_canonical_c0(request: C0Request) -> C0Result:
    try:
        # Call canonical C0 retrieval
        c0_response = canonical_c0.retrieve(request)
        return C0Result.success(c0_response)
    except C0UnavailableError:
        # FAIL-CLOSED: Do not fabricate evidence
        return C0Result.unavailable(
            disposition=ExitDisposition.SAFE_ABSTAIN,
            reason="C0 grounding required but canonical C0 unavailable"
        )
    except C0TimeoutError:
        return C0Result.unavailable(
            disposition=ExitDisposition.REROUTE,
            reason="C0 retrieval timeout; retry with different parameters"
        )
```

**C0Unavailable / Grounding-Blocked Packet**:
```python
@dataclass(frozen=True)
class C0UnavailablePacket:
    """Sealed packet emitted when C0 cannot provide evidence."""
    status: Literal["UNAVAILABLE", "BLOCKED", "TIMEOUT"]
    disposition: ExitDisposition  # SAFE_ABSTAIN or REROUTE
    reason: str
    retry_policy: Optional[RetryPolicy]
    # NO fabricated evidence fields
    # NO fake C0EvidenceContract
```

**L2 Behavior on C0 Unavailable**:
- L2 must not render a personalized pack
- L2 may render a minimal Tier 1 pack marked as degraded
- L2 must pass C0UnavailablePacket to Exit unchanged
- L2 must not invent interviewer/company context

**Exit X3 Disposition on C0 Unavailable**:
- Usually `SAFE_ABSTAIN` (user fixes inputs and retries)
- Or `REROUTE` (retry with different parameters per policy)
- Never `ALLOW_FINISH` with fabricated evidence
- Never `SAFE_FALLBACK` unless explicitly configured for degraded mode

### 4. Local Filesystem Boundary

**Rule**: L2 may write only inside the configured local build workspace.

**Permitted Path Pattern**:
```
reports/qna/<interview-slug>/
├── 00_START_HERE_RUNTIME_ROOT.md
├── 00A_SOURCE_SET_AND_EGRESS_VERIFIER.md
├── ...
├── pack_manifest.json
└── source_register.json
```

**Configuration**:
```python
# config/build_paths.py
LOCAL_BUILD_WORKSPACE = Path("reports/qna")  # Relative to repo root
# May be overridden by env var APPS_QNA_BUILD_ROOT

# L2 writes only within this boundary
def validate_l2_write_path(path: Path) -> bool:
    resolved = path.resolve()
    workspace = LOCAL_BUILD_WORKSPACE.resolve()
    return resolved.is_relative_to(workspace)
```

**Enforcement**:
- L2 E5 Seal stage validates all write paths
- Violation raises `L2WriteBoundaryViolation`
- Exit disposition becomes `SAFE_ABSTAIN`

**Not L4 Durable State**:
- The local artifact is sealed but not durably indexed
- No automatic cache/memory/retrieval records
- No UWG commit for default path

**Not a UWG Write**:
- L2 calls local filesystem directly, not through UWG
- UWG is only used for optional future durable commit path
- Default path has no L4 write

## End of Plan

