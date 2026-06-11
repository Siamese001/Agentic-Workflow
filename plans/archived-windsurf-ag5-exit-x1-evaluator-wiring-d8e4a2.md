---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\ag5-exit-x1-evaluator-wiring-d8e4a2.md'
original_relative_path: 'ag5-exit-x1-evaluator-wiring-d8e4a2.md'
source_sha256: 8c8a62c5b4d4cff44fef97444bf3bb3eeccaefedbda94bcc5cd696f6a627e551
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-10'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# AG-5 Exit X1 Evaluator Wiring

**Objective**: Wire the actual Exit X1A-X1J evaluator logic so groundedness, replay, observability, safety, output quality, and write eligibility are evaluated through structured `X1CheckoutResult` items instead of scalar `eval_score` or implicit checks.

**Parent**: AG-4 Evidence Contract Carrier Repair (completed 2026-05-10).

**Hard Laws** (constitutional, no exceptions):
- Do not generate embeddings.
- Do not mutate ChromaDB.
- Do not wire R1B in this plan.
- Do not re-ingest ChromaDB.
- Do not clean duplicate repo_* collections.
- Do not restore app-local runtimes.
- Do not bypass Exit.
- Do not bypass C0 evidence contracts.
- UNKNOWN is never PASS.
- NOT_APPLICABLE requires reason.
- No final X3 may ignore material FAIL or UNKNOWN from X1.
- Additive or behavior-preserving changes only unless tests prove intended fail-closed behavior.

## AG-4 Completion Status

AG-4 carriers exist:
- `EvidenceItem`: 6 → 29 fields
- `FinalEvidenceContract`: 16 → 43 fields (+20 AG-4)
- `ExitReviewPacket`: 65 → 82 fields (+17 AG-4 opaque-ref carriers)
- `X1CheckoutResult`: NEW (10 X1A..X1J slots + verdict helpers)
- `SealedL2Artifact`: 32 → 39 fields (+7 AG-4 carrier refs)
- `apps_rg` C0 emitter populates AG-4 fields
- 51 AG-4 invariant tests pass
- 139 regression tests pass
- CI gate verifies 102 required AG-4 fields

AG-4 remaining caveat (this plan's scope):
- X1A-X1J carrier exists, but actual Exit evaluator logic is not wired
- Default UNKNOWN slots fail closed (correct but not sufficient for runtime groundedness)

## Wave Structure

### W0 — Discovery
- Locate current Exit evaluation flow
- Locate X3Disposition creation
- Locate scalar `eval_score` usage
- Locate helper checks around output schema, safety, replay, audit, groundedness, write eligibility
- Locate all tests asserting Exit success/failure
- Produce map from current checks to X1A-X1J slots

**Deliverable**: Discovery report in `artifacts/apps_embedding_gap_analysis/ag5_w0_discovery.json`

### W1 — Build ExitReviewPacket Creation Path
Wire Exit to normalize all terminal inputs into `ExitReviewPacket`:
- RET exact cache
- RET semantic cache (if present)
- RET fallback
- SealedL2Artifact
- SealedWorkflowPackage
- ReClearedHITLPacket (if present)

**Required proof**:
- ExitReviewPacket includes route refs, evidence refs, prompt refs, trace refs, replay refs, runtime gate refs, audit refs where available
- Missing required grounded evidence becomes UNKNOWN or FAIL, not PASS
- Existing successful paths still work where evidence is not required

**Files**: `agentic_core/L3_orchestration/exit_eval/v6/exit_review_packet_builder.py` (new)

### W2 — Implement X1 Evaluator Mapping

Wire these structured X1 checks:

| Gate | Focus | Checks |
|------|-------|--------|
| X1A Today's Rules | Policy/blueprint | policy_hash, blueprint_hash, registry_digest_set, threshold_profile, grader_roster |
| X1B Answered It | Output presence | task completion, requested format, output expectation, user intent alignment |
| X1C Safe to Leave | Safety/leakage | safety, leakage, side effects, sandbox, egress, mutation authority |
| X1D Answer Good | Groundedness | **This is W4** — groundedness, faithfulness, citations, support_status; compare intent/evidence/output refs |
| X1E Trajectory OK | Route sanity | route, tool choice, retry, heal, workflow path, no hidden reroute |
| X1F Story Adds Up | Consistency | internal consistency, contradiction handling, cross-step coherence |
| X1G Replay Eligible | Replay | replay_manifest, deterministic digest, idempotency refs |
| X1H Observable | Auditability | OTEL span refs, trace refs, audit refs |
| X1I Consistency Across Runs | Pass-k | NOT_APPLICABLE with reason unless pass-k activated |
| X1J Write Eligibility | UWG gate | Only when proposed_state_diff exists; requires CommitRequest/UWG path |

**Key invariant**: X1D for grounded route MUST have FinalEvidenceContract; missing it → FAIL or UNKNOWN.

**Files**: `agentic_core/L3_orchestration/exit_eval/v6/x1_evaluators.py` (new)

### W3 — Aggregation Rules
Wire `X1CheckoutResult` into X2/X3 aggregation.

**Rules**:
- UNKNOWN is not PASS
- NOT_APPLICABLE requires reason
- Any material FAIL blocks ALLOW_FINISH
- Any material UNKNOWN on safety, evidence, replay, write, privacy, or high-impact path escalates/blocks/reroutes/safe-abstains per policy
- Multiple PASS items do not cancel one hard FAIL
- X3Disposition must reference X1CheckoutResult
- X3Disposition must emit exactly one X3

**Files**: `agentic_core/L3_orchestration/exit_eval/v6/x1_aggregation.py` (new)

### W4 — Groundedness Evaluator (X1D)
First deterministic groundedness evaluator (not LLM judge yet).

**Inputs**:
- L1PlanContract intent/task/support expectation refs
- FinalEvidenceContract support_status, evidence_items, citation_map, contradiction_report
- SealedL2Artifact output refs
- PromptEnvelope refs when model path

**Checks**:
- Grounded route has FinalEvidenceContract
- support_status PASS or WEAK_WITH_CAVEATS only where policy allows
- Required citation anchors exist
- BLOCKED/EMPTY/CONFLICTED/UNKNOWN evidence does not pass silently
- Output references only supported evidence where claims require support
- Retrieved text remains data only

**Verdicts**: PASS (meets policy), PARTIAL (weak support, caveats required), WEAK (below threshold but not empty), FAIL (BLOCKED/CONFLICTED/EMPTY), UNKNOWN (not computed), NOT_APPLICABLE (cache hit / abstain route).

**Files**: `agentic_core/L3_orchestration/exit_eval/v6/x1d_groundedness_evaluator.py` (new)

### W5 — Preserve Scalar eval_score Compatibility
Do not remove scalar `eval_score`. If it remains, make it derived from X1CheckoutResult aggregate. Structured X1 verdicts are authoritative for Exit disposition.

**Strategy**:
- `eval_score` becomes `@property` or helper method on X1CheckoutResult
- Legacy callers using scalar still work (backward compat)
- New callers use `X1CheckoutResult.is_overall_pass()` or per-gate verdicts

### W6 — Tests

Test file: `tests/_apps_contract/test_ag5_exit_x1_evaluator_wiring.py`

Test inventory (minimum 20 tests):
1. ExitReviewPacket built for every terminal source type (6 SourceType values)
2. X1CheckoutResult produced before X3Disposition
3. X3Disposition references X1CheckoutResult
4. X1D fails grounded routes with missing FinalEvidenceContract
5. X1D fails/warns when evidence EMPTY/BLOCKED/CONFLICTED/UNKNOWN
6. X1H fails/warns when required OTEL/audit refs missing
7. X1G fails when replay required but missing
8. X1J applies only when proposed_state_diff exists
9. UNKNOWN never passes
10. NOT_APPLICABLE without reason raises/fails validation
11. ALLOW_FINISH blocked by material FAIL
12. Non-grounded safe paths pass with NOT_APPLICABLE reason
13. No ChromaDB mutation (AST scan)
14. No embedding generation (AST scan)
15. X1A policy check uses registry_digest_set
16. X1B answered-it requires output.content
17. X1C safe-to-leave checks sandbox/egress allowlists
18. X1E trajectory-ok validates no hidden reroute
19. X1F story-adds-up checks contradiction_report
20. X1I consistency-across-runs NOT_APPLICABLE with reason

### W7 — CI Gate
Create: `ops_scripts/ci/check_exit_x1_evaluator_wiring.py`

**Gate fails if**:
- X3Disposition can be emitted without X1CheckoutResult
- Grounded route can pass without FinalEvidenceContract
- UNKNOWN can be treated as PASS
- NOT_APPLICABLE can omit reason
- Scalar eval_score is the only quality carrier
- Material FAIL can still ALLOW_FINISH
- proposed_state_diff can bypass X1J/UWG eligibility

### W8 — Output Artifacts

1. `artifacts/apps_embedding_gap_analysis/ag5_exit_x1_evaluator_wiring_report.md` — full report
2. `artifacts/apps_embedding_gap_analysis/ag5_x1_mapping_matrix.json` — X1A..X1J → current checks mapping
3. `artifacts/apps_embedding_gap_analysis/ag5_exit_aggregation_rules.json` — aggregation policy rules
4. `artifacts/apps_embedding_gap_analysis/ag5_acceptance_evidence.json` — acceptance evidence bundle

## Acceptance Invariant

AG-5 is complete only when:
- Exit cannot emit ALLOW_FINISH for grounded/model path unless ExitReviewPacket and structured X1CheckoutResult exist
- Material FAIL/UNKNOWN are handled fail-closed
- X3Disposition is based on structured X1/X2 evidence rather than scalar eval_score alone
- UNKNOWN is never treated as PASS
- NOT_APPLICABLE requires reason
- All 20+ tests pass
- CI gate is green

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0 | Discovery | 5-10 files | Mapping implicit checks to X1 slots | ~8k | pending |
| W1 | ERP Builder | 1 new module | Normalizing 6 source types | ~6k | pending |
| W2 | X1 Evaluators | 1 new module | 10 gate implementations | ~12k | pending |
| W3 | Aggregation | 1 new module | X2/X3 integration rules | ~5k | pending |
| W4 | X1D Groundedness | 1 new module | Deterministic evaluator | ~8k | pending |
| W5 | eval_score compat | 1-2 files | Backward compat wiring | ~3k | pending |
| W6 | Tests | 1 new test file | 20+ invariant tests | ~10k | pending |
| W7 | CI Gate | 1 new gate | Static AST + runtime checks | ~4k | pending |
| W8 | Artifacts | 4 files | Evidence bundles | ~3k | pending |

## Definition of Done

| DoD | Description | Verification |
|-----|-------------|------------|
| DoD-1 | W0 discovery produces mapping JSON | `artifacts/apps_embedding_gap_analysis/ag5_w0_discovery.json` exists |
| DoD-2 | ExitReviewPacket builder normalizes all 6 SourceType | `python -m pytest tests/_apps_contract/test_ag5_exit_x1_evaluator_wiring.py::TestExitReviewPacket -v` passes |
| DoD-3 | X1A..X1J evaluators exist and produce X1Item | Each gate has dedicated test |
| DoD-4 | X1CheckoutResult aggregated into X2/X3 | `X3Disposition` references `X1CheckoutResult` |
| DoD-5 | X1D groundedness evaluator deterministic | No LLM calls; uses FEC fields |
| DoD-6 | Scalar eval_score preserved (derived) | Backward compat test passes |
| DoD-7 | 20+ tests pass | `python -m pytest tests/_apps_contract/test_ag5_exit_x1_evaluator_wiring.py -v` all green |
| DoD-8 | CI gate verifies wiring | `python ops_scripts/ci/check_exit_x1_evaluator_wiring.py` exits 0 |
| DoD-9 | No ChromaDB mutation | AST scan in tests confirms no chromadb/vector_db imports |
| DoD-10 | No embedding generation | AST scan confirms no bge_embed/embed_texts calls |
| DoD-11 | X3 cannot ALLOW_FINISH without X1 | Test proves fail-closed behavior |
| DoD-12 | Acceptance artifacts emitted | 4 artifacts in `artifacts/apps_embedding_gap_analysis/` |

## Verification vs Deferral

| Verification | Deferral |
|--------------|----------|
| W1-W4 implemented with tests | Real LLM-judge X1D (future plan) |
| CI gate active | Full X1A..X1J runtime evaluators (W6 tests prove contract presence; full runtime wiring follows) |
| 20+ tests covering invariants | Per-app C0 FEC producer wiring (apps_research, apps_rfp, etc. — separate plans) |

## ADG_HOTSPOT_REPORT

### Evidence
- **Source**: ADG MCP `adg_health` + `adg_nodes_by_layer`
- **Backend**: redis_cache
- **Snapshot**: adg_indexed_05052026_0722.sqlite

### Hotspot Analysis
Exit evaluation surface is in `agentic_core/L3_orchestration/exit_eval/v6/`:

| File | Layer | Fan-in | Fan-out | Violations | Impact Score |
|------|-------|--------|---------|------------|--------------|
| types.py | L3 | 12 | 8 | 0 | High |
| app_specific_evaluator.py | L3 | 8 | 6 | 0 | High |
| pipeline.py | L3 | 6 | 10 | 0 | Medium |

**X1Eval surface**: NEW files (no existing fan-in/fan-out). Additive only.

## ADG_GRAPH_LAYER_EVIDENCE

### Materialized Views
- `mv_hotspot_centrality`: L3 orchestration nodes rank highest for exit_eval surface
- `mv_graph_critical_path_blast_radius`: Exit path touches L3→L2→L1→L0 binding chain

### Semantic Edges
- `ExitReviewPacket` → `SealedL2Artifact` via `reads_from` (source_contract_ref)
- `ExitReviewPacket` → `FinalEvidenceContract` via `reads_from` (final_evidence_contract_ref)
- `X1CheckoutResult` → `ExitReviewPacket` via `flows_to` (evaluation consumes packet)

### P-Views
- v_p1_mislayered: None in exit_eval (L3 stays L3)
- v_p2_duplicated: `ExitReviewPacket` has 3 sister definitions (AG-4 chose not to consolidate; AG-5 also additive-only)

## SSOT Folder Routing

New files per constitutional §31:
- `ops_scripts/ci/check_exit_x1_evaluator_wiring.py` — CI gate
- `tests/_apps_contract/test_ag5_exit_x1_evaluator_wiring.py` — tests
- `agentic_core/L3_orchestration/exit_eval/v6/*` — evaluator modules (L3 stays L3)
- `artifacts/apps_embedding_gap_analysis/ag5_*` — output artifacts

## AG-4 Parent Reference

AG-4 plan: `.windsurf/plans/ag4-evidence-contract-carrier-repair-d2f9a3.md`
AG-4 acceptance: `artifacts/apps_embedding_gap_analysis/ag4_acceptance_evidence.json`

## Plan Metadata

- Created: 2026-05-10
- Slug: ag5-exit-x1-evaluator-wiring-d8e4a2
- Status: In Progress
- Author: Cursor Agent
- Estimated Waves: 9
- Estimated Tokens: ~60k

## Notes

This plan wires evaluators that consume AG-4 carriers. It does NOT create new carriers (that was AG-4). It does NOT wire R1B or ChromaDB retrieval (that would violate hard laws). It is purely deterministic Exit-side evaluation logic.
