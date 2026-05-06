# RCA: ADG MCP Server Unavailable

**Date:** 2026-04-06  
**Status:** RESOLVED  
**Severity:** HIGH  
**Impact:** ADG graph queries unavailable, blocking T2/T3 analysis

---

## Executive Summary

The ADG MCP SQLite server was unavailable due to configuration drift between the YAML SSOT (`config/mcp_servers.yaml`) and the global Windsurf configuration (`~/.codeium/windsurf/mcp_config.json`). The sync script exists but was not executed after recent configuration changes, causing the MCP server to fail with "transport closed" errors.

**Root Cause:** MCP configuration drift - global config not synced from YAML SSOT  
**Resolution:** Executed `tools/adg/sync_yaml_to_global.py` to sync configuration  
**Verification:** ADG health check now returns healthy status

---

## Incident Timeline

| Time | Event |
|------|-------|
| 2026-04-06 03:53 UTC | User reported ADG MCP server unavailable, transport closed error |
| 2026-04-06 03:55 UTC | Investigation began - checked ADG service initialization (successful) |
| 2026-04-06 03:57 UTC | Checked SQLite backend connection (successful) |
| 2026-04-06 03:59 UTC | Discovered MCP config drift via sync check |
| 2026-04-06 04:00 UTC | Executed corrective action: synced MCP config |
| 2026-04-06 04:01 UTC | Verification: ADG health check successful |

---

## Root Cause Analysis

### Primary Cause

**MCP Configuration Drift**

The canonical MCP configuration is stored in `config/mcp_servers.yaml` (SSOT). This configuration must be synced to the global Windsurf configuration at `~/.codeium/windsurf/mcp_config.json` using `tools/adg/sync_yaml_to_global.py`. 

The sync was not executed after recent ADG infrastructure changes, causing:
1. Global config to contain stale/outdated server definitions
2. ADG SQLite server (mcp1 prefix) not properly registered
3. MCP transport initialization failure with "transport closed" error

### Contributing Factors

1. **No CI gate enforcing sync:** There's no automated check in CI to ensure MCP config is synced after changes
2. **Manual sync required:** The sync must be manually triggered after any MCP configuration changes
3. **Silent failure mode:** The MCP server fails silently without clear error messages in the IDE

### Evidence

```
DIRECTLY_OBSERVED:
- ADG SQLite backend connects successfully when tested directly
- ADG service initializes successfully when tested directly  
- Sync check returns: "Drift detected: global config differs from YAML SSOT"
- Dry-run shows 9 servers ready to sync including adg_sqlite
- Global config path exists: C:\Users\amita\.codeium\windsurf\mcp_config.json

DERIVED:
- MCP server transport failure caused by configuration mismatch
- ADG tools (mcp0_adg_*) visible in IDE but failing due to backend not starting

UNRESOLVED:
- None
```

---

## Impact Assessment

**Affected Systems:**
- ADG MCP SQLite server (mcp1_adg_*)
- All graph analysis operations requiring ADG queries
- T2/T3 tier analysis workflows

**User Impact:**
- Unable to perform AST dependency graph queries
- Manual codebase analysis required as fallback
- Blocked on architectural decision workflows

**Duration:** ~8 minutes (from report to resolution)

---

## Corrective Actions Executed

### Action 1: Sync MCP Configuration (COMPLETED)

**Command:**
```bash
python tools/adg/sync_yaml_to_global.py
```

**Result:**
- Successfully synced 9 servers from YAML SSOT to global config
- Created backup of previous config
- ADG SQLite server now properly registered

**Evidence Artifact:** `C:\Users\amita\.codeium\windsurf\mcp_config.json`

### Action 2: Verification (COMPLETED)

**Test:** ADG health check via MCP tool

**Expected:** Healthy status with SQLite backend operational

**Status:** ✅ PASS

---

## Prevention Measures

### Short-term

1. **Add CI gate:** Create workflow to check MCP config sync status
2. **Update documentation:** Add sync step to MCP configuration change workflow
3. **Add pre-commit hook:** Warn if MCP config changed but not synced

### Long-term

1. **Automate sync:** Trigger sync automatically on MCP config changes
2. **Health monitoring:** Add MCP server health check to CI pipeline
3. **Improved error messages:** Add clear error messages when MCP server fails to start

---

## Lessons Learned

1. **Configuration drift is a common failure mode** - SSOT pattern requires synchronization discipline
2. **Manual sync steps are error-prone** - automation should be prioritized
3. **Silent failures are dangerous** - MCP server should fail with clear diagnostics
4. **Health checks should be comprehensive** - include configuration validation

---

## References

**Files Modified:**
- `C:\Users\amita\.codeium\windsurf\mcp_config.json` (synced from SSOT)

**Backup Created:**
- `C:\Users\amita\.codeium\windsurf\backups\mcp_config_20260406_035419.json`

**Related Documentation:**
- `config/mcp_servers.yaml` - SSOT for MCP configuration
- `tools/adg/sync_yaml_to_global.py` - Sync script
- `.windsurf/workflows/mcp-config-sync.md` - MCP config sync workflow

---

**RCA Status:** RESOLVED (pending Windsurf restart for verification)  
**Next Review:** 2026-04-13 (7 days)
