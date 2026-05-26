# Governance dedup closeout receipt — governance-dedup-closeout-e8a4c2

**Date:** 2026-05-26  
**Status:** PASS  
**Parent:** [cursor-governance-two-tier-b4e8f2](../../.cursor/plans/_archive/2026-05/cursor-governance-two-tier-b4e8f2.md) (COMPLETED)  
**Source audit:** [governance_dedup_audit_20260526.md](governance_dedup_audit_20260526.md)

## Executive summary

All six deferred items from the 2026-05-26 governance dedup audit are **resolved (PASS)** or **explicitly deferred (GAP-4, P4)** with mitigation documented. Five waves (W0–W4) executed; W5 emits this manifest and closes the plan.

## Deferred-item resolution

| Gap | Title | Wave | Status | Evidence |
|-----|-------|------|--------|----------|
| GAP-1 | Dispatch shadow period | W1 | PASS | Operator waiver in [governance_dispatch_shadow.jsonl](../../artifacts/cursor/governance_dispatch_shadow.jsonl) |
| GAP-2 | Obsolete hook scripts | W1 | PASS | [governance_dedup_w1_receipt.md](governance_dedup_w1_receipt.md) — `_legacy_cursor/` archive |
| GAP-3 | Native config legacy refs | W2 | PASS | [governance_dedup_w2_receipt.md](governance_dedup_w2_receipt.md) — allowlist yaml |
| GAP-4 | MCP redirect stubs | — | DEFERRED (P4) | AGENTS.md stub note; optional autogen Skill → § anchors |
| GAP-5 | Plan sprawl | W3 | PASS | [governance_dedup_w3_receipt.md](governance_dedup_w3_receipt.md) — 11 top-level plans |
| GAP-6 | Windsurf always_on | W4 | PASS | [governance_dedup_w4_receipt.md](governance_dedup_w4_receipt.md) — 0 B always_on |

## Wave receipts

| Wave | Focus | Receipt |
|------|-------|---------|
| W0 | Hook matrix + shadow baseline | [governance_dedup_w0_receipt.md](governance_dedup_w0_receipt.md) |
| W1 | Obsolete script retirement | [governance_dedup_w1_receipt.md](governance_dedup_w1_receipt.md) |
| W2 | CI allowlist + RULES_INDEX | [governance_dedup_w2_receipt.md](governance_dedup_w2_receipt.md) |
| W3 | Plan sprawl archive | [governance_dedup_w3_receipt.md](governance_dedup_w3_receipt.md) |
| W4 | Windsurf always_on demotion | [governance_dedup_w4_receipt.md](governance_dedup_w4_receipt.md) |
| W5 | Closeout manifest | this file |

## Final metrics

| Metric | Value |
|--------|-------|
| Tier-1 bytes | 19,674 (~4,918 tokens) — **PASS** |
| `alwaysApply` rules | 4 (`000`–`003`) |
| Windsurf `always_on` | **0 files / 0 B** |
| Active top-level plans | **11** (≤ 20) |
| Post-agent SSOT | `after_agent_governance_dispatch.py` |

## Definition of Done

| DoD | Requirement | Status |
|-----|-------------|--------|
| DoD-1 | Audit deferred items in receipt | PASS (GAP-4 DEFERRED P4) |
| DoD-2 | `check_ag_hook_wiring.py` | PASS |
| DoD-3 | `check_cursor_optimized_config.py` + `check_agents_md_sync.py` | PASS |
| DoD-4 | Hook unit tests | 34 passed |
| DoD-5 | Plan on disk + audit link-back | PASS |

## Verification commands

```bash
python ops_scripts/ci/check_ag_hook_wiring.py
python ops_scripts/ci/check_agents_md_sync.py
python .cursor/scripts/check_cursor_optimized_config.py
python .cursor/scripts/generate_rules_index.py --check
python ops_scripts/ci/check_always_on_token_budget.py
pytest tests/unit/ops_scripts/hooks/cursor/ -q
```

## Marker

```
PLAN_COMPLETE: plan=governance-dedup-closeout-e8a4c2 note="W0-W5 PASS; GAP-4 optional P4 deferred"
WAVE_COMPLETE: plan=governance-dedup-closeout-e8a4c2 wave=5 note="closeout manifest on disk"
```
