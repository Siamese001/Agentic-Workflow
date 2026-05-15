# Cursor-native Agentic AI controls

This folder is the active Cursor operating surface for the Agentic AI project.

## Active always-on rules

Only three rules are always-on after the optimization pass:

- `.cursor/rules/000-agentic-core-operating-contract.mdc`
- `.cursor/rules/001-cursor-runtime-seam-execution.mdc`
- `.cursor/rules/002-pass-blocked-proof-contract.mdc`

Everything else is task-scoped reference material, a skill, an agent, a hook, a script, a schema, or archived history.

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
