# Patch Plan: apps_rg Ingress Contract v1 Enhancements

> Incremental improvements to the apps_rg ingress contract for better type safety, validation, and runtime clarity.

---

## Context (SCQA)

- **Situation** — The user is reviewing `apps_rg/contracts/apps_rg_ingress_contract_v1.py`, specifically the `RuntimeCustomizationPackage` section (lines 134-198). This model carries declarative refs, digests, policies, and metadata that downstream stages consume.
- **Complication** — As apps_rg evolves (Wave 2.5 ensemble judge restoration, Wave 3 L3 workflow runner, Wave 4 L2 ENSEMBLE_MODEL lane), the contract may need refinements for:
  - Better type safety on optional vs required fields
  - Clearer validation rules for profile refs
  - Improved documentation for downstream consumers
  - Alignment with recent pattern changes from other apps
- **Question** — What specific patches are needed to the ingress contract to support current and near-future apps_rg capabilities?
- **Answer** — This plan scopes incremental, non-breaking contract enhancements: validation improvements, docstring clarifications, and field refinements based on recent patterns from apps_rfp/apps_underwriting_ai.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `apps_rg/contracts/apps_rg_ingress_contract_v1.py` | Current contract definition | ✅ Read (lines 134-198) |
| `apps_rfp/contracts/` | Pattern reference for comparison | 🔲 Read if needed |
| `apps_underwriting_ai/contracts/` | Pattern reference for comparison | 🔲 Read if needed |
| `.windsurf/rules/apps-folder-taxonomy.md` | Folder structure enforcement | ✅ Verified |

---

## Wave Structure

| Wave | Phase IDs | Focus | Status |
|------|-----------|-------|--------|
| W1 | 1.1-1.4 | Contract validation improvements | 🟢 READY TO START |
| W2 | 2.1-2.3 | Field refinements + docstring updates | 🔲 |
| W3 | 3.1-3.2 | Cross-app contract alignment + verification | 🔲 |

**Total: 3 waves, ~12K tokens**

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| 1.1 | Field validation for profile refs | `apps_rg_ingress_contract_v1.py` | Distinguish empty string "" from valid ref format | ~3K | 🔲 |
| 1.2 | Required vs Optional field audit | Same file | Some fields have defaults but should be required | ~2K | 🔲 |
| 1.3 | Docstring improvements | Same file | Clarify U0 preservation contract | ~2K | 🔲 |
| 1.4 | Validation unit tests | `tests/unit/apps_rg/contracts/` | Add contract validation tests | ~3K | 🔲 |
| 2.1 | Pattern alignment with apps_rfp | Compare contracts | Adopt proven patterns from sibling apps | ~2K | 🔲 |
| 2.2 | Pattern alignment with apps_underwriting_ai | Compare contracts | Consistency across apps_* suite | ~2K | 🔲 |
| 2.3 | RuntimeCustomizationPackage refinements | `apps_rg_ingress_contract_v1.py` | Field-specific improvements | ~3K | 🔲 |
| 3.1 | Integration smoke test | `apps_rg/` entry point | Verify contract loads correctly | ~2K | 🔲 |
| 3.2 | Notion registration + plan complete | Notion Plans DB | Mark plan complete | ~1K | 🔲 |

---

## Execution Plan

### Wave 1 — Contract Validation Improvements

**Phase 1.1 — Field validation for profile refs**

Current state in `RuntimeCustomizationPackage`:
```python
workflow_manifest_ref: str = Field(default="", description="...")
```

Problem: Empty string `""` is ambiguous — it could mean:
- "Not provided"
- "Use default"
- "Invalid ref format"

**Patch options:**
1. Use `Optional[str]` with `None` default for truly optional refs
2. Add validator to check ref format (e.g., `^[a-z0-9_-]+/[a-z0-9_/-]+\.yaml$`)
3. Keep `""` for "single_step" semantics but document clearly

**Recommended approach:**
```python
from typing import Optional

workflow_manifest_ref: Optional[str] = Field(
    default=None,
    description="Ref to managed workflow manifest. None → single_step workflow."
)
```

**Phase 1.2 — Required vs Optional field audit**

Review all fields in:
- `RuntimeCustomizationPackage`
- `QualityThresholdsSection`
- `OutputRequirementsSection`
- `ProvenanceRequirementsSection`
- `ManifestIntegritySection` (lines 120-133)

Check: Does every `default=` field actually need a default? Should any be required?

**Phase 1.3 — Docstring improvements**

Clarify key contracts:
1. "U0 validates and preserves this section verbatim"
2. "U0 does NOT execute any of these references"
3. Which fields are blocking preconditions for which waves

**Phase 1.4 — Validation unit tests**

New test file: `tests/unit/apps_rg/contracts/test_ingress_contract_v1.py`

Cover:
- Valid instantiation with all fields
- Valid instantiation with minimal fields
- Invalid ref format detection
- Missing required field errors
- Edge cases (empty strings, None values)

### Wave 2 — Pattern Alignment

**Phase 2.1 — Compare with apps_rfp contracts**

Read `apps_rfp/contracts/` if exists:
- What patterns do they use for similar sections?
- Any validation decorators worth adopting?

**Phase 2.2 — Compare with apps_underwriting_ai contracts**

Read `apps_underwriting_ai/contracts/`:
- Contract inheritance patterns
- Field naming conventions
- Documentation style

**Phase 2.3 — RuntimeCustomizationPackage refinements**

Apply lessons from cross-app comparison:
- Rename ambiguous fields
- Add computed properties if helpful
- Refine validation logic

### Wave 3 — Verification & Closeout

**Phase 3.1 — Integration smoke test**

Verify contract loads in actual apps_rg context:
```bash
python -c "from apps_rg.contracts.apps_rg_ingress_contract_v1 import RuntimeCustomizationPackage; print('OK')"
```

**Phase 3.2 — Notion registration + plan complete**

Register this patch plan in Notion and mark complete.

---

## Definition of Done

| # | Criterion | Verification | Status |
|---|---|---|---|
| DoD-1 | Profile ref fields use `Optional[str]` instead of `str = ""` | Code review | 🔲 |
| DoD-2 | All required fields lack defaults (no `= Field(default=...)` for required) | Code review | 🔲 |
| DoD-3 | Docstrings clarify U0 preservation contract | Code review | 🔲 |
| DoD-4 | Unit tests cover validation scenarios | `pytest tests/unit/apps_rg/contracts/` passes | 🔲 |
| DoD-5 | Contract imports successfully in apps_rg context | Smoke test passes | 🔲 |
| DoD-6 | No breaking changes to existing valid payloads | Backward compat check | 🔲 |
| DoD-7 | Plan registered in Notion | Notion row exists | 🔲 |

---

## Rollback Strategy

1. Revert contract changes: `git checkout apps_rg/contracts/apps_rg_ingress_contract_v1.py`
2. Delete test file if created
3. Mark Notion plan Status="Retired" with reason

---

## Non-Goals

- ❌ Add new major sections to the contract (out of scope for patch)
- ❌ Break backward compatibility with existing payloads
- ❌ Refactor entire apps_rg architecture
- ❌ Change contract version (still v1)
- ❌ Modify downstream consumers (U0, L3, L2) — contract-only changes

---

## Verification-vs-Deferral

| Item | Verified This Plan | Deferred |
|---|---|---|
| Field validation improvements | ✅ | — |
| Docstring updates | ✅ | — |
| Unit test coverage | ✅ | — |
| Cross-app pattern alignment | ✅ | — |
| Integration with Wave 2.5/3/4 features | — | ✅ Deferred to those wave plans |
| Downstream consumer updates | — | ✅ Out of scope (contract only) |

---

## Notes

**Current Contract Structure (from line 167 review):**
- `RuntimeCustomizationPackage` — 20 profile/policy ref fields
- `write_policy` — currently `"read_only"` | `"deferred_writeback"`, defaults to `"read_only"`
- All profile refs default to `""` (empty string)

**Key insight from displayed lines:**
The contract is well-structured but could benefit from:
1. Clearer distinction between "not provided" (`None`) and "empty ref" (`""`)
2. Validation that refs follow canonical path format
3. Documentation of which fields are blocking preconditions for which waves

**Pattern from other apps:**
apps_rfp and apps_underwriting_ai likely have similar contracts — worth checking for consistency.
