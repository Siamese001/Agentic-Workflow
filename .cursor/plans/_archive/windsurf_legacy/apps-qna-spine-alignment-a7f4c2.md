---
plan_id: apps-qna-spine-alignment-a7f4c2
plan_type: refactor
---

# apps_qna Spine Alignment — Zero-Loss Refactor to Canonical agentic_core

Refactor apps_qna from a legacy static card builder to a governed, evidence-backed, two-tier live interview runtime card pack generator aligned with the canonical agentic_core spine.

---

## Context (SCQA)

**Situation** — apps_qna currently operates as a standalone static card builder with a legacy execution path. The `__main__.py` imports `run_qna` from `apps_qna.scripts` and directly instantiates `CardPackBuilder`. The spine_manifest.yaml claims only `build_time_compiler` route, which legitimately requires zero canonical authority contracts. While some spine integration exists (spine_handoff.py, spine_adapter.py), apps_qna does not participate in the full agentic_core spine for live interview runtime pack generation. The app lacks C0 grounding integration, two-tier card architecture, proper L2 E1-E5 execution receipts, and Exit v6/X3 control flow.

**Complication** — apps_qna needs to support live interview runtime mode where interviewer/company/person personalization is required. The current architecture cannot: (a) route deterministically through L0/L1, (b) call canonical C0 when grounding is required, (c) validate uploaded sealed briefing packets, (d) assemble domain card context from verified evidence, (e) render two-tier packs through L2 E1-E5, (f) seal artifacts properly, or (g) emit governed Exit dispositions. The existing static build path also has impure entrypoint, legacy direct execution, and lacks proper FEC/Exit integration.

**Question** — How do we refactor apps_qna to align with the canonical agentic_core spine while preserving existing static build functionality (either via compatibility shim or explicit deprecation), and prevent the same wiring failures identified across apps_lic, apps_rg, and apps_research?

**Answer** — Execute a zero-loss refactor through P0 (entrypoint purity + governance tests), W0 (thin-slice spine proof), and waves W1-W6 covering route model, C0 adapter, two-tier router, L2 E1-E5 render, Exit v6, and acceptance sweep. The outcome is apps_qna as a domain overlay that validates requests, plans evidence, routes deterministically, uses canonical C0 when grounding is required, validates uploaded briefings, assembles domain card context, renders two-tier packs through L2, seals artifacts, sends output to Exit, and lets L6 learn only after the run completes.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.windsurf/rules/adg-canonical-invariants.md` | ADG structural dependencies | ✅ |
| `.windsurf/rules/plan-location.md` | Plan SSOT location | ✅ |
| `apps_qna/__main__.py` | Entrypoint impurity baseline | ✅ |
| `apps_qna/spine_manifest.yaml` | Current route claims | ✅ |
| `apps_qna/builder/card_pack_builder.py` | Legacy builder coupling | ✅ |
| `apps_qna/types/qna_types.py` | Existing type contracts | ✅ |
| `apps_qna/config/route_registry.yaml` | Route definitions | ✅ |
| `apps_qna/integrations/spine_handoff.py` | Current spine integration | ✅ |
| ADG snapshot `artifacts/adg/adg_indexed_*.sqlite` | Structural dependency graph | 🔲 (verify before W1) |
| `agentic_core/L0_routing/types/route_contract_v15.py` | Canonical route contracts | 🔲 |
| `agentic_core/L1_cognition/planning/` | L1 plan contracts | 🔲 |
| `agentic_core/L3_orchestration/exit_eval/` | Exit v6 contracts | 🔲 |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| P0 | P0.1-P0.3 | Entrypoint purity + registry scaffold + governance tests | ~35K | Existing tests pass; no runtime break | 🔲 TODO | 20 governance tests green; registry scaffold exists |
| W0 | W0.1-W0.3 | Thin-slice spine proof before full refactor | ~25K | P0 complete; canonical refs readable | 🔲 TODO | 11 W0 tests pass; U0→L1→L0→L2→Exit proven |
| P1.5 | P1.5.1-P1.5.3 | Two-tier card templates + domain card context assembly | ~40K | W0 complete; template audit complete | 🔲 TODO | Tier 1/2 templates have real bodies; no placeholders |
| W1 | W1.1-W1.4 | Route model + U0/L1/L0 spine contracts | ~30K | P1.5 template audit done | 🔲 TODO | U0 Intake, L1 Planner, L0 Router emit canonical contracts |
| W2 | W2.1-W2.4 | C0 adapter + uploaded briefing evidence contract | ~35K | W1 routing proven | 🔲 TODO | C0 adapter calls canonical C0; briefing validator exists |
| W3 | W3.1-W3.4 | Two-tier router + card architecture | ~30K | W2 evidence paths proven | 🔲 TODO | Router selects exactly one primary route; Tier 1/2 cards |
| W4 | W4.1-W4.4 | L2 E1-E5 deterministic render + seal | ~35K | W3 router proven | 🔲 TODO | L2 E1-E5 receipts; manifest with hashes; no L4 write |
| W5 | W5.1-W5.4 | Exit v6 + egress verifier + cache safety | ~25K | W4 L2 proven | 🔲 TODO | Exit emits exactly one X3; R1A/R1B/R5 cache correct |
| W6 | W6.1-W6.4 | Acceptance sweep + legacy quarantine + docs | ~20K | W5 Exit proven | 🔲 TODO | 50 governance tests pass; RUNBOOK updated; legacy path deprecated or shimmed |

**Total: ~275K tokens across 7 waves + P0, all GREEN for scope estimation**

---

## Out Of Scope

The following are explicitly NOT part of this plan:

- Real LLM-judge implementations (stubs acceptable per deferred scope from apps-eval-harness-parity-f8d4a2)
- Production-log mining with PII redaction (deferred to future plan)
- Holdout vs dev eval-set separation (deferred)
- Per-app rubric migrations to new grader types (opt-in; schema ready per apps-eval-harness-deferred-e4a1b7)
- SSOT consolidation of legacy policy/threshold YAMLs (deferred)
- Canonical Prompt Assembly implementation (apps_qna does not call model at build time; domain card context assembly only)
- apps_rg/apps_lic/apps_research/app_underwriting_ai changes (each has their own plans)
- UWG/L4 durable write implementation for default path (local filesystem output is default; UWG only for approved future-run state)
- C0 retrieval wiring (C0 adapter calls canonical C0; retrieval implementation is separate)
- Provider SDK integration (apps_qna does not call providers directly)

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P0.1 | Governance tests entrypoint purity | `tests/governance/test_apps_qna_*.py` (6 files) | __main__.py imports builder, C0 adapter, L2 directly | ~12K | 🔲 TODO |
| P0.2 | Registry scaffold | `apps_qna/integrations/qna_capability_registry.py`, `qna_l2_step_adapters.py`, `qna_c0_adapter.py`, `qna_exit_fec_producer.py` | No canonical capability registry; no L2 step adapters | ~12K | 🔲 TODO |
| P0.3 | Entrypoint refactor target | `apps_qna/__main__.py` | Direct builder instantiation; legacy runner path | ~11K | 🔲 TODO |
| W0.1 | U0 Intake + L1 Planner | `apps_qna/u0_intake.py`, `l1_planner.py`, `types/spine_contracts.py` | No U0/L1 spine contracts | ~8K | 🔲 TODO |
| W0.2 | L0 Router + C0 Adapter scaffold | `apps_qna/l0_router.py`, `c0_adapter.py` | No canonical route resolution | ~8K | 🔲 TODO |
| W0.3 | L2 E1-E5 + Exit wiring proof | `apps_qna/l2/e{1-5}.py`, `exit_wiring.py`, `tests/test_w0_apps_qna_thin_slice.py` | No L2 stage modules; no Exit receipts | ~9K | 🔲 TODO |
| P1.5.1 | Domain Card Context Assembly | `apps_qna/card_context/*.py` (5 files) | No evidence-to-card-context shaping layer | ~15K | 🔲 TODO |
| P1.5.2 | Tier 1 Template Bodies | `apps_qna/templates/tier_1/*.md.j2` (5 files) | Placeholder text; vague generic shells | ~12K | 🔲 TODO |
| P1.5.3 | Tier 2 Template Bodies | `apps_qna/templates/tier_2/*.md.j2` (14 files) | Missing trigger metadata; overfire risk | ~13K | 🔲 TODO |
| W1.1 | U0 Intake ValidatedRequest | `apps_qna/u0_intake.py` | No canonical ValidatedRequest emission | ~7K | 🔲 TODO |
| W1.2 | L1 Planner Contract | `apps_qna/l1_planner.py`, `types/spine_contracts.py` | No L1PlanContract emission | ~7K | 🔲 TODO |
| W1.3 | L0 Route Resolution | `apps_qna/l0_router.py` | No canonical RouteContract emission | ~8K | 🔲 TODO |
| W1.4 | Spine Manifest Update | `apps_qna/spine_manifest.yaml` | Only claims build_time_compiler | ~8K | 🔲 TODO |
| W2.1 | C0 Adapter Implementation | `apps_qna/c0_adapter.py` | Calls C0 directly; no adapter boundary | ~9K | 🔲 TODO |
| W2.2 | Briefing Validator | `apps_qna/briefing_validator.py`, `types/briefing_contracts.py` | No uploaded briefing validation | ~8K | 🔲 TODO |
| W2.3 | Evidence Contract Types | `apps_qna/types/evidence_contracts.py` | No FinalEvidenceContract shape | ~9K | 🔲 TODO |
| W2.4 | C0 + Briefing Integration | `apps_qna/l1_planner.py`, `l0_router.py` | No C0/briefing routing logic | ~9K | 🔲 TODO |
| W3.1 | Two-Tier Router Core | `apps_qna/router/two_tier_router.py` | No specialist trigger metadata | ~7K | 🔲 TODO |
| W3.2 | Tier 1 Always-On Cards | `apps_qna/templates/tier_1/*.md.j2` | Not compact; missing egress verifier | ~7K | 🔲 TODO |
| W3.3 | Tier 2 Specialist Cards | `apps_qna/templates/tier_2/*.md.j2` | No narrow trigger metadata | ~8K | 🔲 TODO |
| W3.4 | Router Manifest + Selection | `apps_qna/router/two_tier_router.py` | Multiple primary routes possible | ~8K | 🔲 TODO |
| W4.1 | L2 E1 Prep | `apps_qna/l2/e1_prep.py` | No execution context binding | ~8K | 🔲 TODO |
| W4.2 | L2 E2 Valid | `apps_qna/l2/e2_valid.py` | No evidence/template validation | ~9K | 🔲 TODO |
| W4.3 | L2 E3 Execute + E4 Heal | `apps_qna/l2/e3_exec.py`, `e4_heal.py` | No deterministic render; heal invents facts | ~9K | 🔲 TODO |
| W4.4 | L2 E5 Seal | `apps_qna/l2/e5_seal.py` | No manifest with hashes; direct L4 write risk | ~9K | 🔲 TODO |
| W5.1 | Exit v6 Wiring | `apps_qna/exit_wiring.py` | No ExitReviewPacket emission | ~6K | 🔲 TODO |
| W5.2 | Egress Verifier | `apps_qna/l2/e3_exec.py` (egress checks) | No egress verification stage | ~6K | 🔲 TODO |
| W5.3 | Cache Safety R1A/R1B | `apps_qna/l0_router.py` (cache integration) | Silent semantic cache return risk | ~7K | 🔲 TODO |
| W5.4 | R5 Fallback | `apps_qna/l0_router.py` (fallback path) | No degraded pack path | ~6K | 🔲 TODO |
| W6.1 | Governance Test Sweep | `tests/governance/test_apps_qna_*.py` | Missing negative controls | ~6K | 🔲 TODO |
| W6.2 | Legacy Quarantine | `apps_qna/builder/card_pack_builder.py`, `scripts/run_qna.py` | Legacy path still reachable | ~6K | 🔲 TODO |
| W6.3 | RUNBOOK Update | `apps_qna/RUNBOOK.md` | No eval harness section | ~4K | 🔲 TODO |
| W6.4 | Acceptance Verification | `tests/test_w6_acceptance.py` | Missing acceptance criteria verification | ~4K | 🔲 TODO |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## ADG_HOTSPOT_REPORT

> Per constitutional §22, hotspot-first refactoring gate.

| Rank | Node | Layer | Fan-In | Archetype | Impact Score | Surfaces |
|------|------|-------|--------|-----------|--------------|----------|
| 1 | `apps_qna/__main__.py:main` | N/A (app entry) | High (app root) | ORCHESTRATOR | TBD | Execution, Write |
| 2 | `apps_qna/builder/card_pack_builder.py:CardPackBuilder` | L2-equivalent | High (builder) | STATE_NODE | TBD | Write, State |
| 3 | `apps_qna/integrations/spine_handoff.py:build_pack_via_spine` | L0/L2 bridge | Medium | CENTRAL_DEPENDENCY | TBD | Execution |

**Action**: Run `adg_violations` + `adg_p0_wave_plan` after plan creation to populate actual hotspot ranking.

---

## ADG_GRAPH_LAYER_EVIDENCE

> Per constitutional §22, graph-layer primitives must drive T2/T3 refactoring plans.

### Materialized Views Required

| MV | Purpose | Evidence |
|----|---------|----------|
| `mv_hotspot_centrality` | Rank apps_qna files by degree centrality | TBD |
| `mv_graph_critical_path_blast_radius` | Identify blast radius for __main__.py changes | TBD |
| `mv_graph_chokepoint_bridges` | Find import chokepoints between apps_qna and agentic_core | TBD |

### Semantic Edges Required

| Edge Type | Source → Target | Purpose |
|-----------|-----------------|---------|
| `imports` | apps_qna/__main__.py → apps_qna.scripts.run_qna | Baseline impurity |
| `imports` | apps_qna/__main__.py → apps_qna.builder.card_pack_builder | Direct L2 coupling |
| `flows_to` | apps_qna/u0_intake.py → agentic_core.L0_routing.intake | U0 spine contract |
| `flows_to` | apps_qna/l0_router.py → agentic_core.L0_routing | L0 route resolution |
| `flows_to` | apps_qna/c0_adapter.py → agentic_core.L3_orchestration | C0 grounding |

### P-Views Cross-Reference

| P-View | Expected Matches | Verification |
|--------|------------------|--------------|
| `v_p0_critical_layer_breaks` | apps_qna → agentic_core layer violations | Check after refactor |
| `v_p1_mislayered_infra` | apps_qna claiming L0/L1/L3 without delegation | Check P0 completion |
| `v_p2_duplicated_dormant` | Legacy runner vs new spine path duplication | Check W6 completion |

---

## Gap Register

**GAP-1: __main__.py impure entrypoint**
- apps_qna/__main__.py imports and calls `run_qna` from `apps_qna.scripts`
- Directly instantiates `CardPackBuilder` in legacy path
- Imports builder, C0 adapter (planned), L2 stages (planned) would violate purity
- Impact: Cannot participate in canonical spine route/capability resolution

**GAP-2: No canonical capability registry**
- apps_qna lacks `register_live_interview_pack_capability()`
- No `resolve_live_interview_pack_capability(app_name, route_id)`
- No L2 step adapters registered for qna domain
- Impact: L0 cannot resolve apps_qna capabilities

**GAP-3: No C0 adapter boundary**
- apps_qna has no `c0_adapter.py` module
- No call to canonical agentic_core C0 for grounding
- No preservation of C0 evidence refs, source refs, support status
- Impact: Grounding_required=true path cannot satisfy evidence requirements

**GAP-4: No uploaded briefing validator**
- apps_qna has no `briefing_validator.py`
- No `UploadedBriefingEvidenceContract` type
- No validation of sealed briefing packets
- Impact: Cannot bypass C0 when valid briefing provided

**GAP-5: No two-tier card architecture**
- Current templates are single-tier (22 cards)
- No Tier 1 always-on / Tier 2 specialist split
- No compact target overlay separate from raw briefing
- Impact: Cards overfire; no routing precedence; giant briefing dumps

**GAP-6: No L2 E1-E5 execution receipts**
- apps_qna lacks L2 stage modules (e1_prep, e2_valid, e3_exec, e4_heal, e5_seal)
- No `L2.E1.qna_execution_context_bound` receipts
- No manifest with evidence refs, tiering, card hashes
- Impact: Cannot prove deterministic execution; no sealed artifacts

**GAP-7: No Exit v6 / X3 integration**
- apps_qna has no `exit_wiring.py`
- No `ExitReviewPacket` with evidence coverage, tier coverage, source refs
- No single X3 disposition emission
- Impact: No governed exit control; L6 could mutate current run

**GAP-8: No cache safety (R1A exact / R1B advisory)**
- No R1A exact cache with full digest match
- No R1B semantic cache advisory-only enforcement
- Risk of silent similar-pack return
- Impact: Could return wrong interviewer panel, stale overlay

**GAP-9: Local output mislabeled as durable**
- Current `reports/qna/<slug>/` output called UWG write in some contexts
- No distinction between local sealed artifact vs L4/UWG durable state
- Impact: Violates state boundary; L2 could write L4 directly

**GAP-10: Template placeholders and generic shells**
- Current templates have minimal placeholders (better than most apps)
- But Tier 1 cards not compact; Tier 2 lacks narrow trigger metadata
- No egress verifier card with source collision rules
- Impact: Generic packs; internal label leakage; fake precision

---

## Execution Plan

### P0 — Entrypoint Purity and Core Route Resolution

**Scope**: Prevent apps_qna from behaving like a standalone static card runner. Establish governance tests, registry scaffold, and entrypoint target.

**P0.1 Governance Tests**:

Create or update tests:
- `tests/governance/test_apps_qna_entrypoint_purity.py`
- `tests/governance/test_apps_qna_route_resolution.py`
- `tests/governance/test_apps_qna_no_legacy_static_runner.py`
- `tests/governance/test_apps_qna_c0_boundary.py`
- `tests/governance/test_apps_qna_l4_write_boundary.py`
- `tests/governance/test_apps_qna_prompt_assembly_boundary.py`

Required hard tests (1-20 per user specification):
1. `test_apps_qna_main_is_pure_shim`
2. `test_apps_qna_main_does_not_import_card_builder`
3. `test_apps_qna_main_does_not_import_c0_adapter`
4. `test_apps_qna_main_does_not_import_two_tier_router`
5. `test_apps_qna_main_does_not_import_l2_stage_modules`
6. `test_apps_qna_main_does_not_import_provider_sdks`
7. `test_apps_qna_main_does_not_import_l4_write_surfaces`
8. `test_apps_qna_main_contains_no_l2_callable_construction`
9. `test_apps_qna_main_contains_no_inline_card_render_closure`
10. `test_apps_qna_no_legacy_runner_feature_flag_for_grounded_path`
11. `test_apps_qna_legacy_static_runner_not_reachable_for_grounded_interview_path`
12. `test_apps_qna_core_runner_resolves_live_pack_capability`
13. `test_apps_qna_route_registry_selects_single_action_with_grounding_flag`
14. `test_apps_qna_grounded_route_requires_c0_or_uploaded_briefing`
15. `test_apps_qna_direct_path_uses_no_l3`
16. `test_apps_qna_route_resolution_failure_fails_closed_through_exit`
17. `test_apps_qna_no_generic_pack_when_grounding_required`
18. `test_apps_qna_no_direct_l4_writes`
19. `test_apps_qna_no_provider_calls_in_build_path`
20. `test_apps_qna_exit_emits_x3_but_does_not_write_l4`

**P0.2 Registry Scaffold**:

Create:
- `apps_qna/integrations/qna_capability_registry.py`
- `apps_qna/integrations/qna_l2_step_adapters.py`
- `apps_qna/integrations/qna_c0_adapter.py`
- `apps_qna/integrations/qna_exit_fec_producer.py`

Required exports:
- `register_live_interview_pack_capability()`
- `resolve_live_interview_pack_capability(app_name, route_id)`
- `register_qna_l2_steps()`
- `get_qna_step_adapter(step_name)`

Required routes:
- `apps_qna.live_interview_runtime_pack_v1` (R4_SINGLE_ACTION, grounding_required=true)
- `apps_qna.live_interview_runtime_pack_from_uploaded_brief_v1` (R4_SINGLE_ACTION, uploaded_briefing_required=true)

**P0.3 Entrypoint Target**:

Refactor `apps_qna/__main__.py`:
- Parse CLI args only
- Build raw request envelope only
- Call canonical agentic_core runner with `app_name="apps_qna"`
- Fail closed if runner/capability unavailable
- Never fallback to legacy static runner for grounded interview path

**Commands**:
```bash
python -m pytest tests/governance/test_apps_qna_*.py -v --tb=short
python -m apps_qna --help  # verify pure entrypoint
```

**Acceptance**: 20 governance tests pass; registry scaffold compiles; entrypoint imports only CLI-safe types.

---

### W0 — Thin-Slice Spine Proof Before Full Refactor

**Scope**: Prove the smallest runnable spine-correct apps_qna path before expanding waves.

**W0 Files to Create**:
- `apps_qna/u0_intake.py`
- `apps_qna/l1_planner.py`
- `apps_qna/l0_router.py`
- `apps_qna/c0_adapter.py`
- `apps_qna/briefing_validator.py`
- `apps_qna/types/spine_contracts.py`
- `apps_qna/types/briefing_contracts.py`
- `apps_qna/types/evidence_contracts.py`
- `apps_qna/types/assembly_types.py`
- `apps_qna/l2/e1_prep.py`
- `apps_qna/l2/e2_valid.py`
- `apps_qna/l2/e3_exec.py`
- `apps_qna/l2/e4_heal.py`
- `apps_qna/l2/e5_seal.py`
- `apps_qna/router/two_tier_router.py`
- `apps_qna/exit_wiring.py`
- `tests/test_w0_apps_qna_thin_slice.py`
- `tests/fixtures/apps_qna/mock_c0.py`
- `tests/fixtures/apps_qna/valid_briefing_fixture.py`
- `tests/fixtures/apps_qna/minimal_interview_config.yaml`

**W0 Files to Modify**:
- `apps_qna/__main__.py` (shim mode)
- `apps_qna/spine_manifest.yaml` (add R4_SINGLE_ACTION route)
- `apps_qna/types/qna_types.py` (extend if needed)
- `apps_qna/builder/card_pack_builder.py` (legacy path shim)
- `apps_qna/integrations/spine_handoff.py` (integration check)

**W0 Tests** (11 tests):
1. `test_apps_qna_u0_emits_validated_request`
2. `test_apps_qna_l1_emits_plan_contract`
3. `test_apps_qna_l0_emits_single_route_contract`
4. `test_apps_qna_uploaded_briefing_bypasses_c0`
5. `test_apps_qna_mock_c0_returns_final_evidence_contract`
6. `test_apps_qna_l2_renders_two_tier_pack`
7. `test_apps_qna_exit_emits_x3_disposition`
8. `test_apps_qna_manifest_has_evidence_refs`
9. `test_apps_qna_manifest_has_tiering_and_hashes`
10. `test_apps_qna_no_direct_l2_to_l4_write`
11. `test_apps_qna_existing_static_build_not_broken_or_explicitly_deprecated`

**Commands**:
```bash
python -m pytest tests/test_w0_apps_qna_thin_slice.py -v
python -m apps_qna --interview test-w0 --company TestCo --dry-run --w0-mode
python -m apps_qna --interview test-w0 --company TestCo --briefing tests/fixtures/apps_qna/valid_briefing_fixture.json --dry-run --w0-mode
```

**Acceptance**: All 11 W0 tests pass; U0→L1→L0→L2→Exit proven; existing static path not broken (or explicitly deprecated with shim).

---

### P1.5 — Two-Tier Card Template Bodies and Domain Card Context Assembly

**Scope**: Ensure apps_qna has real, implementation-grade two-tier card templates and domain card-context assembly layer.

**P1.5.1 Domain Card Context Assembly**:

Create:
- `apps_qna/card_context/card_context_assembler.py`
- `apps_qna/card_context/context_budget.py`
- `apps_qna/card_context/overlay_compressor.py`
- `apps_qna/card_context/personalization_hook_selector.py`
- `apps_qna/card_context/no_claim_list_builder.py`
- `apps_qna/card_context/domain_card_context_schema.py`

Domain Card Context Assembly owns:
- evidence-to-card-context shaping
- target overlay compression
- personalization hook selection
- no-claim list generation
- card render input construction
- card budget metadata

Must NOT:
- retrieve, route, call providers, execute tools
- emit Exit disposition, write durable state
- upgrade weak evidence to strong
- treat uploaded briefing or C0 evidence as instruction

**P1.5.2 Tier 1 Template Bodies** (5 files):

Create or update:
- `apps_qna/templates/tier_1/00_start_here_runtime_root.md.j2`
- `apps_qna/templates/tier_1/00a_source_set_and_egress_verifier.md.j2`
- `apps_qna/templates/tier_1/01_card_selection_manifest.md.j2`
- `apps_qna/templates/tier_1/03_interviewer_lens_and_company_bridge.md.j2`
- `apps_qna/templates/tier_1/nn_target_company_interviewer_overlay.md.j2`

Template body requirements:
- No placeholders, no TODO, no "insert here"
- Concrete implementation-grade live runtime instructions
- Tier 1 cards must be compact
- Target overlay must be compact and passive
- Full raw C0 briefing must not be dumped into overlay
- Every unsupported personal claim must be blocked or listed in no-claim list

**P1.5.3 Tier 2 Template Bodies** (14 files):

Create or update:
- `apps_qna/templates/tier_2/star_proof.md.j2`
- `apps_qna/templates/tier_2/star_failure_learning.md.j2`
- `apps_qna/templates/tier_2/rag_context.md.j2`
- `apps_qna/templates/tier_2/governance_hitl.md.j2`
- `apps_qna/templates/tier_2/tools_mcp_gateway.md.j2`
- `apps_qna/templates/tier_2/agentic_architecture.md.j2`
- `apps_qna/templates/tier_2/ds_to_platform.md.j2`
- `apps_qna/templates/tier_2/platform_productization.md.j2`
- `apps_qna/templates/tier_2/client_advisory_roi.md.j2`
- `apps_qna/templates/tier_2/role_scope_mandate.md.j2`
- `apps_qna/templates/tier_2/exec_translation_fit.md.j2`
- `apps_qna/templates/tier_2/cross_exam_depth.md.j2`
- `apps_qna/templates/tier_2/hardest_genai_default_story.md.j2`
- `apps_qna/templates/tier_2/routing_evals_and_edge_cases.md.j2`

Each Tier 2 template must include:
- Frontmatter name, description with exact triggers
- Purpose, trigger rules, hard gates, answer shape
- Failure patterns, readout realism rules
- Optional compact examples
- No broad always-on instructions

**Acceptance**: All Tier 1/2 templates have real bodies (no placeholders); domain card context assembly layer exists with clear boundaries.

---

### W1 — Route Model + U0/L1/L0 Spine Contracts

**Scope**: Implement U0 Intake, L1 Planner, L0 Router with canonical contracts.

**W1.1 U0 Intake**:
- `apps_qna/u0_intake.py` emits `ValidatedRequest`
- Parse CLI args into canonical envelope
- Schema validation per Interview type

**W1.2 L1 Planner**:
- `apps_qna/l1_planner.py` emits `L1PlanContract`
- Plan evidence requirements
- Determine grounding_required flag

**W1.3 L0 Router**:
- `apps_qna/l0_router.py` emits `RouteContract`
- Resolve capability: `apps_qna.live_interview_runtime_pack_v1`
- Route family: R4_SINGLE_ACTION
- Set grounding_required, c0_required, uploaded_briefing_required flags

**W1.4 Spine Manifest Update**:
- Update `apps_qna/spine_manifest.yaml`
- Add claimed route: `R4_SINGLE_ACTION`
- Document execution_form: SINGLE_STEP
- Document l3_required: false
- Document authority contracts required

**Acceptance**: U0, L1, L0 all emit canonical contracts; router selects exactly one route; no L3 by default.

---

### W2 — C0 Adapter + Uploaded Briefing Evidence Contract

**Scope**: Implement C0 adapter boundary and uploaded briefing validation.

**W2.1 C0 Adapter**:
- `apps_qna/c0_adapter.py` calls canonical agentic_core C0
- Shape app-specific C0 request from interview config
- Return canonical FinalEvidenceContract unchanged
- Preserve C0 evidence refs, source refs, support status, freshness
- Fail closed if canonical C0 unavailable
- Never fabricate research, retrieve independently, or score evidence locally

**W2.2 Briefing Validator**:
- `apps_qna/briefing_validator.py` validates uploaded sealed briefings
- `apps_qna/types/briefing_contracts.py` defines UploadedBriefingEvidenceContract
- Fields: briefing_id, briefing_hash, created_at, max_age, source_register_ref, interviewer_coverage[], company_context_status, role_context_status, supported_claims[], unsupported_claims[], no_claim_list[], freshness_status, evidence_sufficiency, policy_hash, blueprint_hash, schema_version, audit_refs[]

**W2.3 Evidence Contract Types**:
- `apps_qna/types/evidence_contracts.py`
- FinalEvidenceContract shape for C0 output
- Interviewer coverage summary, company/role context summary
- Public writing/speaking summary, likely_interviewer_lens
- Allowed/prohibited personalization hooks
- Source register, freshness report, contradiction report
- No_claim_list, target_overlay_inputs, specialist_card_context_hints

**W2.4 Integration**:
- L1 Planner: route to C0 path vs uploaded briefing path
- L0 Router: set flags based on evidence availability
- Fail closed if grounding required but no evidence available

**Acceptance**: C0 adapter calls canonical C0 only; briefing validator exists with all states (SUFFICIENT, STALE, INCOMPLETE, MISMATCH, INVALID_HASH, UNSAFE_ORIGIN, UNSUPPORTED); evidence contracts properly typed.

---

### W3 — Two-Tier Router + Card Architecture

**Scope**: Implement two-tier card router and specialist selection.

**W3.1 Two-Tier Router Core**:
- `apps_qna/router/two_tier_router.py`
- Route family: R4_SINGLE_ACTION
- Route IDs: `apps_qna.live_interview_runtime_pack_v1`, `apps_qna.live_interview_runtime_pack_from_uploaded_brief_v1`
- Select exactly one primary route by precedence
- Attach support cards only when required

**W3.2 Tier 1 Always-On Cards**:
- Compact always-on cards
- 00_START_HERE_RUNTIME_ROOT (live q-prefix rule, non-q ingest-only)
- 00A_SOURCE_SET_AND_EGRESS_VERIFIER (source collision, fake precision blocking)
- 01_CARD_SELECTION_MANIFEST (mode gate, route precedence)
- 03_INTERVIEWER_LENS_AND_COMPANY_BRIDGE
- NN_TARGET_COMPANY_INTERVIEWER_OVERLAY

**W3.3 Tier 2 Specialist Cards**:
- Trigger-selected only
- STAR_PROOF, STAR_FAILURE_LEARNING, RAG_CONTEXT, GOVERNANCE_HITL, TOOLS_MCP_GATEWAY, AGENTIC_ARCHITECTURE, DS_TO_PLATFORM, PLATFORM_PRODUCTIZATION, CLIENT_ADVISORY_ROI, ROLE_SCOPE_MANDATE, EXEC_TRANSLATION_FIT, CROSS_EXAM_DEPTH, HARDEST_GENAI_DEFAULT_STORY, ROUTING_EVALS_AND_EDGE_CASES

**W3.4 Router Manifest**:
- Card selection manifest with evidence refs
- Route precedence rules
- Support card attachment rules
- Card budget metadata

**Acceptance**: Router selects exactly one primary route; Tier 1 always-on, Tier 2 trigger-selected; no overfire; ambiguity resolved by precedence not accumulation.

---

### W4 — L2 E1-E5 Deterministic Render + Seal

**Scope**: Implement L2 execution stages with deterministic render and seal.

**W4.1 L2.E1 Prep**:
- `apps_qna/l2/e1_prep.py`
- Verify route_family = R4_SINGLE_ACTION
- Verify execution_form = SINGLE_STEP
- Verify side_effect_class = FILESYSTEM_SANDBOX_WRITE
- Verify evidence present (FinalEvidenceContract or UploadedBriefingEvidenceContract)
- Bind execution context
- Receipt: `L2.E1.qna_execution_context_bound`

**W4.2 L2.E2 Valid**:
- `apps_qna/l2/e2_valid.py`
- Validate interview config schema
- Validate company, role, interviewer set present
- Validate evidence status usable (PASS, WEAK_WITH_CAVEATS, or SUFFICIENT)
- Verify source refs exist for target overlay claims
- Verify no unsupported claims in overlay
- Verify Tier 1/2 templates exist with real bodies
- Verify semantic cache did not auto-return similar pack
- Receipt: `L2.E2.qna_evidence_and_template_validated`

**W4.3 L2.E3 Execute + E4 Heal**:
- `apps_qna/l2/e3_exec.py` - Render Tier 1 cards, Tier 2 specialist cards, compact target overlay, card selection manifest, routing evals, source register, no-claim list, CardPackManifest draft
- `apps_qna/l2/e4_heal.py` - Allowed: repair markdown formatting, file naming, card ordering, trim over-budget overlay, add caveat. Forbidden: retrieve new evidence, call provider, change route, invent facts, upgrade weak evidence, write L4
- Receipts: `L2.E3.qna_card_pack_rendered`, `L2.E4.qna_local_heal_applied`

**W4.4 L2.E5 Seal**:
- `apps_qna/l2/e5_seal.py`
- sealed_qna_artifact, CardPackManifest, per-card hashes, source_register, no_claim_list, target_overlay_ref, evidence contract ref, card_budget_report, route_selection_manifest, template registry hash, manifest_hash, policy_hash, blueprint_hash, replay refs, trace refs, terminal class, local output path
- Receipt: `L2.E5.qna_artifact_sealed`

**Acceptance**: All L2 E1-E5 receipts emitted; manifest has evidence refs, tiering, card hashes; no direct L2→L4 write.

---

### W5 — Exit v6 + Egress Verifier + Cache Safety

**Scope**: Integrate Exit v6, egress verification, and cache safety.

**W5.1 Exit v6 Wiring**:
- `apps_qna/exit_wiring.py`
- apps_qna FEC producer attaches: route_id, route_family, execution_form, grounding_required, c0_required, c0_invoked, uploaded_briefing_used, evidence sufficiency, interviewer/company/role coverage, source register, no-claim list, target overlay coverage, Tier 1/2 card lists, card selection manifest, card budget report, egress verifier presence, forbidden label scan, unsupported claim scan, fake precision scan, local artifact path, manifest hash
- Exit emits exactly one X3: ALLOW_FINISH, SAFE_ABSTAIN, SAFE_FALLBACK, REROUTE, ESCALATE_HITL, DENY/BLOCK_COMMIT

**W5.2 Egress Verifier**:
- Embedded in L2.E3
- Final verifier role: source collision rule, unsupported claim blocking, fake precision blocking, no invented metrics, no unsupported company/interviewer claims, no forced company bridge for pure technical questions, no vendor-first technical answer, readout realism check

**W5.3 Cache Safety R1A/R1B**:
- R1A Exact Cache: requires full material digest match (interview YAML hash, company/role/interviewer identity, template registry version, evidence snapshot hash, policy_hash, blueprint_hash)
- R1B Semantic Cache: advisory only, never silent terminal return
- Must not silently return similar prior pack with wrong interviewer or stale overlay

**W5.4 R5 Fallback**:
- Emergency degraded pack only when explicitly degraded
- Clearly marked degraded, no personalization claims
- Minimal Tier 1 controls only
- Pass through Exit as SAFE_FALLBACK

**Acceptance**: Exit emits exactly one X3; egress verifier blocks internal labels and fake precision; cache safety prevents silent wrong-pack return; R5 fallback marked degraded.

---

### W6 — Acceptance Sweep + Legacy Quarantine + Docs

**Scope**: Governance test sweep, legacy path deprecation/shim, documentation update.

**W6.1 Governance Test Sweep**:

Add remaining governance tests (21-57 per user specification):
21. `test_apps_qna_tier_1_cards_exist`
22. `test_apps_qna_tier_1_cards_are_always_on`
23. `test_apps_qna_tier_2_cards_are_not_always_on`
24. `test_apps_qna_specialist_cards_have_narrow_trigger_metadata`
25. `test_apps_qna_router_selects_exactly_one_primary_route`
26. `test_apps_qna_support_cards_attach_only_when_required`
27. `test_apps_qna_ambiguity_resolved_by_precedence_not_card_accumulation`
28. `test_apps_qna_target_overlay_is_passive_and_compact`
29. `test_apps_qna_target_overlay_does_not_dump_raw_briefing`
30. `test_apps_qna_no_placeholder_card_templates`
31. `test_apps_qna_non_q_prompt_ingest_only`
32. `test_apps_qna_q_prompt_generates_live_answer`
33. `test_apps_qna_diagnostics_bypass_live_answer_mode`
34. `test_apps_qna_egress_blocks_internal_card_names`
35. `test_apps_qna_egress_blocks_raw_layer_labels`
36. `test_apps_qna_egress_blocks_fake_precision`
37. `test_apps_qna_egress_blocks_unsupported_company_claims`
38. `test_apps_qna_egress_blocks_vendor_first_technical_answer`
39. `test_apps_qna_egress_blocks_vector_db_equals_rag`
40. `test_apps_qna_egress_blocks_mcp_equals_authority`
41. `test_apps_qna_l2_e1_binds_execution_context`
42. `test_apps_qna_l2_e2_validates_evidence_and_templates`
43. `test_apps_qna_l2_e3_renders_two_tier_pack`
44. `test_apps_qna_l2_e4_heal_cannot_invent_facts`
45. `test_apps_qna_l2_e5_seals_manifest_and_hashes`
46. `test_apps_qna_exit_receives_sealed_l2_artifact`
47. `test_apps_qna_exit_emits_exactly_one_x3`
48. `test_apps_qna_no_direct_l4_write`
49. `test_apps_qna_l6_after_runtime_only`
50. `test_apps_qna_local_output_not_uwg_write`
51. `test_apps_qna_r1a_exact_cache_requires_full_digest_match`
52. `test_apps_qna_r1a_misses_on_interviewer_change`
53. `test_apps_qna_r1a_misses_on_evidence_snapshot_change`
54. `test_apps_qna_r1b_semantic_cache_is_advisory_only`
55. `test_apps_qna_r1b_never_silent_terminal_return`
56. `test_apps_qna_r5_fallback_marked_degraded`
57. `test_apps_qna_r5_fallback_no_personalization_claims`

**W6.2 Legacy Quarantine**:
- Option A: Deprecate `apps_qna/scripts/run_qna.py` and `CardPackBuilder` direct path with `apps_shared.config.legacy_yaml_deprecation` pattern
- Option B: Shim legacy path through new spine via compatibility adapter
- Decision: Author-Gate required at W6.2

**W6.3 RUNBOOK Update**:
- Update `apps_qna/RUNBOOK.md` with "## Eval Harness" section per apps-eval-harness-closeout-b7c9d2 pattern
- Document rubric, threshold, hitl_policy
- Document gate run command
- Document ledger pointers

**W6.4 Acceptance Verification**:
- Create `tests/test_w6_acceptance.py` with 57 governance test sweep
- Verify negative controls fail closed
- Verify acceptance criteria per user specification

**Commands**:
```bash
python -m pytest tests/governance/test_apps_qna_*.py tests/test_w0_apps_qna_thin_slice.py tests/test_w6_acceptance.py -v
python -m apps_qna --interview acceptance-test --company TestCo --dry-run
```

**Acceptance**: 57 governance tests pass; RUNBOOK updated; legacy path quarantined or shimmed; acceptance criteria verification complete.

---

## Rules

1. **Entrypoint purity**: `__main__.py` is pure shim; never imports builder, C0 adapter, L2 stages, provider SDKs, L4 write surfaces
2. **Capability registry**: agentic_core owns route/capability resolution; apps_qna owns domain declarations and adapters only
3. **Direct path uses no L3**: Default apps_qna is not an L3 managed workflow; no Hop 1/2/3/4 terminology in direct path
4. **C0 grounding**: `grounding_required=true` requires canonical C0 FinalEvidenceContract or valid UploadedBriefingEvidenceContract
5. **C0 adapter boundary**: C0 adapter calls canonical C0 only; never retrieves independently, fabricates research, or scores evidence locally
6. **Briefing is not C0 FEC**: UploadedBriefingEvidenceContract is distinct from C0 FinalEvidenceContract; never mislabel
7. **Domain card context assembly**: Explicitly not canonical Prompt Assembly; no PA unless emitting CompiledPromptArtifact
8. **Two-tier cards**: Tier 1 always-on (compact), Tier 2 specialist (trigger-selected with narrow metadata)
9. **Router selects exactly one**: Ambiguity resolved by precedence, not card accumulation
10. **Target overlay compact**: Passive, evidence-backed, no raw briefing dump
11. **L2 heal discipline**: Cannot invent facts, retrieve, call provider, change route, upgrade weak evidence, write L4
12. **Exit exactly one X3**: Exit emits exactly one X3 disposition; no multiple X3s
13. **Local output ≠ UWG**: `reports/qna/<slug>/` is local sealed artifact, not UWG/L4 durable state
14. **L6 after runtime only**: L6 learns only after Exit; never mutates current run
15. **Negative controls fail closed**: All failure modes result in safe abstain, fallback, or exit denial

---

## Success Criteria

- [ ] `__main__.py` is pure shim; imports only CLI-safe types
- [ ] 57 governance tests pass (entrypoint, C0 boundary, L2 discipline, Exit, cache, egress)
- [ ] U0 Intake emits canonical ValidatedRequest
- [ ] L1 Planner emits canonical L1PlanContract
- [ ] L0 Router emits canonical RouteContract with correct flags
- [ ] C0 Adapter calls canonical agentic_core C0 only
- [ ] Briefing Validator exists with all evidence states
- [ ] Two-tier card architecture: Tier 1 always-on, Tier 2 trigger-selected
- [ ] Router selects exactly one primary route by precedence
- [ ] L2 E1-E5 receipts emitted with proper validation
- [ ] Exit v6 emits exactly one X3 disposition
- [ ] CardPackManifest has evidence refs, tiering, card hashes, source register
- [ ] No direct L2→L4 write
- [ ] R1A exact cache requires full digest match
- [ ] R1B semantic cache advisory-only
- [ ] R5 fallback marked degraded
- [ ] Local output is sandboxed filesystem write, not UWG/L4
- [ ] RUNBOOK updated with Eval Harness section
- [ ] Legacy static path deprecated or shimmed

---

## Implementation Commands

```bash
# P0: Governance tests + registry scaffold
python -m pytest tests/governance/test_apps_qna_*.py -v

# W0: Thin-slice proof
python -m pytest tests/test_w0_apps_qna_thin_slice.py -v

# W1-W5: Feature waves
python -m pytest tests/test_w1_*.py tests/test_w2_*.py tests/test_w3_*.py tests/test_w4_*.py tests/test_w5_*.py -v

# W6: Acceptance sweep
python -m pytest tests/test_w6_acceptance.py tests/governance/test_apps_qna_*.py -v

# Full suite
python -m pytest tests/ -k "apps_qna" --tb=short -q

# Entrypoint verification
python -m apps_qna --help
python -m apps_qna --interview test --company TestCo --dry-run
```

---

## Rollback Strategy

If things go wrong:
1. Revert `apps_qna/__main__.py` to pre-P0 state (legacy runner still functional)
2. Remove governance tests (do not break existing test suite)
3. Delete W0-W6 created files (keep P0.2 registry scaffold for future attempts)
4. Restore `apps_qna/spine_manifest.yaml` to original state
5. Document failure mode in plan file for next attempt

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Governance tests passing | 57/57 | `pytest tests/governance/test_apps_qna_*.py` |
| W0 thin-slice tests passing | 11/11 | `pytest tests/test_w0_apps_qna_thin_slice.py` |
| Entrypoint import count | ≤5 imports | Static analysis of `__main__.py` |
| Route contracts emitted | 2 routes | U0/L1/L0 integration tests |
| X3 dispositions per run | Exactly 1 | Exit wiring tests |
| Direct L4 writes | 0 | Governance tests + ADG edge check |
| Template placeholders | 0 | Manual review + lint |
| Legacy path functional | Yes (deprecated) | Backward compatibility test |

---

## Cursor Agent Alignment Checks

- **Plan type**: refactor → ADG graph-layer evidence required (§22)
- **Tier**: T3 (multi-wave, cross-layer, architecture decisions)
- **Structured reasoning**: SR_INTAKE → SR_PLAN → SR_APPROVAL → SR_EXECUTE → SR_VERIFY
- **ADG first**: Hotspot report + graph-layer evidence sections present
- **Memory lifecycle**: Session start recalled; plan-end writeback to memory/notion required
- **MCP serialization**: Remote MCPs (notion) one-per-response per §25
- **Notion wave deferral**: Mid-plan Notion writes blocked per §35; batch at plan completion

---

## AG_QUEUE_SEED

AG_QUEUE_SEED: plan=apps-qna-spine-alignment-a7f4c2 id=w6-legacy-path-decision depends_on=w6.1 title="W6.2 Legacy Path: Deprecate vs Shim"
AG_QUEUE_SEED: plan=apps-qna-spine-alignment-a7f4c2 id=w0-acceptance-early depends_on=w0.3 title="W0 Early Exit: Is thin-slice sufficient?"
AG_QUEUE_SEED: plan=apps-qna-spine-alignment-a7f4c2 id=p1.5-template-audit depends_on=p0.3 title="P1.5 Template Audit: Keep or Replace?"

---

PLAN_CREATED: slug=apps-qna-spine-alignment-a7f4c2 path=.windsurf/plans/apps-qna-spine-alignment-a7f4c2.md waves=7 phases=33 tokens=275K
