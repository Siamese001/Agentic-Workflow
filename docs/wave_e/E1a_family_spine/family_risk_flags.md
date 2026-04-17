# Wave E1a — Family Risk Flags

**Scope:** Explicit, per-family risk flags that downstream lanes MUST read before authoring atoms, edges, or authority bindings.

Risk levels:
- **HIGH** — blocks downstream work on that family until resolved by E1c or HITL.
- **MEDIUM** — does not block start; downstream lanes proceed but must cite the flag.
- **LOW** — advisory; downstream lanes should be aware.

---

## Over-Broad Families (atom-split expected by E1b)

### F01 — Request Intake and Envelope Check — MEDIUM
Two internal concerns bundled. E1b MUST split into separate atoms:
- Atom(s) covering intake admission (shape, auth).
- Atom(s) covering envelope-level policy preconditions.
The single-claim-per-atom rule will naturally produce the split.

### F08 — Runtime Exit Control and Evaluation Spine — MEDIUM
Two internal concerns bundled. E1b MUST split into separate atoms:
- Atom(s) covering termination flow through the single spine.
- Atom(s) covering result-acceptance evaluation.
- Atom(s) covering the "no ad-hoc exit paths" prohibition.

### F12 — L6 Observability and Future-Run Learning — MEDIUM
Two internal concerns bundled. E1b MUST split into separate atoms:
- Atom(s) covering observation of the current run.
- Atom(s) covering the MUST-NOT-influence-current-run constraint.
- Atom(s) covering the future-run feed-forward contract.
The EXCLUDED atom for "no current-run influence" belongs here.

### F07 — L2 Heal, Retry, and Recovery — LOW
Three sub-concerns ("heal", "retry", "recovery") could each justify separate atoms. Not flagged HIGH because E1b's single-claim rule will produce the split automatically.

---

## Ambiguous Boundaries (E1c must confirm)

### F04 — Context Assembly and Grounding — HIGH (schema-drift)
**Risk:** The seed registry named this family "C0 Context Assembly + Grounding", but `C0` is NOT a valid value in the `owning_layer` enum (`L0..L6` only).
**Mitigation applied in E1a:** Normalized the title (dropped the `C0` prefix) and assigned provisional `owning_layer: L1`.
**Required downstream action:** E1c MUST either:
  (a) confirm `L1` is correct, or
  (b) propose a schema revision to add a `C0` layer (requires E0 revision via HITL), or
  (c) re-home F04 to a different existing layer.
**Blocker for E1b:** No. E1b may proceed assuming `L1`, marking any atom whose claim depends on the layer choice as `UNRESOLVED` or `WEAK_EVIDENCE` until E1c confirms.

### F01 owning_layer (L0 vs L5) — MEDIUM
Provisional `L0`. See family_boundary_notes.md.

### F08 owning_layer (L5 vs L3) — MEDIUM
Provisional `L5`. See family_boundary_notes.md.

### F09 owning_layer (L4 vs L5) — MEDIUM
Provisional `L4`. See family_boundary_notes.md.

---

## Authority-Class Provisional Choices (E1c must confirm)

### CONSTITUTIONAL-grade families — confirmation needed
The following six families were assigned `authority_class: CONSTITUTIONAL` because their intents restate governing semantics declared as "non-negotiable" in the project constitution and in the E0 schema's frontmatter:
- F02 (L1 decomposes and plans)
- F03 (L0 is route authority)
- F09 (Universal Write Gate is sole durable write path)
- F10 (L4 is authoritative durable state)
- F11 (L5 is cross-cutting policy authority)
- F12 (L6 supports future-run learning only)
**Risk:** CONSTITUTIONAL is the strongest class. If E1c determines a family's normative weight is better expressed as GOVERNANCE or ARCHITECTURAL, the authority_class MUST be lowered accordingly in the canonical record.
**Recommended E1c action:** For each of the six, locate the specific constitutional-tier source (`.windsurf/rules/constitutional.md`, AGENTS.md always-on) and record it as a `SRC-RULE-*` or `SRC-INT-*`. If no constitutional-tier source can be cited, downgrade to GOVERNANCE and log the downgrade.

### ARCHITECTURAL-grade families
F04, F05, F06 assigned `ARCHITECTURAL`. Defensible as layer-charter claims. E1c confirms on source availability.

### GOVERNANCE-grade families
F01, F08 assigned `GOVERNANCE`. Defensible as rule- or ADR-backed claims. E1c confirms on source availability.

### OPERATIONAL-grade families
F07 assigned `OPERATIONAL`. Defensible as runtime-behavior claim. E1c may upgrade to ARCHITECTURAL if heal/retry/recovery is charter-level.

---

## Blocker Summary

| Family | Flag | Level | Blocks E1b? | Blocks E1c? | Blocks E1d? |
|---|---|---|---|---|---|
| F01 | atom-split expected | MEDIUM | no | no | no |
| F01 | owning_layer L0 vs L5 | MEDIUM | no | confirm | no |
| F04 | `C0` not in layer enum | HIGH | no (provisional L1) | **confirm required** | no |
| F07 | sub-concern split | LOW | no | no | no |
| F08 | atom-split expected | MEDIUM | no | no | no |
| F08 | owning_layer L5 vs L3 | MEDIUM | no | confirm | no |
| F09 | owning_layer L4 vs L5 | MEDIUM | no | confirm | no |
| F12 | atom-split expected | MEDIUM | no | no | no |
| F02, F03, F09, F10, F11, F12 | CONSTITUTIONAL provisional | MEDIUM | no | source cite required | no |

**No HIGH flag blocks E1b, E1c, or E1d from starting.** The only HIGH flag (F04 layer-naming) has a provisional resolution (`L1`) that E1b can proceed against; E1c owns the confirmation.
