---
plan_id: l5-l4-00c-parent-gap-b8e4f2
plan_type: audit
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# L5 / L4-UWG / 00C Parent-Pack Gap Remediation

Close documented gaps between the repo and the **REQ-ID parent packs** for 00A (L5 certification), 00B (L4/UWG), and 00C (runtime gate mesh), producing reconciled traceability and release-gate proof — without weakening existing FortKnox-certified behavior.

> **Evidence companion:** [l5-l4-00c-parent-gap-evidence-b8e4f2.md](../docs/reports/plans/l5-l4-00c-parent-gap-evidence-b8e4f2.md)

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: W1
LAST_UPDATED: 2026-05-23

---

## Context (SCQA)

- **Situation** — The repo has substantial L4/UWG implementation (`agentic_core/L4_state/uwg/`), L5 certification contracts, and a 29-gate runtime mesh (`agentic_core/L5_safety/runtime_gates/`). Prior traceability matrices ([l4_uwg_requirements_traceability_matrix.md](../docs/reports/plans/l4_uwg_requirements_traceability_matrix.md), [runtime_gates_doctrine_requirements_matrix.md](../docs/reports/plans/runtime_gates_doctrine_requirements_matrix.md)) were written against **detailed** child doctrine files.
- **Complication** — New **parent** packs ([00A](../docs/reference/00A_L5_Governance_Safety/00A_L5_Governance_Safety.md), [00B](../docs/reference/00B_L4_State_Archive_and_UWG/00B_L4_State_Archive_and_UWG.md), [00C](../docs/reference/00C_Runtime_Gates_Current_Run_Mesh/00C_Runtime_Gates_Current_Run_Mesh.md)) use REQ-ID tables with **DOC_ONLY** release gates, different vocabulary (e.g. 6 gate dispositions vs 15 mesh dispositions; 5 L5 cert_status tokens vs `L5_CERTIFIED`), and **G21–G24 semantic reordering** vs running code.
- **Question** — How do we produce an honest gap inventory and a phased remediation plan that preserves certified runtime paths while aligning evidence to the parent contracts?
- **Answer** — Reconcile spec authority first (00C.7 vs 00C parent), then refresh REQ-ID traceability rows, then implement the highest-risk runtime gaps (L5 runtime bind, HITL reclearance cert, named validators) without bypassing UWG or Exit boundaries.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | Spec reconciliation + REQ-ID inventory | ✅ DONE | — | 2 |
| W2 | 00A L5 certification runtime gaps | 🔲 TODO | — | — |
| W3 | 00B parent validator linkage + receipt parity | 🔲 TODO | — | — |
| W4 | 00C schema mapping / gate-band decision | 🔲 TODO | — | — |
| W5 | Integrated proof + Notion/00X writeback | 🔲 TODO | — | — |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Parent REQ-ID → repo row mapping (three packs) | ✅ DONE |
| W1.2 | 00C authority decision (parent §5 vs 00C.7) | ✅ DONE |
| W2.1 | RuntimeCertificationBinding producer | 🔲 TODO |
| W2.2 | L5HITLReclearanceResult + cert_status alignment | 🔲 TODO |
| W2.3 | Cross-child + no-write release validators | 🔲 TODO |
| W3.1 | UWG/L4 receipt field parity vs parent §5 | 🔲 TODO |
| W3.2 | Named validator scripts ↔ CI gates | 🔲 TODO |
| W4.1 | GateVerdict export schema adapter (if parent wins) | 🔲 TODO |
| W4.2 | G21–G24 relabel or ADR (if parent wins) | 🔲 TODO |
| W5.1 | Regenerate proof bundles + traceability matrices | 🔲 TODO |

---

## Out Of Scope

- Rewriting child packs `00A.1`–`00A.8a`, `00B.1`–`00B.9`, `00C.1`–`00C.9` atomic tables (separate plans per child).
- End-to-end scenario proof pack `99` (consumes outputs of this plan).
- App-specific `apps_rg` overlay behavior except boundary/no-bypass tests.
- Generic `agentic_core` refactors not required to close a parent REQ_ID row.

---

## Wave 1 — Spec reconciliation and inventory

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W1.1** — Build machine-readable gap matrix: 44 parent REQ rows (11+12+21) × {MET, PARTIAL, DRIFT, MISSING} | ~25K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** — 00C SSOT decision: **00C.7** (see ADR) | ~10K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Gap matrix: [l5-l4-00c-parent-gap-matrix-b8e4f2.json](../docs/reports/plans/l5-l4-00c-parent-gap-matrix-b8e4f2.json)
- ADR: [ADR-00C-7-gate-verdict-ssot-b8e4f2.md](../docs/adr/ADR-00C-7-gate-verdict-ssot-b8e4f2.md)

---

## Wave 2 — 00A L5 certification gaps

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — Implement run-start `RuntimeCertificationBinding` producer (REQ-L5-RUNTIME-BIND-001) | ~40K tokens | PHASE_STATUS: TODO
- **W2.2** — Emit `L5HITLReclearanceResult`; map cert_status to parent 5-token vocabulary (REQ-L5-HITL-RECLEAR-001, vocabulary) | ~35K tokens | PHASE_STATUS: TODO
- **W2.3** — `l5_cross_child_consistency_validator` + `l5_no_write_validator` wired to CI (REQ-L5-CROSS-CHILD-CONSISTENCY-001, REQ-L5-NO-WRITE-001) | ~25K tokens | PHASE_STATUS: TODO

**Acceptance**:
- `coverage_matrix.md` rows R0615, R0620–R0622 move from PARTIAL/UNCOVERED to FULL or documented STRUCTURAL with tests
- No `FORBIDDEN_RUNTIME_DISPOSITIONS` regressions

---

## Wave 3 — 00B L4/UWG parent alignment

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — Diff `UWGCommitReceipt` / audit append JSON vs parent §5 required fields | ~20K tokens | PHASE_STATUS: TODO
- **W3.2** — Add CI aliases: `uwg_sole_admission_validator` → existing anti-bypass suite; refresh [l4_uwg_requirements_traceability_matrix.md](../docs/reports/plans/l4_uwg_requirements_traceability_matrix.md) parent §4 rows | ~30K tokens | PHASE_STATUS: TODO

**Acceptance**:
- Parent REQ-UWG-* / REQ-L4-* rows show IMPL+TEST+RUNTIME (not DOC_ONLY-only)
- `pytest tests/l4 tests/uwg` remains green

---

## Wave 4 — 00C gate mesh alignment

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** — If W1.2 selects parent §5: add `GateVerdict` JSON export adapter (6 dispositions, 4 results) without breaking internal 15-disposition mesh | ~45K tokens | PHASE_STATUS: TODO
- **W4.2** — If W1.2 selects parent gate bands: plan G21–G24 migration OR update parent pack to match 00C.7 (preferred if certification bundles depend on current IDs) | ~50K tokens | PHASE_STATUS: TODO

**Acceptance**:
- RTC-REQ-080–084 evidence still passes
- `runtime_gate_verdict_bundle.json` regen with documented digest change only if band migration executed

---

## Wave 5 — Proof consolidation

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Phases**:
- **W5.1** — Regenerate `l4_uwg_runtime_proof.json`, `runtime_gates_runtime_proof.json`; update 00X no-loss map | ~20K tokens | PHASE_STATUS: TODO

**Acceptance**:
- All three parent packs have linked traceability rows in 00X
- Notion Plans row Status progression documented

---

## Gap Register

**GAP-1: 00C parent vs 00C.7 schema drift**
- Parent §5 mandates 6 dispositions (`REROUTE_HINT`, `ESCALATE_HINT`, …); mesh uses 15 canonical dispositions + aliases.
- Impact: External auditors reading parent pack will fail schema validation against live bundles.

**GAP-2: G21–G24 semantic reorder in parent §4**
- Parent: G21 Output, G22 Security, G23 Replay, G24 Audit.
- Code: G21 Schema, G22 Quality, G23 Security, G24 Replay; audit/trace at G28.
- Impact: Wrong gate invoked if REQ-ID traceability follows parent without reconciliation.

**GAP-3: L5 RuntimeCertificationBinding not produced at run start**
- Contracts exist; integrated runtime does not emit `runtime_certification_binding_<run_id>.json` per REQ-L5-RUNTIME-BIND-001.

**GAP-4: L5HITLReclearanceResult missing**
- G06 HITL gate exists; L5 certification artifact for reclearance absent (R0615 UNCOVERED).

**GAP-5: Parent-named release validators absent**
- 00A/00B/00C list `*_validator` release-gate symbols; enforcement is behavioral tests + FortKnox, not named scripts.

**GAP-6: L4/UWG traceability matrix stale vs REQ-ID rewrite**
- Matrix references pre-rewrite detailed filenames; parent §4 REQ IDs not row-keyed.

**GAP-7: L5 cert_status vocabulary mismatch**
- Parent: `certified` / `not_certified` / …; code: `L5_CERTIFIED` / `L5_NOT_CERTIFIED`.

**GAP-8: Dual UWG package surfaces**
- `agentic_core/UWG/`, `L4_state/uwg/`, `runtime/uwg/` — consolidation needed for sole-admission proof narrative.

---

## Definition of Done

DoD-1: Machine-readable gap matrix for all 44 parent REQ rows exists and is linked from 00X.
- Evidence: [l5-l4-00c-parent-gap-matrix-b8e4f2.json](../docs/reports/plans/l5-l4-00c-parent-gap-matrix-b8e4f2.json)
- Status: DONE

DoD-2: 00C authority decision documented (parent §5 vs 00C.7).
- Evidence: [ADR-00C-7-gate-verdict-ssot-b8e4f2.md](../docs/adr/ADR-00C-7-gate-verdict-ssot-b8e4f2.md) — **00C.7 wins**
- Status: DONE

DoD-3: L5 runtime bind + HITL reclearance artifacts emit in integrated certification run.
- Evidence: `certification/agentic_core/integrated_runtime/latest/` contains binding + hitl reclear JSON when applicable
- Status: TODO

DoD-4: Test suites remain green for scoped seams.
- Evidence: `pytest tests/l4 tests/uwg tests/runtime_gates tests/governance/test_l5_cross_child_certification.py -q` → 0 failed
- Status: TODO

DoD-5: Traceability matrices refreshed and Notion Plans row updated to Completed.
- Evidence: Updated `l4_uwg_requirements_traceability_matrix.md`, `runtime_gates_doctrine_requirements_matrix.md`, `coverage_matrix.md`; Notion Plans Status=Completed
- Status: TODO

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers per template — especially if G21–G24 migration touches `agentic_core` gate registry (requires core addition author gate).

| Decision | When | Continues? |
|---|---|---|
| ACCEPTED | In-charter, absorbable | Yes, expanded scope |
| DEFERRED | Child-pack atomic tables | Yes, original scope |
| SPLIT_TO_NEW_PLAN | Full 00C.1–00C.9 rewrite | Yes, original scope |
| REJECTED | Gold-plating | Yes, original scope |
