# Wave E1 Integration — Merge Conflicts Register

Every non-trivial merge decision applied during the E1 integration pass, with resolution and rationale.

---

## MC-01 — Placeholder SRC IDs in 56 E1b atoms

**Conflict:** E1b atoms cite mnemonic SRC IDs (`SRC-ADR-L0`..`SRC-ADR-L6`, `SRC-ADR-WG`, `SRC-ADR-EXIT`) that do NOT match the schema regex `^SRC-(INT|EXT|ADR|RULE|CODE|DEC)-[0-9]{3}$`.
**Resolution:** Apply E1c's canonical placeholder-to-real mapping (see `docs/wave_e/E1c_authority_scope/evidence_binding_notes.md §1`):
- `SRC-ADR-L0..L6` → `SRC-INT-003`
- `SRC-ADR-WG` → `SRC-INT-003`
- `SRC-ADR-EXIT` → `SRC-INT-003` (with downgrade where SRC-ADR-EXIT was sole binding; see MC-05)
**Applied to:** All 56 E1b atoms NOT superseded by E1c. Duplicates collapsed after mapping.
**Evidence:** Canonical `atoms.yaml` contains zero `SRC-ADR-*` or `SRC-ADR-EXIT` references.

## MC-02 — E1c atom patches (F04.01, F04.04, F08.05)

**Conflict:** E1c re-published three atoms with same IDs as E1b versions. Schema does not define a formal patch mechanism; `supersedes: <own_id>` used by E1c is non-standard (the schema's `supersedes` field is for cross-ID replacement).
**Resolution:** Apply last-writer-wins per atom ID. Integration uses the E1c version for F04.01, F04.04, F08.05; drops the `supersedes` field (self-reference is meaningless post-merge). E1b's corresponding versions are discarded.
**Evidence:** Canonical F04.01 and F04.04 carry E1c's DRAFT/evidence_class values (promoted to ACTIVE); canonical F08.05 is WEAK_EVIDENCE per E1c downgrade.

## MC-03 — F07 family `authority_class` correction

**Conflict:** E1a set `F07.authority_class: OPERATIONAL` (rank 5). F07.04 binds `SRC-RULE-001` (rank 1). Schema rule: "A Family's authority_class MUST be the MINIMUM rank number across its atoms' authority bindings." F07's minimum rank is 1 (CONSTITUTIONAL).
**Resolution:** Integration corrects `F07.authority_class` from OPERATIONAL to **CONSTITUTIONAL** in canonical `families.yaml`. Logged as `HITL-INT-F07-AUTH`.
**Note:** E1c flagged this (`DEC-E1c-F07-AUTH-CLASS`) and recommended ARCHITECTURAL; integration applied the strict schema-rule computation which yields CONSTITUTIONAL, not ARCHITECTURAL.
**Evidence:** `families.yaml` F07.authority_class == CONSTITUTIONAL, with `notes:` field recording the correction.

## MC-04 — Provisional `owning_layer` values on F01 / F04 / F08 / F09

**Conflict:** E1a set provisional owning_layers; E1c confirmed via decision log (DEC-E1c-F01/04/08/09-LAYER).
**Resolution:** Canonical uses E1c-confirmed values: F01=L0, F04=L1, F08=L5, F09=L4. `families.yaml.notes` records each confirmation.
**Evidence:** No UNRESOLVED atom remains due to layer ambiguity.

## MC-05 — `SRC-ADR-EXIT` unsourced

**Conflict:** Six atoms (F08.01, F08.02, F08.03, F08.04, F08.05, F09.05) cite `SRC-ADR-EXIT`, which has no real source. E1c materialized 5 sources but not an exit-spine source.
**Resolution per atom:**
- F08.02 (also cited SRC-RULE-001 + SRC-ADR-L5): retains NORMATIVE via SRC-RULE-001 + SRC-INT-003 (from mapped SRC-ADR-L5).
- F08.05 (sole binding was SRC-ADR-EXIT): E1c patched to WEAK_EVIDENCE with SRC-INT-003. Applied.
- F08.01, F08.03, F08.04: E1b marked WEAK_EVIDENCE. Integration maps SRC-ADR-EXIT → SRC-INT-003 and retains WEAK_EVIDENCE classification.
- F09.05: E1b marked WEAK_EVIDENCE. Same treatment.
**Residual:** F08 scorecard falls to 0.20 (RED). Blocker carried forward to Wave F.
**Evidence:** F08 canonical atoms all bind to SRC-INT-003 post-map.

## MC-06 — OOS overlap check (OOS-001 / OOS-002)

**Conflict:** OOS-001 (E1b, L6→L0 current-run influence) and OOS-002 (E1c, L6→L2 heal/retry current-run influence) are related but distinct.
**Resolution:** Both retained as separate exclusions. Overlap rule: neither exclusion's `scope_statement` subsumes the other. OOS-001 covers route decisions; OOS-002 covers heal/retry path. `related_atoms` overlap on F12.02/F12.03 but the exclusion targets differ.
**Evidence:** Both present in canonical `exclusions.yaml`; no de-duplication required.

## MC-07 — Authority bindings deduplication after placeholder mapping

**Conflict:** After mapping `SRC-ADR-L*` → `SRC-INT-003`, several atoms have duplicate `SRC-INT-003` entries (e.g. atom previously binding to `[SRC-ADR-L1, SRC-ADR-L2]` becomes `[SRC-INT-003, SRC-INT-003]`).
**Resolution:** Deduplicate `authority_binding` lists per atom, preserving order of first occurrence.
**Evidence:** Canonical atoms show single `SRC-INT-003` entry where duplicates would have resulted.

## MC-08 — Promotion DRAFT → ACTIVE

**Conflict:** Per contract, integration promotes DRAFT to ACTIVE only when authority bindings, edge endpoints, exclusion references, and status/evidence rules all resolve.
**Resolution:** All 58 non-EXCLUDED atoms cleared the checks:
- Authority binding: non-empty for NORMATIVE and WEAK_EVIDENCE atoms; valid SRC IDs only.
- Edge endpoints: all 23 edge endpoints resolve to atoms in canonical set.
- Exclusion refs: F12.06 references OOS-001 which exists.
- Status/evidence: no UNRESOLVED after E1c patches; F04.01 and F04.04 promoted after layer confirmation.
**Evidence:** Canonical `atoms.yaml` — 58 × `status: ACTIVE` + 1 × `status: EXCLUDED`. Canonical `edges.yaml` — all 23 × `status: ACTIVE`.

## MC-09 — No new Family IDs minted

**Conflict:** Verify no sub-wave minted a family beyond F01..F12.
**Resolution:** All 12 family IDs in canonical `families.yaml` match the E1-Setup seed registry exactly. No sub-wave attempted a new family mint.
**Evidence:** `id_allocations.log` shows family reservations only from `E1-Setup`.

## MC-10 — No canonical edge targets EXCLUDED atom

**Conflict:** Schema rule: ACTIVE edges cannot target EXCLUDED endpoints.
**Resolution:** Verified — F12.06 (the sole EXCLUDED atom) is not an endpoint of any of the 23 edges.
**Evidence:** See `integration_validation_report.md` orphan-and-endpoint checks.
