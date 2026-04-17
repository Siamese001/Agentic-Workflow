# Wave E0 — ID Conventions (FROZEN)

**Version:** 1.0.0
**Status:** FROZEN — downstream Wave E lanes MUST NOT invent new ID formats.

## Principles

1. **Stable.** An ID, once assigned, is never reused or renumbered even if the entity is deprecated or excluded.
2. **Human-readable.** No UUIDs, no hashes. IDs are skimmable in plans, diffs, and chat.
3. **Self-locating.** The ID alone reveals entity type and, where relevant, parent family.
4. **Regex-checkable.** Every ID format has a single regex that CI can enforce.
5. **Monotonic within kind.** New IDs take the next unused integer in their namespace.

## Canonical Formats

| Entity | Format | Regex | Example |
|---|---|---|---|
| Family | `F<NN>` | `^F[0-9]{2}$` | `F12` |
| Requirement Atom | `F<NN>.<NN>` | `^F[0-9]{2}\.[0-9]{2}$` | `F12.03` |
| Interaction Edge | `INT-F<NN>.<NN>-F<NN>.<NN>-<NN>` | `^INT-F[0-9]{2}\.[0-9]{2}-F[0-9]{2}\.[0-9]{2}-[0-9]{2}$` | `INT-F12.03-F16.02-01` |
| Exclusion | `OOS-<NNN>` | `^OOS-[0-9]{3}$` | `OOS-014` |
| Source Authority | `SRC-<SUBTYPE>-<NNN>` | `^SRC-(INT\|EXT\|ADR\|RULE\|CODE\|DEC)-[0-9]{3}$` | `SRC-EXT-007` |
| Coverage Scorecard | `SCORE-F<NN>-<WAVE>` | `^SCORE-F[0-9]{2}-(E[0-9]+[a-z]?\|INTEGRATION)$` | `SCORE-F12-E1a` |

`<NN>` = zero-padded 2 digits. `<NNN>` = zero-padded 3 digits. `<WAVE>` = the wave label (`E1a`, `E2`, ..., or the literal `INTEGRATION`).

## Numbering Rules

- **Family numbers** are allocated by E0 or by the integration pass only. A sub-wave MAY propose a new family but MUST reserve the number via the integration pass before publishing atoms.
- **Atom numbers** start at `01` per family and are dense within a family at time of creation. Gaps created by later deprecation MUST NOT be refilled.
- **Interaction suffix** (the trailing `-NN`) disambiguates multiple edges between the same atom pair. Always start at `01` per ordered pair `(source, target)`.
- **SRC / OOS** use a single global namespace per subtype. `SRC-EXT-007` and `SRC-ADR-007` are different records.

## Parent/Child Consistency

- An atom's `family_id` MUST equal the `F<NN>` prefix of its own ID.
- An interaction edge's `source_atom_id` and `target_atom_id` MUST both refer to existing atom IDs.
- A scorecard's `family_id` MUST equal the `F<NN>` component of its own ID.

## Deprecation and Supersession

- Deprecated atoms keep their ID. Set `status: DEPRECATED` and, if replaced, set `superseded_by`.
- Superseding atoms take a new ID in the same family. Never recycle the old number.
- Deleted entities are forbidden. Use `status: DEPRECATED` or an `Exclusion` record.

## Cross-Wave Allocation Protocol

Downstream sub-waves (E1a, E1b, E2, ...) run in parallel. To avoid ID collisions:

1. **Reserve before publish.** A sub-wave reserves a contiguous atom ID range per family via a short entry in `docs/wave_e/00_schema/id_allocations.log` (created on first use). Format: `F12  atoms 03-08  reserved_by=E1a  at=<timestamp>`.
2. **Interaction IDs** require no reservation — uniqueness of the `(source, target, edge_kind)` triple plus the `-NN` suffix is sufficient.
3. **SRC and OOS IDs** are allocated monotonically; sub-waves MAY take the next free number at time of publish, but two parallel lanes SHOULD coordinate via the integration pass if they anticipate large SRC/OOS volumes.

## What NOT To Do

- Do **not** use ad-hoc prefixes (`REQ-`, `R-`, `FAM-`, `EDGE-`, etc.).
- Do **not** embed semantic tags in IDs (e.g. `F12-security.03`). Semantics belong in fields, not in the ID.
- Do **not** renumber on refactor. Once `F12.03` exists, it is `F12.03` forever.
- Do **not** create IDs without the matching entity record in the schema YAML.
