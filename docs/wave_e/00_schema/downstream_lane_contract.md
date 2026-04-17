# Wave E0 — Downstream Lane Contract (FROZEN)

**Version:** 1.0.0
**Status:** FROZEN — this document is the operating agreement for every parallel sub-wave in Wave E.

## 1. Governing Semantics (non-negotiable)

- **L1** decomposes and plans.
- **L0** is route authority.
- **L5** is cross-cutting policy authority.
- **L4** is authoritative durable state.
- **Universal Write Gate** is the sole durable write path.
- **L6** supports future-run learning only, never current-run mutation.

Any atom, edge, or exclusion that contradicts these semantics is invalid and MUST be rejected by the integration pass.

## 2. Lane Separation

Wave E runs as a set of parallel sub-waves (E1a, E1b, E1c, ... E<N>) that each produce **proposal artifacts**. Exactly one later **integration pass** publishes the canonical merged requirement graph. Sub-waves MUST NOT publish to the canonical location.

| Artifact location | Who writes | When |
|---|---|---|
| `docs/wave_e/00_schema/` | E0 only (this wave) | Frozen. No edits without a new E0 revision. |
| `docs/wave_e/<sub_wave>/proposals/` | Each sub-wave | During sub-wave execution. |
| `docs/wave_e/<sub_wave>/scorecards/` | Each sub-wave | End of sub-wave. |
| `docs/wave_e/99_integration/` | Integration pass only | After all sub-waves complete. |

Sub-waves MUST NOT write outside their own `docs/wave_e/<sub_wave>/` tree.

## 3. What Sub-Waves MUST Reuse Verbatim

Sub-waves MUST NOT invent new:

- **Field names.** Only the fields listed in `requirement_graph_schema.yaml`.
- **ID formats.** Only the formats in `id_conventions.md`.
- **Status enum values.** Only values in `coverage_status_enums.yaml`.
- **Evidence class values.** Same file.
- **Authority classes.** Only those in `authority_classes.yaml`.
- **Edge kinds.** Only those in the `InteractionEdge.edge_kind` enum.
- **Exclusion reason enum.** Only those in `Exclusion.reason`.

If a sub-wave believes a new field, enum value, or ID format is genuinely required, it MUST stop, open a HITL request, and propose an E0 revision. It MUST NOT ship proposals that depend on a non-existent schema extension.

## 4. Proposal Artifact Shape (per sub-wave)

Each sub-wave produces, under `docs/wave_e/<sub_wave>/proposals/`:

- `families.yaml` — zero or more new/updated Family records.
- `atoms.yaml` — zero or more new/updated RequirementAtom records.
- `edges.yaml` — zero or more new/updated InteractionEdge records.
- `exclusions.yaml` — zero or more new Exclusion records.
- `sources.yaml` — zero or more new SourceAuthorityRecord entries.
- `scorecards/SCORE-F<NN>-<WAVE>.yaml` — one scorecard per family touched.
- `README.md` — scope statement, lane ID, families touched, open blockers.

All records MUST validate against the E0 schema. Draft status is expected; `ACTIVE` is not assigned until the integration pass.

## 5. ID Allocation Between Parallel Lanes

- **Family numbers** are reserved via `docs/wave_e/00_schema/id_allocations.log` (append-only; create on first use). A lane MUST reserve family numbers before publishing atoms that reference them.
- **Atom numbers** are reserved by contiguous range per family (see `id_conventions.md` §Cross-Wave Allocation Protocol).
- **Interaction, OOS, and SRC IDs** are allocated monotonically at publish time; collisions are resolved by the integration pass (later lane renumbers).
- Lanes MUST NOT reuse family numbers or atom numbers already present in any prior wave's published artifacts.

## 6. Evidence Discipline

- Every atom with `evidence_class: NORMATIVE` MUST cite at least one `SourceAuthorityRecord` of rank ≤ ARCHITECTURAL.
- Unsupported claims MUST be marked `UNRESOLVED` or `WEAK_EVIDENCE`, not silently downgraded.
- Excluded claims MUST have both `evidence_class: EXCLUDED` and an `OOS-*` exclusion record. Prose footnotes are forbidden as the sole record of an exclusion.
- Interaction edges are first-class entities. "See comment in family X" is not an edge.

## 7. Scope Fences (what a sub-wave MUST NOT do)

A sub-wave MUST NOT:

- Publish to `docs/wave_e/99_integration/`.
- Edit any file under `docs/wave_e/00_schema/`.
- Mark any atom, edge, or family `ACTIVE`. Only the integration pass promotes `DRAFT` → `ACTIVE`.
- Delete or renumber IDs allocated by another lane.
- Invent new enum values, field names, or ID prefixes.
- Introduce L6 observations as authority for current-run mutation (explicitly forbidden by governing semantics).
- Treat `ADVISORY` authority as sufficient support for a `NORMATIVE` atom.

## 8. Integration Pass Responsibilities

The integration pass (a single later wave) MUST:

1. Collect all `docs/wave_e/<sub_wave>/proposals/` trees.
2. Validate each record against the E0 schema (ERRORs block).
3. Resolve ID collisions per the allocation protocol.
4. Merge records into `docs/wave_e/99_integration/canonical/`.
5. Promote `DRAFT` to `ACTIVE` only when authority bindings, edge endpoints, and exclusion references all resolve.
6. Produce `SCORE-F<NN>-INTEGRATION` scorecards and a top-level coverage report.
7. Record all merge decisions in the HITL Decision Ledger.

## 9. Stop Conditions for a Sub-Wave

A sub-wave is complete when:

- All proposal files validate against the E0 schema with zero ERRORs.
- Every NORMATIVE atom has at least one valid authority binding.
- Every edge has both endpoints defined in either this sub-wave's proposals or an already-merged prior wave.
- Every exclusion referenced by an atom exists in `exclusions.yaml`.
- A scorecard exists for every family touched, with blockers explicitly listed.
- The sub-wave README declares "ready for integration" or lists the specific blockers preventing readiness.

## 10. Quick Checklist for a Sub-Wave Lead

- [ ] Read all five files under `docs/wave_e/00_schema/`.
- [ ] Reserve family numbers and atom ID ranges before writing proposals.
- [ ] Use only the frozen enums, field names, and ID formats.
- [ ] Cite authority for every NORMATIVE claim (rank ≤ 4).
- [ ] Make every edge and every exclusion a first-class record.
- [ ] One claim per atom. If in doubt, split.
- [ ] Produce one scorecard per touched family.
- [ ] Do not write outside `docs/wave_e/<sub_wave>/`.
- [ ] Do not mark anything `ACTIVE`.
- [ ] Raise a HITL request rather than bending the schema.
