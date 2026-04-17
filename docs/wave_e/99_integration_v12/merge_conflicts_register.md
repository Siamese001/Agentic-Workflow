# v1.2 Merge Conflicts Register

F2 integration pass. Base: canonical v1.1. Delta: F2 source-authoring proposals.

## Conflict inventory

**Total non-trivial conflicts: 0.**

F2's scope was narrow (6 sources + 9 atom patches + 1 supplementary binding) and did not touch any of the v1.1 entities that prior waves had already stabilized. All v1.1 records pass through unchanged except for the 10 atoms whose `evidence_class` and/or `authority_binding` were updated by F2.

## Minor merge decisions (trivial)

| # | Decision | Resolution |
|---|---|---|
| M-v12-01 | Where to append F2 sources in `sources.yaml` | Appended after SRC-INT-004 under comment `# === F2 additions ===`. No conflict with existing ordering. |
| M-v12-02 | Whether to preserve `authority_binding: [SRC-INT-003]` when adding a new SRC-ADR-NNN | Preserved: authority_binding becomes `[SRC-INT-003, SRC-ADR-NNN]`. Additive, not replacement. Justified by schema rule that each binding lists all contributing sources. |
| M-v12-03 | Whether F2's proposal files rationale text should leak into canonical atoms | **Rejected.** F2 proposals included `rationale:` and `status: DRAFT` fields per the sidecar shape. Canonical atoms retain only schema-defined fields (id, family_id, claim, evidence_class, authority_binding, status, owning_layer). Rationale stays in `docs/wave_e/F2_source_authoring/source_authoring_log.md`. |
| M-v12-04 | DRAFT → ACTIVE promotion discipline | All 10 patched atoms were already `status: ACTIVE` in v1.1. The F2 proposal file marks them DRAFT (convention for a proposal file) but v1.2 canonical preserves ACTIVE — the patch is an evidence-binding update, not a new atom. |
| M-v12-05 | Whether edges referencing upgraded atoms should be re-evaluated | **Deferred.** Edges `INT-F08.04-F09.01-01`, `INT-F09.05-F08.04-01`, `INT-F07.03-F02.01-01`, `INT-F07.03-F05.01-01`, `INT-F12.08-F08.03-01` still carry `evidence_class: WEAK_EVIDENCE`. F2 proposed no edge patches, so v1.2 inherits them unchanged. Logged as D-v12-01 in the HITL ledger. |

## Sources considered and NOT integrated

Per `authored_source_index.md`:

| Candidate | Reason declined |
|---|---|
| `docs/architecture/write_governance_note.md` | `invalid_for_normative_use=True`; F09 is already GREEN in v1.2. |
| `docs/specs/hardening/UWG_ISOLATION_SPEC.md` | F09 already GREEN; no atom benefits. |
| `docs/specs/hardening/L6_DRIFT_SAFEGUARDS_SPEC.md` | F12 already GREEN. |
| `docs/specs/hardening/POLICY_EPOCH_SPEC.md` | F11 already GREEN. |
| `docs/contracts/guardian_to_L6.md` | F12.07/.08 already NORMATIVE post-F1. |
| `docs/requirements/normative_requirements_spec.md` | Scope is retrieval/routing, not agentic-workflow context. |

None of these were added because adding them would not change any atom state.

## ADVISORY discipline

SRC-ADR-001 (healing_dispatch_routing_adr) is the only ADVISORY-class source in v1.2. It is bound as **supplementary** context to F07.03 only, via the proposal rationale. v1.2 canonical does NOT list SRC-ADR-001 in F07.03's `authority_binding` array because the array is reserved for sources that actually support the declared `evidence_class`. F07.03 stays WEAK_EVIDENCE with binding `[SRC-INT-003]` — the ADR-001 context remains documented in the F2 sidecars.

Validation confirms: zero atoms cite SRC-ADR-001 in authority_binding, so no atom is supported only by ADVISORY evidence.

## Outcome

v1.2 is a clean additive merge. No conflicts required HITL escalation beyond the routine decisions above.
