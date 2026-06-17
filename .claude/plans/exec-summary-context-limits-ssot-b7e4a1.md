---
plan_id: exec-summary-context-limits-ssot-b7e4a1
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
dod_exempt: false
---

# Executive summary — context limits SSOT consolidation (24k)

Centralize exec-summary char/token defaults and env resolvers in `executive_summary_context_limits.py`; remove duplicate hardcoded defaults across lane, token_budget, and regen_dispatch.

> **Related:** [executive_summary_24k_context_budget_rationalization_20260526.md](../../docs/reports/apps_rg/executive_summary_24k_context_budget_rationalization_20260526.md)

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1  
PLAN_STATUS: COMPLETE  
CURRENT_WAVE: —  
LAST_COMPLETED_WAVE: W3  
LAST_UPDATED: 2026-05-26  

PLAN_CREATED: slug=exec-summary-context-limits-ssot-b7e4a1 path=.claude/plans/exec-summary-context-limits-ssot-b7e4a1.md status=Complete

---

## Context (SCQA)

| | |
|---|---|
| **Situation** | 24k alignment raised briefing/targeting caps; `VLLM_MAX_MODEL_LEN` lives in L0 + `.env`. |
| **Complication** | Scratch `2048`, reserved `512`, first-pass `0.92`, and context window `24576` still duplicated across `token_budget`, `lane`, `qwen_regen_dispatch`. |
| **Question** | Single code SSOT + env key catalog; `.env` only for infra overrides. |
| **Answer** | Extend `executive_summary_context_limits.py` with resolvers; wire consumers; unit tests. |

---

## Status Tables

### Wave Progress

| Wave | Focus | Status |
|------|--------|--------|
| W1 | `context_limits` resolvers + wire lane/token_budget/regen_dispatch/bullet selector | Done |
| W2 | Tests + `.env.example` env key catalog | Done |
| W3 | Notion registration + closeout receipt | Done |

---

## Scope

### In scope

- [executive_summary_context_limits.py](apps_rg/runtime/sections/executive_summary_context_limits.py)
- [executive_summary_token_budget.py](apps_rg/runtime/sections/executive_summary_token_budget.py) — `QWEN_LOCAL_MAX_MODEL_LEN` fallback
- [executive_summary_qwen_regen_dispatch.py](apps_rg/runtime/sections/executive_summary_qwen_regen_dispatch.py)
- [executive_summary_lane.py](apps_rg/runtime/sections/executive_summary_lane.py)
- [bullet_pool_claude_selector.py](apps_rg/runtime/judges/bullet_pool_claude_selector.py)
- Unit tests

### Out of scope

- `agentic_core` repair_policy / regen delta policy
- Per-section lane `*_QWEN_MAX_TOKENS` (headline, unify, ibm)
- Live Brown runtime proof (unit proof only)

---

## Definition of done

- [x] One module owns char caps, output token caps, reserved tokens, first-pass utilization default, env key names
- [x] No duplicate `2048` / `24576` literals outside `context_limits` + L0 `model_registry`
- [x] `lane` resolves scratch max output at call time (not import time)
- [x] Pytest seam tests PASS (38 passed, 2026-05-26)
- [x] Closeout: [executive_summary_context_limits_ssot_closeout_20260526.md](../../docs/reports/apps_rg/executive_summary_context_limits_ssot_closeout_20260526.md)
- [x] E2E: [exec_summary_context_limits_ssot_e2e_20260526.md](../../docs/reports/apps_rg/exec_summary_context_limits_ssot_e2e_20260526.md) — live [exec_summary_20260526_203341](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_203341) **X3_ALLOW**
