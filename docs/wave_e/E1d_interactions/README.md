# Wave E1d — Interaction Matrix and Failure Analysis

**Lane ID:** `E1d_interactions`
**Scope:** Model cross-atom interactions as first-class `InteractionEdge` records. Capture criticality and silent-failure risk in sidecar markdown. No new atom IDs, no source-registry work.

## Deliverables

- `proposals/edges.yaml` — **23** DRAFT InteractionEdge records.
- `proposals/families.yaml`, `atoms.yaml`, `exclusions.yaml`, `sources.yaml` — schema-valid empty lists.
- `scorecards/SCORE-F<NN>-E1d.yaml` — 12 scorecards capturing per-family edge participation.
- `interaction_candidates.md` — full candidate catalog with Pass A analysis; 9 candidates not emitted (require new atoms in Wave F).
- `interaction_failure_modes.md` — per-edge criticality / silent-failure / test-priority matrix.
- `priority_interactions_for_wave_f.md` — Wave F test-authoring handoff.

## 1. Edge Count Emitted

**23 edges**, all `status: DRAFT`.

| edge_kind | Count |
|---|---:|
| REQUIRES | 13 |
| REFINES | 4 |
| FORBIDS | 3 |
| DEPENDS_ON | 2 |
| CONDITIONAL_ON | 1 |
| IMPLIES | 1 |
| **TOTAL** | **23** |

| evidence_class | Count |
|---|---:|
| NORMATIVE | 15 |
| WEAK_EVIDENCE | 8 |
| UNRESOLVED, EXCLUDED, ADVISORY, INTERNAL_ONLY | 0 |

All 23 edges have valid `authority_binding` (≥1 SRC), all endpoints are stable E1b atom IDs, no duplicates, no BIDIRECTIONAL used (conservative).

## 2. Candidate Interactions Not Emitted

**9 candidates** (C1..C9 in `interaction_candidates.md`). None could be emitted because each requires at least one atom ID that does not exist in E1b's atom set. Examples:

- **C1** — F01.06 rejection reason code feeds L6 observability (needs consumer atom in F12).
- **C2** — F04 context bound by L5 policy on allowable sources (needs new F11 atom).
- **C3** — F07 retry budget set by L5 policy (needs new F11 atom).
- **C4** — F04 context attribution feeds audit trail (needs audit-trail atom).
- **C5** — F08 outcome observed for future learning (needs F12 consumer atom).
- **C6** — F03 route rationale feeds F04 context (needs new atom).
- **C7**, **C8**, **C9** — intentional non-edges (no real target, not a conflict, CO_REQUIRES redundant).

## 3. Top Silent-Failure Intersections

From `interaction_failure_modes.md`, ranked:

1. **INT-F06.05-F09.01-01** — L2 bypassing the Write Gate. CRIT + silent. Highest priority.
2. **INT-F12.02-F03.01-01** — L6 biasing L0 routing silently. Governing-semantic break.
3. **INT-F09.04-F11.04-01** — Gate accepting policy-less writes.
4. **INT-F06.02-F03.01-01** — L2 ignoring resolved L0 route.
5. **INT-F10.03-F09.01-01** — Direct L4 writes bypassing the gate.
6. **INT-F05.03-F03.02-01 / INT-F06.04-F03.02-01** — non-L0 choosing routes.
7. **INT-F07.04-F09.01-01** — heal/retry writing privately.
8. **INT-F12.03-F09.01-01** — L6 triggering writes.
9. **INT-F12.02-F11.01-01** — L5 policy re-evaluating from L6 mid-run.

**All 9 CRIT edges have silent-failure risk.** Wave F must gate these first.

## 4. Top High-Criticality Interactions Awaiting Stable Atom IDs

Every CRIT interaction that E1d could identify HAD stable endpoints and was emitted. The candidates awaiting new atom IDs (§2 above) are MEDIUM-priority at worst. Specifically:

- **C2** (context bound by policy) — would be a HIGH-criticality REQUIRES if emitted; currently sidecar-only.
- **C5** (exit outcome observed for learning) — would be a MEDIUM-criticality DEPENDS_ON.
- **C3** (retry budget from policy) — MEDIUM.

No CRIT interaction is stranded. The edge graph's most important nodes (F09 gate, F03 route, F11 policy, F02 reasoning, F12 no-influence) all received their critical edges.

## 5. Ready for Integration?

**YES — E1d declares ready for integration pass.**

All output is schema-valid. All endpoints resolve. Integration pass can now:

1. Merge E1a `DRAFT` families, E1b `DRAFT` atoms (+ E1c patches to F04.01, F04.04, F08.05), E1c sources/exclusions, and E1d edges.
2. Apply the E1c placeholder-to-real SRC mapping (evidence_binding_notes.md §1) to the 56 E1b atoms not re-published by E1c.
3. Promote `DRAFT` → `ACTIVE` only where authority bindings, edge endpoints, and exclusion references all resolve.

### Blockers Carried Forward (NOT blocking E1d itself)

| # | Blocker | Owner | Impact |
|---|---|---|---|
| B1 | Placeholder SRC IDs in 56 E1b atoms need mapping (evidence_binding_notes.md §1). | Integration pass | Well-documented; mechanical. |
| B2 | `SRC-ADR-EXIT` unsourced. F08 stays partial. | Future wave (exit-spine ADR) | Does not block edges; cited WEAK_EVIDENCE on relevant edges. |
| B3 | F07 family authority_class should be revised (DEC-E1c-F07-AUTH-CLASS). | E1a (advisory) | Warning at integration, not blocker. |
| B4 | 9 interaction candidates need new atoms in Wave F. | Wave F | Does not block current integration. |

## 6. Validation Self-Check

- [x] All 23 edges match `^INT-F[0-9]{2}\.[0-9]{2}-F[0-9]{2}\.[0-9]{2}-[0-9]{2}$`.
- [x] No edge has `source_atom_id == target_atom_id`.
- [x] No duplicate `(source, target, edge_kind)` triples.
- [x] The single `CONDITIONAL_ON` edge (INT-F07.03-F02.01-01) has a `condition`.
- [x] No edge uses `BIDIRECTIONAL` (all DIRECTED).
- [x] No edge uses `CONFLICTS_WITH` (which would require `UNRESOLVED` or `DEPRECATED` endpoint — none apply).
- [x] All edges have `authority_binding` length ≥ 1.
- [x] No edge status is `ACTIVE`.

## 7. Cross-Lane Notes

- **To integration pass:** 23 edges are ready. `interaction_failure_modes.md` rankings are advisory input for CI test ordering, not part of the canonical schema.
- **To Wave F:** Use `priority_interactions_for_wave_f.md` as the test-authoring handoff. 9 P1 + 8 P2 + 4 P3 + 0 P4 edges mapped to concrete test sketches.
- **To any future E-wave extending atoms:** The 9 candidates in `interaction_candidates.md` are already specified; when their endpoint atoms land, the edges can be emitted directly without re-analysis.
