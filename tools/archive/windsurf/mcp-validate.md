---
description: Validate MCP configuration standards
---

# MCP Validation Workflow

Run this workflow to validate MCP server configurations against hardened standards.

## Quick Commands

```bash
# Validate all MCP configs
python ops_scripts/ci/validate_mcp_config.py

# Check if global config is synced
python tools/adg/sync_yaml_to_global.py --check

# Sync YAML to global config
python tools/adg/sync_yaml_to_global.py
```

## Standards Checklist

Python MCPs must use:
- ✅ Absolute Python path (not just `python`)
- ✅ `-c exec()` pattern with `sys.path.insert()`
- ✅ `__file__` definition before exec
- ✅ `encoding='utf-8'` in open()
- ✅ Absolute paths to scripts

NPM MCPs must have:
- ✅ Verified package exists (`npm view <package>`)
- ✅ No 404 packages

## Troubleshooting

**Red MCP in Windsurf:**
1. Check config: `python ops_scripts/ci/validate_mcp_config.py`
2. Verify sync: `python tools/adg/sync_yaml_to_global.py --check`
3. Restart Windsurf

**Module not found:**
- Ensure `sys.path.insert(0, repo_root)` in exec string

**Unicode errors:**
- Ensure `encoding='utf-8'` in open()

**__file__ error:**
- Ensure `__file__ = path` before exec
