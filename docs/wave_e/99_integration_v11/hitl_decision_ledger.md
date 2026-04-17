# F1 Integration — HITL Decision Ledger (v1.1)

New v1.1-specific decisions only. v1 ledger entries (HITL-INT-001..010) remain applied.

---

## HITL-INT-V11-001 — Accept F12.05 patch (WEAK → NORMATIVE)

**Subject:** F1 proposes upgrading F12.05 with richer authority_binding.
**Options:**
- (a) Reject; keep F12.05 WEAK_EVIDENCE as in v1.
- (b) Accept, with v1 binding union-merged into F1's binding set.
- (c) **Accept F1's binding set wholesale (last-writer-wins per v1 HITL-INT-001).** ← Chosen.
**Decision:** (c). Confidence: 0.93.
**Rationale:** F1's binding list (`SRC-RULE-001, SRC-INT-001, SRC-INT-003, SRC-INT-004`) includes the v1 binding (`SRC-INT-003`) and adds strictly more support. The NORMATIVE classification is defensible because SRC-RULE-001 §17 directly mandates the memory lifecycle that F12.05 invokes. No information loss vs. option (b).

## HITL-INT-V11-002 — Admit F12.07 and F12.08 as ACTIVE NORMATIVE

**Subject:** F1 proposes two new atoms under F12.
**Options:**
- (a) Admit both as DRAFT only (do not promote to ACTIVE in this integration pass).
- (b) **Admit both as ACTIVE NORMATIVE.** ← Chosen.
- (c) Admit one, defer the other.
**Decision:** (b). Confidence: 0.90.
**Rationale:** Both atoms meet the v1 ACTIVE promotion criteria: valid binding (≥1 rank≤ARCHITECTURAL source), resolved owning_layer, clear claim, no blocking deps, no duplicate `(family_id, claim)` collision. F12.07 cleanly refines F12.05's concrete mechanism. F12.08 closes interaction candidate C5 with memory-lifecycle grounding. Both are NORMATIVE because their claims are directly supported by SRC-RULE-001 §17 memory lifecycle text.

## HITL-INT-V11-003 — Accept SRC-INT-004 as a new source

**Subject:** F1 proposes a section-anchor source into AGENTS.md.
**Options:**
- (a) Reject (section anchors don't need dedicated SRC records).
- (b) **Accept.** ← Chosen.
**Decision:** (b). Confidence: 0.82.
**Rationale:** The schema does not forbid multiple SRC records pointing at different sections of the same document. A precise anchor improves auditability: consumers of F12.05/07/08 can trace directly to the Memory Lifecycle section rather than the whole AGENTS.md file. Adds minimal maintenance surface (one record). Follows the pattern already established by SRC-INT-002 (anchored at a section of the downstream lane contract).

## HITL-INT-V11-004 — Do NOT fabricate F04/F07/F08 sources

**Subject:** Three RED families remain RED after F1. Temptation to accept F1's "honest deferral" as-is vs. author speculative sources in integration.
**Options:**
- (a) Author speculative sources or promote existing WEAK atoms to NORMATIVE at integration time.
- (b) **Preserve F1's deferrals exactly; keep F04/F07/F08 RED; log blockers.** ← Chosen.
**Decision:** (b). Confidence: 1.00.
**Rationale:** Contract rule: "Do not fabricate sources. If a placeholder maps to no resolvable source, keep the affected atom DRAFT or WEAK_EVIDENCE and log the blocker." Integration pass authority does not extend to source fabrication. The honest outcome is that three families stay RED and carry forward as blockers B1–B3.

## HITL-INT-V11-005 — Coverage score not rounded up (unchanged from v1 HITL-INT-009)

**Subject:** v1.1 global score is 0.77586... Contract rule persists.
**Decision:** Report as **0.776**, bucket YELLOW (threshold ≥0.75). Do not round to 0.78 or above. Confidence: 1.00.
**Rationale:** Contract explicitly bans rounding up. Decimal precision chosen to show the bucket flip honestly.

## HITL-INT-V11-006 — Canonical v1.1 publishable with F04/F07/F08 RED

**Subject:** Publish v1.1 despite persistent RED families.
**Options:**
- (a) Block v1.1 publication until RED families close.
- (b) **Publish v1.1 with RED families; document blockers for Wave F+.** ← Chosen.
**Decision:** (b). Confidence: 0.92.
**Rationale:** Same logic as v1 HITL-INT-010. F1 delivered honest, bounded improvement (F12 GREEN, global YELLOW). Blocking publication would waste that improvement. The RED families are a documented Wave F+ charter.
