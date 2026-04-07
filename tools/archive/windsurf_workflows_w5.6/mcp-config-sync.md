---
description: Sync MCP config from YAML SSOT to global path after any config edit
---

# MCP YAML Sync Workflow

Invoke with `/mcp-yaml-sync`. Run after any edit to `config/mcp_servers.yaml`.

---

## STEP 1: Validate YAML SSOT

// turbo
```
python ops_scripts/ci/validate_mcp_yaml.py
```

- Exit 0 → YAML is valid, continue to STEP 2
- Exit 1 → validation failed, fix errors before syncing

---

## STEP 2: Sync YAML → global JSON

```
python tools/adg/sync_yaml_to_global.py
```

The script:
1. Reads `config/mcp_servers.yaml`
2. Validates the YAML structure and tool mappings
3. Converts to Windsurf's JSON format
4. Backs up the current global config (timestamped)
5. Writes to global config path
6. Verifies round-trip integrity

---

## STEP 3: Health check all servers

// turbo
```
python ops_scripts/ci/mcp_health_check.py
```

- Exit 0 → all 14 servers healthy
- Exit 1 → failures detected, investigate output

---

## STEP 4: Restart Windsurf

MCP servers only reload on IDE restart. After sync, restart Windsurf to pick up the new config.

---

## STEP 5: Verify MCP servers respond

Call any MCP tool to confirm servers are live:
- `mcp9_mem_get_stats` — verifies memory server
- `mcp1_adg_status` — verifies ADG SQLite server
- `mcp12_redis_health` — verifies Redis server

---

## References

- YAML SSOT: `config/mcp_servers.yaml`
- Sync script: `tools/adg/sync_yaml_to_global.py`
- Health check: `ops_scripts/ci/mcp_health_check.py`
- Validation script: `ops_scripts/ci/validate_mcp_yaml.py`
- Rule: `.windsurf/rules/mcp-config-ssot.md`
