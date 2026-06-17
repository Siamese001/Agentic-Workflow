# ADR-094 — MCP Serialization Sentinel (Layer 1) — Existence and Retirement Procedure

- **Status**: Retired (superseded by ADR-097 cleanup)
- **Date**: 2026-05-02
- **Retired**: 2026-06-15 status reconciliation
- **Supersedes**: prior MCP Registry row `_serialization_sentinel (Layer 1 — MCP serialization enforcement)` (archived with the MCP Registry DB on 2026-05-02 — see consolidation note in `AGENTS.md` Notion Workspace Map history)
- **Superseded by**: ADR-097 (`mcp-serialization.md` retired; W5 cleanup scope)
- **Related**: historical constitutional `§25` (MCP serialization), historical `.claude/rules/mcp-serialization.md`, upstream `anthropics/claude-agent-sdk-typescript#41`

> **Current-state note (2026-06-15):** this ADR is retained as the retirement
> runbook and historical rationale. Active MCP routing is governed by
> `.mcp.json`, `.claude/mcp-notes.md`, and `.claude/skills/mcp-integration/`.
> Do not re-enable the sentinel from this file.

## Context

The original constitutional `§25` "one remote MCP per response" rule (now scoped to remote MCPs only — see `.claude/rules/mcp-serialization.md`) is enforced at two layers:

| Layer | Mechanism | Posture |
|---|---|---|
| **Layer 0 — reactive** | `post_cursor_agent_mcp_serialization_audit.py` post-hook logs violations to `artifacts/windsurf/mcp_serialization_violations.jsonl` | Logs after the hang already happened |
| **Layer 1 — preventive** | `_serialization_sentinel.py` cross-process sentinel imported by `pre_mcp_gate.py`, `pre_run_gate.py`, `pre_read_gate.py`, `pre_write_gate.py` | Blocks dispatch with exit 2 before the SDK fires its 4-minute internal timeout |

Layer 1 was added 2026-04-25 after Codex batched `todo_list + mcp1_adg_health` in one `<function_calls>` block and the turn hung on the MCP call until the user cancelled. Layer 0 logged the violation post-hoc but could not prevent the hang.

## Historical Decision

Layer 1 stays in effect until the upstream Anthropic SDK race is fixed and verified. The retirement procedure is one-shot (no rolling deprecation) and is encoded here so the runbook survives the MCP Registry DB archival.

## Implementation Surface

**Files added (must be removed at retirement)**:
- `.claude/governance/scripts/_serialization_sentinel.py` (~217 lines)
- `tests/unit/ops_scripts/hooks/windsurf/test_serialization_sentinel.py` (18 tests)

**Files partially modified (must be reverted at retirement, each has 1 import + 1 call site)**:
- `.claude/governance/scripts/pre_mcp_gate.py` — import lines 43-46 + call lines 1359-1365
- `.claude/governance/scripts/pre_run_gate.py` — import lines 23-27 + call lines 235-239
- `.claude/governance/scripts/pre_read_gate.py` — import lines 131-132 + call lines 167-171
- `.claude/governance/scripts/pre_write_gate.py` — import line 34 + call lines 325-329

(Line numbers reflect 2026-04-25 state; verify current line numbers before editing.)

## Coverage Surface

Layer 1 catches MCP-with-sibling tool batches that trigger upstream race `anthropics/claude-agent-sdk-typescript#41`:

- **Caught from MCP side**: MCP↔run_command, MCP↔read_file, MCP↔write_to_file/edit/multi_edit (native tools that have legacy editor pre-hooks)
- **Caught when paired with MCP**: native tools without their own pre-hooks (`todo_list`, `grep_search`, `find_by_name`, `list_dir`, `ask_user_question`, `skill`)

Returns exit 2 with a copy-pasteable remediation message instead of letting the SDK time out at 4 minutes.

## Operator Knobs

In effect until retirement:

- `MCP_SERIAL_BYPASS=1` — disable for one session (logs a bypass row to `artifacts/windsurf/mcp_serialization_violations.jsonl`)
- `MCP_SERIAL_WINDOW_S=2.0` — override correlation window (default 1.0s)
- `.windsurf/config/mcp_serialization_ttl.json` `retired_after` — sunsets the layer instantly (no code changes required)

## Retirement Procedure

**Step 1**. Operator verifies the upstream fix shipped. Watch `https://windsurf.com/changelog` for the `claude-agent-sdk-typescript` bump that closes `anthropics/claude-agent-sdk-typescript#41`.

**Step 2**. Create `.windsurf/config/mcp_serialization_ttl.json`:

```json
{
  "retired_after": "<UTC-date>",
  "issue_url": "https://github.com/anthropics/claude-agent-sdk-typescript/issues/41",
  "verified_by": "<operator>"
}
```

The sentinel honors this immediately — `record_and_check()` and `block_if_violation()` go fail-open — so all 4 gates become no-ops without code changes.

**Step 3**. After ≥7 days with zero new entries in `artifacts/windsurf/mcp_serialization_violations.jsonl`, delete the files-added list and revert the files-modified list above.

**Step 4**. Set `.claude/rules/mcp-serialization.md` front-matter to `trigger: manual` with a deprecation banner; remove from always-on load.

**Step 5**. Update `constitutional.md §25` to `status: retired (date <UTC>)` with link to this ADR.

**Step 6**. Add a closing note to this ADR with retirement date + upstream fix PR link, and flip ADR `Status: Active` → `Status: Retired`.

## Verification Commands (must pass before retirement is permitted)

```sh
python -m pytest tests/unit/ops_scripts/hooks/windsurf/test_serialization_sentinel.py  # 18/18 pass
python -m pytest tests/unit/ops_scripts/hooks/windsurf/test_pre_mcp_gate.py            # 245/245 pass (no regressions)
```

## Why This Lives Here Now

The MCP Registry Notion DB was archived 2026-05-02 because ~70% of its content was a mirror of `.mcp.json`. The 30% that was genuinely value-add (BACKLOG proposals, retirement runbooks) is migrated to the right SSOT — backlog proposals to the Backlog Items DB, retirement runbooks to ADRs (this file). See consolidation log at `artifacts/maintenance/notion_consolidation_2026_05_02/`.
