---
plan_id: exec-summary-x1d-dimension-verdicts-e8f4a2
plan_type: product
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Executive Summary X1D — Dimension Verdicts & Debug Matrix

**North star:** Each proof judge returns **machine-readable pass/fail per rubric dimension** (8 fixed ids). Operators get `x1d_dimension_matrix.json` per run; regen hints prefer dimension tags over keyword guessing.

**Related:** [`exec-summary-x1d-transport-parity-d8f2a1.md`](exec-summary-x1d-transport-parity-d8f2a1.md) (same packet / contract hash). [`exec-summary-operator-ship-a3f7c2.md`](exec-summary-operator-ship-a3f7c2.md) (DRAFT_READY vs CERTIFIED). Does **not** split judges by dimension or change 3/3 cert bar.

> **plan_id discipline:** `exec-summary-x1d-dimension-verdicts-e8f4a2` ↔ file stem ↔ markers `plan=exec-summary-x1d-dimension-verdicts-e8f4a2`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETED
CURRENT_WAVE: —
LAST_COMPLETED_WAVE: W4
LAST_UPDATED: 2026-05-24
PLAN_COMPLETE: plan=exec-summary-x1d-dimension-verdicts-e8f4a2 note="dimension_verdicts+matrix+regen hints; 22 pytest PASS"
NOTION_PAGE_ID: 36b27693-f55c-8108-b39a-d2d83a6421d8
NOTION_PLAN_URL: https://www.notion.so/exec-summary-x1d-dimension-verdicts-e8f4a2-36b27693f55c8108b39ad2d83a6421d8
PLAN_CREATED: slug=exec-summary-x1d-dimension-verdicts-e8f4a2 path=.cursor/plans/exec-summary-x1d-dimension-verdicts-e8f4a2.md status=Completed notion_page=36b27693-f55c-8108-b39a-d2d83a6421d8

---

## Context (SCQA)

- **Situation** — X1D panel uses one holistic 0–5 score; rubric lists 8 dimensions in prose only. X2 isolates hard gates; judge findings are unstructured.
- **Complication** — Cannot answer “which dimension failed for Claude vs OpenAI?” without hand-reading rationale. Regen hints bucket feedback via keyword taxonomy (`synthesis`, `jd_emphasis`).
- **Question** — How to debug and remediate without breaking transport parity or certification?
- **Answer** — Required `dimension_verdicts` in judge JSON (with validated inference fallback), `x1d_dimension_matrix.json` artifact, dimension-tagged regen lines.

---

## Architecture Invariants

| ID | Invariant |
|----|-----------|
| INV-1 | No `agentic_core` edits. |
| INV-2 | One judge call per provider; same `judge_packet_hash` / `canonical_contract_hash`. |
| INV-3 | Headline `score` / `pass` unchanged for X3 aggregation. |
| INV-4 | `deterministic_alignment` must reflect X2 snapshot (all gates pass → pass true). |
| INV-5 | Eight dimension ids are fixed SSOT; no ad hoc keys. |

---

## Waves

| Wave | Scope | DoD |
|------|-------|-----|
| W1 | Schema + `executive_summary_x1d_dimension_verdicts.py` + normalize + `JudgeOutput` | Unit tests PASS |
| W2 | `x1d_dimension_matrix.json` on lane + operator guide § | Artifact shape tested |
| W3 | Regen hints from `dimension_verdicts` | Remediation message tests PASS |
| W4 | Notion + receipt | Plan synced; pytest bundle PASS |

---

## Product Decisions

| ID | Decision |
|----|----------|
| PD-1 | `dimension_verdicts` required in prompt schema; missing → infer from findings/flags then validate. |
| PD-2 | Gemini `responseSchema` includes optional `dimension_verdicts` object (not blocking transport audit). |
| PD-3 | Matrix columns = 8 dimensions × 3 judges + consensus `fail_count≥2`. |
| PD-4 | Out of scope: per-dimension isolated judge API calls; threshold changes. |

---

## Key files

- [`apps_rg/runtime/judges/executive_summary_x1d_dimension_verdicts.py`](apps_rg/runtime/judges/executive_summary_x1d_dimension_verdicts.py) (new)
- [`apps_rg/runtime/judges/executive_summary_judge_packet.py`](apps_rg/runtime/judges/executive_summary_judge_packet.py)
- [`apps_rg/runtime/judges/executive_summary_x1d.py`](apps_rg/runtime/judges/executive_summary_x1d.py)
- [`apps_rg/runtime/sections/executive_summary_judge_remediation.py`](apps_rg/runtime/sections/executive_summary_judge_remediation.py)
- [`apps_rg/runtime/sections/executive_summary_lane.py`](apps_rg/runtime/sections/executive_summary_lane.py)
- [`docs/apps_rg/executive_summary_operator_guide.md`](docs/apps_rg/executive_summary_operator_guide.md)
- [`tests/unit/apps_rg/test_executive_summary_x1d_dimension_verdicts.py`](tests/unit/apps_rg/test_executive_summary_x1d_dimension_verdicts.py)
