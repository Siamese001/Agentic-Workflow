# Wave F3 — Final Source Closure (Proposal Lane)

This directory contains the F3 source-authoring proposal. Canonical v1.2 YAML was NOT modified. An integration pass (v1.3) applies these proposals.

## Mandate

Close the remaining content-level blockers on canonical v1.2:

- **B3** — Context-assembly ADR (F04.02, F04.03, F04.04)
- **F07.03** — Normative escalation-target authority
- **B6** — L3 orchestration charter (F05.04)

## Outcome

All three blockers are resolved. 5 of 5 targeted weak atoms close.

### Authored source artifacts (real repo paths, resolvable)

| New SRC ID | ADR | Repo path | Authority class |
|---|---|---|---|
| SRC-ADR-007 | ADR-CTX-001 Context Assembly Grounding Invariants | `docs/architecture/context_assembly_adr.md` | ARCHITECTURAL |
| SRC-ADR-008 | ADR-L3-001 L3 Orchestration Charter | `docs/architecture/l3_orchestration_charter_adr.md` | ARCHITECTURAL |
| SRC-ADR-009 | ADR-ESC-001 Unrecoverable Failure Escalation to L3 | `docs/architecture/unrecoverable_failure_escalation_adr.md` | ARCHITECTURAL |

All three ADRs are `invalid_for_normative_use=False`. All three are grounded in existing implementation:

- ADR-CTX-001 on `agentic_core/L1_cognition/reasoning/context_assembler.py`.
- ADR-L3-001 on `agentic_core/L3_orchestration/` + `orchestrator_state_retry.py`.
- ADR-ESC-001 on the `HEALER_RETRY_HARDENING_SPEC.md` retry bounds + ADR-L3-001 receiving contract.

ADR-F25-int (SRC-ADR-001, healing_dispatch_routing_adr.md) is NOT modified. It remains ADVISORY and `invalid_for_normative_use=True` by design.

### Atom closures

| Atom | Family | v1.2 | Post-F3 | Outcome |
|---|---|---|---|---|
| F04.02 | F04 | WEAK | NORMATIVE | CLOSED |
| F04.03 | F04 | WEAK | NORMATIVE | CLOSED |
| F04.04 | F04 | WEAK | NORMATIVE | CLOSED |
| F05.04 | F05 | WEAK | NORMATIVE | CLOSED |
| F07.03 | F07 | WEAK | NORMATIVE | CLOSED |

### Family bucket movement (projected post-integration)

| Family | v1.2 | Post-F3 |
|---|---|---|
| F04 | 0.250 RED | **1.000 GREEN** (two-level flip) |
| F05 | 0.750 YELLOW | **1.000 GREEN** |
| F07 | 0.750 YELLOW | **1.000 GREEN** |
| All other families | GREEN | GREEN |

**Projected global coverage:** 60 NORMATIVE / 60 ACTIVE = **1.000 GREEN**.
**Projected bucket distribution:** 12 GREEN / 0 YELLOW / 0 RED.

## Readiness statement

**Ready for integration.** An integration pass to produce canonical v1.3 can apply `proposals/sources.yaml` (3 adds) and `proposals/atoms.yaml` (5 patches). No family, edge, or exclusion changes are proposed.

### Intentional non-actions (preserved for a later wave)

- **OOS-003:** revisit trigger now satisfied by SRC-ADR-007 but exclusion stays ACTIVE pending an exclusion-review pass. Flagged in `final_weak_atom_closure_matrix.md`.
- **8 weak edges** (follow-up D-v12-01): unchanged. Potential upgrade candidates in a later targeted edge-evidence pass.
- **B7 interaction candidates** (C1, C2, C3, C4, C6, C9): unchanged. None cleanly supportable as a free byproduct of F3's three sources.
- **Validation test hooks** listed in each ADR's §5: implementation-debt items, out of scope for source authoring.

## Directory contents

```
docs/wave_e/F3_final_source_closure/
├── README.md                              (this file)
├── source_authoring_decisions.md          (6 non-trivial decisions)
├── final_weak_atom_closure_matrix.md      (per-atom closure citations)
├── escalation_authority_decision.md       (F07.03 option analysis)
├── l3_charter_alignment_notes.md          (ADR-L3-001 cross-layer alignment)
├── proposals/
│   ├── families.yaml                      (empty - no family changes)
│   ├── atoms.yaml                         (5 atom evidence-class patches)
│   ├── edges.yaml                         (empty with documented rationale)
│   ├── exclusions.yaml                    (empty with documented rationale)
│   └── sources.yaml                       (3 new SourceAuthorityRecords)
└── scorecards/
    ├── SCORE-F04-F3.yaml
    ├── SCORE-F05-F3.yaml
    └── SCORE-F07-F3.yaml
```

## Scope compliance checklist

- ✅ No new family IDs minted.
- ✅ No family redesign.
- ✅ No edits to schema files (`docs/wave_e/00_schema/`).
- ✅ No edits to canonical v1.2 YAML.
- ✅ No edits to v1.1 or proposal-wave-F2 files.
- ✅ No fabricated sources or locators. All three ADRs live at real repo paths with implementation grounding.
- ✅ No atom status changes (all remain ACTIVE; only evidence_class and authority_binding patched).
- ✅ No edges patched.
- ✅ Claim meaning preserved verbatim for all 5 patched atoms.
- ✅ No new atoms added.
- ✅ All authored ADRs directly support the atoms they are bound to.
