# Cursor-native Agentic AI controls

This folder is the active Cursor operating surface for the Agentic AI project.

## Active always-on rules (Option A — four rules)

These four `.mdc` files have `alwaysApply: true` (measured with `AGENTS.md` in `governance_tier_inventory.json`):

- `.cursor/rules/000-agentic-core-operating-contract.mdc`
- `.cursor/rules/001-cursor-runtime-seam-execution.mdc`
- `.cursor/rules/002-pass-blocked-proof-contract.mdc`
- `.cursor/rules/003-cursor-author-gate-hitl.mdc`

Everything else is task-scoped reference material, a skill, an agent, a hook, a script, a schema, or archived history.

## Hooks (pre / post Cursor)

| Cursor event | Hook entry | Role |
|--------------|------------|------|
| `beforeSubmitPrompt` | `hooks/before_submit_prompt.py` | Legacy-surface guard + ADG-first warning |
| `beforeSubmitPrompt` | `scripts/pre_user_prompt_author_gate_reminder.py` | Author-Gate replay (informational) |
| `afterAgentResponse` | `hooks/after_agent_governance_dispatch.py` | **SSOT** post-agent chain (ADG, AG audits, Notion, dispatch) |
| Other events | `hooks/before_*`, `after_file_edit`, `stop` | Shell/MCP/read gates, edit audit, stop audit |

Do not wire duplicate post-agent chains. Legacy chain/hooks live under `_legacy_cursor/` (see W1 archive README). Active SSOT: `after_agent_governance_dispatch.py`.

## Operating model

Cursor should execute like a bounded repo agent:

1. Patch one narrow runtime seam.
2. Avoid plan sprawl.
3. Avoid deferred-scope escape hatches.
4. Run exact commands and gates.
5. Report PASS, PARTIAL, FAIL, or BLOCKED with evidence.

## Historical material

Historical migrated plans are retained under:

- `.cursor/plans/_archive/**`
- `.cursor/_zero_loss_originals/**`
- `.cursor/windsurf_compat/**`

They are reference-only. They are not active execution instructions.

## Validation

Run from the repo root after unzipping:

```bash
python .cursor/scripts/check_cursor_optimized_config.py --strict
python .cursor/scripts/check_cursor_native_config.py --strict
python -m json.tool .cursor/mcp.json
python -m json.tool .cursor/hooks.json
```
