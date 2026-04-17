# Wave E1 — Setup Lane

**Role:** Integration-lead pre-lane. Removes the missing-input blocker for E1a / E1b / E1c / E1d.
**Status:** Complete for its declared scope. NOT an atom-drafting lane.

## Scope (exactly what this lane does)

- Mint the initial Family ID set (F01..F12) with titles and intents.
- Assign lane ownership across E1a, E1b, E1c, E1d.
- Initialize `docs/wave_e/00_schema/id_allocations.log` with the Family reservations.

## Out of Scope (explicitly)

- No atom drafting. `proposals/atoms.yaml` is not produced here.
- No interaction edges, no exclusions, no sources, no scorecards.
- No canonical integration. Nothing written under `docs/wave_e/99_integration/`.
- No promotion of any Family to `ACTIVE`. Families are reserved; E1a will publish them as `DRAFT` in its own `proposals/families.yaml`.

## Artifacts Produced

- `docs/wave_e/E1_setup/README.md` (this file)
- `docs/wave_e/E1_setup/family_seed_registry.md` — the 12 minted Family IDs with titles and intents.
- `docs/wave_e/E1_setup/lane_assignments.md` — the E1a/E1b/E1c/E1d ownership matrix.
- `docs/wave_e/00_schema/id_allocations.log` — append-only reservation log, initialized.

## Operating Rules (binding on all E1 lanes)

1. **Only Chat 1 / integration lead may mint new Family IDs in this run.** All currently-valid Family IDs are those listed in `family_seed_registry.md` (F01..F12).
2. **Downstream lanes may reserve atom ID ranges only for already-minted Family IDs.** Reservations go in `docs/wave_e/00_schema/id_allocations.log`, one append per reservation, matching the format declared there.
3. **If a lane believes a new Family is required**, it MUST:
   - Log a `proposed_new_family:` block in its own lane `README.md` (title, intent, rationale, which existing Family it would otherwise stretch).
   - Stop short of minting the ID.
   - Surface a HITL request back to the integration lead.

## Ready-for-Integration Declaration

This E1-setup lane is **READY**. It produces no proposal YAML (by design) and no scorecards (no families "touched" in the proposal-artifact sense — Families are reserved, not published, in this lane).

## Remaining Ambiguities for E1a / E1b / E1c / E1d

None that block lane start. All downstream lanes now have:
- A sub-wave directory name (`E1a`, `E1b`, `E1c`, `E1d`).
- A concrete, minted Family ID set (F01..F12).
- A primary/secondary ownership split per lane.
- An append-only ID allocation log to reserve atom ranges against.

Two minor items downstream lanes should handle on first publish:
- Reserve their atom ID ranges per family in `id_allocations.log` before publishing `atoms.yaml`.
- Declare cross-lane authority bindings via `SRC-*` records produced in whichever lane owns the source; other lanes may cite by ID without re-declaring.
