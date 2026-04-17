# Wave F4 — Exclusion Review Log

Scope: review OOS-003 in light of Wave F3's new sources. OOS-001 and OOS-002 are not re-evaluated — neither's revisit trigger is implicated by v1.3 deltas.

## OOS-003 review

### Original record (v1.2 / v1.3 canonical)

```yaml
id: OOS-003
title: "Adding a C0 layer to the owning_layer enum"
scope_statement: >
  F04 is re-homed to L1 per DEC-E1c-F04-LAYER. A C0 layer may be
  revisited only via an explicit E0 schema revision with HITL approval.
reason: NOT_YET_DECIDED
decided_at_wave: E1c
decided_by: "E1c_authority_scope lane"
revisit_trigger: >
  Future wave surfaces a concrete operational constraint that L1 cannot
  satisfy for context grounding.
related_atoms: [F04.01, F04.02, F04.03, F04.04]
related_families: [F04]
```

### Relevant v1.3 change

SRC-ADR-007 (`docs/architecture/context_assembly_adr.md`, ADR-CTX-001) declares three context-grounding invariants (CTX-I1 attribution, CTX-I2 single-grounded-path, CTX-I3 idempotence) and implements them inside the L1-owned `agentic_core/L1_cognition/reasoning/context_assembler.py`. The v1.3 canonical state has F04.01–F04.04 all ACTIVE NORMATIVE under `owning_layer: L1`.

### Revisit trigger test

The original revisit trigger requires a "concrete operational constraint that L1 cannot satisfy for context grounding". SRC-ADR-007 presents the opposite evidence: a concrete invariant set that L1 CAN and MUST satisfy, with real implementation grounding. No operational constraint that L1 fails on has been surfaced.

Therefore the *trigger condition* itself has been resolved in the negative direction: there is no pressure to open a C0 layer. The hold was predicated on "we might later need C0 if L1 can't"; v1.3 establishes that L1 does.

### Disposition options considered

| Option | Description | Evaluation |
|---|---|---|
| **A — Retain unchanged** | Leave OOS-003 reason=NOT_YET_DECIDED. | Creates a permanent "undecided" exclusion even though the decision is now effectively made. Dishonest signal. |
| **B — Retire (delete from exclusions.yaml)** | Remove OOS-003 entirely. | Loses history. Future reviewers would lack the paper trail for why C0 was considered and dismissed. |
| **C — Revise to SUPERSEDED** | Change reason to SUPERSEDED, cite SRC-ADR-007 in notes, keep scope_statement and revisit_trigger for traceability. | Preserves history; records the supersession source; matches the schema enum (SUPERSEDED is exactly this case). |
| **D — Revise to OUT_OF_CHARTER** | Mark as outside charter after-the-fact. | Mis-fits: OOS-003 was never out-of-charter — it was a real open question that has since been resolved. |

### F4 bar

> *Retire OOS-003 only if the new canonical source set truly supersedes its rationale.*

SRC-ADR-007 directly supersedes the *rationale to hold OOS-003 open*. The hold existed to preserve the option of adding a C0 layer. The new ADR demonstrates L1 owns context grounding normatively — no C0 layer is needed. This meets the "truly supersedes" bar.

### Disposition

**Option C: Revise to SUPERSEDED.** See `proposals/exclusions.yaml`.

- `reason`: NOT_YET_DECIDED → **SUPERSEDED**
- `decided_at_wave`: E1c → **F4**
- `decided_by`: "E1c_authority_scope lane" → **"F4_edge_exclusion_cleanup lane"**
- `revisit_trigger`: rewritten to document that the original trigger was satisfied by SRC-ADR-007 and no C0 layer is warranted.
- `scope_statement`, `related_atoms`, `related_families`: unchanged (historical context preserved).

## OOS-001 review

Revisit trigger: none declared. OOS-001 remains unchanged.

## OOS-002 review

Revisit trigger: none declared. OOS-002 remains unchanged.

## Cross-check: no ACTIVE atom cites any OOS as authority

Per schema rule *"An Exclusion MUST NOT be referenced by any ACTIVE atom as authority"*:

- No v1.3 ACTIVE atom has any OOS-NNN in `authority_binding` ✅
- F12.06 (EXCLUDED) references OOS-001 via its rationale — this is a rationale reference, not an authority binding ✅

The OOS-003 revision is therefore safe: no ACTIVE atom depends on OOS-003 in any way.
