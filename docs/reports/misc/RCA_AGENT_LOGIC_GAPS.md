# RCA: Agent Logic Gaps - "Friendly Fire" Archiving

## Executive Summary

Three agents besides `LocationAgent` have similar logic gaps that cause "friendly fire" archiving instead of intelligent file re-alignment:

| Agent | Logic Gap | Risk Level |
|-------|-----------|------------|
| **HierarchyAgent** | Archives depth violations instead of flattening/nesting | 🔴 HIGH |
| **FilesystemAgent** | Falls back to `archives/uncategorized/` without intelligent placement | 🟡 MEDIUM |
| **GravityEnforcerAgent** | Missing healing dispatch - detection only | 🟢 LOW |

---

## 1. HierarchyAgent - HIGH RISK

### Location
`agentic_core/L5_safety/validators/HierarchyAgent.py`

### Logic Gap
The `_archive_depth_violation` method **always archives** files that violate depth rules instead of using smart re-alignment:

```python
def _archive_depth_violation(self, file_path: Path, rel: Path, depth: int, expected: int, subdir: str, label: str) -> int:
    """Archive a file for depth violation."""
    try:
        archive_path = self.archive_root / subdir / rel
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        # PROBLEM: Always archives, never flattens or nests
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        archive_path.write_text(header + content, encoding="utf-8")
        file_path.unlink()  # DESTRUCTIVE
```

### Missing Intelligence
- No `VARIABLE_DEPTH_SUBFOLDERS` exemption check
- No flattening logic for DEEP violations
- No nesting logic for SHALLOW violations
- No dispatch table for different violation types

### Recommended Fix
```python
def _heal_depth_violation(self, file_path: Path, rel: Path, depth: int, expected: int) -> int:
    """Smart depth re-alignment instead of archiving."""
    if depth > expected:
        # DEEP: Flatten (move up)
        new_parts = rel.parts[:expected] + (rel.parts[-1],)
        target_path = self.project_root.joinpath(*new_parts)
    else:
        # SHALLOW: Nest (add depth_aligned spacers)
        deficit = expected - depth
        spacers = tuple(["depth_aligned"] * deficit)
        new_parts = rel.parts[:-1] + spacers + (rel.parts[-1],)
        target_path = self.project_root.joinpath(*new_parts)

    # Move instead of archive
    target_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.rename(target_path)
    return 1
```

---

## 2. FilesystemAgent - MEDIUM RISK

### Location
`agentic_core/L5_safety/validators/FilesystemAgent.py`

### Logic Gap
The `_determine_archive_subpath` method has a **fallback to `archives/uncategorized/`** when AST analysis fails:

```python
def _determine_archive_subpath(self, file_path: Path) -> Path:
    # ... AST analysis attempts ...

    # FINAL FALLBACK: Uncategorized purge
    uncat = self.archives_root / "uncategorized"  # PROBLEM
    uncat.mkdir(exist_ok=True)
    return uncat
```

### Missing Intelligence
- No check if file belongs in a sovereign territory
- No attempt to find correct placement via `is_path_allowed()`
- Falls back to archive instead of leaving file in place

### Recommended Fix
```python
def _determine_archive_subpath(self, file_path: Path) -> Optional[Path]:
    """Returns None if file should NOT be archived."""
    from agentic_core.L5_safety.validators.structure_blueprint import is_path_allowed

    rel_path = file_path.relative_to(self.project_root)

    # Check if file is in a valid sovereign territory
    if is_path_allowed(str(rel_path)):
        return None  # Don't archive - file is valid

    # ... existing AST analysis ...
```

---

## 3. GravityEnforcerAgent - LOW RISK

### Location
`agentic_core/L5_safety/validators/GravityEnforcerAgent.py`

### Logic Gap
The agent is **detection-only** with no healing dispatch table. However, it correctly skips archives:

```python
SKIP_DIRS = {'__pycache__', '.git', 'node_modules', '.venv', 'venv', ARCHIVES_DIR}
```

### Current State
- Detection-only mode (no destructive actions)
- Properly skips archive directories
- No healing strategies defined

### Recommendation
- Add `HEALING_STRATEGIES` dispatch table if healing is enabled
- Ensure any future healing uses smart re-alignment, not archiving

---

## Pattern: The "Archive Fallback" Anti-Pattern

All three agents share a common anti-pattern:

```
Detection → Unknown Violation Type → Fallback to Archive
```

### The Fix Pattern (from LocationAgent)

```python
HEALING_STRATEGIES = {
    "SHALLOW VIOLATION": "_heal_depth_violation",
    "DEEP VIOLATION": "_heal_depth_violation",
    "APP-SPECIFIC IN CORE": "_heal_app_specific_violation",
    # ... explicit handlers for ALL violation types
}

def _apply_healing_strategy(self, file_path, msg, ...):
    for pattern, method_name in self.HEALING_STRATEGIES.items():
        if pattern in msg:
            return getattr(self, method_name)(...)

    # CRITICAL: Only archive if NO handler matches
    # Consider logging a warning instead of archiving
    Logger.warning(f"No handler for: {msg}")
    return {"action_taken": "SKIPPED: No handler"}
```

---

## Test Cases to Add

### HierarchyAgent Tests
1. Deep file in apps_* → Should flatten, NOT archive
2. Shallow file in tests/ → Should nest, NOT archive
3. File in VARIABLE_DEPTH_SUBFOLDERS → Should be exempt

### FilesystemAgent Tests
1. Valid file with bad suffix → Should clean suffix, keep in place
2. File in sovereign territory → Should NOT be archived
3. Truly orphaned file → May archive to categorized location

---

## Priority Order for Fixes

1. **HierarchyAgent** - Highest risk, actively archives depth violations
2. **FilesystemAgent** - Medium risk, archives to uncategorized
3. **GravityEnforcerAgent** - Low risk, detection-only

---

## Related Files

- `agentic_core/L5_safety/validators/LocationAgent.py` - Reference implementation
- `agentic_core/L5_safety/validators/structure_blueprint.py` - SSOT definitions
- `tests/core/architecture/test_location_agent_comprehensive.py` - Test patterns
