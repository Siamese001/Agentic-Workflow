# System Learning Phase 5 — Evidence File

## 1. Commit Hash

```
ef297c802ebab37955beea8c6b13990eb8bcefa1
```

## 2. File List (git diff --name-only HEAD~1..HEAD)

```
system_learning/engines/rca_engine.py
system_learning/engines/telemetry_consumer.py
system_learning/types/rca_types.py
system_learning/types/telemetry_types.py
tests/unit_min_deps/system_learning/test_rca_engine.py
tests/unit_min_deps/system_learning/test_rca_types.py
tests/unit_min_deps/system_learning/test_telemetry_consumer.py
```

7 files changed, 1186 insertions(+)

## 3. pytest -q (Run 1)

```
tests/unit_min_deps/system_learning/test_rca_types.py::TestRCATypes::test_deterministic_hash_stability PASSED
tests/unit_min_deps/system_learning/test_rca_types.py::TestRCATypes::test_findings_ordering_canonical PASSED
tests/unit_min_deps/system_learning/test_rca_types.py::TestRCATypes::test_changing_evidence_changes_hash PASSED
tests/unit_min_deps/system_learning/test_rca_types.py::TestRCATypes::test_report_id_equals_report_hash PASSED
tests/unit_min_deps/system_learning/test_rca_types.py::TestDeterminism::test_canonical_bytes_deterministic PASSED
tests/unit_min_deps/system_learning/test_rca_types.py::TestDeterminism::test_compute_report_hash_deterministic PASSED
tests/unit_min_deps/system_learning/test_rca_engine.py::TestRCAEngine::test_analyze_failures_basic PASSED
tests/unit_min_deps/system_learning/test_rca_engine.py::TestRCAEngine::test_exact_findings_counts PASSED
tests/unit_min_deps/system_learning/test_rca_engine.py::TestRCAEngine::test_determinism_same_slice_identical_report_id PASSED
tests/unit_min_deps/system_learning/test_rca_engine.py::TestRCAEngine::test_invalid_window_rejected PASSED
tests/unit_min_deps/system_learning/test_rca_engine.py::TestRCAEngine::test_malformed_utf8_rejected PASSED
tests/unit_min_deps/system_learning/test_rca_engine.py::TestRCAEngine::test_empty_slice_produces_unknown_category PASSED
tests/unit_min_deps/system_learning/test_rca_engine.py::TestRCAEngine::test_no_matching_patterns_produces_unknown PASSED
tests/unit_min_deps/system_learning/test_rca_engine.py::TestDeterminism::test_analyze_failures_deterministic PASSED
tests/unit_min_deps/system_learning/test_telemetry_consumer.py::TestTelemetryConsumer::test_deterministic_slice_id_across_two_calls PASSED
tests/unit_min_deps/system_learning/test_telemetry_consumer.py::TestTelemetryConsumer::test_sorting_stable_and_canonical PASSED
tests/unit_min_deps/system_learning/test_telemetry_consumer.py::TestTelemetryConsumer::test_invalid_window_rejected PASSED
tests/unit_min_deps/system_learning/test_telemetry_consumer.py::TestTelemetryConsumer::test_empty_window_produces_empty_slice PASSED
tests/unit_min_deps/system_learning/test_telemetry_consumer.py::TestTelemetryConsumer::test_window_filtering PASSED
tests/unit_min_deps/system_learning/test_telemetry_consumer.py::TestTelemetryConsumer::test_payload_hash_computed PASSED
tests/unit_min_deps/system_learning/test_telemetry_consumer.py::TestTelemetryConsumer::test_same_timestamp_different_kind_sorted PASSED
tests/unit_min_deps/system_learning/test_telemetry_consumer.py::TestDeterminism::test_consume_telemetry_deterministic PASSED

22 passed in 0.04s
```

## 4. pytest -q (Run 2 — Determinism Proof)

```
22 passed in 0.04s
```

Identical result. All 22 tests pass on both runs.

## 5. Deterministic report_id/slice_id Assertion (from test_rca_engine.py, lines 76-97)

```python
def test_determinism_same_slice_identical_report_id(self):
    """Same audit_slice produces identical report_id."""
    report1 = analyze_failures(
        snapshot_id="snap123",
        audit_slice=AUDIT_SLICE_FIXTURE,
        window_start_utc=1700000000,
        window_end_utc=1700003600,
    )

    report2 = analyze_failures(
        snapshot_id="snap123",
        audit_slice=AUDIT_SLICE_FIXTURE,
        window_start_utc=1700000000,
        window_end_utc=1700003600,
    )

    assert report1.report_id == report2.report_id
    assert report1.report_hash == report2.report_hash
```

## Acceptance Criteria Checklist

| Criterion | Status |
|-----------|--------|
| All types/engines deterministic, fail-closed, input-injected only | PASS |
| No activation pointer updates or store commits | PASS |
| All tests pass twice identically | PASS |
| RCA report with deterministic hash | PASS |
| Telemetry slice with deterministic hash | PASS |
| No wall-clock/randomness/env access | PASS |
| No cross-layer imports | PASS |

## Phase 5 Implementation Summary

**Wave 5.1 — RCA Report Types + Deterministic Hashed Report:**
- `RCAFinding`: category, signature, count, evidence_hash
- `RCAReport`: report_id, snapshot_id, window_start_utc, window_end_utc, findings, report_hash
- `canonical_bytes(report)`: sorted keys, stable ordering of findings by (category, signature)
- `report_hash = SHA-256(canonical_bytes(report))`
- `report_id = report_hash`
- Deterministic hash stability across two constructions with same inputs ✓
- Findings ordering is canonical ✓
- Changing one byte in evidence changes report_hash ✓

**Wave 5.2 — RCA Engine (Pure Analyzer):**
- `analyze_failures(snapshot_id, audit_slice, window_start_utc, window_end_utc) -> RCAReport`
- Deterministic parsing rules for audit_slice:
  - Treat audit_slice as UTF-8 text lines (fail-closed if decode fails)
  - Classify into categories: SYNTAX, IMPORT, TEST_DISCOVERY, POLICY_BLOCK, TIMEOUT, UNKNOWN
  - Signature = stable normalized line prefix or stable regex capture
  - Count occurrences per (category, signature)
  - evidence_hash = SHA-256 of canonical normalized evidence bytes
  - Findings sorted deterministically
- No randomness/time/env ✓
- Fail-closed on malformed input ✓

**Wave 5.3 — Telemetry Consumer (Read-Only Slice Builder):**
- `TelemetryEvent`: ts_utc, kind, payload_hash
- `TelemetrySlice`: slice_id, window_start_utc, window_end_utc, events, slice_hash
- `TelemetryStore` Protocol: `read_events(window_start_utc, window_end_utc) -> tuple[tuple[int, str, bytes], ...]`
- `consume_telemetry(store, window_start_utc, window_end_utc) -> TelemetrySlice`
- Enforces:
  - window_start < window_end ✓
  - Deterministic sorting by (ts_utc, kind, payload_hash) ✓
  - slice_hash = SHA-256(canonical_bytes(slice)) ✓
  - slice_id = slice_hash ✓
- No wall-clock, no env, no randomness ✓

**Coverage:**
- Deterministic hash stability ✓
- Findings ordering canonical ✓
- Changing evidence changes hash ✓
- Exact findings match expected categories, signatures, counts ✓
- Same slice => identical report_id ✓
- Invalid window rejected ✓
- Malformed UTF-8 rejected ✓
- Empty slice produces UNKNOWN category ✓
- Deterministic slice_id across two calls ✓
- Sorting stable and canonical ✓
- Window filtering ✓
- Payload hash computed ✓

**Key Invariants:**
- Zero execution authority preserved
- No activation pointer updates in Phase 5
- All types/engines are deterministic and side-effect free
- Fail-closed on any violation
- No wall-clock, randomness, or environment access
- Read-only inputs, proposal-only outputs
- No store commits
