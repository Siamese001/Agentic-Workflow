---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-qna-spine-integration-e9c5b3.md'
original_relative_path: '_archive\\2026-05\\apps-qna-spine-integration-e9c5b3.md'
source_sha256: c2a9efd8cf6bc95f2c989b0530fe38b1c6d184ac5db5c4b718e541dfdef0746e
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-qna-spine-integration-e9c5b3
plan_type: refactor
---

# apps_qna Spine Integration — Unified Grounded Runtime Refactor

Merge and streamline two prior plans (a7f4c2, d7e3a1) into one integrated zero-loss refactor. Transform apps_qna from static template compiler to governed, evidence-backed, two-tier live interview runtime pack compiler riding the canonical agentic_core spine.

**Retires**: `apps-qna-spine-alignment-a7f4c2` (Deprioritized) + `apps-qna-grounded-spine-refactor-v2-d7e3a1` (Deprioritized)  
**Integrated**: This plan supersedes both with optimized wave structure and deduplicated deliverables.

---

## Context (SCQA)

**Situation** — Two plans emerged for apps_qna spine alignment: a7f4c2 (comprehensive but ~275K tokens, 33 phases) and d7e3a1 (refined architecture, ~245K tokens, 30 phases). Both currently Deprioritized in Notion. apps_qna remains a static card builder with impure __main__.py, no canonical C0 integration, no two-tier architecture, no Exit v6/X3 control, and risks repeating wiring failures seen in apps_lic/apps_rg/apps_research.

**Complication** — apps_qna needs live interview runtime capability with interviewer/company/person personalization through canonical spine (U0→L1→L0→C0→L2→Exit). Must distinguish C0 FinalEvidenceContract from UploadedBriefingEvidenceContract, use R4_SINGLE_ACTION routes, emit domain card context (not canonical Prompt Assembly), and produce sealed local artifacts (not UWG/L4 by default). Prior plans had overlapping coverage and redundant phases.

**Question** — How do we integrate, deduplicate, and streamline the two prior plans into one executable plan that delivers spine-correct grounded runtime in minimal waves with clear acceptance criteria?

**Answer** — Unified 5-wave structure: W0 (thin-slice spine proof), W1 (entrypoint purity + registry), W2 (C0 adapter + briefing), W3 (two-tier router + templates), W4 (Exit + egress + cache + acceptance). Consolidates 57 governance tests, thin C0 adapter, distinct evidence contracts, canonical R4_SINGLE_ACTION routes, explicit domain assembly, local artifact output, and L6 shadow-only evaluation.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `apps_qna/__main__.py` | Entrypoint impurity baseline | ✅ |
| `apps_qna/spine_manifest.yaml` | Current route claims (build_time_compiler only) | ✅ |
| `apps_qna/builder/card_pack_builder.py` | Legacy builder coupling | ✅ |
| `apps_qna/integrations/spine_handoff.py` | Existing ValidatedRequest wrapper | ✅ |
| `agentic_core/L0_routing/types/route_contract_v15.py` | Canonical RouteIdV15, ExecutionFormV15 | 🔲 |
| `agentic_core/L3_orchestration/types/c0_evidence_contract_types.py` | C0EvidenceContract shape | 🔲 |
| Prior plans a7f4c2 + d7e3a1 | Consolidated requirements | ✅ |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| W0 | W0.1-W0.4 | Thin-slice spine proof (U0→L1→L0→C0/Briefing→L2→Exit) | ~35K | ✅ DONE | 18 tests pass; spine contracts emit correctly |
| W1 | W1.1-W1.3 | Entrypoint purity + registry scaffold + governance | ~30K | ✅ DONE | __main__.py pure shim; 20 governance tests green |
| W2 | W2.1-W2.4 | C0 thin adapter + briefing validator + evidence contracts | ~40K | ✅ DONE | C0 calls canonical only; briefing distinct from C0 |
| W3 | W3.1-W3.4 | Two-tier router + Tier 1/2 templates + domain assembly | ~50K | ✅ DONE | Router selects 1 primary; Tier 1 always-on, Tier 2 trigger |
| W4 | W4.1-W4.4 | Exit v6 wiring + egress verifier + cache + acceptance | ~45K | ✅ DONE | Single X3 per run; 86 tests pass; legacy shimmed |

**Total: ~200K tokens across 5 waves, 18 phases** (streamlined from ~275K/33 phases)

---

## Out Of Scope

- Real LLM-judge implementations (stubs acceptable)
- Production-log mining with PII redaction
- Holdout vs dev eval-set separation
- Per-app rubric migrations to new grader types
- SSOT consolidation of legacy YAMLs
- Canonical Prompt Assembly (apps_qna does domain card context assembly only)
- UWG/L4 durable write for default path (local filesystem is default)
- C0 retrieval implementation (adapter calls canonical; retrieval is separate)
- Provider SDK integration (apps_qna does not call providers)
- Other apps (apps_rg/apps_lic/apps_research have own plans)

---

## Phase-Level Summary

| Phase ID | Title | Scope | Est. Tokens | Status |
|----------|-------|-------|-------------|--------|
| W0.1 | U0 Intake + L1 Plan | `u0_intake.py`, `l1_planner.py`, `types/spine_contracts.py` | ~8K | ✅ DONE |
| W0.2 | L0 Router + C0 Adapter scaffold | `l0_router.py`, `c0_adapter.py` | ~9K | ✅ DONE |
| W0.3 | Briefing Validator + L2 E1-E3 | `briefing_validator.py`, `l2/e1_prep.py`, `e2_valid.py`, `e3_exec.py` | ~10K | ✅ DONE |
| W0.4 | Exit wiring + W0 tests | `exit_wiring.py`, `tests/test_w0_thin_slice.py` | ~8K | ✅ DONE |
| W1.1 | Entrypoint purity refactor | `__main__.py` (shim only), remove direct builder imports | ~10K | ✅ DONE |
| W1.2 | Registry scaffold | `qna_capability_registry.py`, `qna_l2_step_adapters.py`, `qna_exit_fec_producer.py` | ~10K | ✅ DONE |
| W1.3 | Governance tests (20 tests) | `tests/governance/test_apps_qna_*.py` | ~10K | ✅ DONE |
| W2.1 | C0 thin adapter | `c0_adapter.py` (shape request, call canonical, return unchanged) | ~10K | ✅ DONE |
| W2.2 | Briefing validator | `briefing_validator.py`, `types/briefing_contracts.py` | ~10K | ✅ DONE |
| W2.3 | Evidence contract types | `types/evidence_contracts.py` (FinalEvidenceContract, UploadedBriefingEvidenceContract) | ~10K | ✅ DONE |
| W2.4 | Evidence integration tests | `tests/test_w2_evidence_paths.py` | ~10K | ✅ DONE |
| W3.1 | Two-tier router core | `router/two_tier_router.py`, route precedence rules | ~12K | ✅ DONE |
| W3.2 | Tier 1 template bodies | `templates/tier_1/*.md.j2` (4 cards: 00, 00A, 01, 03) | ~12K | ✅ DONE |
| W3.3 | Tier 2 specialist specs | `templates/tier_2/*.md.j2` (14 specialists), `card_specs/tier_2.py` | ~14K | ✅ DONE |
| W3.4 | Domain card context assembly | `card_context/card_context_assembler.py`, `context_budget.py`, `overlay_compressor.py` | ~12K | ✅ DONE |
| W4.1 | L2 E4-E5 + egress verifier | `l2/e4_heal.py`, `e5_seal.py`, `egress/blocking_rules.py` | ~12K | ✅ DONE |
| W4.2 | Exit v6 wiring + FEC producer | `exit_wiring.py`, `qna_exit_fec_producer.py` | ~11K | ✅ DONE |
| W4.3 | Cache safety (R1A/R1B/R5) | `cache/r1a_exact.py`, `r1b_semantic.py`, `r5_fallback.py` | ~12K | ✅ DONE |
| W4.4 | Acceptance sweep + legacy quarantine | `tests/test_acceptance.py`, RUNBOOK/docs updates, legacy shim | ~10K | ✅ DONE |

---

## Consolidated Gap Register

**GAP-1: __main__.py impure entrypoint**
- Imports `run_qna` from scripts, instantiates CardPackBuilder directly
- Resolution: W1.1 makes __main__.py pure CLI envelope parser only

**GAP-2: No canonical capability registry**
- Missing `register_live_interview_pack_capability()`, L2 step adapters
- Resolution: W1.2 creates registry scaffold

**GAP-3: No C0 adapter boundary**
- No thin adapter to canonical C0; risk of parallel C0 implementation
- Resolution: W2.1 thin adapter only (shape request, call canonical, return unchanged)

**GAP-4: No uploaded briefing validator**
- No UploadedBriefingEvidenceContract distinct from C0 contract
- Resolution: W2.2 briefing validation with SUFFICIENT/STALE/INCOMPLETE/MISMATCH states

**GAP-5: No two-tier card architecture**
- Flat 22-card structure; no Tier 1 always-on / Tier 2 specialist split
- Resolution: W3.2-W3.3 implement 4 Tier 1 always-on + 14 Tier 2 trigger-selected

**GAP-6: No L2 E1-E5 execution receipts**
- No stage modules, no manifest with evidence refs/hashes
- Resolution: W0.3, W4.1 implement E1-E5 with sealed artifacts

**GAP-7: No Exit v6 / X3 integration**
- No ExitReviewPacket, no single X3 disposition
- Resolution: W0.4, W4.2 wire Exit with exactly one X3 per run

**GAP-8: Cache safety gaps**
- Risk of silent semantic cache return with wrong interviewer/stale overlay
- Resolution: W4.3 R1A exact (full digest), R1B advisory-only, R5 marked degraded

**GAP-9: Local output mislabeled as durable**
- Confusion between reports/qna/ local artifact vs UWG/L4 state
- Resolution: W4.4 clarify local filesystem only; UWG for optional future commit path only

---

## Target Architecture

```
USER (CLI: python -m apps_qna --interview <slug> [--briefing <path>])
 |
 v
U0 Intake ────────────────────────────────────────────────────────────►
 |   • CLI envelope → ValidatedRequest (request_id, trace_root, hashes)
 v
L1 Plan ──────────────────────────────────────────────────────────────►
 |   • Declare: C0 required OR briefing sufficient
 |   • Emit: L1PlanContract
 v
L0 Route ─────────────────────────────────────────────────────────────►
 |   • Check R1A exact cache ──► [RET] if digest match
 |   • Select: exactly one RouteContract (R4_SINGLE_ACTION)
 v
C0 Context Engine (via thin adapter) ──────────────────────────────────►
 |   • Canonical agentic_core C0 (not parallel implementation)
 |   • Required if no briefing OR briefing invalid
 |   • Emits: canonical FinalEvidenceContract
 |   • Production unavailable → Exit SAFE_ABSTAIN (fail-closed)
 |
Briefing Bypass Path (alternative) ──────────────────────────────────►
 |   • Validate uploaded sealed briefing
 |   • On pass → emit UploadedBriefingEvidenceContract (distinct from C0)
 |   • On fail → route to C0 OR Exit
 v
Domain Card Context Assembly ─────────────────────────────────────────►
 |   • NOT canonical Prompt Assembly (no model execution)
 |   • Shapes: C0 evidence OR briefing evidence → card render inputs
 v
L2 E1-E5 Deterministic Build ──────────────────────────────────────────►
 |   E1 Prep ──────► freeze refs, bind policy_hash, workspace
 |   E2 Valid ─────► validate schema, evidence, routes
 |   E3 Exec ──────► render Tier 1 always-on + Tier 2 via router
 |   E4 Heal ──────► formatting repair only (NO fact invention)
 |   E5 Seal ──────► CardPackManifest, hashes, source register
 v
Exit X1/X2/X3 ────────────────────────────────────────────────────────►
 |   • Checkout sealed L2 artifact
 |   • Emit exactly one X3: ALLOW_FINISH, SAFE_ABSTAIN, REROUTE,
 |     ESCALATE_HITL, SAFE_FALLBACK (degraded, marked)
 v
reports/qna/<slug>/ sealed local artifact ─────────────────────────────►
 |   • Tier 1 cards (always-on runtime control)
 |   • Tier 2 cards (specialist, router-selected)
 |   • NOT UWG/L4 durable write (default)
 v
L6 Post-Run Evaluation (shadow only) ──────────────────────────────────►
     • Reads runtime exhaust; evaluates routing quality
     • Does not mutate current run
```

---

## Key Contracts

| Contract | Owner | Role in apps_qna |
|----------|-------|------------------|
| ValidatedRequest | agentic_core.L0_routing.intake | Wrap CLI → ValidatedRequest |
| L1PlanContract | agentic_core.L1_cognition.planning | Emit declaring C0 vs briefing |
| RouteContract (v15) | agentic_core.L0_routing.types | Emit R4_SINGLE_ACTION |
| C0EvidenceContract | agentic_core.L3_orchestration.types | Consume via thin adapter |
| UploadedBriefingEvidenceContract | apps_qna (app-owned) | Distinct from C0 contract |
| DomainCardContextAssembly | apps_qna (app-owned) | Shape evidence → card context |
| CardPackManifest | apps_qna (app-owned, extended) | Evidence refs, tiering, hashes |
| Exit X3 Disposition | agentic_core.L3_orchestration.exit_eval | Wire L2 → Exit; emit one X3 |

---

## Route Model

**Route Family**: `R4_SINGLE_ACTION` (canonical enum from RouteIdV15)  
**Execution Form**: `SINGLE_STEP` (canonical enum from ExecutionFormV15)

| Route | ID | Grounding | Evidence Source |
|-------|-----|-------------|-----------------|
| Live Interview Runtime Pack (Grounded) | `apps_qna.live_interview_runtime_pack_v1` | grounding_required: true, c0_required: true | Canonical C0 → FinalEvidenceContract |
| Live Interview Runtime Pack (Briefing) | `apps_qna.live_interview_runtime_pack_from_uploaded_brief_v1` | grounding_required: false, uploaded_briefing_required: true | Validated briefing → UploadedBriefingEvidenceContract |

**Prompt Assembly Status**:
- `core_prompt_assembly_required: false` (no model/provider call)
- `domain_card_context_assembly_required: true` (app shapes evidence for cards)

---

## C0 Adapter Boundaries

**C0-Owned** (canonical agentic_core): Retrieval graph traversal, evidence shaping/scoring, FinalEvidenceContract production, source register, freshness assessment, claim confidence, contradiction detection.

**apps_qna Adapter** (`c0_adapter.py`): Shape app-specific C0 request from interview parameters, call canonical C0 retrieval endpoint, return canonical FinalEvidenceContract unchanged, handle C0 errors (fail-closed → SAFE_ABSTAIN), no evidence transformation, no fact invention.

**Production Fail-Closed**: If canonical C0 unavailable → Exit SAFE_ABSTAIN. No degraded operation with invented evidence.

---

## Two-Tier Card Architecture

**Tier 1: Always-On Runtime Cards** (compact control layer)
- `00_START_HERE_RUNTIME_ROOT.md` — Live mode gate, q-prefix rules
- `00A_SOURCE_SET_AND_EGRESS_VERIFIER.md` — Fake precision blocking, unsupported claim blocking
- `01_CARD_SELECTION_MANIFEST.md` — Deterministic routing, route precedence
- `03_INTERVIEWER_LENS_AND_COMPANY_BRIDGE.md` — Relevance bridge (passive)

**Tier 2: Specialist Cards** (trigger-selected only)
- STAR_PROOF, STAR_FAILURE_LEARNING, RAG_CONTEXT, GOVERNANCE_HITL, TOOLS_MCP_GATEWAY, AGENTIC_ARCHITECTURE, DS_TO_PLATFORM, PLATFORM_PRODUCTIZATION, CLIENT_ADVISORY_ROI, ROLE_SCOPE_MANDATE, EXEC_TRANSLATION_FIT, CROSS_EXAM_DEPTH, HARDEST_GENAI_DEFAULT_STORY, ROUTING_EVALS_AND_EDGE_CASES

---

## W0 Thin-Slice Acceptance Tests

```python
# tests/test_w0_thin_slice.py

def test_u0_emits_validated_request() -> None:
    """U0 emits ValidatedRequest with request_id, trace_root."""

def test_l1_emits_plan_contract() -> None:
    """L1 emits L1PlanContract declaring C0 vs briefing."""

def test_l0_emits_single_route_contract() -> None:
    """L0 emits exactly one RouteContract (R4_SINGLE_ACTION)."""

def test_uploaded_briefing_bypasses_c0() -> None:
    """Valid briefing emits UploadedBriefingEvidenceContract, bypasses C0."""

def test_mock_c0_returns_final_evidence_contract() -> None:
    """C0 adapter returns canonical FinalEvidenceContract."""

def test_l2_renders_two_tier_pack() -> None:
    """E3 renders Tier 1 always-on + Tier 2 via router."""

def test_exit_emits_x3_disposition() -> None:
    """Exit emits exactly one X3 disposition."""

def test_manifest_has_evidence_refs() -> None:
    """CardPackManifest includes evidence refs, tiering, hashes."""

def test_no_direct_l2_to_l4_write() -> None:
    """L2 writes to local workspace only."""

def test_existing_static_build_not_broken() -> None:
    """Legacy static build path still works (backward compat shim)."""
```

---

## Governance Test Inventory (20 tests W1.3)

1. `test_main_is_pure_shim` — __main__.py only parses CLI
2. `test_main_does_not_import_card_builder` — No direct builder import
3. `test_main_does_not_import_c0_adapter` — No direct C0 import
4. `test_main_does_not_import_l2_stage_modules` — No L2 imports
5. `test_main_does_not_import_provider_sdks` — No provider SDKs
6. `test_main_contains_no_l2_callable_construction` — No handmade closures
7. `test_main_contains_no_inline_card_render_closure` — No inline render
8. `test_grounded_route_requires_c0_or_uploaded_briefing` — Evidence required
9. `test_direct_path_uses_no_l3` — No L3 by default
10. `test_route_resolution_failure_fails_closed_through_exit` — Fail-closed routing
11. `test_no_generic_pack_when_grounding_required` — No generic fallback
12. `test_no_direct_l4_writes` — L2 does not write L4
13. `test_no_provider_calls_in_build_path` — No provider calls
14. `test_exit_emits_x3_but_does_not_write_l4` — Exit discipline
15. `test_c0_adapter_calls_canonical_c0_only` — Thin adapter only
16. `test_c0_adapter_does_not_retrieve_directly` — No direct retrieval
17. `test_uploaded_briefing_contract_is_not_c0_fec` — Contract distinction
18. `test_l2_e4_heal_cannot_invent_facts` — Healing boundaries
19. `test_r1b_never_silent_terminal_return` — Cache safety
20. `test_local_output_not_uwg_write` — Local/UWG boundary

---

## W4 Acceptance Criteria (37 additional tests)

| Category | Tests |
|----------|-------|
| Tier 1/2 cards | 5 tests (exist, always-on vs trigger, no overfire) |
| Router | 4 tests (exactly one primary, precedence, support card budget) |
| Target overlay | 4 tests (compact, no raw briefing dump, passive) |
| Egress | 6 tests (blocks internal labels, fake precision, vendor-first) |
| L2 E1-E5 | 5 tests (receipts, no fact invention, sealing) |
| Exit | 4 tests (single X3, no L4 write, receives sealed artifact) |
| Cache | 5 tests (R1A exact, R1B advisory, R5 degraded) |
| L6/UWG | 4 tests (after-runtime only, local≠UWG) |

**Total: 57 governance/acceptance tests**

---

## Rules

1. **Entrypoint purity**: __main__.py is pure CLI envelope parser
2. **Capability registry**: agentic_core owns route/capability resolution
3. **Direct path uses no L3**: Default apps_qna is not L3 managed workflow
4. **C0 grounding**: grounding_required=true requires C0 FinalEvidenceContract OR valid UploadedBriefingEvidenceContract
5. **C0 adapter boundary**: Thin adapter only; no parallel C0 implementation
6. **Briefing ≠ C0**: UploadedBriefingEvidenceContract distinct from FinalEvidenceContract
7. **Domain assembly ≠ PA**: Explicitly not canonical Prompt Assembly
8. **Two-tier cards**: Tier 1 always-on (compact), Tier 2 specialist (trigger-selected)
9. **Router selects exactly one**: Ambiguity resolved by precedence
10. **L2 heal discipline**: Formatting repair only; NO fact invention
11. **Exit exactly one X3**: No multiple X3s per run
12. **Local output ≠ UWG**: reports/qna/ is local artifact; UWG for optional future state only
13. **L6 after runtime only**: No current-run mutation

---

## Success Criteria

- [ ] 10 W0 thin-slice tests pass
- [ ] 20 W1 governance tests pass
- [ ] 37 W4 acceptance tests pass
- [ ] __main__.py imports ≤5 items (CLI-safe types only)
- [ ] C0 adapter calls canonical C0 only (thin adapter pattern)
- [ ] UploadedBriefingEvidenceContract distinct from FinalEvidenceContract
- [ ] Router selects exactly one primary route (R4_SINGLE_ACTION)
- [ ] Tier 1 cards always load, Tier 2 cards load by trigger only
- [ ] Exit emits exactly one X3 disposition per run
- [ ] CardPackManifest includes evidence refs, tiering, card hashes
- [ ] No direct L2→L4 write
- [ ] R1A exact cache requires full digest match
- [ ] R1B semantic cache advisory-only (never silent return)
- [ ] Local output is sandboxed filesystem write (not UWG)
- [ ] RUNBOOK updated with spine flow diagram
- [ ] Legacy static path shimmed (backward compat)

---

## Implementation Commands

```bash
# W0 thin-slice
python -m pytest tests/test_w0_thin_slice.py -v

# W1 governance
python -m pytest tests/governance/test_apps_qna_*.py -v

# W4 acceptance
python -m pytest tests/test_acceptance.py -v

# Full suite
python -m pytest tests/ -k "apps_qna" --tb=short -q

# Entrypoint verification
python -m apps_qna --help
python -m apps_qna --interview test --company TestCo --dry-run
```

---

## Rollback Strategy

1. Restore `__main__.py` to pre-W1 state
2. Remove W0-W4 created files (keep registry scaffold for retry)
3. Revert `spine_manifest.yaml` to `build_time_compiler`
4. Re-enable legacy `spine_handoff.py` path
5. Document learnings for next attempt

---

## AG_QUEUE_SEED

AG_QUEUE_SEED: plan=apps-qna-spine-integration-e9c5b3 id=w4-legacy-shim depends_on=w4.3 title="W4.4 Legacy Path: Shim vs Deprecate"

---

## Plan Retirement Notice

**This plan supersedes and retires:**
- `apps-qna-spine-alignment-a7f4c2` (Notion: 35627693-f55c-8182-866f-fc910485b8ff) — Status: Deprioritized → Retired
- `apps-qna-grounded-spine-refactor-v2-d7e3a1` (Notion: 35627693-f55c-8169-bc80-fd9cd5a2590c) — Status: Deprioritized → Retired

**Integration notes**:
- Consolidated W0 from d7e3a1 (thin-slice proof first)
- Consolidated governance rigor from a7f4c2 (57 tests)
- Deduplicated phases: P0+W0 merged into unified W0-W1
- Streamlined waves: 5 waves (18 phases) vs 7 waves (33 phases)
- Reduced token estimate: ~200K vs ~275K

---

PLAN_CREATED: slug=apps-qna-spine-integration-e9c5b3 path=.windsurf/plans/apps-qna-spine-integration-e9c5b3.md waves=5 phases=18 tokens=200K
