# Wave F4 — Edge-Evidence and Exclusion Cleanup (Proposal Lane)

Bounded cleanup pass targeting the two non-family remnants after canonical v1.3:
- 8 WEAK_EVIDENCE edges carried forward unchanged since v1.1
- OOS-003 exclusion whose revisit trigger is now satisfied

This directory contains F4 proposals only. Canonical v1.3 YAML is NOT modified. A later integration pass (v1.4) applies these proposals.

## Base

- `docs/wave_e/99_integration_v13/canonical/` (v1.3 with all 60 ACTIVE atoms NORMATIVE)
- All 15 canonical sources available; no new sources authored in F4.

## Scope fences (explicit)

- **In scope:** evaluate each of the 8 v1.3 weak edges against the existing canonical source set; propose edge `evidence_class` and/or `authority_binding` updates where a canonical source directly supports the edge claim. Review OOS-003 against SRC-ADR-007 and propose a state transition if the exclusion's rationale is genuinely superseded.
- **Out of scope:** no new families, no new atoms, no reopening of closed atoms, no new sources, no B7 interaction candidate closures, no edge-kind or direction changes.

## Outcome summary

| Scope item | Result |
|---|---|
| 8 weak edges evaluated | **8 upgrade proposals to NORMATIVE**; 0 remain WEAK |
| OOS-003 reviewed | **Revision proposal**: reason NOT_YET_DECIDED → SUPERSEDED |
| B7 byproducts | **None.** No B7 candidate is triggered as a free byproduct of the edge upgrades. |
| New schema drift | **None.** No new fields, enums, or ID formats. |

## Artifacts

- `proposals/families.yaml` — empty
- `proposals/atoms.yaml` — empty (explicitly: no atom claims reopened)
- `proposals/edges.yaml` — 8 edge patches (evidence_class and authority_binding only)
- `proposals/exclusions.yaml` — 1 revision patch (OOS-003)
- `proposals/sources.yaml` — empty (F4 reuses v1.3 sources only)
- `weak_edge_upgrade_matrix.md` — per-edge direct-support analysis
- `exclusion_review_log.md` — OOS-003 review against SRC-ADR-007
- `cleanup_decision_log.md` — every non-trivial F4 decision

## Ready for integration

**YES.** All proposals validate against the frozen E0 schema. Every edge upgrade cites at least one existing canonical source that directly states the edge claim (not merely supports the endpoint atoms). The OOS-003 revision follows the "truly supersedes" bar defined in the F4 contract.

After a v1.4 integration pass accepts these proposals:
- 26/26 edges would be NORMATIVE.
- OOS-003 would move to reason=SUPERSEDED with SRC-ADR-007 cited.
- Only remaining open items would be B7 (6 deferred interaction candidates), which requires a future wave with explicit HITL approval.

## Remaining blockers after F4 proposals are integrated

| # | Blocker | Notes |
|---|---|---|
| B7 | 6 deferred interaction candidates from E1d | Requires new atoms or edges. Explicitly out of F4 scope. |

No other blockers remain. The atom surface is fully closed and — assuming a v1.4 pass accepts this F4 proposal — the edge surface and exclusion surface are also closed.
