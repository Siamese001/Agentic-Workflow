# ADR: 00C.7 owns GateVerdict schema (parent §5 is export checklist only)

**Status:** Accepted (W1 decision, plan `l5-l4-00c-parent-gap-b8e4f2`)  
**Date:** 2026-05-23

## Context

The REQ-ID rewrite of [00C_Runtime_Gates_Current_Run_Mesh.md](../reference/00C_Runtime_Gates_Current_Run_Mesh/00C_Runtime_Gates_Current_Run_Mesh.md) parent §5 defines a minimal `GateVerdict` JSON (6 dispositions, 4 results). The long-standing child pack [00C.7_Runtime_Gates_Verdict_Schema_Disposition_Matrix.md](../reference/00C_Runtime_Gates_Current_Run_Mesh/00C.7_Runtime_Gates_Verdict_Schema_Disposition_Matrix.md) defines the implementation-grade contract (15 dispositions, 5 results, extended fields). The running mesh, 452+ tests, and FortKnox certification bundles implement **00C.7**.

## Decision

1. **SSOT for runtime gate verdicts:** `00C.7` + `agentic_core/L5_safety/runtime_gates/types.py` (`GateDecision.to_verdict()`, `SCHEMA_VERSION=00C-1.0.0`).
2. **Parent 00C §5:** Non-authoritative for mesh internals; treat as REQ-ID audit checklist. Doc follow-up should add explicit deferral to 00C.7.
3. **Gate IDs G01–G29:** Stable; do **not** relabel modules to match parent §4 semantic titles (G21–G24 band mismatch). Child files `00C.5` / `00C.6` + layer dispatch map govern semantics.
4. **External export (optional W4):** A thin adapter may project 00C.7 verdicts to a six-disposition `export_profile` for auditors; mesh serialization unchanged.

## Consequences

- W4 gate-band migration is **cancelled** unless parent pack is rewritten to match 00C.7.
- FortKnox / integrated-runtime bundles remain valid without digest-breaking schema churn.
- Parent §4 rows for G21–G24 remain **DRIFT** in gap matrix until docs amended.

## Evidence

- [l5-l4-00c-parent-gap-matrix-b8e4f2.json](../reports/plans/l5-l4-00c-parent-gap-matrix-b8e4f2.json)
- [runtime_gates_doctrine_requirements_matrix.md](../reports/plans/runtime_gates_doctrine_requirements_matrix.md)
