# Legacy Cursor post-agent scripts (archived W1)

**Plan:** `governance-dedup-closeout-e8a4c2` wave W1 (2026-05-26)  
**SSOT chain:** `.cursor/hooks/after_agent_governance_dispatch.py` → active `.claude/governance/scripts/post_cursor_agent_*.py`

These files are **not** wired in `hooks.json`. Kept for manual replay, historical tests, and zero-loss audit. Do not re-wire without updating `check_ag_hook_wiring.py`.

| Script | Reason archived |
|--------|-----------------|
| `post_cursor_agent_author_gate_audit.py` | Superseded by individual AG audits in governance dispatch |
| `post_cursor_agent_author_gate_suite.py` | Orchestration duplicate |
| `post_cursor_agent_notion_plans_status_audit.py` | Superseded by `unified_notion_status_auditor` |
| `post_cursor_agent_plan_creation_audit.py` | Overlap with registration capture + CI |
| `post_cursor_agent_plan_complete_audit.py` | Lifecycle capture + CI |
| `post_cursor_agent_plans_dup_audit.py` | Advisory duplicate detector |
| `post_cursor_agent_heartbeat.py` | Native `_post_handlers/heartbeat.py` in dispatch |
| `post_cursor_agent_cleanup.py` | Native `_post_handlers/cleanup.py` |
| `post_cursor_agent_grep_budget_audit.py` | Native `_post_handlers/grep_budget.py` |
| `post_cursor_agent_read_budget_audit.py` | Native `_post_handlers/read_budget.py` |
| `post_cursor_agent_token_telemetry.py` | Native `_post_handlers/token_telemetry.py` |
| `post_cursor_agent_adr_registry_capture.py` | ADR Notion registry archived 2026-05-02 |

Manual replay: `python .claude/governance/scripts/manual_post_cursor_agent_replay.py` (point at legacy path if needed).
