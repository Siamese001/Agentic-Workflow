---
description: Process fix for status reconciliation and CI gate validation for deferred scope
---

# Notion Plan Status Reconciliation — Implementation

Parent RCA: notion-plan-identity-deferred-scope-a3b7e2 status discipline gap

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1-P2 | Process fix: wave_execution_state.py status reconciliation | ~8k | Deferred scope ledger readable | 🟡 IN PROGRESS | complete() suggests Waiting when all deferred items blocked |
| W2 | P3-P4 | Validation: CI gate enhancement for stale In Progress plans | ~6k | Notion API queryable | ⏳ NOT STARTED | Gate flags In Progress + empty Waiting For + >7d deferred entries |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|---------------|-------------|--------|
| P1 | _cmd_complete() deferred scope analysis | wave_execution_state.py, _wave_execution_state.py | Ledger query pattern, time-gate detection | ~4k | IN PROGRESS |
| P2 | Notion PATCH with Waiting status + Waiting For population | wave_execution_state.py | Direct HTTP PATCH pattern, property shape | ~4k | NOT STARTED |
| P3 | Gate query for deferred scope age | check_notion_plans_status_canonical.py | SQLite ledger query, Notion API query | ~3k | NOT STARTED |
| P4 | Gate violation reporting | check_notion_plans_status_canonical.py | JSON report, exit code discipline | ~3k | NOT STARTED |

## Definition of Done

| DoD | Criterion | Verification |
|-----|-----------|--------------|
| DoD-1 | W1 complete: _cmd_complete() reads deferred_scope_calibration ledger | code inspection |
| DoD-2 | W1 functional: Detects time-gated (DS-2) and volume-gated (DS-1) items | test with a3b7e2 plan |
| DoD-3 | W1 functional: Patches Notion Status→Waiting when all remaining work blocked | test with a3b7e2 plan |
| DoD-4 | W1 functional: Populates Waiting For with blocker descriptions | test with a3b7e2 plan |
| DoD-5 | W2 complete: Gate queries Plans DB for In Progress + empty Waiting For | code inspection |
| DoD-6 | W2 functional: Gate queries deferred scope ledger for >7d entries | test with synthetic data |
| DoD-7 | W2 functional: Gate emits actionable JSON report | test with --json flag |
| DoD-8 | CI integration: Gate registered in run_contract_gates.py | code inspection |
| DoD-9 | Smoke-run: `python -m tools.windsurf.wave_execution_state.py complete --plan notion-plan-identity-deferred-scope-a3b7e2` executes | manual run |
| DoD-10 | Smoke-run: `python ops_scripts/ci/check_notion_plans_status_canonical.py --fail-closed` exits 0 baseline | manual run |

## Deferred Scope

None — this is the fix for the deferred scope handling gap itself.

## Gap Register

None.

## Verification vs Deferral

| Item | This Plan | Deferred to Future |
|------|-----------|-------------------|
| Auto-rollback (DS-2 from parent) | — | Remains deferred pending 30d data |
| Real-time webhook (DS-1) | — | Remains deferred pending volume threshold |

## Notes

- This plan fixes the RCA-identified gap where "In Progress" was retained when "Waiting" was semantically correct
- Pattern established: ledger query → blocker analysis → Notion PATCH → CI gate validation
- Target plan for validation: notion-plan-identity-deferred-scope-a3b7e2 (Notion page 35c27693-f55c-8105-acc7-c121fe6860e4)
