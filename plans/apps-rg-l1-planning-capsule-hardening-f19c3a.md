---
plan_id: apps-rg-l1-planning-capsule-hardening-f19c3a
plan_format: v2
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
---

# apps_rg L1 Planning Capsule Hardening - keep L1 bounded, auditable, and downstream-consumable

Preserve the current authority split, but make L1 materially useful: richer intent projection, explicit ambiguity and completion semantics, and receipts that prove downstream consumers actually read the plan instead of re-deriving it later.

Feedback folded into scope:
- Keep L1 as reasoning plus plan generation, not routing or evidence authority.
- Prefer bounded refinement and explicit completion criteria over a vague "loop".
- Make ambiguity severity visible and version-bound the planning priors.
- Treat `route_hints` as advisory only; if a core rename is still desired after this pass, split that into a follow-up plan.

> **plan_id discipline**: `plan_id` matches the filename stem `apps-rg-l1-planning-capsule-hardening-f19c3a`. Wave markers use `plan=apps-rg-l1-planning-capsule-hardening-f19c3a`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-06-19

---

## Context (SCQA)

- **Situation** - `l1_plan_apps_rg` already exists and is called before `l0_route_apps_rg` in the front-spine path. The current contract already carries task, query, support, output, priors, route hints, and ambiguity data.
- **Complication** - L1 is technically on-path but semantically thin. Too much meaningful intent is still being re-derived later in section lanes, and some of the current naming still invites authority confusion.
- **Question** - How do we keep L1 as a bounded planner while making it auditable and useful enough that downstream stages actually consume it?
- **Answer** - Enrich the apps_rg-local planning projection, keep authority boundaries intact, and add receipts plus tests that prove downstream stages used the L1 plan instead of bypassing it.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | Map current L1 consumers and define the local planning capsule boundary | ~12K | Existing `apps_rg` and `agentic_core` contract reads are enough to prove the current seam | 🔲 TODO | We have a field-by-field consumer map and a concrete proposal for what stays local vs deferred |
| W2 | W2.1, W2.2 | Enrich `l1_binding.py` output and wire downstream receipts | ~22K | The existing `L1PlanContract` surfaces are sufficient for the first pass | 🔲 TODO | L1 emits explicit completion, ambiguity, and advisory-feature signals; L0/PA publish receipts showing they consumed them |
| W3 | W3.1, W3.2 | Verify behavior and decide whether a core follow-up is actually required | ~16K | Focused tests and proof runs can expose any remaining gap cleanly | 🔲 TODO | Tests prove no bypass, no authority leakage, and any remaining gap is isolated into a follow-up plan |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Inventory current L1 call sites and downstream field usage | 🔲 TODO |
| W1.2 | Define the apps_rg-local planning capsule and receipt shape | 🔲 TODO |
| W2.1 | Enrich L1 outputs with completion, ambiguity, and version-bound priors | 🔲 TODO |
| W2.2 | Wire L0 / PA / section-spine receipts to prove L1 consumption | 🔲 TODO |
| W3.1 | Add negative tests for bypass, authority leakage, and hidden replanning | 🔲 TODO |
| W3.2 | Run focused verification and split any remaining core-only gap into a new plan | 🔲 TODO |

---

## Out Of Scope

- Giving L1 route authority, evidence authority, or PA authority.
- Renaming core contract fields in `agentic_core` as part of this plan.
- Adding hidden tool calls, evidence retrieval, or state mutation inside L1.
- Broad redesign of section lanes beyond the signals they already consume.

---

## Wave 1 - Boundary Map and Capsule Shape

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W1.1** - Map the current L1 call graph and the exact fields each consumer reads | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** - Define the local planning capsule boundary, including advisory route features, completion criteria, ambiguity severity, and priors metadata | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Commands**:
```bash
rg -n "l1_plan_apps_rg|l0_route_apps_rg|governed_pa_compose|load_section_proof_for_lane|route_hints|ambiguity_register|planning_prior_refs" apps_rg agentic_core tests -g "*.py"
```

**Acceptance**:
- A single map shows where L1 is produced and where it is actually consumed.
- The plan captures which fields can be enriched locally without a core contract change.
- Any remaining desire to rename a core field is explicitly deferred, not smuggled in.

---

## Wave 2 - L1 Enrichment and Receipts

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** - Enrich `apps_rg/runtime/bindings/l1_binding.py` output shape | ~12K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** - Add downstream receipts in L0 and PA so the plan's intent is visible at runtime | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Commands**:
```bash
python -m pytest tests/unit -k "l1 or l0_route or governed_pa" -q
python -m pytest tests/proof -k "wave_bridges or l1" -q
```

**Acceptance**:
- L1 emits explicit completion criteria, ambiguity severity, and version-bound priors.
- Advisory route features are encoded in a way that cannot be mistaken for route authority.
- L0 and PA emit receipts or artifacts showing the L1 plan was read and used.

---

## Wave 3 - Verification and Follow-Up Decision

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** - Add negative tests for direct raw-input routing, hidden replanning, and authority leakage | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** - Run focused verification and decide whether the remaining gap needs a core follow-up plan | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Commands**:
```bash
python -m pytest tests/unit tests/proof -q
python scripts/governance/codex_readiness.py --json
git diff -- plans/apps-rg-l1-planning-capsule-hardening-f19c3a.md
```

**Acceptance**:
- A bypass from raw inputs directly to downstream routing is not possible without a failing test.
- L1 remains a planner only, with no evidence or routing authority.
- Any remaining need for core field renames or deeper contract changes is split into a separate plan.

---

## Execution Details

### W1.1 - Current Consumer Map
**Scope**: Read the current L1 production and consumption paths in `apps_rg`, `agentic_core`, and the proof/section loaders.

### W1.2 - Local Capsule Definition
**Scope**: Define the apps_rg-local intent capsule: completion criteria, ambiguity severity, version-bound priors, and advisory route features.

### W2.1 - L1 Enrichment
**Scope**: Enrich `l1_binding.py` output without changing authority boundaries. Use existing contract surfaces first; do not add hidden replanning.

### W2.2 - Downstream Receipts
**Scope**: Make L0 and PA emit receipts or artifacts that prove they consumed the L1 plan instead of reconstructing the same intent from raw inputs.

### W3.1 - Negative Tests
**Scope**: Verify the plan fails closed on bypasses, authority leakage, and any hidden second-pass planning behavior.

### W3.2 - Follow-Up Decision
**Scope**: Decide whether the remaining gap is small enough to keep local or must be split into a separate core plan.

---

## Gap Register

**GAP-1: L1 is present but semantically thin**
- The current contract is on the right side of the authority split, but much of the useful intent is still implicit.

**GAP-2: Naming can blur authority**
- `route_hints` is easy to read as route authority unless the payload shape is clearly constrained and receipts prove otherwise.

**GAP-3: Planning semantics are not fully explicit**
- Completion criteria, ambiguity severity, and version-bound priors should be visible enough that downstream stages do not have to guess.

**GAP-4: Consumption is not yet provable enough**
- The current path proves L1 exists; this plan needs to prove that downstream consumers actually read it.

---

## Definition of Done

DoD-1: L1 remains a planner only, with no route or evidence authority.
- Evidence: current call paths still route through L0 and C0 for their respective authority.
- Status: TODO

DoD-2: L1 output includes explicit planning semantics.
- Evidence: enriched `L1PlanContract` payload or apps_rg-local projection carries completion criteria, ambiguity severity, and version-bound priors.
- Status: TODO

DoD-3: Downstream consumers prove they used the plan.
- Evidence: L0 and PA receipts reference the L1 plan fields or digest.
- Status: TODO

DoD-4: Negative tests fail closed on bypass and leakage cases.
- Evidence: focused unit/proof tests catch raw-input routing, hidden replanning, and authority drift.
- Status: TODO

DoD-5: Any remaining core-only change is split, not implied.
- Evidence: a separate follow-up plan is minted if the local pass hits a real core contract limit.
- Status: TODO

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```text
DISCOVERED_SCOPE: plan=apps-rg-l1-planning-capsule-hardening-f19c3a wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=apps-rg-l1-planning-capsule-hardening-f19c3a decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=apps-rg-l1-planning-capsule-hardening-f19c3a reason="<summary>" added="<waves/phases>" authorized="yes"
```

| Decision | When | Continues? |
|---|---|---|
| ACCEPTED | In-charter and absorbable | Yes, expanded scope |
| DEFERRED | Valid but time-gated | Yes, original scope |
| SPLIT_TO_NEW_PLAN | Too large or core-gated | Yes, original scope |
| REJECTED | Gold-plating | Yes, original scope |

---

## Supersedes

| Predecessor slug | Reason |
|---|---|
| _None - net-new plan._ | This is a fresh hardening pass, not a replacement for an existing active plan. |

---

## Marker Quick Reference

```text
WAVE_START: plan=apps-rg-l1-planning-capsule-hardening-f19c3a wave=<N>
WAVE_COMPLETE: plan=apps-rg-l1-planning-capsule-hardening-f19c3a wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=apps-rg-l1-planning-capsule-hardening-f19c3a phase=<W1.1>
PLAN_COMPLETE: plan=apps-rg-l1-planning-capsule-hardening-f19c3a note="<final outcome>"
```

> Manual maintenance: update wave, phase, and DoD status deliberately as evidence arrives. If the local pass proves that a core contract rename is required, split it into a follow-up plan instead of broadening this one by implication.

