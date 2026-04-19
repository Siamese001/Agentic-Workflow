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

### Layer 1 — Zero-drift on-machine (preferred)

**Symlink** `~/.codeium/windsurf/mcp_config.json` → `.windsurf/mcp_config.json`. When set up, the repo SSOT and the Windsurf-read path are the same file on disk — edit once, no sync step required, drift structurally impossible.

One-time contributor setup (Windows — requires Developer Mode or admin):

```
pwsh -File tools/setup/setup_symlinks.ps1
```

POSIX (macOS / Linux / WSL):

```
bash tools/setup/setup_symlinks.sh
```

When the symlink is in place, `.windsurf/scripts/post_write_mcp_config_sync.py` detects same-inode and prints "No-op: repo SSOT and global config are the same file (symlink in place)." The hook stays installed as a safety net for contributors who skip the symlink step.

### Layer 2 — Copy-based sync (fallback)

Contributors who cannot create symlinks rely on the post-write hook to copy `.windsurf/mcp_config.json` → `~/.codeium/windsurf/mcp_config.json` on every save. This is fully backward compatible but NOT zero-drift: the two files can diverge between save and sync.

### Layer 3 — PR-blocking CI gates (guaranteed)

Runs on every pull request regardless of whether a contributor symlinked or not. Located in `.github/workflows/config-sync-gates.yml`:

| Gate | Source | Detects |
|------|--------|---------|
| **T6b** `check_mcp_sync_integrity.py` | `mcp_config.json` ↔ AGENTS.md MCP Quick Reference section | Content drift |
| **T6c** `check_agents_mcp_coverage.py` | `mcpServers` keys vs AGENTS.md rows | Missing rows |
| **T6d** `check_agents_md_sync.py` | AGENTS.md autogen markers (MCP-QUICK-REFERENCE, NOTION-MAP) vs generator output | Block-level drift |
| **T6e** `check_exclusion_sync.py` | `config/excluded_paths.yaml` ↔ `.pre-commit-config.yaml` + `.gitignore` | Exclusion drift |
| **T6**  `_validate_pytest_config.py --strict` | `pytest.ini` ↔ `pyproject.toml` | Pytest config split |

### Layer 4 — Legacy linting (complementary)

- `post_write_audit.py` — lints writes, logs to `artifacts/windsurf/mcp_lint_audit.jsonl`
- `validate_mcp_config.py` — schema check (if present)
- `check_mcp_config_sovereignty.py` — scope check (if present)

---

## Change Procedure

With the symlink (recommended):

```
1. Edit .windsurf/mcp_config.json
2. python .windsurf/scripts/sync_mcp_config.py   # regenerates AGENTS.md autogen blocks
3. Commit both files
4. Restart Windsurf
```

Without the symlink (fallback):

```
1. Edit .windsurf/mcp_config.json
2. Save — post_write_mcp_config_sync.py copies to ~/.codeium/windsurf/ + refreshes AGENTS.md
3. Commit
4. Restart Windsurf
```

---

## Rollback Procedure

If a bad MCP config is deployed:

```
1. git log .windsurf/mcp_config.json   -- find last good commit
2. git checkout <good-sha> -- .windsurf/mcp_config.json
3. python .windsurf/scripts/sync_mcp_config.py   -- regenerates AGENTS.md + syncs global (no-op if symlinked)
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
