# ADR-020: Single MCP Config Sync Script (YAML → Global JSON)

**Status**: ACCEPTED  
**Date**: 2026-04-07  
**Phase**: Wave 2 Phase 2.7 — MCP Config Simplification  
**Deciders**: SVP Engineering (Codex)

---

## Context

Three scripts existed for converting `config/mcp_servers.yaml` to the legacy editor global
`mcp_config.json` format:

| Script | Location | Status |
|--------|----------|--------|
| `sync_yaml_to_global.py` | `tools/adg/` | **CANONICAL** — active, used by post-commit hook |
| `expand_mcp_config.py` | `tools/mcp/` | DEPRECATED — older implementation, no callers |
| `yaml_to_json_config.py` | `tools/mcp/` | DEPRECATED — partial reimplementation, no callers |

Having three scripts for the same job creates confusion about which is authoritative,
increases maintenance burden, and risks drift between implementations.

---

## Decision

**Keep `tools/adg/sync_yaml_to_global.py` as the single canonical sync script.**

Archive `expand_mcp_config.py` and `yaml_to_json_config.py` to `tools/archive/windsurf/`.

---

## Rationale

- `sync_yaml_to_global.py` is already wired into the post-commit hook and CI
- It handles `${REPO_ROOT}` expansion, backup, drift-check (`--check`), and dry-run (`--dry-run`)
- The two archived scripts have zero active callers (confirmed via ADG edge_fanin)
- SVP priority: **operational simplicity** — reduce moving parts

---

## Consequences

- **Positive**: One script to maintain, document, and trust
- **Positive**: `mcp-config-ssot.md` references are now accurate
- **Negative**: None — archived scripts are preserved for historical reference
- **Migration**: `tools/mcp/expand_mcp_config.py` → `tools/archive/windsurf/`
- **Migration**: `tools/mcp/yaml_to_json_config.py` → `tools/archive/windsurf/`

---

## Enforcement

- `.codex/rules/mcp-config-ssot.md` — references only `sync_yaml_to_global.py`
- `docs/guides/MCP_Registry.md` — documents the sync workflow
- Post-commit hook: `python tools/adg/sync_yaml_to_global.py` (triggered on `config/mcp_servers.yaml` commits)
