---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\v15_baseline_status.md'
original_relative_path: 'v15_baseline_status.md'
source_sha256: cf0aea521cbda096396b51069eb790da28fa998fdd700ff6c4072b0e2de99320
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-09'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# V15 Forensic Audit — Baseline Status

**Baseline Date**: 2026-02-09
**Branch**: `agentic-core-v5.2`

---

## Compliance Summary

| Priority | Items | Status | Evidence |
| --- | --- | --- | --- |
| P1 | 24 | 24/24 COMPLIANT | [p1_audit_delta.md](p1_audit_delta.md) |
| P2 | 17 | 17/17 COMPLIANT | [p2_audit_delta.md](p2_audit_delta.md) |
| P3 | 3 | Deferred — not in scope | — |
| P4 | 9 | Deferred — not in scope | — |
| P5 | 9 | Deferred — not in scope | — |
| P6 | 2 | Deferred — not in scope | — |

**Total remediated**: 41 / 64 (P1 + P2)
**Total deferred**: 23 (P3–P6, frozen — no scope creep)

---

## Discovery Integrity Pin

| Artifact | SHA-256 |
| --- | --- |
| `artifacts/forensic_discovery_output.json` | `f09ec166b82746f6d62cf1c7e9215de70ec29534f784bee95d13798b04da4fd4` |
| `agentic_core/L0_maintenance/scripts/forensic_discovery_prep.py` | `b08c3cdbabf064c9be69aa0b063d8573bf97392a30d8fff531a5fc9a2b1d2d31` |

Any change to discovery output or script invalidates this baseline.

---

## Test Suites

| Suite | File | Tests | Skips |
| --- | --- | --- | --- |
| P1 | `tests/guardian/test_v15_p1_compliance.py` | 60 | 0 |
| P2 | `tests/guardian/test_v15_p2_compliance.py` | 64 | 0 |
| Baseline Pins | `tests/guardian/test_v15_baseline_pins.py` | 3 | 0 |

---

## Typed Artifact Locations

| Module | Purpose |
| --- | --- |
| `agentic_core/L0_maintenance/types/v15_types.py` | P1 typed artifacts |
| `agentic_core/L0_maintenance/types/v15_contracts.py` | P1 enforcement contracts |
| `agentic_core/L0_maintenance/types/v15_p2_types.py` | P2 typed artifacts |
| `agentic_core/L0_maintenance/types/v15_p2_contracts.py` | P2 enforcement contracts |

---

## Scope Freeze Declaration

P3–P6 items remain at their current status as documented in
[p0_p1_remediation_backlog.md](p0_p1_remediation_backlog.md).
No P3–P6 work shall be undertaken without explicit authorization.
This baseline is the authoritative reference for the V15 audit closure state.

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

