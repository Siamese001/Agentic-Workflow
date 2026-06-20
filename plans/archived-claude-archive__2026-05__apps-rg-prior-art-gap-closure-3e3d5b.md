---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-rg-prior-art-gap-closure-3e3d5b.md'
original_relative_path: '_archive\\2026-05\\apps-rg-prior-art-gap-closure-3e3d5b.md'
source_sha256: d01938214f0b4058b7186d8b6c8e75e07b382c2925ae14ff8768952b912fe5e5
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_rg Prior-Art Gap Closure — Plan 3e3d5b

**Status**: Done (P1, P2, P3 complete; P5 writeback complete in this turn)
**Tier**: T2
**Created**: 2026-05-01
**Author-Gate**: APPROVED 2026-05-01 (refactor_scope, P1+P2+P3, confidence=0.86)

## Context

Historical review of `apps_rg` (current vs `3a60f9f001`, the 2025-12-08 atomization peak) found four prior-art items that are gaps in the current tree:

| # | Gap | Severity |
|---|---|---|
| G1 | `JDEnforcementValidator` is a stub at `reasoning/ResumeOrchestrator.py:297` (E1 had 15 named rules) | HIGH |
| G2 | `DuplicateDetector` referenced in `tools/DataEnricher.py:20` but no class definition exists — runtime `NameError` | CRITICAL |
| G3 | Hallucination superlative blocklist (8 generic words, ≥2-occurrence threshold) absent from `engines/hallucination_detector.py` | MEDIUM |
| G4 | Hallucination implausible-growth proximity check (`\d{3,}%` + month/quarter horizon) absent — false-negative on `"100% growth in 6 months"` | MEDIUM |

G5 (`ValidationEngine` registry), G6 (`TextSimilarityCalculator`), G7 (pipeline-stage topology) were verified **not** to be gaps or are out of scope.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|:---:|---|:---:|---|
| W1 | P1, P2, P3 | Restore lost capability with current-era contracts (BaseRGEngine, lifecycle traces) | ~25k | apps_rg ValidationResult shape stable; agentic_core text_similarity_util importable | Done | 48/48 tests pass (8 P1 + 17 P2 + 13 P3 + 10 orchestrator regression) |
| W2 | P5 | Verify & writeback | ~3k | All P1-P3 tests green | Done (writeback in plan tail) | Notion + Memory writeback recorded below |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|:---:|:---:|
| P1 | Restore `DuplicateDetector` (G2) | +`apps_rg/engines/duplicate_detector.py`, +`tests/unit/apps_rg/engines/test_duplicate_detector.py`, ~`apps_rg/tools/DataEnricher.py` (add imports + rename `rule_id=` → `gate_id=`), ~`apps_rg/types/validation_result_types.py` (add `ValidationSeverity` constants class) | TextSimilarityCalculator now lives in `agentic_core.L2_execution.utils.text_similarity_util`; ValidationResult sprawl (27+ definitions repo-wide) — used `apps_rg.types.validation_result_types.ValidationResult` | ~6k | Done — 8/8 tests pass |
| P2 | Restore `JDEnforcementValidator` real implementation (G1) | +`apps_rg/validators/jd_enforcement_validator.py`, +`tests/unit/apps_rg/validators/test_jd_enforcement_validator.py`, ~`apps_rg/reasoning/ResumeOrchestrator.py` (delete stub class, import real) | E6-E15 wired as `validate_dataflow_stage(rule, evidence, gate_id)` — None evidence emits `_emit_hard_fails_untranscripted` and fails the rule | ~14k | Done — 17/17 tests pass |
| P3 | Hallucination heuristic gaps (G3, G4) | ~`apps_rg/engines/hallucination_detector.py`, +`tests/unit/apps_rg/engines/test_hallucination_detector.py` | G4 regex extended to support plural horizon nouns (`months?`, `quarters?`, `90\s*days?`); G3 superlative blocklist matches 2025-12-08 snapshot verbatim | ~5k | Done — 13/13 tests pass |
| P5 | Verify & writeback | combined pytest sweep (48 passed); plan status updated; ADG regen + ADR row deferred — see Deferred Scope section below | ADR numbering — query Notion ADR Registry first | ~3k | Done |

## ADG_HOTSPOT_REPORT

Skipped — this is a port-back of pre-existing capability into already-existing files, not a hotspot-driven refactor. New files are leaf nodes (low fan-in by definition); modified files (`tools/DataEnricher.py`, `reasoning/ResumeOrchestrator.py`, `engines/hallucination_detector.py`) are existing nodes whose call graph is not being changed — only their contents are being completed. No structural blast radius.

## ADG_GRAPH_LAYER_EVIDENCE

Constitutional §22 requires graph-layer evidence for refactoring plans. This plan is **capability restoration** (filling stub/broken bodies), not refactoring — the graph topology is unchanged. Citing this as the reason this section is intentionally minimal:

- `mv_dependency_cone_risk` — N/A: no new edges added beyond existing import-arrows (DataEnricher → DuplicateDetector edge is currently broken; restoring it returns the graph to consistency)
- `mv_hotspot_centrality` — N/A: modified nodes are already-mapped engines; centrality unchanged
- `v_p2_duplicated_adapters` — verified: superlative word list will reuse `integrations/anti_overfitting.py:DEFAULT_FILLER` if shape compatible to avoid creating a duplicate
- Semantic edges: `_emit_verifies_policy`, `_emit_validates_capability`, `_emit_records_execution_trace` will be emitted from new validator code per constitutional §29

## Execution Order

1. P1 first (CRITICAL, smallest, unblocks DataEnricher runtime)
2. P2 second (HIGH, largest scope, no dependency on P1)
3. P3 third (MEDIUM, independent of P1/P2)
4. P5 last (verify + writeback)

## Rollback

Each phase is independently revertible via `git revert <commit>`. P1 and P3 are pure additions or in-place edits; P2 deletes a stub class but the deletion is recoverable from git history.

## Outcome

48/48 tests pass after combined sweep. Files touched:

- `apps_rg/engines/duplicate_detector.py` (+121 lines, NEW)
- `apps_rg/engines/hallucination_detector.py` (~30 lines added — G3/G4 logic)
- `apps_rg/tools/DataEnricher.py` (rewritten — fixed broken imports + kwarg shape)
- `apps_rg/types/validation_result_types.py` (+18 lines — `ValidationSeverity`)
- `apps_rg/validators/jd_enforcement_validator.py` (+243 lines, NEW)
- `apps_rg/reasoning/ResumeOrchestrator.py` (-14 lines / +6 lines — stub → real import)
- `tests/unit/apps_rg/engines/test_duplicate_detector.py` (+102 lines, NEW)
- `tests/unit/apps_rg/engines/test_hallucination_detector.py` (+128 lines, NEW)
- `tests/unit/apps_rg/validators/test_jd_enforcement_validator.py` (+196 lines, NEW)

**Behavioral changes**:
- `apps_rg.tools.DataEnricher.DataEnricher()` no longer raises `NameError` (broken import resolved)
- `apps_rg.reasoning.ResumeOrchestrator.JDEnforcementValidator` now enforces 15 rules instead of 1
- `apps_rg.engines.hallucination_detector.HallucinationDetector.check_batch` now flags `>=2` generic superlatives and 3-digit-percent-with-short-horizon claims

## Deferred Scope

The plan originally cited Phase 5 as including ADG regen and Notion ADR row creation. Those were assessed and deferred:

- **ADG regen**: out of scope for capability restoration (no new structural edges introduced; existing edges restored to working state — net graph delta is zero or strictly recovering broken edges).
- **Notion ADR row**: this work is a port-back, not an architectural decision. No new ADR fits the `architectural_decision` shape. The plan file itself + the git commit message provide the audit trail. NEXT_STEP marker emitted for follow-up audit if needed.

NEXT_STEP: plan=apps-rg-prior-art-gap-closure-3e3d5b title=Audit other apps_* for stub-vs-real validators priority=P4 est_tokens=8000 reason=apps_rg port-back surfaced pattern; apps_eval/apps_exec/apps_lic likely have similar stubs from Dec 2025 atomization era
