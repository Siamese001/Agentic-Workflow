# Wave E1c — Evidence Binding Notes

**Scope:** Document the placeholder-to-real SRC mapping, per-family evidence policy, and the rank floor applied to each NORMATIVE atom.

---

## 1. Placeholder-to-Real SRC Mapping (critical for integration pass)

E1b atoms cite mnemonic SRC IDs (e.g. `SRC-ADR-L0`, `SRC-ADR-WG`, `SRC-ADR-EXIT`) that do NOT match the schema regex `^SRC-(INT|EXT|ADR|RULE|CODE|DEC)-[0-9]{3}$`. E1c publishes real IDs and a canonical mapping. Integration pass MUST apply this mapping to every E1b atom that is NOT re-published by E1c's `proposals/atoms.yaml`.

| E1b placeholder ID | Real ID (E1c) | Notes |
|---|---|---|
| `SRC-RULE-001` | `SRC-RULE-001` | Identity — E1b used the canonical form |
| `SRC-RULE-002` | `SRC-RULE-002` | Identity |
| `SRC-INT-001` | `SRC-INT-001` | Identity |
| `SRC-INT-002` | `SRC-INT-002` | Identity |
| `SRC-ADR-L0` | `SRC-INT-003` | Layer charter → governing-semantics frontmatter |
| `SRC-ADR-L1` | `SRC-INT-003` | " |
| `SRC-ADR-L2` | `SRC-INT-003` | " |
| `SRC-ADR-L3` | `SRC-INT-003` | " |
| `SRC-ADR-L4` | `SRC-INT-003` | " |
| `SRC-ADR-L5` | `SRC-INT-003` | " |
| `SRC-ADR-L6` | `SRC-INT-003` | " |
| `SRC-ADR-WG` | `SRC-INT-003` | Write Gate monopoly is in governing semantics |
| `SRC-ADR-EXIT` | *(no real source)* | Downgrades atoms whose only binding is this placeholder |

**Why most `SRC-ADR-L*` map to the same `SRC-INT-003`**: per-layer ADRs do not yet exist in this project. The governing-semantics frontmatter in `requirement_graph_schema.yaml` is the single authoritative ARCHITECTURAL-rank surface that covers all six governing-semantic layers plus the Write Gate monopoly. Collapsing them to one source is accurate; separating them would require fabricating ADRs that do not exist.

**`SRC-ADR-EXIT` has no real source**: the evaluation spine concept is NOT stated in the governing semantics. F08.05 is downgraded in E1c's `proposals/atoms.yaml`. Atoms citing this placeholder that E1c did NOT re-publish (F08.01, F08.02, F08.03, F08.04, F09.05) retain the placeholder and integration pass must decide: (a) substitute `SRC-INT-003` as nearest source, keeping evidence_class as E1b published, or (b) downgrade. E1c recommends (a) for atoms that have other bindings and (b) for atoms with SRC-ADR-EXIT as sole binding.

## 2. Per-Family Evidence Policy (post-E1c)

| Family | Evidence policy | Defendable? |
|---|---|---|
| F01 | NORMATIVE via SRC-INT-001 + SRC-INT-003 (owning_layer L0 provisional). | Yes, provisional |
| F02 | NORMATIVE via SRC-RULE-001 + SRC-INT-001 + SRC-INT-003 (L1 governing semantic). | **Yes, strong** |
| F03 | NORMATIVE via SRC-RULE-001 + SRC-INT-001 + SRC-INT-003 (L0 governing semantic). | **Yes, strong** |
| F04 | NORMATIVE for F04.01 (post-patch); WEAK_EVIDENCE for F04.02/03/04. | Partial (layer resolved; idempotence weak) |
| F05 | NORMATIVE via SRC-INT-003 (L3 charter) + SRC-RULE-001 for no-plan/no-route. | Yes |
| F06 | NORMATIVE via SRC-RULE-001 + SRC-INT-003 + SRC-INT-001 (multi-source). | **Yes, strong** |
| F07 | Mostly WEAK_EVIDENCE; F07.04 NORMATIVE via SRC-RULE-001 (write gate monopoly). | Weak for operational claims; family class should rise to ARCHITECTURAL (see scope_decision_log.md) |
| F08 | 1 NORMATIVE (F08.02) + 4 WEAK_EVIDENCE after E1c downgrade of F08.05. | Blocked until a dedicated exit-spine source lands |
| F09 | NORMATIVE via SRC-RULE-001 + SRC-INT-001 + SRC-INT-003 (Write Gate governing semantic). | **Yes, strong** |
| F10 | NORMATIVE via SRC-RULE-001 + SRC-INT-001 + SRC-INT-003 (L4 governing semantic). | **Yes, strong** |
| F11 | NORMATIVE via SRC-RULE-001 + SRC-INT-001 + SRC-INT-003 (L5 governing semantic). | **Yes, strong** |
| F12 | NORMATIVE via SRC-RULE-001 + SRC-INT-001 + SRC-INT-003 (L6 governing semantic). | **Yes, strong** |

Eight of twelve families have **strong** defendable normative evidence policy. Four have caveats: F01 (layer provisional), F04 (idempotence weak), F07 (operational claims weak), F08 (exit-spine unsourced).

## 3. NORMATIVE Rank-Floor Check

Per `authority_classes.yaml`, NORMATIVE atoms require authority_binding with rank ≤ 4 (ARCHITECTURAL or better). SRC records materialized by E1c:

| SRC ID | Rank | Usable for NORMATIVE binding? |
|---|---:|---|
| SRC-RULE-001 | 1 (CONSTITUTIONAL) | Yes |
| SRC-RULE-002 | 2 (GOVERNANCE) | Yes |
| SRC-INT-001 | 2 (GOVERNANCE) | Yes |
| SRC-INT-002 | 2 (GOVERNANCE) | Yes |
| SRC-INT-003 | 4 (ARCHITECTURAL) | Yes |

All five E1c-materialized sources clear the NORMATIVE floor. No NORMATIVE atom is under-sourced on rank after placeholder mapping; the only rank-related issue is F08.05 where E1c could not find any source (real or placeholder) so the atom is downgraded.

## 4. ADVISORY vs. WEAK_EVIDENCE Distinction

E1c reviewed every WEAK_EVIDENCE atom to confirm it is not actually ADVISORY:

- **ADVISORY** = the claim itself is non-binding ("SHOULD", recommendation).
- **WEAK_EVIDENCE** = the claim is binding (MUST / MUST NOT) but support is thin.

Every E1b atom uses a MUST / MUST NOT verb in its claim; no atom is phrased as a recommendation. Therefore all 13 WEAK_EVIDENCE atoms are correctly classified as WEAK_EVIDENCE, not ADVISORY. No reclassification to ADVISORY is recommended.

## 5. OUT_OF_CHARTER vs. NOT_YET_DECIDED Distinction

E1c authored two new exclusions:
- **OOS-002** (OUT_OF_CHARTER) — extends OOS-001 (which was also OUT_OF_CHARTER). These claim the item will NEVER be in scope under current governing semantics.
- **OOS-003** (NOT_YET_DECIDED) — the `C0` layer alternative. Explicitly left open for a future HITL-backed E0 revision.

The distinction matters for revisit behavior: OUT_OF_CHARTER exclusions do NOT get `revisit_trigger` fields; NOT_YET_DECIDED exclusions SHOULD (OOS-003 has one).

## 6. Open Blockers

- **SRC-ADR-EXIT is unsourced.** Six F08/F09 atoms reference it. Only F08.05 was re-published by E1c (downgraded). The other five atoms retain the placeholder. Integration pass decides per atom.
- **Per-layer ADRs are missing.** The L0..L6 layer charters collapse to `SRC-INT-003` in E1c. A future wave SHOULD author per-layer ADRs so that each layer has an independent source (cleaner attribution, finer-grained authority).
- **F07 authority_class.** Family is OPERATIONAL (rank 5). F07.04 cites rank-1 CONSTITUTIONAL. Under the Family authority_class rule ("MUST be the MINIMUM rank across atoms"), F07's family authority_class should be CONSTITUTIONAL or at least ARCHITECTURAL. E1a must revise. See `scope_decision_log.md`.
