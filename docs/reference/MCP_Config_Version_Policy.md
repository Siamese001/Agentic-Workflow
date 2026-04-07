# MCP Config Version Check Policy

**Status**: ACTIVE  
**Phase**: Wave 2 Phase 2.5  
**Enforcement**: CI gate + post_write_code hook (Wave 1 Phase 1.5)  
**SSOT**: `global_rules.md` §MCP Authority: One SSOT Per Capability

---

## Policy Statement

Every change to MCP server configuration MUST be validated against a schema before
the configuration is deployed to Windsurf. Unvalidated config changes can silently
break all MCP tool calls for the session.

---

## Version Fields

Each MCP server entry in `config/mcp_servers.yaml` MUST include:

```yaml
servers:
  adg_sqlite:
    version: "1.0"          # semantic version of this config entry
    last_validated: "2026-04-07"   # ISO date of last successful validation
    transport: stdio        # stdio | sse | url
    command: python
    args: [...]
    env: {}
```

Required fields:
- `version` — semantic version string (MAJOR.MINOR)
- `transport` — must be one of: `stdio`, `sse`, `url`
- `command` — executable path or name
- `args` — argument list (may be empty)

---

## Validation Rules

| Check | Severity | Action |
|-------|----------|--------|
| Missing `transport` field | CRITICAL | Block deploy |
| Unknown `transport` value | CRITICAL | Block deploy |
| Missing `command` field | CRITICAL | Block deploy |
| API key as literal string (not `${VAR}`) | CRITICAL | Block deploy |
| `version` field missing | WARNING | Log, allow |
| Server count decreased by >2 | WARNING | Log, require confirmation |

---

## Enforcement Points

1. **Post-write audit** (`post_write_audit.py`): Lints `mcp_config.json` writes for schema issues, logs to `artifacts/windsurf/mcp_lint_audit.jsonl`
2. **CI validation**: `python ops_scripts/ci/validate_mcp_yaml.py` — runs on every change to `config/mcp_servers.yaml`
3. **Pre-commit**: `mcp-config-sync` hook validates before commit

---

## Change Procedure

When modifying MCP server configuration:

```
1. Edit config/mcp_servers.yaml  (SSOT — never edit global JSON directly)
2. Run: python ops_scripts/ci/validate_mcp_yaml.py
3. If valid: python tools/adg/sync_yaml_to_global.py
4. Commit both yaml + any generated changes
5. Restart Windsurf to pick up new config
```

---

## Rollback Procedure

If a bad MCP config is deployed:

```
1. git log config/mcp_servers.yaml   -- find last good commit
2. git checkout <good-sha> -- config/mcp_servers.yaml
3. python tools/adg/sync_yaml_to_global.py
4. Restart Windsurf
```

The `post_write_audit.py` hook maintains `artifacts/windsurf/mcp_lint_audit.jsonl`
with timestamped records of every config write — use this to trace when drift occurred.

---

## References

- MCP Registry: `docs/reference/MCP_Registry.md`
- YAML SSOT rule: `.windsurf/rules/mcp-config-ssot.md`
- Sync workflow: `.windsurf/workflows/mcp-config-sync.md`
- Audit log: `artifacts/windsurf/mcp_lint_audit.jsonl`
