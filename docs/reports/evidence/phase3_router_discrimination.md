# Phase 3: Router Discrimination — Evidence

## BRANCH_BASELINE

```text
Branch: file_classification_enhancements
Commit: 51a3f31139b21a17ae0c9995c71a670f219a5342
Status: clean (tracked files)
Last commit: 51a3f3113 Phase 2: orchestrator hardening + invariant validation
```

## FCA_ROUTER_AUDIT

### rg -n "_router|Router" agentic_core/L5_safety/reasoning/FileClassificationAgent.py

```text
980:  # Architectural distinction: Router (L0) vs. Orchestrator (L3)
981:  # Router: Single target selection, direct pass-through call, thin CLI wrapper
1199: # ROUTER VS. ORCHESTRATOR DETECTION (Architectural Classification)
1206:  Distinguish between L0 routers and L3 orchestrators based on behavioral patterns.
1212:  True if file exhibits orchestrator behavior, False if router or neither.
1290:  # Router anti-patterns
1291:  router_patterns = ["select_handler", "route_to", "dispatch_single", "thin_wrapper"]
1297:  has_router_pattern = any(p in content for p in router_patterns)
1330:  if has_router_pattern and not has_multi_stage_functions: return False
```

### rg -n "_detect_orchestrator_patterns" FileClassificationAgent.py

```text
985:  is_orchestrator = self._detect_orchestrator_patterns(tree, path, content, primary_name)
1202: def _detect_orchestrator_patterns(self, tree, path, content, primary_name) -> bool:
```

## BLUEPRINT_ROUTER_AUDIT

### classification.py router references

```text
175:  engines: .*_(engine|executor|task|impl|router|service|...)\.py$  — folder purity regex
261:  r".*_router\.py$"  — already in ENGINE_SUFFIX_PATTERNS (engines regex)
No _router entry in CLASSIFICATION_SUFFIX_PATTERNS (lines 26-42)
No Router.py entry in SUFFIX_TO_FOLDER (lines 107-130)
No _router in KNOWN_ARCHITECTURAL_SUFFIXES (lines 432-451)
```

## IMPLEMENTATION_DELTA

### classification_kernel.py

- Added `is_router` check before `is_orchestrator`: `path.stem.endswith("_router")` => return "ENGINE"

### FileClassificationAgent.py

- Added `ROUTER_INVARIANT_FAIL` stats dict with subkeys: mutation, workflow, inheritance, structure
- Expanded `router_patterns` list in `_detect_orchestrator_patterns` (+6 patterns)
- Added `_validate_router_invariants()` method (report-only, 4 invariant checks)
- Added router intercept at priority 5.9 in `classify_file` before orchestrator check
- Router detection: `path.stem.endswith("_router")` (stem-only)

## KERNEL_ROUTER_SHORTCUT_HARDENING

```text
Change: Removed `primary_name.endswith("Router")` from both kernel and FCA
        router shortcut detection. Only `path.stem.endswith("_router")` remains.

Rationale:
  - Class-name suffix "Router" is ambiguous — any class ending in "Router"
    (e.g. MessageRouter, EventRouter) would be coerced to ENGINE even if the
    file stem does not follow the _router.py naming convention.
  - Stem-only matching aligns with the blueprint CLASSIFICATION_SUFFIX_PATTERNS
    entry `r"_router\.py$": "ENGINE"` and KNOWN_ARCHITECTURAL_SUFFIXES.
  - Eliminates false-positive ENGINE classification for non-router files that
    happen to contain a class with "Router" in the name.

Files changed:
  - classification_kernel.py line 265: stem-only
  - FileClassificationAgent.py line 1033: stem-only
  - FileClassificationAgent.py line 1497: _validate_router_invariants guard
  - test_phase3_router_discrimination.py: test uses _router stem filename
  - test_phase5_authority_boundary.py: test uses _router stem filename
```

### classification.py (blueprint)

- Added `r"_router\.py$": "ENGINE"` to CLASSIFICATION_SUFFIX_PATTERNS
- Added `"Router.py": "engines"` to SUFFIX_TO_FOLDER
- Added `"_router"` to KNOWN_ARCHITECTURAL_SUFFIXES

## TEST_OUTPUT

```text
tests/unit/file_classification_agent/test_phase3_router_discrimination.py  7 passed
tests/unit/file_classification_agent/test_phase2_orchestrator_hardening.py 6 passed
tests/unit/file_classification_agent/test_phase1_enforcer_seam.py         13 passed
Total: 26 passed, 0 failed
```

## COMMIT

```text
Commit: f7839e1a5
Branch: file_classification_enhancements
Parent: 51a3f3113 (Phase 2)
Files:
  - agentic_core/L5_safety/core_kernel/classification_kernel.py
  - agentic_core/L5_safety/reasoning/FileClassificationAgent.py
  - agentic_core/L5_safety/config/structure_blueprint/classification.py
  - tests/unit/file_classification_agent/test_phase3_router_discrimination.py
  - artifacts/evidence/phase3_router_discrimination.md
```

## CONVERGE_CONFIDENCE

```text
converge_confidence: 90%
rationale:
  - 7/7 new tests pass
  - 0 regressions across 26 total tests
  - No new FileTypes introduced (router => ENGINE)
  - Phase 1 ENFORCER/SEAM logic untouched
  - Phase 2 Orchestrator invariant logic untouched
  - Blueprint, kernel, FCA all aligned
  - Report-only invariant validation (no reclassification)
```
