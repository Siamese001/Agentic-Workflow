# SSOT Heal-Mode Enablement — Phase 1 Evidence

**Date:** 2026-02-20
**Objective:** Enable true heal-mode run (non–dry-run, mutations allowed where authorized) on Windows

## Summary

| Wave | Description | Status |
|------|-------------|--------|
| 1 | Pin blockers (long-path gate, artifact write sites, mutation deny sites) | ✅ |
| 2 | Implement minimal unblocks (path scan, operational output allowlist) | ✅ |
| 3 | Proof: true heal-mode run without --validate | ✅ |

---

## WAVE 1 — Blockers Pinned

### Long-Path Preflight Gate

- **File:** `agentic_core/L0_routing/scripts/execute_ssot.py`
- **Lines:** 731-750 (original)
- **Condition:** `if val != 1` and `not self.dry_run`
- **Error path:** `errors.append("Windows LongPathsEnabled is NOT active")`

### Runtime Artifact Write Sites

1. **runtime_state.json**
   - **File:** `agentic_core/L0_routing/scripts/execute_ssot.py:1168`
   - **Layer/Op:** L0 / json.dump
   - **Guard:** `assert_no_persistent_write("L0", "json.dump")`

2. **Compliance Reports**
   - **File:** `agentic_core/L0_routing/scripts/execute_ssot.py:2223`
   - **Layer/Op:** L0 / json.dump
   - **Guard:** `assert_no_persistent_write("L0", "json.dump")`

### Mutation Prohibition Module

- **File:** `agentic_core/L0_routing/enforcement/mutation_prohibition.py`
- **Function:** `assert_no_persistent_write()`
- **Forbidden layers:** `frozenset({"L0", "L4", "L6"})`

---

## WAVE 2 — Minimal Unblocks Implemented

### A) Windows Long-Path Preflight Replacement

Replaced hard-block with deterministic path-length scan:

```python
# [HEALMODE-FIX] Replace hard-block with deterministic path-length scan
if platform.system() == "Windows":
    # Check for explicit skip override
    if os.environ.get("AGENTIC_SKIP_LONGPATH_PREFLIGHT") == "1":
        logging.info("AGENTIC_SKIP_LONGPATH_PREFLIGHT=1: skipping")
    else:
        # Scan for paths exceeding conservative threshold (240 chars)
        threshold = 240
        long_paths = []
        # ... scan logic ...
        if long_paths:
            msg = f"Found {len(long_paths)} path(s) > {threshold} chars"
            if not self.dry_run:
                errors.append(msg)
            else:
                logging.warning(msg)
```

### B) Operational Output Allowlist

Added narrow allowlist for runtime artifacts in `mutation_prohibition.py`:

```python
_OPERATIONAL_OUTPUT_PATTERNS: tuple[str, ...] = (
    "runtime_state.json",
    "compliance_reports/",
    "compliance_report_",
    "executive_summary_",
)

def _is_operational_output(path: str | None) -> bool:
    """Check if path is an allowed operational output (not source mutation)."""
    if path is None:
        return False
    for pattern in _OPERATIONAL_OUTPUT_PATTERNS:
        if pattern in path:
            return True
    return False
```

Updated `assert_no_persistent_write()` to check allowlist:

```python
# G-12-1 Exception: Allow operational outputs (runtime artifacts)
if _is_operational_output(path):
    return
```

### C) Updated Call Sites

1. `execute_ssot.py:1168-1169`:
   ```python
   # G-12-1: mutation prohibition guard (path allows operational output)
   assert_no_persistent_write("L0", "json.dump", str(state_path))
   ```

2. `execute_ssot.py:2223-2224`:
   ```python
   # G-12-1: mutation prohibition guard (path allows operational output)
   assert_no_persistent_write("L0", "json.dump", str(json_path))
   ```

---

## WAVE 3 — Proof: True Heal-Mode Run

### In-Process Invocation Snippet

```python
import sys
from pathlib import Path

REPO_ROOT = Path(r'C:\Git\Agentic-Workflow')
sys.path.insert(0, str(REPO_ROOT))

from agentic_core.L0_routing.scripts.execute_ssot import main

# TRUE HEAL-MODE: No --validate, no --dry-run
args = ['--domains']
sys.argv = ['execute_ssot'] + args
main()
```

**Args shown:** `['--domains']` — **NO --validate, NO --dry-run**

### Execution Output

```text
======================================================================
WAVE 3 - True Heal-Mode Run (No --validate)
======================================================================
REPO_ROOT: C:\Git\Agentic-Workflow
Args: ['--domains']
(TRUE HEAL-MODE - no validation flags)

HEAL_RUN_COMPLETED
```

### JSON Load OK

```text
Checking: C:\Git\Agentic-Workflow\runtime_state.json
runtime_state.json EXISTS
JSON_LOAD_OK
```

### Blocker Pattern Scan (0 matches)

```text
Blocker pattern scan:
  NO_MATCH: MUTATION_PROHIBITION DENY
  NO_MATCH: Atomic Write Failed
  NO_MATCH: Failed to save comprehensive reports
  NO_MATCH: Traceback

ALL_BLOCKERS_CLEAR
```

### Allowlist Unit Tests

```text
Operational Output Allowlist Tests
==================================================
Test 1: runtime_state.json allowed from L0
  PASS
Test 2: compliance_report allowed from L0
  PASS
Test 3: source file blocked from L0
  PASS

All tests passed!
```

---

## Files Changed

- `agentic_core/L0_routing/enforcement/mutation_prohibition.py`
- `agentic_core/L0_routing/scripts/execute_ssot.py`
- `tests/guardian/test_mutation_prohibition.py`

---

## Acceptance Criteria Met

- [x] Heal-mode completes without validation flag
- [x] runtime_state.json written successfully and parses
- [x] No mutation prohibition errors for runtime artifacts
- [x] Evidence proves run mode and artifact persistence
- [x] Operational output allowlist tests pass
- [x] Source files still blocked from L0 writes
