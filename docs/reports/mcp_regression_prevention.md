# MCP Config & Operating Model — Regression Prevention

**Date:** 2026-04-07
**Status:** ACTIVE
**Scope:** All 14 MCP servers and supporting toolchain

---

## Historical Regression Inventory

The following regressions have been observed across prior sessions, RCA reports, and the current hardening effort.

### R1. Config Drift — YAML SSOT ≠ Global JSON
**Frequency:** Recurring (at least 2 incidents)
**Impact:** MCP servers fail with "transport closed"; blocked T2/T3 analysis
**Root Cause:** YAML SSOT edited but `sync_yaml_to_global.py` not run afterward
**Evidence:** `RCA_ADP_MCP_SERVER_UNAVAILABLE_20260406.md`
**Current Prevention:** `--check` mode for drift detection, workflow `/mcp-config-sync`
**Gap:** No automated CI gate catches drift before it causes runtime failure

### R2. Non-existent npm/PyPI Packages in Config
**Frequency:** 4 instances found in single audit
**Impact:** Servers fail to start — red in Windsurf, no diagnostics
**Packages affected:**
- `@modelcontextprotocol/server-fetch` → doesn't exist (fixed: `uvx mcp-server-fetch`)
- `@modelcontextprotocol/server-task-manager` → doesn't exist (fixed: `@blizzy/mcp-task-manager`)
- `@modelcontextprotocol/server-memory` → wrong choice (fixed: custom SQLite `adg_memory_server.py`)
- `@modelcontextprotocol/server-redis` → STRING-only (fixed: custom Python `redis_mcp_server.py`)
**Current Prevention:** Package versions pinned in YAML; health check validates startup
**Gap:** No automated `npm view` / `pip index versions` validation in CI

### R3. `npx` vs `npx.cmd` on Windows
**Frequency:** Affected all 6 npx-based servers simultaneously
**Impact:** Silent hang — Windsurf shows spinner forever, no error
**Root Cause:** Bare `npx` on Windows causes `FileNotFoundError`, Windsurf swallows the error
**Evidence:** `mcp-failure-rca.md` Step 6A, Known Failure Registry
**Current Prevention:** Windsurf now resolves `npx` correctly; all commands use `npx` (not `npx.cmd`)
**Gap:** If Windsurf behavior changes, all npx servers break simultaneously

### R4. Hardcoded Paths in JSON Config
**Frequency:** Every manual edit to global config introduced hardcoded `C:\\Git\\Agentic-Workflow` paths
**Impact:** Config not portable, breaks on machine change
**Current Prevention:** Sync script expands `${REPO_ROOT}` from YAML `repo_root` field
**Gap:** Direct edits to global JSON bypass SSOT and re-introduce hardcoding

### R5. Multiple Conversion Scripts, None Correct
**Frequency:** 3 competing scripts existed simultaneously
**Impact:** Confusion about which script to use; some wrote to deprecated targets
**Scripts:** `expand_mcp_config.py`, `yaml_to_json_config.py`, `sync_yaml_to_global.py`
**Current Prevention:** Single canonical script: `tools/adg/sync_yaml_to_global.py` (standalone, no MCPLoader)
**Gap:** Deprecated scripts still exist in repo (marked deprecated in rules, not yet deleted)

### R6. MCPLoader / agentic_core Dependency
**Frequency:** Broke whenever agentic_core was refactored
**Impact:** Config sync script fails, can't regenerate global config
**Current Prevention:** Sync script is now standalone (only needs PyYAML, no agentic_core imports)
**Gap:** `validate_mcp_yaml.py` still depends on MCPLoader

### R7. API Key Leakage into Generated Config
**Frequency:** 1 instance caught during this hardening session
**Impact:** Secrets written in plaintext to `~/.codeium/windsurf/mcp_config.json`
**Root Cause:** `.env` values loaded into expansion table alongside build-time vars
**Current Prevention:** Sync script only expands build-time vars (REPO_ROOT, GITKRAKEN_EXE); API keys like `${BRAVE_API_KEY}` pass through as placeholders
**Gap:** No automated check that generated config doesn't contain resolved secrets

### R8. Dead/Ghost Servers in Config
**Frequency:** 3 dead servers found in single audit
**Servers:** `postgres_memory` (no DB), `browser/puppeteer` (superseded by playwright), `sequential_thinking` (removed)
**Impact:** Wasted resources, confusion, config bloat
**Current Prevention:** Removed from YAML; health check would catch non-functional servers
**Gap:** No lifecycle management — servers are added but never retired

### R9. Environment Variable Handling Inconsistency
**Frequency:** Affected health check, sync script, and runtime simultaneously
**Impact:** Health check falsely reports failures; sync drops env vars
**Patterns:** `${VAR}`, `${VAR:-default}`, literal values — each handled differently
**Current Prevention:** Health check handles placeholders; sync preserves all env vars
**Gap:** No schema validation for env var syntax in YAML

### R10. SQLite File Lock Conflicts
**Frequency:** Recurring during ADG regeneration
**Impact:** ADG regeneration blocked; requires manual connection close
**Evidence:** `RCA_SQLITE_FILE_LOCK_ARCHIVE_CLEANUP_20260406.md`
**Current Prevention:** `mcp1_adg_close_connections` tool; workflow step before regen
**Gap:** No automatic lock release before ADG generation

### R11. Stale `.pyc` Bytecode After Code Changes
**Frequency:** Multiple incidents documented in Known Failure Registry
**Impact:** MCP server loads old bytecode, fails with AttributeError or stale behavior
**Current Prevention:** Manual `__pycache__` cleanup in RCA workflow
**Gap:** No automatic bytecode invalidation

---

## Prevention Recommendations

### Gate 1: Pre-commit Drift Check (HIGH — eliminates R1)

Add to pre-commit hooks:
```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: mcp-config-drift
      name: MCP config drift check
      entry: python tools/adg/sync_yaml_to_global.py --check
      language: python
      files: config/mcp_servers\.yaml
      pass_filenames: false
```

**What it does:** Blocks commit if YAML SSOT was edited but global config wasn't synced.
**Prevents:** R1 (config drift)

### Gate 2: Package Existence Validation (HIGH — eliminates R2)

Add a CI step or pre-commit hook that validates npm packages exist:
```python
# ops_scripts/ci/validate_mcp_packages.py
# For each npx-based server in YAML:
#   npm view <package> version → must return a version, not 404
# For each uvx-based server:
#   pip index versions <package> → must return versions
```

**What it does:** Catches phantom packages before they reach the config.
**Prevents:** R2 (non-existent packages)

### Gate 3: Secret Leak Scanner (MEDIUM — eliminates R7)

Add post-sync validation:
```python
# After sync, scan generated JSON for known secret patterns:
# - API keys (length > 20, alphanumeric)
# - Tokens matching known prefixes (ghp_, sk-, etc.)
# - Values that were in .env but shouldn't be in JSON
```

**What it does:** Catches API keys accidentally expanded into generated config.
**Prevents:** R7 (API key leakage)

### Gate 4: Health Check in CI (HIGH — eliminates R2, R3, R8, R9)

Already built: `ops_scripts/ci/mcp_health_check.py`. Add to CI pipeline:
```yaml
# Run after any change to config/ or tools/mcp/ or tools/adg/mcp/
- name: MCP Health Check
  run: python ops_scripts/ci/mcp_health_check.py
```

**What it does:** Validates all 14 servers can start and respond.
**Prevents:** R2, R3, R8, R9 (broken servers, dead servers, env var issues)

### Gate 5: Single Script Enforcement (MEDIUM — eliminates R5)

Delete deprecated scripts or move to `tools/archive/`:
- `tools/mcp/expand_mcp_config.py`
- `tools/mcp/yaml_to_json_config.py`

**What it does:** Eliminates confusion about which script to use.
**Prevents:** R5 (multiple competing scripts)

### Gate 6: Standalone validate_mcp_yaml.py (LOW — eliminates R6)

Rewrite `validate_mcp_yaml.py` to use `yaml.safe_load` directly instead of MCPLoader, matching the sync script pattern.

**What it does:** Removes last MCPLoader dependency from config toolchain.
**Prevents:** R6 (agentic_core breakage cascading to config tools)

### Gate 7: Auto-Sync on Commit (MEDIUM — strengthens R1 prevention)

Add post-commit hook that auto-syncs when `config/mcp_servers.yaml` changes:
```bash
# .git/hooks/post-commit
changed=$(git diff-tree --no-commit-id --name-only -r HEAD | grep "config/mcp_servers.yaml")
if [ -n "$changed" ]; then
    python tools/adg/sync_yaml_to_global.py
fi
```

**What it does:** Eliminates the manual sync step entirely.
**Prevents:** R1 (forgetting to sync)

### Gate 8: Bytecode Cleanup Before MCP Restart (LOW — eliminates R11)

Add to health check and RCA workflow:
```python
# Before probing any Python-based MCP server, clear its __pycache__
for cache_dir in ["tools/adg/core/__pycache__", "tools/mcp/__pycache__", "tools/memory/__pycache__"]:
    shutil.rmtree(cache_dir, ignore_errors=True)
```

**What it does:** Prevents stale bytecode from masking fixes.
**Prevents:** R11 (stale `.pyc` failures)

---

## Priority Matrix

| Gate | Eliminates | Effort | Impact | Priority |
|------|-----------|--------|--------|----------|
| 1. Pre-commit drift check | R1 | 30min | HIGH | **P0** |
| 4. Health check in CI | R2,R3,R8,R9 | 1hr | HIGH | **P0** |
| 2. Package existence check | R2 | 2hr | HIGH | **P1** |
| 5. Delete deprecated scripts | R5 | 15min | MEDIUM | **P1** |
| 7. Auto-sync on commit | R1 | 30min | MEDIUM | **P1** |
| 3. Secret leak scanner | R7 | 1hr | MEDIUM | **P2** |
| 6. Standalone validator | R6 | 1hr | LOW | **P2** |
| 8. Bytecode cleanup | R11 | 30min | LOW | **P2** |

---

## Operating Model Summary

```
Edit YAML SSOT ─→ Pre-commit validates ─→ Sync auto-runs ─→ Health check passes ─→ Commit
                         │                       │                    │
                    drift check              backup created     14/14 healthy
                    packages exist           API keys preserved  no dead servers
```

**Single command to verify everything:**
```bash
python tools/adg/sync_yaml_to_global.py --check && python ops_scripts/ci/mcp_health_check.py
```

---

## References

- YAML SSOT: `config/mcp_servers.yaml`
- Sync script: `tools/adg/sync_yaml_to_global.py`
- Health check: `ops_scripts/ci/mcp_health_check.py`
- SSOT rule: `.windsurf/rules/mcp-config-ssot.md`
- Sync workflow: `.windsurf/workflows/mcp-config-sync.md`
- Failure RCA workflow: `.windsurf/workflows/mcp-failure-rca.md`
- Prior RCA: `docs/reports/rcas/RCA_ADP_MCP_SERVER_UNAVAILABLE_20260406.md`
- SSOT conflicts: `docs/reports/ssot_conflicts_analysis.md`
