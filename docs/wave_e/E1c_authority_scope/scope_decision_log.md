# Wave E1c — Scope Decision Log

Stable-ID record of every scope / layer / authority decision made by E1c.

---

## DEC-E1c-F04-LAYER
**Subject:** F04 Context Assembly owning_layer resolution (E1a HIGH flag).
**Candidates:** (a) confirm L1, (b) move to L3, (c) escalate E0 revision to add C0.
**Decision:** Confirm **L1**.
**Rationale:** Context grounding is the input surface of reasoning; placing it with its principal consumer is the cleanest ownership rule. L3 consumes but does not assemble. Option (c) rejected in OOS-003 (no concrete architectural driver).
**Impact:** F04 owning_layer=L1 across all atoms. F04.01 patched NORMATIVE/DRAFT; F04.04 patched WEAK_EVIDENCE/DRAFT.

## DEC-E1c-F01-LAYER
**Subject:** F01 Request Intake — confirm owning_layer L0.
**Decision:** Confirm **L0**. Intake rejection is a boundary action; F01 consumes L5 policy (F01.03 → SRC-RULE-001) but does not author.
**Impact:** No atom patches; E1b's L0 assignment stands.

## DEC-E1c-F08-LAYER
**Subject:** F08 Runtime Exit Spine — confirm owning_layer L5.
**Decision:** Confirm **L5**. Exit control is a policy judgment; L3 invokes but does not author.
**Impact:** No owning_layer patches. Separate F08.05 downgrade handled in DEC-E1c-EXIT-UNSOURCED.

## DEC-E1c-F09-LAYER
**Subject:** F09 Universal Write Gate — confirm owning_layer L4.
**Decision:** Confirm **L4**. Gate is the sole write path INTO L4, structurally co-located with the state it protects.
**Impact:** No owning_layer patches.

## DEC-E1c-AUTH-CLASS-CONSTITUTIONAL
**Subject:** Confirm CONSTITUTIONAL authority_class for F02, F03, F09, F10, F11, F12.
**Decision:** **Confirmed defendable** via SRC-RULE-001 (`.codex/rules/constitutional.md`, rank 1).
**Rationale:** Six governing semantics these families restate are captured in the project constitutional file.
**Impact:** E1a does not need to revise families.yaml for authority_class on these six.

## DEC-E1c-F07-AUTH-CLASS
**Subject:** F07 authority_class is OPERATIONAL (rank 5) but F07.04 cites SRC-RULE-001 (rank 1). Per schema rule "Family's authority_class MUST be the MINIMUM rank across atoms", F07 should be CONSTITUTIONAL or ARCHITECTURAL.
**Decision:** **Recommend E1a revise F07.authority_class to ARCHITECTURAL.**
**E1c action:** Noted only; families.yaml revision is E1a scope.
**Impact:** Integration pass WARNING until E1a revises. Does not block E1b/E1d.

## DEC-E1c-EXIT-UNSOURCED
**Subject:** `SRC-ADR-EXIT` placeholder has no real source at rank ≤ ARCHITECTURAL.
**Affected atoms:** F08.01, F08.02, F08.03, F08.04, F08.05, F09.05.
**Inspection:** Evaluation spine concept is not in SRC-INT-002 governing semantics nor SRC-RULE-001. Inferred from F08 intent but not canonicalized.
**Decision:**
- **F08.05** (sole binding was SRC-ADR-EXIT): downgrade NORMATIVE → WEAK_EVIDENCE, rebind SRC-INT-003. Patched.
- **F08.02** (has SRC-RULE-001 + SRC-ADR-L5 + SRC-ADR-EXIT): retains NORMATIVE (rank-1 binding survives placeholder mapping).
- **F08.01, F08.03, F08.04, F09.05** (all WEAK_EVIDENCE): classification stays; placeholder maps to SRC-INT-003.
**Impact:** Future wave MUST author an ADR or rule for the runtime exit spine for F08 to reach full NORMATIVE.

## DEC-E1c-PLACEHOLDER-MAPPING
**Subject:** E1b placeholder SRC IDs (SRC-ADR-L0..L6, SRC-ADR-WG) do not match `^SRC-(INT|EXT|ADR|RULE|CODE|DEC)-[0-9]{3}$`.
**Decision:** Map all layer-charter and Write-Gate placeholders to **SRC-INT-003** (governing-semantics frontmatter in `requirement_graph_schema.yaml`).
**Rationale:** Materializing fictitious per-layer ADRs is dishonest; the governing-semantics frontmatter is the single authoritative ARCHITECTURAL-rank surface that covers all six layer roles and the Write Gate monopoly. Full mapping in `evidence_binding_notes.md §1`.
**Impact:** Integration pass MUST apply the mapping to every E1b atom not re-published by E1c's `proposals/atoms.yaml` (56 atoms).

## DEC-E1c-OOS-002
**Subject:** Extend L6-no-current-run-influence to L2 heal/retry path.
**Decision:** Author **OOS-002** (OUT_OF_CHARTER).
**Rationale:** The "adaptive retry via observed anomaly rate" pattern is the L2-side twin of OOS-001 and deserves its own first-class exclusion record rather than being elided.

## DEC-E1c-OOS-003
**Subject:** Record the rejected `C0-as-separate-layer` alternative.
**Decision:** Author **OOS-003** (NOT_YET_DECIDED, with revisit_trigger).
**Rationale:** Preserves the decision surface so the C0 debate does not recur as prose in future waves.
