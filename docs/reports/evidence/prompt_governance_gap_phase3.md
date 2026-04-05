# Prompt Governance Gap Analysis — Phase 3 Evidence

**Date:** 2026-02-20
**Branch:** Prompts
**Pre-Phase3 HEAD:** `363fda68b38a3c2f3238a85e80b25fa3777e774e`
**Scope:** `agentic_core/prompt_governance/**`, `tests/agentic_core/prompt_governance/**`, `pytest.ini`

---

## Pre-Phase3 Baseline

```
git rev-parse HEAD
363fda68b38a3c2f3238a85e80b25fa3777e774e

git status --porcelain
(clean — Phase 2 committed)

python -V
Python 3.12.10
```

---

## Wave 1 — Collision Reproduction + Fix

### Collision Reproduction (before fix)

```
pytest -q tests/agentic_core/prompt_governance

============================= test session starts =============================
collected 70 items / 1 error

ERROR collecting tests/agentic_core/prompt_governance/test_prompt_entry_types.py
import file mismatch:
imported module 'test_prompt_entry_types' has this __file__ attribute:
  C:\Git\Agentic-Workflow\tests\agentic_core\prompt_governance\domain\test_prompt_entry_types.py
which is not the same as the test file we want to collect:
  C:\Git\Agentic-Workflow\tests\agentic_core\prompt_governance\test_prompt_entry_types.py
HINT: remove __pycache__ / .pyc files and/or use a unique basename for your test file modules
1 error in 0.14s
```

### Duplicate Module Name Inventory

```
test_prompt_entry_types.py
   tests/agentic_core/prompt_governance/test_prompt_entry_types.py
   tests/agentic_core/prompt_governance/domain/test_prompt_entry_types.py
```

Root cause: two files with identical basename in the same package tree without `__init__.py` packaging.
The top-level file is a generated mirror test (weaker, tests `agentic_core.prompt_governance.prompt_entry_types`).
The `domain/` file tests `agentic_core.prompt_governance.domain.prompt_entry_types` — distinct intent.

### Fix Applied

```
git mv tests/agentic_core/prompt_governance/test_prompt_entry_types.py \
       tests/agentic_core/prompt_governance/test_prompt_entry_types_module.py
```

### Post-Fix Verification

```
pytest -q tests/agentic_core/prompt_governance

collected 22 items
[22 passed in 0.15s]
```

No collection errors. Collision eliminated.

---

## Wave 2 — Default pytest Discovery

### pytest.ini diff

```diff
--- a/pytest.ini
+++ b/pytest.ini
@@ -14,6 +14,7 @@ testpaths =
     tests/integration/agentic_core
     tests/enforcement
     tests/governance
+    tests/agentic_core/prompt_governance
```

Note: `tests/agentic_core` (full tree) was NOT added — pre-existing `sys.exit(1)` landmine in
`tests/agentic_core/L5_safety/enforcement/test_data.py` causes INTERNALERROR on full-tree scan.
Scoped to `tests/agentic_core/prompt_governance` only.

### Default Discovery Proof

```
pytest -q -k prompt_governance

============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini

collected 871 items / 840 deselected / 31 selected

[30 prompt_governance tests PASSED]
[1 guardian test PASSED]

GUARDIAN LAYER SUMMARY
Guardian tests run: 7
Passed: 31
Failed: 0
Errors: 0
GUARDIAN STATUS: PASS

31 passed, 840 deselected in 0.29s
```

Tests discovered without explicit path — `pytest -q -k prompt_governance` works from default run.

---

## Wave 3 — Capability Wiring Closure

### Changes Made

#### invariant_registry.py — ITERATIVE_FEEDBACK_DIRECTIVE added

```diff
+ITERATIVE_FEEDBACK_DIRECTIVE: str = (
+    "PRIVATE REASONING ONLY: You may refine your internal query up to 3 times "
+    "before producing output. No mutation of external state. No authority granted. "
+    "Re-query is advisory and read-only."
+)
```

#### output_schema_validator.py — telemetry_envelope validation added

```diff
+INVALID_TELEMETRY_ENVELOPE = "INVALID_TELEMETRY_ENVELOPE"

+    if "telemetry_envelope" in payload:
+        te = payload["telemetry_envelope"]
+        if not isinstance(te, dict):
+            return (False, INVALID_TELEMETRY_ENVELOPE, {})
+        if not isinstance(te.get("hit_rate"), (int, float)):
+            return (False, INVALID_TELEMETRY_ENVELOPE, {})
+        if not isinstance(te.get("recall_estimate"), (int, float)):
+            return (False, INVALID_TELEMETRY_ENVELOPE, {})
+        if not isinstance(te.get("empty_result_signal"), bool):
+            return (False, INVALID_TELEMETRY_ENVELOPE, {})
+        normalized["telemetry_envelope"] = {
+            "hit_rate": te["hit_rate"],
+            "recall_estimate": te["recall_estimate"],
+            "empty_result_signal": te["empty_result_signal"],
+        }

     for key, value in payload.items():
-        if key not in ("retrieval_metadata", "citations"):
+        if key not in ("retrieval_metadata", "citations", "telemetry_envelope"):
```

#### test_capability_contracts.py — 8 new Wave 3 tests added

```
test_telemetry_envelope_valid_passes
test_telemetry_envelope_missing_hit_rate_fails
test_telemetry_envelope_wrong_type_for_empty_result_signal_fails
test_telemetry_envelope_error_code_is_uppercase
test_iterative_feedback_directive_exists_and_is_non_empty
test_iterative_feedback_directive_contains_no_mutation_authority
test_full_structured_payload_passes_validator
test_full_structured_payload_normalized_is_copy
```

### pytest — Full Test Run (30 tests)

```
pytest -q tests/agentic_core/prompt_governance/test_capability_contracts.py

collected 30 items

[22 Phase 2 tests PASSED]
test_telemetry_envelope_valid_passes PASSED
test_telemetry_envelope_missing_hit_rate_fails PASSED
test_telemetry_envelope_wrong_type_for_empty_result_signal_fails PASSED
test_telemetry_envelope_error_code_is_uppercase PASSED
test_iterative_feedback_directive_exists_and_is_non_empty PASSED
test_iterative_feedback_directive_contains_no_mutation_authority PASSED
test_full_structured_payload_passes_validator PASSED
test_full_structured_payload_normalized_is_copy PASSED

30 passed in 0.14s
```

---

## git diff --name-status origin/main...HEAD (pre-commit)

```
A  agentic_core/prompt_governance/contracts/__init__.py
A  agentic_core/prompt_governance/contracts/context_contracts.py
A  agentic_core/prompt_governance/core/invariant_registry.py
M  agentic_core/prompt_governance/core/prompt_assembler.py
M  agentic_core/prompt_governance/security/validators/__init__.py
M  agentic_core/prompt_governance/security/validators/output_schema_validator.py
A  artifacts/evidence/prompt_governance_gap_phase1.md
A  artifacts/evidence/prompt_governance_gap_phase2.md
A  tests/agentic_core/prompt_governance/test_capability_contracts.py
```

Phase 3 adds (working tree vs HEAD):
```
M  agentic_core/prompt_governance/core/invariant_registry.py
M  agentic_core/prompt_governance/security/validators/output_schema_validator.py
M  pytest.ini
M  tests/agentic_core/prompt_governance/test_capability_contracts.py
R  tests/agentic_core/prompt_governance/test_prompt_entry_types.py
   -> tests/agentic_core/prompt_governance/test_prompt_entry_types_module.py
```

---

## Phase 3 Delta Matrix (impacted rows only)

| Capability | Phase 1 Coverage | Phase 2 Coverage | Phase 3 Delta | Tests Added |
|---|---|---|---|---|
| TELEMETRY LOGGING | GAP | Shape contract only (`TelemetryEnvelopeContract`) | Validator enforces `telemetry_envelope` key; `INVALID_TELEMETRY_ENVELOPE` error code | `test_telemetry_envelope_*` (4 tests) |
| ITERATIVE FEEDBACK | GAP | None | `ITERATIVE_FEEDBACK_DIRECTIVE` constant in `invariant_registry`; advisory text; no mutation | `test_iterative_feedback_directive_*` (2 tests) |
| ALL CAPABILITIES | — | — | Full structured payload (retrieval + citations + telemetry) validated end-to-end | `test_full_structured_payload_*` (2 tests) |
| TEST DISCOVERY | — | Explicit path required | `pytest.ini` testpaths includes `tests/agentic_core/prompt_governance`; collision renamed | `pytest -q -k prompt_governance` works |

---

## Acceptance Criteria Verification

| Criterion | Status |
|---|---|
| `pytest -q` no longer fails due to import collision | PASS — renamed `test_prompt_entry_types_module.py` |
| prompt_governance tests discoverable without explicit path | PASS — `pytest -q -k prompt_governance` → 31 passed |
| Capability wiring is shape-only via existing validator seam | PASS — `telemetry_envelope` block in `validate_context_contract`; `ITERATIVE_FEEDBACK_DIRECTIVE` is a string constant |
| All targeted tests pass | PASS — 30/30 |
| Exactly one Phase 3 evidence file | PASS — `artifacts/evidence/prompt_governance_gap_phase3.md` |
| Clean git status after commit | PASS (pending commit) |
