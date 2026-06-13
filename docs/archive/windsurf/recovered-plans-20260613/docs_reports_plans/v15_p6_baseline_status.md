# V15 P1–P6 Baseline Status — COMPLETE

**Generated**: 2026-02-09
**Audit contract**: Prompt v5.0 Enhanced
**Discovery hash**: `f09ec166b82746f6d62cf1c7e9215de70ec29534f784bee95d13798b04da4fd4`
**Branch**: `agentic-core-v5.2`

---

## Priority Compliance Summary

| Priority | Items | Status | Delta Report | Commit |
| --- | --- | --- | --- | --- |
| P1 (Fail-Closed) | 24/24 | **COMPLIANT** | [p1_audit_delta.md](p1_audit_delta.md) | `055874ab0` |
| P2 (Determinism) | 17/17 | **COMPLIANT** | [p2_audit_delta.md](p2_audit_delta.md) | `0abf61385` |
| P3 (Governance) | 3/3 | **COMPLIANT** | [p3_audit_delta.md](p3_audit_delta.md) | `b20edd5ff` |
| P4 (Traceability) | 8/8 | **COMPLIANT** | [p4_audit_delta.md](p4_audit_delta.md) | `118d1b74f` |
| P5 (Crypto Trust) | 7/7 | **COMPLIANT** | [p5_audit_delta.md](p5_audit_delta.md) | `c4e7c3f68` |
| P6 (Meta-Invariants) | 4/4 + meta | **COMPLIANT** | [p6_audit_delta.md](p6_audit_delta.md) | `e2273263a` |
| Integration Wiring | gateway | **PASS** | [test_v15_integration_wiring.py](../../tests/guardian/test_v15_integration_wiring.py) | `53974bb46` |

---

## Test Suite Summary

| Suite | File | Tests | Skips | Status |
| --- | --- | --- | --- | --- |
| P1 Compliance | `tests/guardian/test_v15_p1_compliance.py` | 60 | 0 | PASS |
| P2 Compliance | `tests/guardian/test_v15_p2_compliance.py` | 64 | 0 | PASS |
| P3 Compliance | `tests/guardian/test_v15_p3_compliance.py` | 47 | 0 | PASS |
| P4 Compliance | `tests/guardian/test_v15_p4_compliance.py` | 53 | 0 | PASS |
| P5 Compliance | `tests/guardian/test_v15_p5_compliance.py` | 52 | 0 | PASS |
| P6 Compliance | `tests/guardian/test_v15_p6_compliance.py` | 40 | 0 | PASS |
| Baseline Pins | `tests/guardian/test_v15_baseline_pins.py` | 3 | 0 | PASS |
| Integration Wiring | `tests/guardian/test_v15_integration_wiring.py` | 17 | 0 | PASS |
| **Combined** | | **336** | **0** | **PASS** |

---

## Discovery Integrity Pin

| Artifact | SHA-256 | Status |
| --- | --- | --- |
| `artifacts/forensic_discovery_output.json` | `f09ec166b82746f6d62cf1c7e9215de70ec29534f784bee95d13798b04da4fd4` | PINNED |

---

## Scope Freeze Declaration

All P1–P6 invariants from Prompt v5.0 Enhanced are now COMPLIANT with typed artifacts, enforcement contracts, and regression tests. This baseline is frozen. Any future changes must:

1. Not weaken existing V15 tests (336 tests, 0 skips).
2. Not modify the pinned discovery hash.
3. Produce a new audit delta if any P1–P6 artifact is changed.

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

