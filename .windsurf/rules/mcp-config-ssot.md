---
trigger:
  - file_change
  - pre_commit
---
# MCP Config SSOT Rule

## CI Integration

When `config/mcp_servers.yaml` changes:
1. Run validation: `python ops_scripts/ci/validate_mcp_yaml.py`
2. If validation passes, sync to global: `python tools/adg/sync_yaml_to_global.py`
3. CI gate enforces validation before merge

Pre-commit hook triggers validation on commit.

## Source of Truth Location

```
config/mcp_servers.yaml (workspace, version-controlled)
```

The YAML configuration file is the **SSOT** for all MCP server definitions and tool mappings. The global config at `C:\Users\amita\.codeium\windsurf\mcp_config.json` is a **read-only deployment target** that Windsurf reads at startup.

## Hard Constraints

- **NEVER** edit the global file directly — always edit `config/mcp_servers.yaml` first
- **AFTER** every edit to `config/mcp_servers.yaml`, run: `python tools/adg/sync_yaml_to_global.py`
- **ALL** Python MCP servers MUST have `cwd: "${REPO_ROOT}"` in the YAML
- **Drift check** (no writes): `python tools/adg/sync_yaml_to_global.py --check`
- **Health check**: `python ops_scripts/ci/mcp_health_check.py`
- **API keys** stay as `${VAR}` placeholders — Windsurf resolves them from its secrets store

## Why YAML SSOT

1. YAML supports comments and is human-readable
2. Tool mappings are explicit with descriptions
3. CI can validate schema before syncing
4. Sync script is standalone (only needs PyYAML, no MCPLoader)
5. Single file defines servers, tools, aliases, and validation rules

## Validation

```
python ops_scripts/ci/validate_mcp_yaml.py
```

Exit 0 = YAML is valid and complete, Exit 1 = validation failed.

## Sync to Global Config

```
python tools/adg/sync_yaml_to_global.py
```

This converts `config/mcp_servers.yaml` to Windsurf's JSON format and writes to the global config path.

## Enforcement Layers

| Layer | Mechanism |
|-------|-----------|
| Windsurf rule | `.windsurf/rules/mcp-config-ssot.md` (this file) |
| Workflow | `.windsurf/workflows/mcp-config-sync.md` (invoke with `/mcp-config-sync`) |
| Git hook | `.git/hooks/post-commit` — auto-syncs when `config/mcp_servers.yaml` is committed |
| Sync script | `tools/adg/sync_yaml_to_global.py` (validates, backs up, syncs, verifies) |
| Validation | `ops_scripts/ci/validate_mcp_yaml.py` (CI gate) |

## Deprecated Files (DO NOT EDIT)

| File | Status | Action |
|------|--------|--------|
| `.windsurf/mcp_config.json` | DEPRECATED | Read-only redirect notice |
| `mcp_config.json` (repo root) | DEPRECATED | Will be removed |
| `tools/adg/sync_global_config.py` | REMOVED | Use `sync_yaml_to_global.py` |
| `tools/mcp/expand_mcp_config.py` | DEPRECATED | Use `sync_yaml_to_global.py` |
| `tools/mcp/yaml_to_json_config.py` | DEPRECATED | Use `sync_yaml_to_global.py` |

## References

- YAML SSOT: `config/mcp_servers.yaml`
- Global target (read-only): `C:\Users\amita\.codeium\windsurf\mcp_config.json`
- Sync script: `tools/adg/sync_yaml_to_global.py`
- Validation script: `ops_scripts/ci/validate_mcp_yaml.py`
- Health check: `ops_scripts/ci/mcp_health_check.py`
