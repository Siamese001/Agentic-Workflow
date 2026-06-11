---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\adg-13-gap-closure-proof-hardening-6eaa45.md'
original_relative_path: 'adg-13-gap-closure-proof-hardening-6eaa45.md'
source_sha256: 463bbc6cd6a8a74da173aff6fc7849df67a25ca35a5d6cbeddef53b3d796551d
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-24'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG 13-Gap Closure Proof Hardening Plan

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## DEPENDENCY_GRAPH

- **Graph source**: Fresh AST-backed ADG generated via `python tools/generate_full_adg.py` on `03242026_0649`
- **Modules scanned**: `6616`
- **Scanner edges**: `922770`
- **Canonical relations**: `929125`
- **Canonical nodes**: `263888`
- **Primary graph planes**:
  - `G1_imports=280520`
  - `G3_implements=2356`
  - `G4_calls=20583`
  - `GT_covers=10317`
  - `GV_violates=809`
  - `GG_governance=5362`
- **Authority chain**:
  1. `agentic_core/adg/extraction/static_scanner.py` — authoritative extraction and current semantic-depth metrics
  2. `tools/generate_full_adg.py` — authoritative artifact/report generation and packaging
  3. `tests/architecture/test_adg_gap_coverage.py` — scanner gap visitor coverage tests
  4. `tests/architecture/test_adg_digest_stable.py` — determinism tests
  5. `tests/adg/test_adg_hardening_comprehensive.py` — standardized report generation tests

## ROLLBACK_CHECKPOINT

- **Baseline**: `6eaa4569d916a3cb6113caf55a27790718a583d4`
- **Rollback command**: `git reset --hard 6eaa4569d916a3cb6113caf55a27790718a583d4`
- **Phase**: `ADG closure-proof hardening`
- **Acceptance criteria**:
  - Scoped pytest for changed ADG scanner/report tests passes with `0` failures
  - Fresh `python tools/generate_full_adg.py` completes successfully
  - New closure validation output reconciles `violations` table vs `violates` edges from the same artifact
  - Gap closure claims are denominator-backed and fail-gated
  - No scope drift beyond declared files

## SCOPE_DECLARATION

- **Files to modify: 5**
  1. `agentic_core/adg/extraction/static_scanner.py`
     - Reason: current `_check_semantic_depth()` uses weak all-module denominators and current violation propagation is capped below real reachable coverage
  2. `tools/generate_full_adg.py`
     - Reason: current reports contain placeholder/partial determinism fields and do not generate an authoritative 13-gap closure proof report
  3. `tests/architecture/test_adg_gap_coverage.py`
     - Reason: needs denominator-backed semantic-depth tests for new scanner metrics
  4. `tests/architecture/test_adg_digest_stable.py`
     - Reason: needs stronger determinism assertions aligned with closure claims
  5. `tests/adg/test_adg_hardening_comprehensive.py`
     - Reason: needs report-generation assertions for the new closure proof report and stronger report contents
- **Baseline diff**: clean working tree before edits

## AUDIT FINDINGS TO FIX

1. **Violation mismatch is real and currently unexplained in reports**
   - SQLite `violations` table = `5111`
   - `edges.relation_type='violates'` = `809`
   - `COUNT(DISTINCT src_id)` for `violates` = `801`
   - Current reporting mixes these surfaces without labeling them distinctly

2. **Current semantic-depth metrics are too weak to prove closure**
   - `_check_semantic_depth()` divides by `len(result.modules)` for control flow, lineage, and side effects
   - This proves presence across some modules, not coverage across eligible semantic sites

3. **Semantic precision proof is incomplete**
   - `semantic_edge_ratio=1.0` only proves non-empty labels
   - Current system does not report exact-map vs fallback vs raw-edgekind assignment coverage
   - Current artifact shows `225087` edges still inheriting `semantic_type` directly from `edge_kind`

4. **Determinism reporting is placeholder-based**
   - `replay_determinism_report` currently sets `modules_with_determinism_digest=0`, `determinism_score=0.0`, `determinism_status='partial'`
   - It does not prove scanner digest stability, artifact digest stability, or SQLite row stability

5. **Violation propagation is currently truncated**
   - Current `_MAX_PROPAGATION_EDGES=5000`
   - Uncapped 3-hop propagation using the same matching logic reaches `16815` edges
   - Gap 13 cannot be honestly closed while the proof surface is capped below reachable coverage

## IMPLEMENTATION PLAN

### Phase 1 — Strengthen scanner-side closure metrics

1. Add AST/graph-backed eligibility counters for the semantic-depth claims:
   - block-decomposition eligible functions
   - control-flow eligible sites
   - data-lineage eligible assignment targets
   - side-effect eligible callsites
   - dynamic-dispatch eligible callsites
   - type-surface candidates
   - test→exec eligible links
   - propagation-eligible violation targets
2. Persist these counters in `ScanManifest`
3. Replace weak all-module ratios with denominator-backed ratios where possible
4. Expose exact/fallback/raw-edgekind semantic stamping counts so semantic precision can be audited
5. Remove or raise the propagation cap so reported coverage is not artificially truncated

### Phase 2 — Generate authoritative closure-proof report

1. Extend `generate_full_adg.py` to emit a closure-validation report that includes:
   - all 13 gaps
   - denominator, numerator, ratio, threshold, and pass/fail per gap
   - explicit distinction between:
     - total anti-pattern inventory from SQLite `violations` table
     - layer-violation graph edges from `edges.relation_type='violates'`
   - semantic precision breakdown:
     - exact-map ratio
     - fallback ratio
     - raw-edgekind ratio
     - generic semantic ratio
   - determinism proof:
     - scanner digest stability across two scans
     - artifact digest stability across two builds
     - stable node/edge row digests across two generated SQLite artifacts (or explicit partial status if not provable)
2. Make the build fail or hard-warn when any closure gate fails

### Phase 3 — Testing per windsurfrules

1. **Tests before logic completion**
   - add scanner metric tests before finalizing metric implementation
   - add report-generation tests before finalizing report logic
2. **Required test surfaces**
   - `tests/architecture/test_adg_gap_coverage.py`
     - denominator-backed scanner metric tests
     - propagation not truncated when reachable targets exceed legacy cap
   - `tests/architecture/test_adg_digest_stable.py`
     - stronger determinism assertions for stable scanner/artifact digests
   - `tests/adg/test_adg_hardening_comprehensive.py`
     - closure-validation report exists and contains expected reconciliation/proof fields
3. **Validation commands**
   - scoped pytest on all changed ADG tests
   - fresh `python tools/generate_full_adg.py`
   - inspect new closure report and confirm all 13 gates pass on the same artifact

## TARGET OUTPUTS

- Updated scanner metrics that prove **completeness over eligible surfaces**, not just presence
- New authoritative closure-validation report in `artifacts/adg/reports/`
- Reconciled violation accounting (`5111` total violations vs `809` layer-violation edges)
- Stronger determinism proof than `seq=` metadata alone
- Fresh ADG regeneration where 13-gap closure can be defended without denominator ambiguity

## NON-GOALS

- No size optimization until closure proof is complete
- No unrelated refactors outside the declared ADG scanner/report/test scope

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

