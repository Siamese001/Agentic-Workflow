# Wave F3 — Final Weak-Atom Closure Matrix

Outcome of every weak atom targeted by F3.

| Atom | Family | v1.2 evidence | F3 source applied | Post-F3 evidence | Outcome |
|---|---|---|---|---|---|
| F04.02 | F04 | WEAK_EVIDENCE | SRC-ADR-007 (CTX-I1) | NORMATIVE | **CLOSED** |
| F04.03 | F04 | WEAK_EVIDENCE | SRC-ADR-007 (CTX-I2) | NORMATIVE | **CLOSED** |
| F04.04 | F04 | WEAK_EVIDENCE | SRC-ADR-007 (CTX-I3, primary) + SRC-ADR-005 (adjacent) | NORMATIVE | **CLOSED** |
| F05.04 | F05 | WEAK_EVIDENCE | SRC-ADR-008 (L3-I1 step 2) | NORMATIVE | **CLOSED** |
| F07.03 | F07 | WEAK_EVIDENCE | SRC-ADR-008 (L3-I3) + SRC-ADR-009 (ESC-I1) | NORMATIVE | **CLOSED** |

**5 of 5 targeted atoms closed. Zero PARTIAL. Zero DEFERRED.**

## Atom-by-atom citations

### F04.02 — Context attribution
- **Claim:** "Context delivered to reasoning, orchestration, and task execution MUST carry resolvable source attribution."
- **Normative source:** `docs/architecture/context_assembly_adr.md` §3.1 CTX-I1.
- **Key wording:** "Every `ContextItem` delivered to a reasoning, orchestration, or task-execution consumer MUST carry resolvable source attribution."
- **Implementation backing:** `ContextAssembler._convert_to_context_items()` + `_create_context()` compute `source_distribution`.

### F04.03 — No private unattributed substitute
- **Claim:** "Context consumers MUST NOT substitute private, unattributed context for the grounded context set."
- **Normative source:** `docs/architecture/context_assembly_adr.md` §3.2 CTX-I2.
- **Key wording:** "Context consumed by any reasoning, orchestration, or task-execution path MUST originate from a `RAGContext` produced by `ContextAssembler.assemble_context()`... Private, unattributed context substitutes are forbidden."

### F04.04 — Assembly idempotence
- **Claim:** "Context assembly MUST be idempotent for identical request inputs."
- **Primary normative source:** `docs/architecture/context_assembly_adr.md` §3.3 CTX-I3.
- **Key wording:** "Given identical inputs... `ContextAssembler.assemble_context()` MUST return a `RAGContext` whose item set (by `item_id`) and per-item attribution fields are identical across invocations."
- **Adjacent supplementary source:** SRC-ADR-005 (REPLAY_DETERMINISM_RULES) retained.

### F05.04 — L3 dispatch to L2
- **Claim:** "L3 MUST dispatch each plan step to L2 for task execution."
- **Normative source:** `docs/architecture/l3_orchestration_charter_adr.md` §3.2 L3-I1 step 2.
- **Key wording:** "L3 MUST dispatch each plan step to L2 for execution, passing the L0-authorized route binding, the L5-validated policy envelope, and the grounded context."
- **Implementation backing:** `agentic_core/L3_orchestration/` module root.

### F07.03 — Unrecoverable failure surfaces to L3
- **Claim:** "Unrecoverable failures MUST surface to L3 for re-planning."
- **Primary normative source:** `docs/architecture/unrecoverable_failure_escalation_adr.md` §3 ESC-I1.
- **Key wording:** "When an L2 task execution produces an unrecoverable failure, the failure MUST surface to L3 as an escalation event."
- **Receiving-half source:** `docs/architecture/l3_orchestration_charter_adr.md` §3.4 L3-I3.
- **Explicitly NOT used:** SRC-ADR-001 (ADR-F25-int); still carries `invalid_for_normative_use=True` by design.

## Projected family state after F3

| Family | v1.2 | Post-F3 projected | Bucket move |
|---|---|---|---|
| F01 | 1.000 GREEN | 1.000 GREEN | — |
| F02 | 1.000 GREEN | 1.000 GREEN | — |
| F03 | 1.000 GREEN | 1.000 GREEN | — |
| F04 | 0.250 RED | **1.000 GREEN** | **RED → GREEN (two-level flip)** |
| F05 | 0.750 YELLOW | **1.000 GREEN** | **YELLOW → GREEN** |
| F06 | 1.000 GREEN | 1.000 GREEN | — |
| F07 | 0.750 YELLOW | **1.000 GREEN** | **YELLOW → GREEN** |
| F08 | 1.000 GREEN | 1.000 GREEN | — |
| F09 | 1.000 GREEN | 1.000 GREEN | — |
| F10 | 1.000 GREEN | 1.000 GREEN | — |
| F11 | 1.000 GREEN | 1.000 GREEN | — |
| F12 | 1.000 GREEN | 1.000 GREEN | — |

**Projected bucket distribution:** 12 GREEN / 0 YELLOW / 0 RED.

**Projected global coverage:** 60 NORMATIVE / 60 ACTIVE = **1.000 GREEN**.

## Remaining open items

- **Follow-up D-v12-01** (8 weak edges): unchanged. F3 does not patch edges.
- **OOS-003 revisit:** flagged. ADR-CTX-001 §4 satisfies the revisit trigger; closure belongs to an exclusion-review pass.
- **B7 interaction candidates** (C1, C2, C3, C4, C6, C9): unchanged. F3 does not emit new atoms or edges.
- **Implementation-debt items:** validation test hooks listed inside each ADR's §5 are out of scope for F3 source authoring.
