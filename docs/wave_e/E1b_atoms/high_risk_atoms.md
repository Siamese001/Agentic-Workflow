# Wave E1b — High-Risk Atoms

**Scope:** Flag atoms whose classification, layer, or phrasing is most likely to change during E1c authority-scope review or integration pass. Downstream lanes should treat these as provisional.

Risk levels:
- **HIGH** — needs E1c decision before integration.
- **MEDIUM** — E1c source materialization may reclassify.
- **LOW** — phrasing or scope may tighten but classification stable.

---

## HIGH — F04 atoms (4 atoms, 2 UNRESOLVED)

- **F04.01, F04.04** are `UNRESOLVED` / `UNRESOLVED` because F04's `owning_layer` is still provisional (`L1`) and the seed used a layer name (`C0`) that is not in the schema enum.
- **F04.02, F04.03** are `WEAK_EVIDENCE` with provisional `owning_layer: L1`.
- **What E1c must decide:** confirm `L1`, move F04 to a different layer, or escalate a schema revision to add `C0`. Whichever resolution E1c chooses, the four atoms' `owning_layer` MUST be updated in lockstep.

## HIGH — F01, F08, F09 layer provisionality

Carried forward from E1a:
- F01 atoms all declare `owning_layer: L0`; would flip to `L5` if E1c reclassifies F01.
- F08 atoms all declare `owning_layer: L5`; would flip to `L3` if E1c reclassifies F08.
- F09 atoms all declare `owning_layer: L4`; would flip to `L5` if E1c reclassifies F09.

None of these block downstream work; E1d can attach edges to the atom IDs regardless of the layer field, because edges are atom-to-atom, not layer-to-layer.

## MEDIUM — Atoms whose NORMATIVE classification depends on SRC materialization

All NORMATIVE atoms cite at least one SRC-* placeholder. If E1c fails to materialize a cited SRC at rank ≤ ARCHITECTURAL (the floor for NORMATIVE per `authority_classes.yaml`), the atom MUST be downgraded to `WEAK_EVIDENCE` or `UNRESOLVED`. Atoms most exposed to downgrade:

- F03.03 "reject unbound route" — cites only `SRC-ADR-L0` (placeholder ADR). If E1c cannot locate an ADR of rank ≤ ARCHITECTURAL for L0 route charter, this atom downgrades.
- F08.02, F08.05 — cite `SRC-ADR-EXIT` (placeholder). Same risk.
- F09.04 — cites `SRC-ADR-WG` + `SRC-ADR-L5` (both placeholders).
- F10.02, F10.04 — cite only `SRC-ADR-L4` (placeholder).

## MEDIUM — Atoms whose phrasing may tighten during E1d edge work

E1d may discover that an atom bundles two interaction-kind implications that would be better split. Candidates:

- F09.04 and F09.05 both say the gate MUST reject on missing signals (from F11 and F08 respectively). These are sound as two atoms, but E1d may want to encode the `(F09 REQUIRES F11)` and `(F09 REQUIRES F08)` edges and could argue for a single "gate MUST reject on missing admission signal" atom with edges carrying the specifics. Keep as-is unless E1d explicitly requests consolidation.
- F11.02..F11.05 are five "L5 binds X" claims. E1d will author five `L5 policies REQUIRES X` or `X REQUIRES L5 policy` edges. If E1d finds the atoms redundant given the edges, consolidation may be proposed at integration.

## MEDIUM — F07 atoms are thin

Three of four F07 atoms (F07.01, F07.02, F07.03) are `WEAK_EVIDENCE`. The bounded-retry claim (F07.02) is the weakest — "bounded attempt count or duration" is a reasonable operational invariant but there is no cited rule or ADR for it in this run. E1c may:
  (a) locate a runbook / operational source (moves to `NORMATIVE` at OPERATIONAL rank, but NORMATIVE requires rank ≤ ARCHITECTURAL, so a downgrade of F07's authority_class is implied), or
  (b) leave as `WEAK_EVIDENCE` until a rule is authored, or
  (c) mark `UNRESOLVED` until heal/retry policy is decided.

## LOW — WEAK_EVIDENCE atoms with clear upgrade path

- F01.06 (structured rejection reason code) — straightforward to back with an ADR.
- F03.04 (one-route-per-step) — determinism is widely implicit; easy to cite.
- F04.02, F04.03 (context attribution, no-private-substitute) — depends on F04 layer resolution first.
- F05.04 (L3 dispatches to L2) — follows structurally from F05/F06 separation.
- F12.05 (future-run consumption by L1 only) — easy to cite once L6 ADR lands.

---

## EXCLUDED Atom Note

**F12.06** references `OOS-001` (authored by E1b in `proposals/exclusions.yaml`). Integration pass must:
1. Resolve `OOS-001` -> `exclusions.yaml` entry.
2. Confirm `F12.06.rationale` references the OOS ID (it does: "Excluded per OOS-001").
3. De-duplicate if E1c independently authors an equivalent exclusion.

---

## Summary

| Level | Count |
|---|---|
| HIGH  | 2 UNRESOLVED atoms (F04.01, F04.04) + carryover layer provisionals on F01/F08/F09 |
| MEDIUM | ~12 NORMATIVE atoms whose binding depends on E1c SRC materialization + 3 F07 WEAK_EVIDENCE atoms |
| LOW   | ~6 WEAK_EVIDENCE atoms with clear upgrade path post-E1c |
