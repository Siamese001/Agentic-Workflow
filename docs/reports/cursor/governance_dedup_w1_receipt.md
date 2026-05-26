# W1 Receipt — governance-dedup-closeout-e8a4c2

**Wave:** W1 — Hook obsolete retirement  
**Date:** 2026-05-26  
**Status:** PASS

## Shadow waiver

| Field | Value |
|-------|--------|
| Planned eligible | 2026-06-02 UTC (7-day W0 baseline) |
| Waiver | Operator requested W1 early — logged in [governance_dispatch_shadow.jsonl](../../artifacts/cursor/governance_dispatch_shadow.jsonl) (`w1_shadow_waiver`) |

## W1.1 — Scripts archived

Moved **12** scripts to [`.cursor/scripts/_legacy_cursor/`](../../.cursor/scripts/_legacy_cursor/README.md):

- `post_cursor_agent_author_gate_audit.py`, `author_gate_suite.py`
- `notion_plans_status_audit.py`, `plan_creation_audit.py`, `plan_complete_audit.py`, `plans_dup_audit.py`
- `heartbeat.py`, `cleanup.py`, `grep_budget_audit.py`, `read_budget_audit.py`, `token_telemetry.py`
- `adr_registry_capture.py` (removed from `post_cursor_agent_dispatch` `LEGACY_SCRIPTS`)

Active post-agent scripts (top-level): **30** (was 42).

## W1.2 — Legacy hook archived

| Item | Location |
|------|----------|
| `after_agent_author_gate_audits.py` | [`.cursor/hooks/_legacy_cursor/`](../../.cursor/hooks/_legacy_cursor/README.md) |

## W1.3 — Tests and wiring

| Check | Result |
|-------|--------|
| `pytest tests/unit/ops_scripts/hooks/cursor/ -q` | **34 passed** |
| `check_ag_hook_wiring.py` | PASS |
| Chain wiring tests | Target `after_agent_governance_dispatch.py` |
| Heartbeat latency test path | Updated to `_legacy_cursor/post_cursor_agent_heartbeat.py` |

## Matrix refresh

| Metric | Before W1 | After W1 |
|--------|-----------|----------|
| `post_agent_scripts_total` | 42 | 30 |
| `obsolete_candidate` | 12 | 0 |

Artifact: [governance_w3_hook_audit_matrix.json](governance_w3_hook_audit_matrix.json)

## Marker

```
WAVE_COMPLETE: plan=governance-dedup-closeout-e8a4c2 wave=1 note="12 scripts+1 hook archived, dispatch adr removed, 34 pytest PASS, AG-WIRE PASS"
```

## Next wave

**W2** — `check_cursor_native_config` allowlist + `generate_rules_index --check` drift fix.
