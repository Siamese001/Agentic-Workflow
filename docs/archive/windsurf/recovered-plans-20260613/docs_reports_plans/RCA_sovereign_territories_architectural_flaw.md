# RCA: SOVEREIGN_TERRITORIES Architectural Flaw - System Directories Should Not Have Validation Metadata

**Date:** 2026-03-11
**Severity:** Critical - Architectural Design Flaw
**Status:** Identified

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Executive Summary

`SOVEREIGN_TERRITORIES` contains a fundamental architectural flaw: it defines validation metadata (depth, subfolders, enforcement rules) for **system directories that should never be validated** (`.backup`, `artifacts`, `.gravity_state`, `logs`, etc.).

This creates absurd validation scenarios where structure validators check:
- "Is this file in `.backup/` at the correct depth?"
- "Does `artifacts/` have the required subfolders?"
- "Is `.gravity_state/` following naming conventions?"

These directories are gitignored, transient, or system-managed and should be **completely excluded from all structure validation**.

## Root Cause Analysis

### The Three Categories Incorrectly Mixed in SOVEREIGN_TERRITORIES

#### Category 1: Code Territories (8 territories)
**Need structure validation:**
- `agentic_core`, `apps_rg`, `apps_lic`, `apps_shared`, `tests`, `ops_scripts`, `system_learning`, `tools`
- **Require**: Depth validation (2/3/4), subfolder enforcement, import analysis, naming rules
- **Validation makes sense**: These contain Python code with architectural constraints

#### Category 2: Data/Docs Territories (2 territories)
**Need routing rules, not structure validation:**
- `data`, `docs`
- **Require**: Artifact routing (where to save reports, logs, datasets)
- **Don't need**: Depth enforcement or strict subfolder validation
- **Current state**: Have depth rules but they're not enforced consistently

#### Category 3: System/Volatile Territories (6 territories)
**Should NEVER be validated:**
- `.backup`, `.github`, `.gravity_state`, `artifacts`, `logs`, `archives`
- **Current state**: Have full `TerritoryDefinition` with depth, subfolders, purpose
- **Reality**:
  - `.backup` - Gitignored healing backups
  - `artifacts` - Gitignored build outputs
  - `.gravity_state` - Gitignored runtime state
  - `logs` - Gitignored runtime logs
  - `archives` - Deprecated code archive
  - `.github` - GitHub Actions workflows (managed by GitHub)

## Evidence: Absurd Validation Metadata

### Example 1: `.backup` Territory
```python
territories[".backup"] = {
    "depth": 2,  # ❌ Why validate depth of gitignored backups?
    "purpose": "Backup and recovery artifacts.",
    "subfolders": {
        "guardian_tests": {"purpose": "Backed-up guardian test files"},
        "phase1": {"purpose": "Phase 1 migration backups"},
        "phase2": {"purpose": "Phase 2 migration backups"},
    },
    "volatile": True,
    "no_cross_layer_imports": True,
    "allow_root_py": True,
}
```
**Problem**: `.backup` is gitignored. Why define required subfolders or depth rules?

### Example 2: `artifacts` Territory
```python
territories["artifacts"] = {
    "depth": 2,  # ❌ Build artifacts don't need depth validation
    "purpose": "Build artifacts, dedup reports, and transient analysis outputs.",
    "subfolders": ["consolidation", "dedup"],
    "volatile": True,
    "enforcement_level": "relaxed",
    "exclude_from_depth_rules": True,  # ⚠️ Contradicts depth: 2 above!
}
```
**Problem**: Has `depth: 2` but also `exclude_from_depth_rules: True` - contradictory metadata.

### Example 3: `logs` Territory
```python
territories["logs"] = {
    "depth": 2,  # ❌ Runtime logs don't need structure enforcement
    "purpose": "Runtime and audit log outputs.",
    "subfolders": {
        "compliance_reports": {"purpose": "Structured compliance report outputs"},
        "sovereign_audit": {"purpose": "Sovereign execution audit trail logs"},
    },
    "volatile": True,
    "allowed_extensions": [".log", ".jsonl", ".json", ".txt"],
}
```
**Problem**: Runtime logs are auto-generated. Validators shouldn't enforce their structure.

## Impact

### 1. Wasted Validation Cycles
Structure validators iterate over all 16 territories including system directories:
```python
for territory, config in SOVEREIGN_TERRITORIES.items():
    # Validates .backup, artifacts, .gravity_state unnecessarily
    validate_depth(territory, config["depth"])
    validate_subfolders(territory, config["subfolders"])
```

### 2. Confusing Semantics
Developers see `.backup` with `depth: 2` and think "Do I need to follow this structure?" when the answer is "No, it's gitignored."

### 3. Maintenance Burden
Every change to system directory structure requires updating `SOVEREIGN_TERRITORIES` even though validation is never applied.

### 4. Incorrect Abstraction
`SOVEREIGN_TERRITORIES` conflates:
- **Whitelist** (approved directory names)
- **Validation rules** (structure enforcement)
- **Routing rules** (artifact placement)
- **System metadata** (purpose, flags)

## Proposed Solution

### Phase 1: Separate Concerns

```python
# ============================================================================
# WHITELIST - Just approved directory names (no metadata)
# ============================================================================
PROJECT_ROOT_WHITELIST: Final[frozenset[str]] = frozenset({
    # Code territories
    "agentic_core", "apps_rg", "apps_lic", "apps_shared",
    "tests", "ops_scripts", "system_learning", "tools",
    # Data/docs territories
    "data", "docs",
    # System directories (never validated)
    ".backup", ".github", ".gravity_state", "artifacts", "logs", "archives",
    # VCS/IDE
    ".git", ".vscode", ".windsurf",
})

# ============================================================================
# CODE TERRITORIES - Full validation rules (8 territories only)
# ============================================================================
CODE_TERRITORIES: Final[dict[str, TerritoryDefinition]] = {
    "agentic_core": {
        "depth": 4,
        "subfolders": {...},
        "forbidden_patterns": [...],
        # Full validation metadata
    },
    "apps_rg": {...},
    "apps_lic": {...},
    "apps_shared": {...},
    "tests": {...},
    "ops_scripts": {...},
    "system_learning": {...},
    "tools": {...},
}

# ============================================================================
# DATA TERRITORIES - Routing rules only (2 territories)
# ============================================================================
DATA_ROUTING_RULES: Final[dict[str, RoutingConfig]] = {
    "data": {
        "artifact_types": ["datasets", "snapshots", "manifests"],
        "routing_map": {...},
    },
    "docs": {
        "artifact_types": ["reports", "plans", "architecture"],
        "routing_map": {...},
    },
}

# ============================================================================
# EXCLUDED FROM VALIDATION - System directories (6 territories)
# ============================================================================
SYSTEM_DIRECTORIES: Final[frozenset[str]] = frozenset({
    ".backup",      # Gitignored healing backups
    ".github",      # GitHub Actions (managed by GitHub)
    ".gravity_state",  # Gitignored runtime state
    "artifacts",    # Gitignored build outputs
    "logs",         # Gitignored runtime logs
    "archives",     # Deprecated code archive
})

# ============================================================================
# ENFORCED TERRITORIES - Subset of CODE_TERRITORIES with active enforcement
# ============================================================================
ENFORCED_TERRITORIES: Final[dict[str, TerritoryDefinition]] = {
    k: v for k, v in CODE_TERRITORIES.items()
    if not v.get("enforcement_level") == "relaxed"
}
```

### Phase 2: Update Validators

**Before:**
```python
for territory, config in SOVEREIGN_TERRITORIES.items():
    if config.get("volatile"):
        continue  # Skip but still had to check
    validate_structure(territory, config)
```

**After:**
```python
# Only iterate over territories that need validation
for territory, config in CODE_TERRITORIES.items():
    validate_structure(territory, config)
# System directories never appear in the loop
```

### Phase 3: Deprecate SOVEREIGN_TERRITORIES

```python
# Backward compatibility shim (deprecated)
@deprecated("Use CODE_TERRITORIES, DATA_ROUTING_RULES, or PROJECT_ROOT_WHITELIST")
def get_sovereign_territories() -> dict:
    """Legacy accessor - returns merged view for backward compatibility."""
    return {
        **CODE_TERRITORIES,
        **{k: {"routing": v} for k, v in DATA_ROUTING_RULES.items()},
        **{k: {"system": True} for k in SYSTEM_DIRECTORIES},
    }
```

## Benefits

### 1. Semantic Clarity
- `CODE_TERRITORIES` - "These have structure rules"
- `SYSTEM_DIRECTORIES` - "These are never validated"
- `PROJECT_ROOT_WHITELIST` - "These are approved at root level"

### 2. Performance
Validators only iterate over 8 territories instead of 16.

### 3. Correctness
Impossible to accidentally validate `.backup` or `artifacts`.

### 4. Maintainability
Adding a new system directory doesn't require defining fake validation rules.

## Relationship to ADG

This fix is **orthogonal to ADG**:
- **ADG**: Analyzes import dependencies between Python modules
- **CODE_TERRITORIES**: Defines physical directory structure rules
- **SYSTEM_DIRECTORIES**: Explicitly excluded from both ADG and structure validation

ADG doesn't make `CODE_TERRITORIES` obsolete - it complements it by analyzing import relationships **within** the validated code territories.

## Migration Path

### Step 1: Create new constants (non-breaking)
Add `CODE_TERRITORIES`, `SYSTEM_DIRECTORIES`, `DATA_ROUTING_RULES` alongside existing `SOVEREIGN_TERRITORIES`.

### Step 2: Update validators (non-breaking)
Change validators to use `CODE_TERRITORIES` instead of filtering `SOVEREIGN_TERRITORIES`.

### Step 3: Update application code (already in progress)
Replace `SOVEREIGN_TERRITORIES` imports with appropriate subset (19/23 files complete).

### Step 4: Deprecate SOVEREIGN_TERRITORIES
Add deprecation warning and migration guide.

### Step 5: Remove after grace period
Delete `SOVEREIGN_TERRITORIES` after all consumers migrated.

## Verification

After migration, verify:
```python
# No validator should ever check system directories
assert ".backup" not in CODE_TERRITORIES
assert "artifacts" not in ENFORCED_TERRITORIES
assert ".gravity_state" not in any_validation_loop()

# System directories are explicitly excluded
assert ".backup" in SYSTEM_DIRECTORIES
assert "artifacts" in SYSTEM_DIRECTORIES
```

## Conclusion

`SOVEREIGN_TERRITORIES` is a **God Object anti-pattern** that mixes:
- Whitelist (names)
- Validation rules (structure)
- Routing rules (artifacts)
- System metadata (flags)

The fix: **Separate concerns** into domain-specific constants that clearly communicate intent and prevent absurd validation scenarios.

The current replacement work (using `CODE_TERRITORIES` instead of `SOVEREIGN_TERRITORIES`) is **correct and necessary** - it's the first step toward eliminating this architectural flaw.

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

