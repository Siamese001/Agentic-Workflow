# MCP Config Version Check Policy

**Status**: ACTIVE  
**Phase**: Wave 2 Phase 2.5 + H1 (2026-05-19)  
**Enforcement**: CI gates + pre-commit (T6e2, T11) + editor sync hooks  
**SSOT**: `.mcp.json` (legacy editor project) · `.mcp.json` (legacy editor mirror)

---

## Policy Statement

Every change to MCP server configuration MUST be validated before the configuration is loaded by an editor. Unvalidated config changes can silently break all MCP tool calls for the session.

**legacy editor-first workflow:** edit `.mcp.json`, run sync, commit. Keep `.mcp.json` aligned for legacy editor contributors (parity gate enforces canonical fleet).

---

## Required Fields

Each entry under `mcpServers` in **both** editor configs MUST include:

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
- `args` — argument list (may be empty array for remote-only servers)
- `disabled` — explicit boolean when present (default effective: enabled)

Filesystem server (Rule #0): `args` must be exactly `[<editor-launcher>, "${env:AGENTIC_REPO_ROOT}"]`.

---

## Validation Rules

| Check | Severity | Gate |
|-------|----------|------|
| Neither `command` nor `url` present | CRITICAL | `check_mcp_config_schema.py` |
| API key as literal string (not `${env:VAR}`) | CRITICAL | schema + review |
| Invalid JSON syntax | CRITICAL | `json.tool` / schema |
| `mcpServers` key missing | CRITICAL | schema |
| Filesystem scope regression (Rule #0) | CRITICAL | **`check_mcp_config_sovereignty.py` (T11)** |
| Editor fleet drift | CRITICAL | `check_mcp_editor_parity.py` |
| AGENTS.md MCP table drift | CRITICAL | `check_mcp_sync_integrity.py` |
| Server count decreased by >2 | WARNING | manual review |

---

## Enforcement Points

### Layer 1 — legacy editor project SSOT (primary)

| Path | Role |
|------|------|
| `.mcp.json` | **Edit here** for Codex |
| `python .cursor/scripts/sync_mcp_config.py` | Refreshes AGENTS.md autogen blocks + global `~/.cursor/cursor/mcp.json` |
| `ops_scripts/ci/check_mcp_config_sovereignty.py` | Rule #0 scope (both editor configs) |

### Layer 2 — legacy editor mirror + global sync

**Symlink (preferred):** `~/.codeium/windsurf/mcp_config.json` → `.mcp.json`

**Fallback:** `post_write_mcp_config_sync.py` copies repo → global on save.

POSIX / Windows setup: `tools/setup/setup_symlinks.sh` · `tools/setup/setup_symlinks.ps1`

### Layer 3 — PR-blocking CI gates

| Gate | Source | Detects |
|------|--------|---------|
| **T6b** | `check_mcp_sync_integrity.py` | `.mcp.json` ↔ AGENTS.md MCP Quick Reference |
| **T6c** | `check_agents_mcp_coverage.py` | Server keys vs AGENTS rows |
| **T6d** | `check_agents_md_sync.py` | Autogen block drift |
| **T6e2** | `check_mcp_config_schema.py --profile all` | Schema / §27 keys |
| **T6e2c** | `check_mcp_editor_parity.py` | legacy editor vs legacy editor fleet |
| **T11** | **`check_mcp_config_sovereignty.py`** | **Rule #0 filesystem scope** |
| **T6e** | `check_exclusion_sync.py` | Exclusion drift |
| **T6** | `_validate_pytest_config.py --strict` | Pytest config split |

Contract runner: `python ops_scripts/ci/run_contract_gates.py` (includes MCP-SCOPE0).

### Layer 4 — Complementary linting

- `post_write_audit.py` — legacy editor MCP lint log (`artifacts/windsurf/mcp_lint_audit.jsonl`)
- `validate_mcp_config.py` — optional schema helper (if present)

---

## Change Procedure (legacy editor-first)

```
1. Edit .mcp.json
2. Align .mcp.json (editor-specific deltas only: GitKraken host, Playwright id, launcher path)
3. python .cursor/scripts/sync_mcp_config.py
4. python ops_scripts/ci/check_mcp_config_sovereignty.py
5. python ops_scripts/ci/check_mcp_editor_parity.py
6. Commit .mcp.json, .mcp.json, AGENTS.md (if autogen changed)
7. Restart legacy editor (and legacy editor if mirror edited)
```

legacy editor-only contributors may edit `.mcp.json` first, then port the same server entries to `.mcp.json` before merge.

---

## Rollback Procedure

```
1. git log .mcp.json .mcp.json
2. git checkout <good-sha> -- .mcp.json .mcp.json
3. python .cursor/scripts/sync_mcp_config.py
4. python ops_scripts/ci/check_mcp_config_sovereignty.py
5. Restart editors
```

Audit trail: `artifacts/windsurf/mcp_lint_audit.jsonl` (legacy editor writes).

---

## References

- Filesystem operator guide: `docs/guides/filesystem_mcp_operations.md`
- MCP config SSOT rule: `.claude/rules/mcp-config-ssot.mdc`
- H0 receipt: `docs/reports/cursor/mcp_scope0_h0_receipt.md`
- Archive (YAML infra — do not restore): `tools/archive/mcp_yaml_infra_w5.2/`
