# Wave E1a — Family Spine Normalization

**Lane ID:** `E1a_family_spine`
**Scope:** DRAFT Family records for F01..F12 — titles, intents, owning_layer, authority_class. No atoms, no edges, no source registry work, no new Family IDs.
**Schema SSOT:** `docs/wave_e/00_schema/requirement_graph_schema.yaml`
**Families touched:** F01, F02, F03, F04, F05, F06, F07, F08, F09, F10, F11, F12 (twelve, all primary-owned).

## Deliverables

- `proposals/families.yaml` — twelve DRAFT Family records.
- `proposals/atoms.yaml`, `proposals/edges.yaml`, `proposals/exclusions.yaml`, `proposals/sources.yaml` — schema-valid empty lists (not E1a scope).
- `scorecards/SCORE-F<NN>-E1a.yaml` — one per family (12 files).
- `family_boundary_notes.md` — provisional owning_layer decisions for F01, F04, F08, F09.
- `family_aliases_and_dedup.md` — title normalization and duplicate-check.
- `family_risk_flags.md` — HIGH/MEDIUM/LOW flags with downstream-lane impact.

## Counts

| Metric | Value |
|---|---|
| Family records drafted | 12 |
| Families in `DRAFT` status | 12 |
| Families in `ACTIVE` status | 0 (by contract; only integration pass promotes) |
| Aliases merged | 12 (all seed titles normalized; see `family_aliases_and_dedup.md`) |
| Over-broad families flagged for E1b atom-split | 3 (F01, F08, F12) + 1 LOW (F07) |
| Families with ambiguous owning_layer | 4 (F01, F04, F08, F09) |
| HIGH risk flags | 1 (F04 schema-drift on `C0` layer name) |
| `proposed_new_family` entries | 0 |

## Authority Class Distribution

| authority_class | Families |
|---|---|
| CONSTITUTIONAL | F02, F03, F09, F10, F11, F12 |
| GOVERNANCE | F01, F08 |
| ARCHITECTURAL | F04, F05, F06 |
| OPERATIONAL | F07 |

All CONSTITUTIONAL assignments are provisional and require source citation by E1c.

## Owning-Layer Distribution

| owning_layer | Families |
|---|---|
| L0 | F01, F03 |
| L1 | F02, F04 |
| L2 | F06, F07 |
| L3 | F05 |
| L4 | F09, F10 |
| L5 | F08, F11 |
| L6 | F12 |

F01, F04, F08, F09 are provisional — see `family_boundary_notes.md`.

## Ready for Integration?

**NO — intentionally.** This lane produces only DRAFT Family records and is a prerequisite for E1b/E1c/E1d but is itself not integration-ready in isolation: an integrated canonical graph requires atoms, edges, sources, and scorecards that this lane does not produce.

This lane IS ready for **E1b / E1c / E1d to start** — all downstream lanes have the DRAFT Family set they need to proceed.

## Blockers

| # | Blocker | Owner | Impact |
|---|---|---|---|
| B1 | F04 owning_layer: `C0` is not in the schema enum; provisional `L1` assigned. | E1c | Does NOT block E1b start. E1b atoms that depend on the layer choice MUST be marked `UNRESOLVED` or `WEAK_EVIDENCE` until E1c confirms. |
| B2 | CONSTITUTIONAL authority_class for F02, F03, F09, F10, F11, F12 is provisional. | E1c | E1c MUST cite a rank-1 source (e.g. `.windsurf/rules/constitutional.md`) or downgrade. |
| B3 | Provisional owning_layer on F01 (L0 vs L5), F08 (L5 vs L3), F09 (L4 vs L5). | E1c | Does NOT block E1b start. |
| B4 | No atoms published by E1a (by scope). | E1b | Expected; E1b is the atom-drafting lane. |
| B5 | No edges published by E1a (by scope). | E1d | Expected. |
| B6 | No source records published by E1a (by scope). | E1c | Expected. E1b may cite `SRC-*` IDs by-reference that E1c will materialize. |

## proposed_new_family

None. E1a found no concern that required a new Family ID. The twelve minted IDs cover the spine.

## Cross-Lane Notes

- **To E1b:** Split F01, F08, F12 into separate atoms per their bundled sub-concerns. Single-claim rule will force this naturally.
- **To E1c:** The four provisional owning_layer choices and the six provisional CONSTITUTIONAL authority_class choices are your confirmation targets.
- **To E1d:** Family-level edges that are already obvious from intent text (e.g. F06 DEPENDS_ON F03, F09 DEPENDS_ON F11, F10 DEPENDS_ON F09) should be authored as `InteractionEdge` records targeting atom IDs once E1b publishes them.

## Operating Rules Inherited from E1-Setup

- Only Chat 1 / integration lead mints new Family IDs.
- E1a reserved no atom ID ranges (atom work is E1b scope); no appends to `id_allocations.log` from this lane.
- All Family records remain `DRAFT` until the integration pass.
