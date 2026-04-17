# v1.4 Coverage Report — Delta vs v1.3

All counts recounted directly from `canonical/*.yaml`.

## Global

| Metric | v1.3 | v1.4 | Δ |
|---|---:|---:|---:|
| Atoms total | 61 | 61 | 0 |
| Atoms ACTIVE | 60 | 60 | 0 |
| Atoms EXCLUDED | 1 | 1 | 0 |
| Atoms NORMATIVE | 60 | 60 | 0 |
| Atoms WEAK_EVIDENCE | 0 | 0 | 0 |
| Atom coverage | 1.000 GREEN | 1.000 GREEN | — |
| Edges total | 26 | 26 | 0 |
| Edges NORMATIVE | 18 | **26** | **+8** |
| Edges WEAK_EVIDENCE | 8 | **0** | **-8** |
| Edge coverage | 0.692 | **1.000** | **+0.308** |

## Per-family atom coverage (unchanged — all already GREEN in v1.3)

| Family | v1.3 | v1.4 | Bucket |
|---|---:|---:|---|
| F01 | 1.000 | 1.000 | GREEN |
| F02 | 1.000 | 1.000 | GREEN |
| F03 | 1.000 | 1.000 | GREEN |
| F04 | 1.000 | 1.000 | GREEN |
| F05 | 1.000 | 1.000 | GREEN |
| F06 | 1.000 | 1.000 | GREEN |
| F07 | 1.000 | 1.000 | GREEN |
| F08 | 1.000 | 1.000 | GREEN |
| F09 | 1.000 | 1.000 | GREEN |
| F10 | 1.000 | 1.000 | GREEN |
| F11 | 1.000 | 1.000 | GREEN |
| F12 | 1.000 | 1.000 | GREEN |

## Per-edge upgrade detail

All 8 v1.3 weak edges upgrade. New bindings below are the result of F4's direct-support analysis (see `F4_edge_exclusion_cleanup/weak_edge_upgrade_matrix.md`).

| Edge | Kind | v1.3 binding | v1.4 binding |
|---|---|---|---|
| INT-F02.01-F01.05-01 | DEPENDS_ON | [SRC-INT-002] WEAK | [SRC-RULE-001, SRC-INT-001, SRC-INT-003] NORMATIVE |
| INT-F05.04-F06.01-01 | REQUIRES | [SRC-INT-003] WEAK | [SRC-INT-003, SRC-ADR-008] NORMATIVE |
| INT-F07.03-F02.01-01 | CONDITIONAL_ON | [SRC-INT-003] WEAK | [SRC-INT-003, SRC-ADR-008, SRC-ADR-009] NORMATIVE |
| INT-F07.03-F05.01-01 | REQUIRES | [SRC-INT-003] WEAK | [SRC-INT-003, SRC-ADR-008, SRC-ADR-009] NORMATIVE |
| INT-F08.04-F09.01-01 | REQUIRES | [SRC-INT-003] WEAK | [SRC-INT-003, SRC-ADR-003] NORMATIVE |
| INT-F09.05-F08.04-01 | REQUIRES | [SRC-INT-003] WEAK | [SRC-INT-003, SRC-ADR-003] NORMATIVE |
| INT-F12.05-F02.01-01 | DEPENDS_ON | [SRC-INT-002] WEAK | [SRC-RULE-001, SRC-INT-001, SRC-INT-004] NORMATIVE |
| INT-F12.08-F08.03-01 | DEPENDS_ON | [SRC-INT-004] WEAK | [SRC-INT-004, SRC-ADR-003] NORMATIVE |

Edge `edge_kind`, `direction`, `status`, and `condition` fields are preserved verbatim across all 8 patches. Only `evidence_class` and `authority_binding` changed.

## Remaining WEAK entities

- **Atoms:** 0 (was 0 in v1.3)
- **Edges:** 0 (down from 8 in v1.3)

## Source contributions (F4)

F4 authored no new sources. All 8 edge upgrades cite only v1.3 canonical sources, demonstrating that the direct-support evidence was already present in the graph — it had simply not been connected to the edges until F4's review pass.

| Source | Edges it now supports (new) | Role |
|---|---:|---|
| SRC-RULE-001 | 3 | Constitutional layer ordering / UWG discipline / memory-lifecycle §17 |
| SRC-INT-001 | 3 | AGENTS.md layer separation |
| SRC-INT-003 | 4 | Governing semantics |
| SRC-INT-004 | 3 | AGENTS.md Memory Lifecycle |
| SRC-ADR-003 | 3 | Eval-pipeline acceptance (spine ↔ UWG) |
| SRC-ADR-008 | 3 | ADR-L3-001 (dispatch + L3-I3 re-plan receiving) |
| SRC-ADR-009 | 2 | ADR-ESC-001 (escalation target) |

## Exclusion delta

OOS-003 moved from `NOT_YET_DECIDED` to `SUPERSEDED` with SRC-ADR-007 cited as supersession source. The cross-enum rule "no ACTIVE atom cites any Exclusion as authority" is preserved: 0 ACTIVE atoms cite OOS-003 (or any other OOS) in v1.4.

OOS-001 and OOS-002 are unchanged.

## Summary

v1.4 closes the edge-evidence gap and the OOS-003 open decision. The graph is now fully NORMATIVE across both atoms and edges. B7 (6 deferred interaction candidates) is the sole remaining follow-up and is outside F4's scope.
