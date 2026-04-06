# SSOT Conflicts Analysis Report

**Generated:** 2026-04-06  
**Purpose:** Identify all multiple Single Source of Truth (SSOT) issues in the repository

## Executive Summary

This report identifies multiple SSOT conflicts where configuration data exists in both YAML files (the intended SSOT) and Python hardcoded constants, causing maintenance burden and potential drift.

---

## Critical SSOT Conflicts

### 1. Territory Definitions (HIGH PRIORITY)

**SSOT Location:** `config/structure_blueprint/territories.yaml`  
**Duplicate Location:** `agentic_core/L5_safety/config/structure_blueprint/_constants.py`

**Issue:**
- `territories.yaml` contains canonical territory definitions (495 lines)
- `_constants.py` contains hardcoded `SOVEREIGN_TERRITORIES` with duplicate territory data (1847 lines)
- The Python file includes a deprecation warning for `SOVEREIGN_TERRITORIES` but still maintains the full definition
- Both sources define the same territories with slight variations, creating drift risk

**Impact:**
- Changes must be made in both places
- High risk of divergence
- Maintenance burden doubled
- The deprecation warning indicates this is known but not resolved

**Evidence:**
```python
# _constants.py line 603-617
def build_sovereign_territories() -> dict[str, TerritoryDefinition]:
    """Build the complete SOVEREIGN_TERRITORIES from templates + overrides.

    DEPRECATED: This function and SOVEREIGN_TERRITORIES are deprecated.
    Use the new territory API in territories.py instead:
    - get_territory_metadata(name) for single territory lookup
    - get_all_territories() for full territory map
    - is_valid_root_folder(name) for root validation
    """
    warnings.warn(
        "SOVEREIGN_TERRITORIES is deprecated. Use get_territory_metadata() or "
        "get_all_territories() from structure_blueprint.territories instead.",
        DeprecationWarning,
        stacklevel=2,
    )
```

**Recommendation:**
- Complete migration to YAML-based territory API
- Remove hardcoded `SOVEREIGN_TERRITORIES` from `_constants.py`
- Update all importers to use `get_territory_metadata()` or `get_all_territories()`

---

### 2. Layer Definitions (HIGH PRIORITY)

**SSOT Location:** `config/structure_blueprint/layers.yaml`  
**Duplicate Location:** `agentic_core/L5_safety/config/structure_blueprint/_constants.py`

**Issue:**
- `layers.yaml` should contain canonical layer definitions
- `_constants.py` contains `LAYER_OVERRIDES` with hardcoded layer data (lines 118-531)
- Layer-specific overrides are embedded in Python code instead of YAML

**Impact:**
- Layer configuration changes require code modifications
- Non-developers cannot modify layer structure
- Harder to audit layer configuration changes

**Evidence:**
```python
# _constants.py lines 118-531
LAYER_OVERRIDES: Final[Mapping[str, Mapping[str, Any]]] = {
    "L0_routing": {
        "purpose": (
            "Core Logic & Routing + Control-Plane Core — "
            "ingestion, route election, capability arbitration, policy-aware dispatch; "
            "plus boot integrity, SSOT discovery, and guardian runner health checks."
        ),
        # ... 400+ lines of hardcoded layer data
    },
    # ... 6 more layers
}
```

**Recommendation:**
- Migrate `LAYER_OVERRIDES` to `layers.yaml`
- Update `yaml_loader.py` to load layer overrides from YAML
- Remove hardcoded layer data from `_constants.py`

---

### 3. Exclusion Lists (MEDIUM PRIORITY)

**SSOT Location:** `config/excluded_paths.yaml`  
**Duplicate Location 1:** `agentic_core/L5_safety/config/structure_blueprint/ssot.py` (SOVEREIGN_EXCLUDED_FOLDERS)  
**Duplicate Location 2:** `agentic_core/config/constants_config.py` (_get_ssot_exclusions)

**Issue:**
- `excluded_paths.yaml` is the intended SSOT for exclusions (133 lines)
- `ssot.py` references `SOVEREIGN_EXCLUDED_FOLDERS` but it's not actually defined there
- `constants_config.py` attempts to import `SOVEREIGN_EXCLUDED_FOLDERS` from ssot.py, causing import errors
- Multiple scripts reference this constant but it doesn't exist in the expected location

**Impact:**
- Import errors in `constants_config.py` (KeyError: 'agentic_core.L5_safety')
- `exclusion_sync_gate.py` cannot verify sync because the constant is missing
- Broken SSOT validation pipeline

**Evidence:**
```python
# constants_config.py line 31-40
def _get_ssot_exclusions() -> tuple[set[str], set[str], set[str]]:
    """Load SSOT exclusions from structure blueprint."""
    try:
        from agentic_core.L5_safety.config.structure_blueprint.ssot import (
            SOVEREIGN_EXCLUDED_FOLDERS,
            SOVEREIGN_TERRITORIES,
        )
    except KeyError as e:
        raise KeyError(
            f"SSOT module structure_blueprint.ssot is missing required exports: {e}"
        ) from e
```

**Recommendation:**
- Define `SOVEREIGN_EXCLUDED_FOLDERS` in `ssot.py` by loading from `excluded_paths.yaml`
- Remove duplicate exclusion logic from other files
- Ensure single import path for exclusion data

---

### 4. AST Signals (MEDIUM PRIORITY)

**SSOT Location:** `config/structure_blueprint/ast_signals.yaml`  
**Duplicate Location:** Embedded in territory definitions in `_constants.py`

**Issue:**
- `ast_signals.yaml` should contain canonical AST signal patterns
- Territory definitions in `_constants.py` embed `ast_signals` directly
- Creates duplication when territories reference signals

**Impact:**
- AST signal changes require updating both YAML and Python
- Risk of signal pattern divergence

**Recommendation:**
- Load `ast_signals.yaml` in territory loader
- Reference signal keys instead of embedding values
- Remove embedded AST signals from `_constants.py`

---

### 5. MCP Server Configuration (LOW PRIORITY)

**SSOT Location:** `config/mcp_servers.yaml`  
**Duplicate Location:** `mcp_config.json` (workspace root)

**Issue:**
- Two separate MCP configuration files exist
- `mcp_config.json` is used by IDE/workspace
- `mcp_servers.yaml` appears to be a backup or alternative format
- Potential for configuration drift

**Impact:**
- MCP server configuration may differ between contexts
- Confusion about which file is authoritative

**Evidence:**
```bash
# Two MCP config files
config/mcp_servers.yaml  # YAML format
mcp_config.json          # JSON format (workspace root)
```

**Recommendation:**
- Consolidate to single SSOT (prefer YAML for consistency with other configs)
- Add sync check between the two during CI
- Document which format is authoritative

---

## Additional SSOT Concerns

### 6. Token Budget Configuration

**Location:** `config/token_budget.yaml`  
**Status:** Appears to be single source (no duplicates found)

### 7. Layer Overrides Schema

**Location:** `config/schemas/layer_overrides.schema.json`  
**Status:** Schema validation file, not a data SSOT

---

## Root Cause Analysis

The primary root cause is **incomplete migration from hardcoded Python constants to YAML-based configuration**. The architecture was designed to use YAML as SSOT, but:

1. **Legacy Python code** still contains hardcoded definitions
2. **Deprecation warnings** were added but migration not completed
3. **Import chains** still reference the old Python constants
4. **No automated sync** exists between YAML and Python duplicates

---

## Recommended Action Plan

### Phase 1: Critical (Immediate)
1. **Fix SOVEREIGN_EXCLUDED_FOLDERS import error**
   - Define the constant in `ssot.py` by loading from `excluded_paths.yaml`
   - Update `constants_config.py` to handle the import correctly
   - Verify `exclusion_sync_gate.py` works

### Phase 2: High Priority (1-2 weeks)
2. **Complete territory migration**
   - Remove `SOVEREIGN_TERRITORIES` from `_constants.py`
   - Update all importers to use `get_territory_metadata()` or `get_all_territories()`
   - Add CI check to prevent re-adding hardcoded territories

3. **Migrate layer overrides to YAML**
   - Move `LAYER_OVERRIDES` to `layers.yaml`
   - Update `yaml_loader.py` to load from YAML
   - Remove hardcoded layer data from `_constants.py`

### Phase 3: Medium Priority (2-4 weeks)
4. **Consolidate AST signals**
   - Load `ast_signals.yaml` in territory loader
   - Update territory definitions to reference signal keys
   - Remove embedded signals from Python code

5. **Resolve MCP config duplication**
   - Choose YAML as SSOT
   - Add sync validation in CI
   - Deprecate JSON format

### Phase 4: Long-term
6. **Add automated SSOT validation**
   - CI gate to check for hardcoded config data
   - Automated sync verification between YAML and Python
   - Linting rules to prevent new SSOT violations

---

## Metrics

- **Total SSOT Conflicts Identified:** 5
- **Critical Priority:** 2
- **High Priority:** 1
- **Medium Priority:** 2
- **Low Priority:** 1
- **Estimated Lines of Duplicate Code:** ~2,000+ lines
- **Estimated Migration Effort:** 2-4 weeks for complete resolution

---

## Conclusion

The repository suffers from **incomplete SSOT migration** where YAML configuration files were introduced but hardcoded Python constants were never fully removed. This creates significant maintenance burden and risk of configuration drift. The most critical issue is the missing `SOVEREIGN_EXCLUDED_FOLDERS` constant causing import errors, followed by the massive duplication in territory and layer definitions.

**Immediate Action Required:** Fix the `SOVEREIGN_EXCLUDED_FOLDERS` import error to restore basic SSOT validation functionality.
