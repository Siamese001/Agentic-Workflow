# Cursor-native agentic project controls

This folder is the Cursor-native operating surface for the Agentic AI project. It preserves the uploaded legacy material without making it active.

## Active Cursor entry points

- `.cursor/rules/*.mdc` — Cursor project rules. Keep always-on rules small and high-signal.
- `.cursor/skills/**/SKILL.md` — Cursor Agent Skills for reusable task procedures.
- `.cursor/agents/*.md` — specialized Cursor subagents for bounded audits and verification tasks.
- `.cursor/hooks.json` and `.cursor/hooks/**` — Cursor hook wrappers for deterministic guardrails.
- `.cursor/mcp.json` — project-scoped Cursor MCP configuration.
- `.cursor/scripts/check_cursor_native_config.py` — strict validation for active Cursor surfaces.

## Archive and compatibility boundaries

- `.cursor/cursor_compat/**` is retained for migration reference only.
- `.cursor/scripts/_legacy_cursor/**` contains legacy hook scripts that were not activated as Cursor hooks.
- `.cursor/plans/_archive/**` preserves converted historical plans.
- `.cursor/_zero_loss_originals/**` contains the uploaded source archive and original migrated reference files.

Archived material is not active Cursor automation unless explicitly promoted into a rule, skill, agent, command, hook, or script.

## Validation

Run this from the repository root after unzipping:

```bash
python .cursor/scripts/check_cursor_native_config.py --strict
python -m json.tool .cursor/mcp.json
python -m json.tool .cursor/hooks.json
```
