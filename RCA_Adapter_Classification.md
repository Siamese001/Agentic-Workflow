# RCA: Adapter Classification Defects

**Date:** 2026-02-07
**Severity:** Medium (structural misclassification + 1 broken import)
**Scope:** 8 Adapter files across 4 locations

---

## Symptom

> "Why do only L5/enforcement have Adapter files? Why are some snake_case and others PascalCase?"

## Full Adapter Inventory

| # | File | Location | Case | Class Inside | Actual Domain |
|---|------|----------|------|-------------|---------------|
| 1 | `AdapterBaseAdapter.py` | L5_safety/enforcement/ | PascalCase | `AdapterBaseAdapter` | L5 Safety (ABC base) |
| 2 | `DomainPlannerAdapter.py` | L5_safety/enforcement/ | PascalCase | `DomainPlannerAdapter` | L5 Safety (wraps L3 agent) |
| 3 | `HumanReviewAdapter.py` | L5_safety/enforcement/ | PascalCase | `HumanReviewAdapter` | L5 Safety (HITL bridge) |
| 4 | `SurgicalHealingAdapter.py` | L5_safety/enforcement/ | PascalCase | `SurgicalHealingAdapter` | L5 Safety (healing bridge) |
| 5 | `VerificationGateAdapter.py` | L5_safety/enforcement/ | PascalCase | `VerificationGateAdapter` | L5 Safety (verification bridge) |
| 6 | `watchdog_adapter.py` | L3_orchestration/enforcement/ | snake_case | `WatchdogAdapter` (inline) | L3 Orchestration (daemon) |
| 7 | `local_disk_adapter.py` | L4_state/enforcement/ | snake_case | `LocalDiskAdapter` | L4 State (filesystem I/O) |
| 8 | `open_telemetry_tracing_adapter_types.py` | apps_shared/common_utils/ | snake_case | `OpenTelemetryTracingAdapter` | L6 Observability (tracing) |

---

## Root Causes

### RC-1: `TYPE_TO_SUBFOLDER` hardcodes ADAPTER → enforcement (PRIMARY)

In `structure_blueprint_config.py` (~line 2291):
```python
"ADAPTER": "enforcement",
```

This rule forces ALL files classified as ADAPTER into `enforcement/` regardless of which layer they belong to. This is architecturally wrong:

- **"Adapter" is a design pattern (Bridge/Wrapper), not a functional role.**
- Agents, engines, strategies describe WHAT a component does.
- "Adapter" describes HOW it wraps something — it should inherit the subfolder of the thing it wraps.

**Result:** `local_disk_adapter.py` was routed to `L4_state/enforcement/` instead of `L4_state/filesystem/`. `watchdog_adapter.py` was routed to `L3_orchestration/enforcement/` instead of staying near the daemon logic it adapts.

The 5 L5_safety adapters are correctly in L5 because they genuinely ARE safety/compliance wrappers (V10 bridge pattern, HITL, verification). The routing happened to be right for L5 but is wrong as a universal rule.

### RC-2: Naming Standard Violation (snake_case vs PascalCase)

The Zero-Ambiguity Standard in `structure_blueprint_config.py` (~line 2602) defines:
```python
"adapter": {
    "pattern": r"^[A-Z][a-zA-Z0-9]*Adapter\.py$",
    "description": "PascalCase ending with 'Adapter'",
    "examples": ["LocalDiskAdapter.py", "S3Adapter.py", "MCPAdapter.py"],
}
```

**Violators:**
- `watchdog_adapter.py` — should be `WatchdogAdapter.py` (but see RC-4)
- `local_disk_adapter.py` — should be `LocalDiskAdapter.py`
- `open_telemetry_tracing_adapter_types.py` — compound suffix issue (see RC-3)

### RC-3: Compound Suffix — `open_telemetry_tracing_adapter_types.py`

This filename carries BOTH `_adapter` (→ ADAPTER) and `_types` (→ TYPES) suffixes. Per the compound suffix RCA, this should have been caught by `COMPOUND_SUFFIX_CONFLICTS`. However, no `_adapter_types` pattern exists in the conflict list.

The file contains a full `OpenTelemetryTracingAdapter` class (509 lines) — it is NOT a types file. It was likely misclassified and renamed with `_types` appended by a prior healing pass.

### RC-4: `watchdog_adapter.py` is NOT really an adapter file

Despite the filename, this is a 500-line mission runner module (`Canon Validator Mission Runner`). It contains `WatchdogAdapter` only as a tiny inline class (lines 147-152, 6 lines). The file's purpose is daemon mode, surgical mode, and standard mode execution — not adapting anything. It was named based on one small internal class rather than its actual purpose.

### RC-5: `AdapterBaseAdapter.py` — Redundant double-suffix naming

The class `AdapterBaseAdapter` has "Adapter" appearing twice. This is an ABC defining the V10 Legacy Bridge Pattern. Better name: `V10LegacyBridgeBase.py` or `AdapterBase.py`.

### RC-6: Broken Import in `DomainPlannerAdapter.py`

Line 21:
```python
from agentic_core.L5_safety.reasoning.adapter_base import (
    AdapterContext, AdapterResult, HealingAdapter,
)
```

**No file `adapter_base.py` exists anywhere in the codebase.** The actual source is `L5_safety/enforcement/AdapterBaseAdapter.py`. This import will fail at runtime.

---

## Impact Assessment

| Issue | Severity | Files Affected |
|-------|----------|----------------|
| RC-1: Wrong subfolder routing | Medium | 2 files misplaced (L3, L4) |
| RC-2: snake_case naming | Low | 2 files non-compliant |
| RC-3: Compound suffix missed | Low | 1 file (apps_shared) |
| RC-4: Misnamed mission runner | Low | 1 file |
| RC-5: Double-suffix base class | Low | 1 file |
| RC-6: Broken import | **High** | 1 file (runtime crash) |

---

## Recommended Fixes

### P0 — Fix broken import (RC-6)
```
DomainPlannerAdapter.py line 21:
  FROM: agentic_core.L5_safety.reasoning.adapter_base
  TO:   agentic_core.L5_safety.enforcement.AdapterBaseAdapter
```

### P1 — Add `_adapter_types` to COMPOUND_SUFFIX_CONFLICTS (RC-3)
Add pattern to `structure_blueprint_config.py`:
```python
(r"_adapter_types$", "ADAPTER", "TYPES", "open_telemetry_tracing_adapter_types.py"),
```
Then rename `open_telemetry_tracing_adapter_types.py` → `OpenTelemetryTracingAdapter.py` (it's a class, not types).

### P2 — Change TYPE_TO_SUBFOLDER for ADAPTER (RC-1)
Remove the hard routing:
```python
# BEFORE:
"ADAPTER": "enforcement",
# AFTER — Option A: Route adapters same as agents (to reasoning/):
"ADAPTER": "reasoning",
# AFTER — Option B: Remove entry, let folder-context decide:
# (delete the ADAPTER line entirely)
```
**Recommendation:** Option B — adapters should inherit placement from the component they wrap, not from a global rule.

### P3 — Rename snake_case adapters to PascalCase (RC-2)
- `local_disk_adapter.py` → `LocalDiskAdapter.py`
- `watchdog_adapter.py` → Rename to reflect actual purpose (e.g., `canon_validator_mission_runner.py` or `MissionRunner.py`)

### P4 — Rename `AdapterBaseAdapter.py` (RC-5)
Consider `AdapterBase.py` or `V10BridgeBase.py` to avoid the double-suffix.

---

## Implementation Status — ALL FIXES APPLIED

| Fix | Status | Detail |
|-----|--------|--------|
| **P0** | ✅ Done | `DomainPlannerAdapter.py` import fixed → `L5_safety.enforcement.AdapterBase` |
| **P0b** | ✅ Done | `verification_script.py` import fixed → `L5_safety.enforcement.AdapterBase` |
| **P1** | ✅ Done | Added 4 ADAPTER compound suffix patterns to `COMPOUND_SUFFIX_CONFLICTS` |
| **P1b** | ✅ Done | Renamed `open_telemetry_tracing_adapter_types.py` → `OpenTelemetryTracingAdapter.py` |
| **P2** | ✅ Done | Removed `"ADAPTER": "enforcement"` from both `SUFFIX_TO_FOLDER` and `FILETYPE_TO_FOLDER` |
| **P3a** | ✅ Done | Renamed `local_disk_adapter.py` → `LocalDiskAdapter.py` (PascalCase compliance) |
| **P3b** | ✅ Done | Renamed `watchdog_adapter.py` → `mission_runner.py` (was not an adapter) |
| **P4** | ✅ Done | Renamed class `AdapterBaseAdapter` → `AdapterBase`, file → `AdapterBase.py`, added backwards-compat alias |

### Final Adapter Inventory (Post-Fix)

| File | Location | Case | Status |
|------|----------|------|--------|
| `AdapterBase.py` | L5_safety/enforcement/ | PascalCase | ✅ Renamed from AdapterBaseAdapter.py |
| `DomainPlannerAdapter.py` | L5_safety/enforcement/ | PascalCase | ✅ Import fixed |
| `HumanReviewAdapter.py` | L5_safety/enforcement/ | PascalCase | ✅ No change needed |
| `SurgicalHealingAdapter.py` | L5_safety/enforcement/ | PascalCase | ✅ No change needed |
| `VerificationGateAdapter.py` | L5_safety/enforcement/ | PascalCase | ✅ No change needed |
| `LocalDiskAdapter.py` | L4_state/enforcement/ | PascalCase | ✅ Renamed from local_disk_adapter.py |
| `mission_runner.py` | L3_orchestration/enforcement/ | snake_case | ✅ Renamed from watchdog_adapter.py (not an adapter) |
| `OpenTelemetryTracingAdapter.py` | apps_shared/common_utils/ | PascalCase | ✅ Renamed from open_telemetry_tracing_adapter_types.py |
