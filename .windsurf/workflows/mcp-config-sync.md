---
description: Sync MCP config from workspace SSOT to global path after any config edit
---

# MCP Config Sync Workflow

Invoke with `/mcp-config-sync`. Run after any edit to `.windsurf/mcp_config.json`.

---

## STEP 1: Validate SSOT has no issues

// turbo
```
python tools/adg/sync_global_config.py --check
```

- Exit 0 → configs already synced, done
- Exit 1 → drift detected, continue to STEP 2

---

## STEP 2: Sync workspace → global

```
python tools/adg/sync_global_config.py
```

The script:
1. Validates the SSOT for missing `cwd` on Python servers
2. Backs up the current global config (timestamped)
3. Overwrites global from workspace
4. Verifies round-trip (0 diffs)

---

## STEP 3: Restart Windsurf

MCP servers only reload on IDE restart. After sync, restart Windsurf to pick up the new config.

---

## STEP 4: Verify MCP servers respond

Call any MCP tool to confirm servers are live:
- `mem_get_stats` — verifies memory server

---

## References

- SSOT: `.windsurf/mcp_config.json`
- Sync script: `tools/adg/sync_global_config.py`
- Rule: `.windsurf/rules/mcp-config-ssot.md`
