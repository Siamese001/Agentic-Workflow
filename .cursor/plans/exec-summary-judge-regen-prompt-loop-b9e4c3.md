---
plan_id: exec-summary-judge-regen-prompt-loop-b9e4c3
plan_type: enhancement
touches_agentic_core: false
touches_governance_ci: false
parent_plan: exec-summary-judge-regen-control-loop-f8a3c2
---

# Executive Summary — Judge Regen Prompt Loop Fix

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: Completed
CURRENT_WAVE: —
LAST_COMPLETED_WAVE: W2
NOTION_PAGE_ID: 36c27693-f55c-818c-9837-e65745a0c107
LAST_UPDATED: 2026-05-26

PLAN_CREATED: slug=exec-summary-judge-regen-prompt-loop-b9e4c3 path=.cursor/plans/exec-summary-judge-regen-prompt-loop-b9e4c3.md status=In Progress notion=36c27693-f55c-818c-9837-e65745a0c107

---

## Context (SCQA)

- **Situation** — Judge regen runs 3 Qwen cycles but Claude stays at 4.0; cycle 2 never rescored (G5 reject).
- **Complication** — Stale REGEN_DELTA, wrong `delta_class` when holistic fail has only minor `synthesis_quality`, token budget drops surgical instructions, thread never advances on G3 fail.
- **Question** — Why does regen not improve Claude, and what is the minimal fix?
- **Answer** — W1 patches: S6 delta routing, thread/judge refresh after rescore, delta pack order, contradictory-finding filter, G5 baseline from last assistant turn.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status |
|------|-------|--------|
| W0 | Plan + Notion registration | Done |
| W1 | Code + unit tests | Done |
| W2 | REAL_LLM Brown re-run proof | Done (PARTIAL — S6 delta + REGEN_DELTA_v1; early stop: Qwen JSON parse) |

---

## W1 — Implementation

| ID | Change | File(s) |
|----|--------|---------|
| R1 | `resolve_delta_class`: holistic below floor + S6 thin → `S6_forward_synthesis`; Claude-only binding | `executive_summary_regen_delta_policy.py` |
| R2 | Filter “all gates pass” findings when judge soft-failed | `executive_summary_judge_remediation.py` |
| R3 | Pack dimension/floors/guards before verbatim judge feedback; EDIT_BUDGET line | `executive_summary_judge_remediation.py` |
| R4 | Advance regen thread + `_judge_prompt_x1d` after rescore (even on G3 reject) | `executive_summary_judge_regen_loop.py`, `executive_summary_lane.py` |
| R5 | G5 compares against last assistant resume in thread | `executive_summary_lane.py` |

---

## Proof

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/unit/apps_rg/test_executive_summary_regen_delta_policy.py tests/unit/apps_rg/test_executive_summary_judge_regen_loop.py -q -o addopts=
```

---

## W2 proof (2026-05-26)

- Run: [exec_summary_20260526_084014](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_084014)
- Receipt: [exec_summary_regen_prompt_loop_w2_receipt_20260526.md](../../docs/reports/cursor/exec_summary_regen_prompt_loop_w2_receipt_20260526.md)
- Verifier: `python tools/cursor/verify_exec_summary_regen_prompt_loop_w2.py artifacts/.../exec_summary_20260526_084014`

## Follow-up (optional)

- Re-run Brown when Qwen regen JSON parse is stable to prove multi-cycle `REGEN_DELTA_v1` diff + Claude rescore on cycle 2.
