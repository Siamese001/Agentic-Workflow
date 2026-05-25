# Deferred Scope Register — Judge Regen Loop Closure

**Parent (COMPLETED):** [core-same-authority-incremental-regen-e7a4b1.md](../../.cursor/plans/core-same-authority-incremental-regen-e7a4b1.md)  
**Follow-up (Not Started):** [exec-summary-judge-regen-loop-closure-d8f3a1.md](../../.cursor/plans/exec-summary-judge-regen-loop-closure-d8f3a1.md)  
**Notion:** [exec-summary-judge-regen-loop-closure-d8f3a1](https://www.notion.so/exec-summary-judge-regen-loop-closure-d8f3a1-36b27693f55c81868829c504c6ba97ad)

## Why split

Parent plan proved **chassis** (frozen compile, same provider, `SameAuthorityRegenRunner`, Brown receipts). Brown `exec_summary_20260525_122058` showed **product loop failure**: core heal PASS, lane revert (`post_regen_x2_failed_after_x2_repair`). Parent W4 unblock criterion #4 was not met.

## Deferred items (DS-1..DS-8)

| ID | Item | Follow-up wave |
|----|------|----------------|
| DS-1 | `JudgeDirectedRegenOrchestrator` / `judge_directed_regen.py` | W3 |
| DS-2 | Lane multi-cycle legacy vs core bridge | W1 |
| DS-3 | Post-regen X2 green before judge rescore | W2, W5 |
| DS-4 | Pre/post `x2_gate_outputs` snapshots | W4 |
| DS-5 | `judge_remediation_cycles` accepted (no revert) | W5 |
| DS-6 | `max_semantic_regen_attempts` > 1 | After W5 PASS |
| DS-7 | Product-default regen env flags | W1 |
| DS-8 | DRAFT_READY vs CERTIFIED (operator ship) | W2 coord |

## Evidence anchor

- [core_same_authority_regen_brown_20260525_122058_receipt.md](../apps_rg/core_same_authority_regen_brown_20260525_122058_receipt.md)
- Run dir: `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_122058`
