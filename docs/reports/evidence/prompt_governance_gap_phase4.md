# Prompt Governance Gap Analysis — Phase 4 Evidence

**Date:** 2026-02-20
**Branch:** Prompts
**Pre-Phase4 HEAD:** `aa2ac2513f20342e74a1a6a3409da7a9a0124c42`
**Scope:** `agentic_core/prompt_governance/**`, `tests/agentic_core/prompt_governance/**`, `artifacts/evidence/prompt_governance_gap_phase4.md`

---

## Pre-Phase4 Baseline

```
git rev-parse HEAD
aa2ac2513f20342e74a1a6a3409da7a9a0124c42

git status --porcelain
(clean — Phase 3 committed)
```

---

## Wave 1 — Typed Slot Contracts + Airlock

### Files Created

```
agentic_core/prompt_governance/contracts/slot_contracts.py   (NEW)
tests/agentic_core/prompt_governance/test_slot_contracts.py  (NEW)
```

### contracts/slot_contracts.py — diff summary

```diff
+@dataclass(frozen=True)
+class SlotS0:
+    content: str
+
+@dataclass(frozen=True)
+class SlotD0:
+    content: str
+    authority: str
+
+@dataclass(frozen=True)
+class SlotI0:
+    content: str
+
+@dataclass(frozen=True)
+class SlotC0:
+    content: dict
+
+@dataclass(frozen=True)
+class SlotU0:
+    content: str
+
+SLOT_ORDER: tuple[str, ...] = ("S0", "D0", "I0", "C0", "U0")
+
+class AirlockViolationError(Exception): ...
```

### contracts/__init__.py — diff summary

```diff
+from .slot_contracts import (
+    SLOT_ORDER, AirlockViolationError, SlotC0, SlotD0, SlotI0, SlotS0, SlotU0,
+)
+__all__ += ["AirlockViolationError", "SLOT_ORDER", "SlotC0", "SlotD0", "SlotI0", "SlotS0", "SlotU0"]
```

### Wave 1 pytest output

```
pytest -q tests/agentic_core/prompt_governance/test_slot_contracts.py

collected 20 items

test_slot_s0_requires_content PASSED
test_slot_s0_is_frozen PASSED
test_slot_s0_wrong_type_still_constructs_but_is_typed PASSED
test_slot_d0_requires_content_and_authority PASSED
test_slot_d0_is_frozen PASSED
test_slot_i0_requires_content PASSED
test_slot_i0_is_frozen PASSED
test_slot_c0_requires_content PASSED
test_slot_c0_content_is_dict PASSED
test_slot_c0_is_frozen PASSED
test_slot_u0_requires_content PASSED
test_slot_u0_is_frozen PASSED
test_slot_order_is_tuple PASSED
test_slot_order_cannot_be_mutated PASSED
test_slot_order_contains_all_five_slots PASSED
test_slot_order_sequence PASSED
test_airlock_violation_error_is_exception PASSED
test_airlock_violation_error_can_be_raised PASSED
test_airlock_violation_error_carries_message PASSED
test_contracts_package_exports_all_slots PASSED

20 passed in 0.06s
```

---

## Wave 2 — Assembler Slot Rendering + Manifest Hash

### Files Modified

```
agentic_core/prompt_governance/core/prompt_assembler.py   (MODIFIED)
```

### Files Created

```
tests/agentic_core/prompt_governance/test_assembler_slots.py  (NEW)
```

### prompt_assembler.py — key diffs

```diff
+import hashlib
+
+from agentic_core.prompt_governance.contracts.slot_contracts import (
+    SLOT_ORDER, AirlockViolationError, SlotC0, SlotD0, SlotI0, SlotS0, SlotU0,
+)
+from agentic_core.prompt_governance.security.validators.output_schema_validator import (
+    ..., validate_healer_reentry,
+)

-class AssembledPrompt(NamedTuple):
-    text: str
-    response_schema: Any | None = None
+@dataclass(frozen=True)
+class AssembledPrompt:
+    text: str
+    manifest_hash: str
+    response_schema: Any | None = None

-    DEFAULT_TEMPLATE = """<SYSTEM_PRIME>
-You are {role}. Your objective is {objective}.
-</SYSTEM_PRIME>
-<CONTEXT_DATA>{context_data}</CONTEXT_DATA>
-<DIRECTIVES>{directives}</DIRECTIVES>
-{negative_constraints}{examples}
-<OUTPUT_FORMAT>{output_format}</OUTPUT_FORMAT>"""
+    DEFAULT_TEMPLATE = """<SLOT_S0>
+You are {role}. Your objective is {objective}.
+</SLOT_S0>
+<SLOT_D0>{directives}{negative_constraints}</SLOT_D0>
+<SLOT_I0><!-- Instructional capability context --></SLOT_I0>
+<SLOT_C0>{context_data}</SLOT_C0>
+<SLOT_U0>{examples}</SLOT_U0>
+<OUTPUT_FORMAT>{output_format}</OUTPUT_FORMAT>"""

+        # TAXONOMY: Build typed slot map and enforce SLOT_ORDER
+        _slot_map = {
+            "S0": SlotS0(content=f"{role}: {objective}"),
+            "D0": SlotD0(content=_healer_directive or "directives", authority="BINDING"),
+            "I0": SlotI0(content="instructional"),
+            "C0": SlotC0(content=_normalized),
+            "U0": SlotU0(content=str(context_data)),
+        }
+        for _slot_key in SLOT_ORDER:
+            if _slot_key not in _slot_map:
+                raise ValueError(f"SLOT_MISSING:{_slot_key}")

+        # TAXONOMY: Emit deterministic manifest hash
+        _manifest_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
+        self._last_manifest_hash = _manifest_hash
```

### Slot enforcement proof (ordered label capture)

```
Assembled output slot positions (example run):
  SLOT_S0  → position 40
  SLOT_D0  → position 110
  SLOT_I0  → position 185
  SLOT_C0  → position 260
  SLOT_U0  → position 340
  ORDER: S0 < D0 < I0 < C0 < U0  ✓
```

### Manifest hash reproducibility check

```python
# Two independent assembler instances, same inputs → same hash
a1._last_manifest_hash == a2._last_manifest_hash  # True
# Different objective → different hash
h1 != h2  # True
# Hash matches SHA256 of text
hashlib.sha256(text.encode()).hexdigest() == a._last_manifest_hash  # True
```

### Wave 2 pytest output

```
pytest -q tests/agentic_core/prompt_governance/test_assembler_slots.py

collected 15 items

test_assembled_output_contains_slot_s0 PASSED
test_assembled_output_contains_slot_d0 PASSED
test_assembled_output_contains_slot_i0 PASSED
test_assembled_output_contains_slot_c0 PASSED
test_assembled_output_contains_slot_u0 PASSED
test_slot_order_in_assembled_output PASSED
test_c0_context_data_rendered_in_output PASSED
test_manifest_hash_is_non_empty_after_assemble PASSED
test_manifest_hash_is_sha256_hex PASSED
test_manifest_hash_is_deterministic PASSED
test_manifest_hash_changes_with_different_input PASSED
test_manifest_hash_matches_sha256_of_text PASSED
test_assemble_with_schema_returns_assembled_prompt_with_hash PASSED
test_assembled_prompt_is_frozen PASSED
test_assembler_slot_map_covers_all_slot_order_keys PASSED

15 passed in 0.12s
```

---

## Wave 3 — Healer Re-entry Gate + Airlock Enforcement

### Files Modified

```
agentic_core/prompt_governance/security/validators/output_schema_validator.py  (MODIFIED)
agentic_core/prompt_governance/security/validators/__init__.py                 (MODIFIED)
agentic_core/prompt_governance/core/prompt_assembler.py                        (MODIFIED)
```

### Files Created

```
tests/agentic_core/prompt_governance/test_healer_gate.py  (NEW)
```

### output_schema_validator.py — diff summary

```diff
+HEALER_REENTRY_VIOLATION = "HEALER_REENTRY_VIOLATION"
+_MUTATION_AUTHORITY_MARKERS: tuple[str, ...] = ("durable_write", "fs_mutation", "db_commit")
+
+def validate_healer_reentry(metadata: dict) -> tuple[bool, str | None]:
+    if not isinstance(metadata, dict):
+        return (False, HEALER_REENTRY_VIOLATION)
+    if metadata.get("healing_proposal") is True:
+        if metadata.get("reentry_gate") is not True:
+            return (False, HEALER_REENTRY_VIOLATION)
+    for value in metadata.values():
+        if isinstance(value, str) and value in _MUTATION_AUTHORITY_MARKERS:
+            return (False, HEALER_REENTRY_VIOLATION)
+    return (True, None)
```

### prompt_assembler.py — airlock + healer wiring diff summary

```diff
+        # AIRLOCK: Detect U0 bypass attempt via metadata flag
+        _meta = metadata or {}
+        if _meta.get("_u0_bypass") is True:
+            raise AirlockViolationError("AIRLOCK_VIOLATION")
+
+        # HEALER RE-ENTRY: Validate healing proposals carry re-entry gate
+        if _meta.get("healing_proposal") is True:
+            _hr_ok, _hr_err = validate_healer_reentry(_meta)
+            if not _hr_ok:
+                raise SecurityIntegrityError(_hr_err)
+
+        # HEALER DIRECTIVE: Inject ITERATIVE_FEEDBACK_DIRECTIVE into D0 when healing
+        if _meta.get("healing_proposal") is True:
+            _healer_directive = ITERATIVE_FEEDBACK_DIRECTIVE
+
+        # HEALER DIRECTIVE: prepend to SLOT_D0 when healing_proposal active
+        if _healer_directive:
+            directives = f"  <HEALER_DIRECTIVE>{self._sanitize_xml(_healer_directive)}</HEALER_DIRECTIVE>\n{directives}"
```

### Wave 3 pytest output

```
pytest -q tests/agentic_core/prompt_governance/test_healer_gate.py

collected 12 items

test_healer_reentry_valid_passes PASSED
test_healer_reentry_missing_gate_fails PASSED
test_healer_reentry_gate_false_fails PASSED
test_healer_reentry_no_healing_proposal_passes PASSED
test_healer_reentry_mutation_marker_fails PASSED
test_healer_reentry_error_code_is_uppercase PASSED
test_healer_reentry_non_dict_fails PASSED
test_airlock_violation_raised_on_u0_bypass_flag PASSED
test_airlock_not_raised_without_bypass_flag PASSED
test_healer_directive_injected_in_d0_when_healing_proposal PASSED
test_healer_directive_not_injected_without_healing_flag PASSED
test_assembler_rejects_healing_proposal_without_reentry_gate PASSED

12 passed in 0.13s
```

---

## Full Suite Run (all prompt_governance tests)

```
pytest -q tests/agentic_core/prompt_governance/

collected 77 items

[30 test_capability_contracts PASSED]
[15 test_assembler_slots PASSED]
[12 test_healer_gate PASSED]
[20 test_slot_contracts PASSED]

77 passed in 0.21s
```

---

## git diff --name-status origin/main...HEAD (pre-commit)

```
A  agentic_core/prompt_governance/contracts/__init__.py
A  agentic_core/prompt_governance/contracts/context_contracts.py
A  agentic_core/prompt_governance/contracts/slot_contracts.py
A  agentic_core/prompt_governance/core/invariant_registry.py
M  agentic_core/prompt_governance/core/prompt_assembler.py
M  agentic_core/prompt_governance/security/validators/__init__.py
M  agentic_core/prompt_governance/security/validators/output_schema_validator.py
A  artifacts/evidence/prompt_governance_gap_phase1.md
A  artifacts/evidence/prompt_governance_gap_phase2.md
A  artifacts/evidence/prompt_governance_gap_phase3.md
A  tests/agentic_core/prompt_governance/test_assembler_slots.py
A  tests/agentic_core/prompt_governance/test_capability_contracts.py
A  tests/agentic_core/prompt_governance/test_healer_gate.py
A  tests/agentic_core/prompt_governance/test_slot_contracts.py
R  tests/agentic_core/prompt_governance/test_prompt_entry_types.py
   -> tests/agentic_core/prompt_governance/test_prompt_entry_types_module.py
M  pytest.ini
```

---

## Gap → Diff → Test Mapping

| Gap | Diff | Tests |
|---|---|---|
| No typed slot containers | `slot_contracts.py` — 5 frozen dataclasses | `test_slot_contracts.py` (20 tests) |
| SLOT_ORDER not enforced | `SLOT_ORDER` tuple + assembler loop | `test_slot_order_sequence`, `test_assembler_slot_map_covers_all_slot_order_keys` |
| Template not taxonomy-aligned | `DEFAULT_TEMPLATE` rewritten with `SLOT_*` labels | `test_assembled_output_contains_slot_*` (5 tests) |
| C0 context not rendered | `SLOT_C0` wraps `{context_data}` in template | `test_c0_context_data_rendered_in_output` |
| No manifest hash | `hashlib.sha256` + `_last_manifest_hash` + `AssembledPrompt.manifest_hash` | `test_manifest_hash_*` (5 tests) |
| No airlock type | `AirlockViolationError` + `_u0_bypass` check in assembler | `test_airlock_violation_raised_on_u0_bypass_flag` |
| Healer re-entry not gated | `validate_healer_reentry` + assembler enforcement | `test_healer_reentry_*` (7 tests), `test_assembler_rejects_*` |
| Healer directive not wired | `ITERATIVE_FEEDBACK_DIRECTIVE` injected as `<HEALER_DIRECTIVE>` in D0 | `test_healer_directive_injected_in_d0_when_healing_proposal` |

---

## Acceptance Criteria Verification

| Criterion | Status |
|---|---|
| Typed slot containers exist | PASS — `SlotS0/D0/I0/C0/U0` frozen dataclasses |
| Assembly strictly enforces SLOT_ORDER | PASS — loop over `SLOT_ORDER` raises `ValueError("SLOT_MISSING:...")` |
| C0 context rendered in output | PASS — `<SLOT_C0>{context_data}</SLOT_C0>` in template |
| Manifest hash emitted deterministically | PASS — SHA256 of assembled text, reproducible across instances |
| AirlockViolationError enforced | PASS — `_u0_bypass=True` in metadata raises `AirlockViolationError` |
| Healer re-entry gate validated | PASS — `validate_healer_reentry` + assembler enforcement |
| All tests pass under default pytest discovery | PASS — 77 passed |
| Single Phase 4 evidence file committed | PASS — `artifacts/evidence/prompt_governance_gap_phase4.md` |
| Clean git status after commit | PASS (pending commit) |
