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

## Required Fields

Each entry in `.windsurf/mcp_config.json` under `mcpServers` MUST include:

```json
{
  "mcpServers": {
    "adg_sqlite": {
      "command": "python",
      "args": ["..."],
      "disabled": false
    }
  }
}
```

Required fields:
- `command` OR `url` — at least one must be present
- `args` — argument list (may be empty array)
- `disabled` — explicit boolean (default `false`)

---

## Validation Rules

| Check | Severity | Action |
|-------|----------|--------|
| Neither `command` nor `url` present | CRITICAL | Block deploy |
| API key as literal string (not `${env:VAR}`) | CRITICAL | Block deploy |
| Invalid JSON syntax | CRITICAL | Block deploy |
| `mcpServers` key missing | CRITICAL | Block deploy |
| Server count decreased by >2 | WARNING | Log, require confirmation |

---

## Enforcement Points

1. **Post-write audit** (`post_write_audit.py`): Lints `.windsurf/mcp_config.json` writes for schema issues, logs to `artifacts/windsurf/mcp_lint_audit.jsonl`
2. **CI validation**: `python ops_scripts/ci/validate_mcp_config.py` — runs on every change to `.windsurf/mcp_config.json`
3. **Sovereignty check**: `python ops_scripts/ci/check_mcp_config_sovereignty.py` — validates filesystem server is present and scoped to repo root

---

## Change Procedure

When modifying MCP server configuration:

```
1. Edit .windsurf/mcp_config.json  (SSOT — single file, mcpServers format)
2. Run: python ops_scripts/ci/validate_mcp_config.py
3. If valid: copy to global — python -c "import shutil,pathlib; shutil.copy('.windsurf/mcp_config.json', str(pathlib.Path.home()/'.codeium/windsurf/mcp_config.json'))"
4. Commit .windsurf/mcp_config.json
5. Restart Windsurf to pick up new config
```

---

## Rollback Procedure

If a bad MCP config is deployed:

```
1. git log .windsurf/mcp_config.json   -- find last good commit
2. git checkout <good-sha> -- .windsurf/mcp_config.json
3. Copy to global: python -c "import shutil,pathlib; shutil.copy('.windsurf/mcp_config.json', str(pathlib.Path.home()/'.codeium/windsurf/mcp_config.json'))"
4. Restart Windsurf
```

The `post_write_audit.py` hook maintains `artifacts/windsurf/mcp_lint_audit.jsonl`
with timestamped records of every config write — use this to trace when drift occurred.

---

## References

- MCP Registry: `docs/guides/MCP_Registry.md`
- SSOT rule: `.windsurf/rules/mcp-config-ssot.md`
- Audit log: `artifacts/windsurf/mcp_lint_audit.jsonl`
- Archive (YAML infra — do not restore): `tools/archive/mcp_yaml_infra_w5.2/`
