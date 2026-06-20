# Codex MCP Process Cohort Cleanup

Generated: 2026-06-11  
Plan: `codex-claude-mcp-access-parity-c6d4e2`  
Scope: fix duplicate MCP process cohorts after multiple Claude parents launched the repo MCP tree.

## Result

Fixed. The duplicate MCP process cohorts were caused by two Claude agent parent processes each owning a full MCP launch tree. The older Claude child MCP cohort was terminated while leaving Claude parent processes intact.

## Runtime Cleanup

Terminated 16 duplicate MCP child processes from older Claude parent PID `31676`:

- GitKraken MCP: 1 process
- `adg_sqlite`: 1 process
- `memory`: 1 process
- `vector_db`: 1 process
- Notion MCP launch tree: 3 processes
- Context7 MCP launch tree: 4 processes
- Playwright MCP launch tree: 5 processes

The newer Claude MCP cohort under parent PID `13272` was preserved.

## Code Fix

Updated `scripts/governance/audit_codex_mcp_transports.py` so `adg_sqlite` detection includes the live launcher command:

```text
tools.mcp.launch_adg_sqlite_mcp
```

Added guarded cleanup helper:

```text
python scripts/governance/cleanup_duplicate_mcp_cohorts.py --json
python scripts/governance/cleanup_duplicate_mcp_cohorts.py --apply --json
```

The helper defaults to dry-run, never terminates Claude parent processes, and does not traverse through nested Claude parents when selecting duplicate MCP children.

## Final Audit

| MCP | Final Process Classification | Process Count | Root Launcher Count |
|---|---|---:|---:|
| `adg_sqlite` | `single` | 1 | 1 |
| `memory` | `single` | 1 | 1 |
| `vector_db` | `single` | 1 | 1 |
| `notion` | `single_launch_tree` | 3 | 1 |
| `context7` | `single_launch_tree` | 4 | 1 |
| `playwright` | `single_launch_tree` | 3 | 1 |

Dry-run cleanup after the fix returns no duplicate targets:

```json
{
  "mode": "dry-run",
  "selection": {
    "keep_parent_pid": 13272,
    "duplicate_parent_pids": [],
    "target_pids": [],
    "targets": []
  }
}
```

## Verification

| Check | Result |
|---|---|
| `python -m py_compile scripts/governance/audit_codex_mcp_transports.py scripts/governance/cleanup_duplicate_mcp_cohorts.py` | Pass |
| `python -m pytest tests/unit/scripts/governance/test_audit_codex_mcp_transports.py -q` | Pass: 10 passed, 3 warnings |
| `python scripts/governance/verify_codex_primary.py` | Pass |
| `python tools/analysis/check_plan_format_forward.py plans/codex-claude-mcp-access-parity-c6d4e2.md` | Pass |

## Remaining Limit

The Codex `adg_sqlite` tool transport still reports `Transport closed`; this cleanup fixed duplicate process cohorts, not the separate Codex tool attachment issue.
