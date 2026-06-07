# Cursor-native zero-loss overwrite status

Generated: `2026-05-15T08:10:44Z`

## Result

This package converts the uploaded `.cursor` export into a Cursor-native operating folder while preserving all original material.

## Active Cursor surfaces

- `.cursor/rules/*.mdc`
- `.cursor/skills/**/SKILL.md`
- `.cursor/agents/*.md`
- `.cursor/hooks.json`
- `.cursor/hooks/**`
- `.cursor/mcp.json`
- `.cursor/scripts/check_cursor_native_config.py`

## Preserved legacy/archive material

- `.cursor/cursor_compat/**`
- `.cursor/scripts/_legacy_cursor/**`
- `.cursor/plans/_archive/**`
- `.cursor/_zero_loss_originals/**`

## Validate

```bash
python .cursor/scripts/check_cursor_native_config.py --strict
python -m json.tool .cursor/mcp.json
python -m json.tool .cursor/hooks.json
```
