# v1.2 Merge Conflicts Register

F2 integration pass. Base: canonical v1.1. Delta: F2 source-authoring proposals. All counts in this document reflect the F2.1 reporting reconciliation pass.

## Conflict inventory

**Total non-trivial conflicts: 0.**

F2's scope was narrow (6 sources + 9 atom evidence-class upgrades + 1 supplementary binding) and did not touch any v1.1 entities that prior waves had stabilized. All v1.1 records pass through unchanged except for the 10 atoms whose `evidence_class` and/or `authority_binding` were updated by F2.

## Minor merge decisions (trivial)

| # | Decision | Resolution |
|---|---|---|
| M-v12-01 | Where to append F2 sources in `sources.yaml` | Appended after SRC-INT-004 under comment `# === F2 additions ===`. No conflict with existing ordering. |
| M-v12-02 | Whether to preserve `authority_binding: [SRC-INT-003]` when adding a new SRC-ADR-NNN | Preserved; authority_binding becomes `[SRC-INT-003, SRC-ADR-NNN]`. Additive, not replacement. |
| M-v12-03 | Whether F2 proposal sidecar fields (`rationale:`, `status: DRAFT`) should leak into canonical atoms | Rejected. Canonical atoms retain only schema-defined fields. Rationale stays in `docs/wave_e/F2_source_authoring/source_authoring_log.md`. |
| M-v12-04 | DRAFT → ACTIVE promotion discipline | All 10 patched atoms were already ACTIVE in v1.1; v1.2 preserves ACTIVE. Proposal-file DRAFT convention does not demote canonical state. |
| M-v12-05 | Whether edges referencing upgraded atoms should be re-evaluated | **Deferred.** F2 proposed no edge patches, so v1.2 inherits all 26 v1.1 edges unchanged. Details logged as D-v12-01 in the HITL ledger. |

## Sources considered and NOT integrated

| Candidate | Reason declined |
|---|---|
| `docs/architecture/write_governance_note.md` | `invalid_for_normative_use=True`; F09 already GREEN in v1.2. |
| `docs/specs/hardening/UWG_ISOLATION_SPEC.md` | F09 already GREEN; no atom benefits. |
| `docs/specs/hardening/L6_DRIFT_SAFEGUARDS_SPEC.md` | F12 already GREEN. |
| `docs/specs/hardening/POLICY_EPOCH_SPEC.md` | F11 already GREEN. |
| `docs/contracts/guardian_to_L6.md` | F12.07/.08 already NORMATIVE post-F1. |
| `docs/requirements/normative_requirements_spec.md` | Scope is retrieval/routing, not agentic-workflow context. |

None of these would change any atom state, so they were not registered.

## ADVISORY discipline

SRC-ADR-001 (`healing_dispatch_routing_adr.md`) is the only ADVISORY-class source in v1.2. Its source document carries `invalid_for_normative_use=True`. Per schema rules, ADVISORY sources cannot support NORMATIVE atoms.

**Canonical discipline preserved:**
- SRC-ADR-001 appears in `sources.yaml` with `authority_class: ADVISORY`.
- SRC-ADR-001 does NOT appear in any atom's `authority_binding` in v1.2. F07.03 (the only atom where SRC-ADR-001 is topically relevant) keeps its v1.1 binding `[SRC-INT-003]` and stays WEAK_EVIDENCE. SRC-ADR-001 is documented as advisory context only in `docs/wave_e/F2_source_authoring/source_authoring_log.md`.

Validation confirms 0 atoms cite SRC-ADR-001 in `authority_binding`; no atom is supported only by ADVISORY evidence.

## Edge evidence unchanged

v1.2 has **26 edges total**: **18 NORMATIVE** + **8 WEAK_EVIDENCE**. The WEAK_EVIDENCE count is identical to v1.1; F2 proposed no edge patches. Full enumeration and endpoint profile in `coverage_report.md` §"Weak edges". Of the 8 weak edges:

- 5 have both endpoints NORMATIVE (candidates for a future edge-evidence upgrade using SRC-ADR-003).
- 3 have at least one WEAK atom endpoint (blocked on atom upgrades).

Not addressed in F2's scope by design. Logged as follow-up D-v12-01.

## Outcome

v1.2 is a clean additive merge. No conflicts required HITL escalation beyond the routine decisions above.
