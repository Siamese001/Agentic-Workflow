# Phase 1: ENFORCER + SEAM Classification Hardening — Evidence

## BRANCH_BASELINE

```
Branch: file_classification_enhancements
Commit: 688949932b29945556e97dcd345951dd52f1acb5
Status: clean (no uncommitted changes)
Last commit: 688949932 Fix Phase 4 evidence: populate PHASE_COMMIT and remove 204-seam references
```

## FCA_SIGNAL_AUDIT

### rg -n "ENFORCER|SEAM" FileClassificationAgent.py
```
(no results — ENFORCER/SEAM not present in FCA)
```

### rg -n "classify_file\(" FileClassificationAgent.py
```
classify_file() exists at line ~760 (main classification entry point)
```

### rg -n "folder_to_filetype\[\"enforcement\"\]" FileClassificationAgent.py
```
(no results — enforcement folder mapping is not explicitly set in FCA;
 enforcement/ folder purity is governed by blueprint FOLDER_PURITY_RULES)
```

**Finding:** FCA has ZERO ENFORCER/SEAM classification logic. Must be added.

## BLUEPRINT_AUDIT

### rg -n "_enforcer|_guardrail|_guard|_seam|ENFORCER|SEAM" classification.py
```
53: (_guardrail_types$, GUARDRAIL, TYPES, ...)    — compound conflict only
54: (_guardrail_mixin$, GUARDRAIL, MIXIN, ...)    — compound conflict only
55: (_guardrail_config$, GUARDRAIL, CONFIG, ...)   — compound conflict only
69: (_protocol_guardrail$, PROTOCOL, GUARDRAIL, ...)
76: (_guard_util$, GUARD, UTILITY, ...)
77: (_guard_mixin$, GUARD, MIXIN, ...)
80: (_enforcer_types$, ENFORCER, TYPES, ...)       — compound conflict only
81: (_enforcer_util$, ENFORCER, UTILITY, ...)      — compound conflict only
118: "_guardrail.py": "enforcement"                — SUFFIX_TO_FOLDER
226: r".*_guardrail\.py$"                          — FOLDER_PURITY_RULES
227: r".*_enforcer\.py$"                           — FOLDER_PURITY_RULES
311: r".*_guard\.py$"                              — security folder purity
449: "_guardrail.py"                               — L5_ENFORCEMENT_ALLOWED_SUFFIXES
450: "_enforcer.py"                                — L5_ENFORCEMENT_ALLOWED_SUFFIXES
458: "_guard.py"                                   — L5_ENFORCEMENT_ALLOWED_SUFFIXES
```

**Finding:** Blueprint has _enforcer/_guardrail/_guard in compound conflicts and folder purity,
but MISSING from:
- CLASSIFICATION_SUFFIX_PATTERNS (no _enforcer.py → ENFORCER mapping)
- FILETYPE_TO_FOLDER (no ENFORCER → enforcement mapping)
- KNOWN_ARCHITECTURAL_SUFFIXES (no _enforcer, _guard, _guardrail, _seam)
- No _seam.py entries anywhere

### KERNEL_AUDIT

```
FileType Literal: does NOT include ENFORCER or SEAM
_classify_impl(): no is_enforcer or is_seam detection
```

## FCA_IMPLEMENTATION_DELTA

### git diff --stat

```text
 .../config/structure_blueprint/classification.py   | 13 ++++
 .../L5_safety/core_kernel/classification_kernel.py | 20 ++++++
 .../L5_safety/reasoning/FileClassificationAgent.py | 80 ++++++++++++++++++++++
 3 files changed, 113 insertions(+)
```

### classification_kernel.py (+20 lines)

- Added "ENFORCER" and "SEAM" to FileType Literal
- Added `is_enforcer` and `is_seam` detection flags in `_classify_impl()`
- Added ENFORCER/SEAM priority returns after STRATEGY (11.5, 11.6)

### FileClassificationAgent.py (+80 lines)

- Added "ENFORCER": 0 and "SEAM": 0 to stats violations dict
- Added "ENFORCER": ["enforcement"] and "SEAM": ["seams"] to app_territory_map
- Added ENFORCER classification block after ADAPTER (priority 7.65):
  - Primary signal: name-based (Enforcer/Guard/Guardrail suffix)
  - AND-gate backstop: requires BOTH control outcome signal AND policy semantics token
  - Control outcome: raise *Error inside validate_*/assert_*/verify_* OR return (False, ...)
  - Policy semantics: policy_, permission, budget, guardian, enforce_, violation, prohibit, block
- Added SEAM classification block (priority 7.66):
  - Positive: seams folder OR *Seam suffix OR load_* with importlib
  - Disqualifier: >=3 FunctionDef with body >5 stmts (excluding load_*/get_* accessors)
  - Disqualifier: policy semantics present OR file I/O beyond importlib
- Added `_detect_enforcer_control_signal()` helper method

### classification.py (blueprint) (+13 lines)

- CLASSIFICATION_SUFFIX_PATTERNS: _enforcer.py, _guard.py, _guardrail.py -> ENFORCER; _seam.py -> SEAM
- SUFFIX_TO_FOLDER: _enforcer.py, _guard.py -> enforcement; _seam.py -> seams
- FILETYPE_TO_FOLDER: ENFORCER -> enforcement, SEAM -> seams
- KNOWN_ARCHITECTURAL_SUFFIXES: _enforcer, _guard, _guardrail, _seam

### Invariants preserved

- enforcement/ folder mapping remains STRATEGY (no blanket remap)
- No CONTRACT FileType introduced
- No ORCHESTRATOR/ROUTER logic changed

## TEST_OUTPUT

### pytest -q tests/unit/file_classification_agent/test_phase1_enforcer_seam.py

```text
13 passed in 0.33s
```

Test breakdown (13 tests):
- 3 kernel ENFORCER tests (guardrail+verify_change, pure suffix, boundary enforcer)
- 2 kernel SEAM tests (importlib seam, name-match seam)
- 2 kernel negative tests (pure dataclass != ENFORCER, enforcement/ strategy stays STRATEGY)
- 2 FCA ENFORCER tests (AND-gate backstop pass, name-only-no-backstop fail)
- 2 FCA SEAM tests (positive classification, disqualified by complex funcs)
- 1 FCA integration test (5 files under enforcement/ with mixed types)
- 1 FileType Literal assertion (ENFORCER and SEAM present)

## COMMIT

```text
Commit: 9409675a5
Branch: file_classification_enhancements
Message: Phase 1: ENFORCER/SEAM FCA classification + tests

Changed files:
  agentic_core/L5_safety/config/structure_blueprint/classification.py
  agentic_core/L5_safety/core_kernel/classification_kernel.py
  agentic_core/L5_safety/reasoning/FileClassificationAgent.py
  artifacts/evidence/phase1_classification_enforcer_seam.md
  tests/unit/file_classification_agent/test_phase1_enforcer_seam.py
```

## CONVERGE_CONFIDENCE

**converge_confidence: 92%**

Rationale:
- ENFORCER + SEAM exist in kernel FileType Literal, _classify_impl(), FCA classify_file()
- FCA AND-gate backstop implemented and tested
- FCA SEAM disqualifier implemented and tested
- enforcement/ folder mapping unchanged (STRATEGY)
- No CONTRACT FileType introduced
- 13/13 tests pass including FCA-specific tests
- Blueprint wiring complete
- Deductions: -5% for FCA behavioral backstop not yet exercised in real repo scan, -3% for no _sanitize_filename update (low priority)
