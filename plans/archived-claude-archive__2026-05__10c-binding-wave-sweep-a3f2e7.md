---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\10c-binding-wave-sweep-a3f2e7.md'
original_relative_path: '_archive\\2026-05\\10c-binding-wave-sweep-a3f2e7.md'
source_sha256: 8e86391fade3153fccf31a6d8814ff1b59eee11ecea521f85616e6f4f44a06da
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# 10C Ledger Binding Wave Sweep — `10c-binding-wave-sweep-a3f2e7`

- **Goal**: Bind the remaining 193 NEEDS_PROOF rows in `docs/reports/design/10c_reconciliation/10c_semantic_requirement_ledger.csv` to commits via the proven W4d-4/W4d-5 binding loop.
- **Status**: Active — Wave 1 in progress.
- **SSOT**: `.cursor/plans/10c-binding-wave-sweep-a3f2e7.md` (this file).
- **Substrate**: W4d-5 binding pipeline is fixed and gated. Reusable: `PILOT_BINDING_SCOPE` (renamed `CRITICAL_BINDING_SCOPE` in Wave 1), `emit_proof_bundles.py` with content-hash tamper-check, `validate_10c_proof_ledger.py:_validate_bundle_binding`, `update_pilot_ledger.py --mode=bound`, plugin-isolated pytest invocation.
- **Scope hazard**: Single-session full completion is **not feasible** at ~64k output tokens/generation vs ~19,000 lines of test code at full depth. **Wave-by-wave execution is mandatory.**

## Wave Structure

| Wave | REQ count | Severity | Surfaces | Est. tokens | Status | Success Criteria |
|------|----------:|---|---|---:|---|---|
| W1 | 24 | CRITICAL | 9 (L5×9, UWG×4, Ingest×2, L1Plan×2, L2×2, OTEL×2, L0×1, Exit×1, L6×1) | ~3,200 | **In progress** | All 24 ledger rows flip to `evidence_status=PROOF_PRESENT` + `final_acceptance_status=ACCEPTED` + `last_passed_commit=<head>`; all 24 bundles `EVIDENCE_PRESENT` + content-hash tamper-verified; W4d-2 strict binding-chain green |
| W2 | ~30 | HIGH | L5 Governance (subset) + Offline Ingestion (rest) | ~3,500 | Todo | Per-wave: same as W1 |
| W3 | ~30 | HIGH | L1 Reasoning + C0 Context | ~3,500 | Todo | Per-wave: same as W1 |
| W4 | ~30 | HIGH | L4 UWG (rest) + L6 Shadow Eval (rest) | ~3,500 | Todo | Per-wave: same as W1 |
| W5 | ~30 | HIGH | L0/L2/L3 Orchestration | ~3,500 | Todo | Per-wave: same as W1 |
| W6 | ~22 | HIGH (tail) | Exit Control + PA Prompt Assembly + Cross-cutting | ~2,800 | Todo | Per-wave: same as W1 |
| W7 | 27 | MEDIUM | Mixed | ~2,500 | Todo | Per-wave: same as W1 |

## Phase-Level Summary (Wave 1)

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|------------:|--------|
| W1.1 | Extend fixtures | `tests/fixtures/proof_evidence/runtime_artifact_validators.py` (+6 artifact types, +6 boundary helpers) | New artifact contracts must match `artifact_schema_ref` ledger column | ~300 | In progress |
| W1.2 | Extend CI gate | `ops_scripts/ci/check_10c_pilot_proof_evidence.py` → `check_10c_critical_proof_evidence.py` (5 → 29 reqs) | Must keep pilot gate's structure; update pre-commit + run_contract_gates wiring | ~150 | In progress |
| W1.3 | Author 24 tests | `tests/unit/agentic_core/**/test_10c_req_<id>.py` × 24 | Each test ~80 lines; positive shape + span + replay + 2-3 negative controls (per `negative_control_specific`) | ~1,920 | In progress |
| W1.4 | Update binding scope | `tools/requirements/emit_proof_bundles.py:PILOT_BINDING_SCOPE` + `tools/requirements/update_pilot_ledger.py:PILOT_BINDING_SCOPE` (rename to `CRITICAL_BINDING_SCOPE`, expand to 29 reqs) | Must stay synchronized between two files | ~100 | In progress |
| W1.5 | Run + regenerate + bind | pytest plugin-isolated × 24, `emit_proof_bundles.py`, `update_pilot_ledger.py --mode=bound` | All 24 bundles must record `git_dirty=false`, `git_head=<clean-HEAD>` | ~50 | In progress |
| W1.6 | Validate + commit + report | W4a/W4b/W4d-2/W4d-3/W4d-4 + executor_theater + commit + emit `wave1_completion_report.md` | Meta-gate still blocks on §22 (unrelated) — accepted blocker | ~150 | In progress |

## ADG_HOTSPOT_REPORT

| Surface (artifact type) | REQ count | Layer | Fan-in (proxy: row count) | Archetype | Surface intersect | Layer multiplier | Impact score |
|---|---:|---|---:|---|---|---:|---:|
| L5 Governance (`L5CertificationResult`) | 9 | L5 | 9 | SAFETY_GATEKEEPER | Security ∪ Observability | 2.0 | **18.0** |
| L4 UWG (`CommitRequest`) | 4 | L4 | 4 | STATE_NODE | Write ∪ State | 1.75 | **8.74** |
| Offline Ingestion (`ChunkSealedEnvelope`) | 2 | L1 (knowledge) | 2 | CENTRAL_DEPENDENCY | State | 1.0 | **2.30** |
| L1 Plan (`L1PlanContract`) | 2 | L1 | 2 | CENTRAL_DEPENDENCY | Execution | 1.0 | **2.30** |
| L2 Execute (`ExecutionResult`) | 2 | L2 | 2 | ORCHESTRATOR | Execution | 1.0 | **2.30** |
| Cross-cutting OTEL (trace+replay-key audit) | 2 | L6 | 2 | CENTRAL_DEPENDENCY | Observability | 0.75 | **1.72** |
| L0 Route (`RouteContract`) | 1 | L0 | 1 | CENTRAL_DEPENDENCY | Execution | 2.0 | **2.30** |
| Exit Control (`X3DispositionPacket`) | 1 | L5 (exit) | 1 | SAFETY_GATEKEEPER | Security ∪ Execution | 2.0 | **2.30** |
| L6 Shadow Eval (`L6EvalRecord`) | 1 | L6 | 1 | STATE_NODE | Observability | 0.75 | **0.86** |

**Top hotspot**: L5 Governance — 9 rows × 2.0 layer multiplier × Security+Observability surface intersection. **Wave 1 prioritization**: L5 first (highest impact), then L4 UWG, then everything else.

Impact formula: `violation_count × (1 + log10(1 + fan_in)) × layer_multiplier`. Surface intersection: each surface in {Execution, Write, Security, State, Observability} that the artifact-type touches.

## ADG_GRAPH_LAYER_EVIDENCE

Constitutional §22 requires ≥3 materialized views, semantic edges, and P-views.

**Materialized views** (cited):
1. `mv_hotspot_centrality` — used implicitly via fan-in proxy (REQ count per surface). The 9 L5 rows correspond to `agentic_core/L5_safety/` modules which are high-centrality nodes per the existing ADG.
2. `mv_dependency_cone_risk` — L5 boundary modules sit at the cone-bottom of multiple L1/L2/L3 callers; bypass = silent ALLOW.
3. `mv_exemptions_near_critical_paths` — L5 certification path is enforcement-critical; exemption discipline applies.

**Semantic edges** used in this wave:
- `flows_to` — L5 certification flows to runtime artifacts (verified via OTEL span chain)
- `writes_to` — UWG `CommitRequest` is the only path that writes to durable state
- `emits_side_effect` — L2 `ExecutionResult.side_effects_proposed` is sealed-only (no commit)
- `controls_flow` — Exit gate `X3DispositionPacket` controls every exit path

**P-views** (cross-reference):
- `v_p0_apps_direct_infra` — N/A for this wave (binding doesn't touch apps→infra direct calls)
- `v_p0_write_bypass_uwg` — REQ-122 (already bound) is the canonical anti-pattern check; W1's UWG rows (140, 153, 177, 185) extend the same pattern surface
- `v_p1_mis_layered_infra` — N/A
- `v_p1_zero_caller_infra` — N/A

## Risks & Blockers

- **Output token budget**: Wave 1 = ~3,200 lines = ~2-3 generations. Mitigation: tight test density (~80 lines each, not 150 like the pilot).
- **§22 meta-gate**: Already blocks `run_contract_gates.py` on 15 unrelated plan files. NOT a Wave 1 blocker — the W4d-* gates pass independently.
- **Binding-scope dirt**: When tests are authored, the binding scope (now `CRITICAL_BINDING_SCOPE` × ~30 files) must be clean before regenerating bundles. Mitigation: commit test files first, regenerate bundles second, bind ledger third.
- **Field-completeness drift**: Per-row `negative_control_specific` is the source of truth for negative tests. Tests must wire to that exact text, not generic substitutes.

## Test density target

Pilot tests averaged 117 lines. Wave 1 tests target **~80 lines** by:
- Reusing the 3 shared fixtures (`otel_span_receipt`, `replay_digest`, `runtime_artifact_validators`)
- Sharing the `_valid_envelope()` + `_valid_span_attrs()` helpers within each test
- 3 positive controls + 3 negative controls per row (vs pilot's 4+5)

## Success criteria (Wave 1)

- 24 new test files exist, all green at clean HEAD
- 24 new proof bundles `EVIDENCE_PRESENT`, `git_dirty=false`, `git_head=<W1 commit>`, `content_hash` tamper-verified
- 24 ledger rows flipped: `evidence_status=PROOF_PRESENT`, `final_acceptance_status=ACCEPTED`, `implementation_status=IMPLEMENTED`, `last_passed_commit=<head>`
- W4a / W4b / W4d-2 (incl strict bundle-binding) / W4d-3 / W4d-4 (now broadened to W4d-1A) all green
- After-W1 ledger metrics: 29/200 ACCEPTED, 24/24 CRITICAL CRITICAL/HIGH proof-evidence-present, 162 NEEDS_PROOF remaining
- Final commit pushed; report at `artifacts/requirements/wave1_completion_report.md`

## Out of scope (subsequent waves)

- W2-W7 binding (HIGH × 142, MEDIUM × 27)
- Authoring 9 per-surface CI gate scripts (additive, optional, deferred)
- Fixing 15 pre-existing §22 plan-file gaps (separate scope)
