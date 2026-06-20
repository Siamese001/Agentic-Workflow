---
slug: ask-user-question-test-hardening-a7f2e3
status: Completed
dod_exempt: false
---

# Ask User Question Test Hardening

**Objective**: Harden test cases for `ask_user_question` to enforce the same style requirements as Author-Gate — confidence levels, clickable options, dominance star, SQLite persistence, and meta-learning shadow learning loop.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1 | E2E 4-requirement contract tests in enriched_choice_builder | ~4k | Builder API stable | ✅ DONE | 7 new tests pass |
| W2 | P2 | SQLite round-trip + integrity tests in ask_user_question_ledger | ~5k | Ledger schema stable | ✅ DONE | 10 new tests pass |
| W3 | P3 | Shadow/meta-learning loop tests (new file) | ~6k | Dashboard + ledger wired | ✅ DONE | 10 new tests pass |
| W4 | P4 | Run all tests green | ~1k | No regressions | ✅ DONE | 62/62 pass |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1 | E2E Four-Requirement Contract | test_enriched_choice_builder.py | Missing Author-Gate-equivalent invariant assertions | ~4k | ✅ DONE |
| P2 | SQLite Round-Trip Integrity | test_ask_user_question_ledger.py | No full-packet round-trip or confidence precision tests | ~5k | ✅ DONE |
| P3 | Shadow Learning Loop | test_ask_user_question_shadow_loop.py (NEW) | No tests for build→write→consult→inform pipeline | ~6k | ✅ DONE |
| P4 | Verification | All 3 test files | Regression risk | ~1k | ✅ DONE |

## Files In Scope

### Modified
- `tests/unit/tools/decisions/test_enriched_choice_builder.py` — +7 tests (TestE2EFourRequirementContract)
- `tests/unit/ledgers/test_ask_user_question_ledger.py` — +10 tests (TestSQLiteRoundTripIntegrity + TestBuildToLedgerIntegration)

### Created
- `tests/unit/ledgers/test_ask_user_question_shadow_loop.py` — +10 tests (NEW FILE: shadow learning loop)

## Test Inventory (27 new tests)

### TestE2EFourRequirementContract (7 tests)
1. `test_all_four_invariants_with_recommendation` — Full pipeline with recommended option satisfies INV-1..INV-4
2. `test_all_four_invariants_without_recommendation` — No-recommendation: zero stars, all invariants hold
3. `test_telemetry_packet_round_trips_with_all_fields` — Packet has all required fields for SQLite writeback
4. `test_confidence_score_precision_two_decimals` — Labels use exactly 2 decimal places across edge values
5. `test_tradeoff_minimum_length_enforced` — Tradeoff text has meaningful content (≥10 chars)
6. `test_mixed_explicit_and_heuristic_confidence` — Explicit wins for telemetry; heuristic default displayed
7. `test_star_never_appears_in_description` — Star only in label, never in description

### TestSQLiteRoundTripIntegrity (8 tests)
1. `test_full_packet_round_trip_preserves_all_fields` — Write→read preserves all fields
2. `test_invariants_json_survives_round_trip` — Invariants list serialized/deserialized correctly
3. `test_confidence_score_precision_preserved` — REAL storage preserves confidence precision
4. `test_duplicate_decision_id_rejected` — IntegrityError on duplicate
5. `test_selected_index_none_when_not_provided` — NULL not 0 when omitted
6. `test_heuristic_default_confidence_source_persisted` — Default confidence source + score persisted
7. `test_list_recent_ordered_by_created_at_desc` — Most recent first
8. `test_packet_json_contains_full_original_packet` — Complete original dict stored

### TestBuildToLedgerIntegration (2 tests)
1. `test_builder_telemetry_writes_to_ledger` — enriched_choice_builder → ledger round-trip
2. `test_builder_no_recommendation_writes_null_recommended` — NULL recommended_index

### TestBuildWriteDashboardLoop (2 tests)
1. `test_single_decision_appears_in_dashboard_metrics` — Dashboard reports decision
2. `test_multiple_decisions_aggregate_in_dashboard` — Counts aggregate by context

### TestVacuumClosureHealth (2 tests)
1. `test_healthy_when_all_have_packets` — 100% coverage passes
2. `test_empty_ledger_is_healthy` — Vacuously true

### TestPrecedentQueryFromLedger (4 tests)
1. `test_list_recent_returns_written_decisions` — Retrievable via list_recent_decisions
2. `test_precedent_query_by_context_filters_correctly` — Context filtering works
3. `test_precedent_preserves_selected_index_for_learning` — Recommendation vs selection mismatch captured
4. `test_confidence_score_retrievable_for_calibration` — Scores survive for calibration

### TestFullShadowLearningCycle (2 tests)
1. `test_shadow_cycle_recommendation_vs_selection_tracking` — Full build→write→consult→adjust→write cycle
2. `test_telemetry_dashboard_reflects_shadow_cycle` — Dashboard reflects learning session

## Definition of Done

| DoD | Criterion | Status |
|-----|-----------|--------|
| DoD-1 | All 4 Author-Gate invariants (clickable, confidence, tradeoff, star) tested for enriched_choice_builder | ✅ DONE |
| DoD-2 | SQLite round-trip preserves all fields including confidence precision | ✅ DONE |
| DoD-3 | Shadow learning loop: build→write→consult→inform tested end-to-end | ✅ DONE |
| DoD-4 | `python -m pytest tests/unit/tools/decisions/test_enriched_choice_builder.py tests/unit/ledgers/test_ask_user_question_ledger.py tests/unit/ledgers/test_ask_user_question_shadow_loop.py` exits 0 | ✅ DONE (62/62 pass) |
| DoD-5 | Plan + results registered in Notion | ✅ DONE |

## Verification vs Deferral

| Item | Verified This Plan | Deferred |
|------|-------------------|----------|
| 4-invariant contract | ✅ 7 tests | — |
| SQLite integrity | ✅ 10 tests | — |
| Shadow learning loop | ✅ 10 tests | — |
| Real LedgerConsulter integration | — | Future: wire ask_user_question decisions into the schema_registry LedgerConsulter framework |
| Weekly calibration report for ask_user_question | — | Future: ops_scripts/calibration/ reporter for recommendation-vs-selection mismatch rates |

PLAN_COMPLETE: plan=ask-user-question-test-hardening-a7f2e3 note="27 new tests, 62/62 green, 3 files touched"
