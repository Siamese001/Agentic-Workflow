# RCA: Six Structural Defects — Registry Nesting, PascalCase Misuse, Test Leakage, Domain Routing

**Date:** 2026-02-07
**Severity:** Medium (structural misplacement, naming violations, no runtime breakage)
**Scope:** 8 files fixed, 3 hardening rules added

---

## Issue 1: `prompt_governance/registry/` Nested Duplicate Folders

**Symptom:** `registry/` contained `domain/` and `utils/` sub-subfolders that duplicated the parent `prompt_governance/domain/` and `prompt_governance/utils/` structure.

**Root cause:** A healing pass or manual creation added LCD-style subfolders inside `registry/`, which is a *leaf* domain folder — not a layer root. The `CORE_SUBFOLDER_MAP` defines `registry` as an approved subfolder of `prompt_governance`, but nothing prevents `registry/` from sprouting its own `domain/` and `utils/` children.

**Fix:**
- Flattened `registry/domain/prompt_registry_config.json` → `registry/prompt_registry_config.json`
- Moved `registry/utils/cleanup_duplicates_util.py` → `prompt_governance/scripts/`
- Removed empty `registry/domain/` and `registry/utils/` folders

---

## Issue 2: PascalCase Non-Agent Files in `runtime/enforcement/`

**Symptom:** `EnvelopeFactory.py` and `ExpansionStrategy.py` used PascalCase naming in `enforcement/`, implying they are agents/adapters. They are not — one is a dataclass factory, the other is a `str, Enum`.

**Root cause:** `SUFFIX_TO_FOLDER` maps `"Strategy.py"` → `enforcement` and `FILETYPE_TO_FOLDER` maps `"FACTORY"` → `enforcement`. The FCA correctly routed by type, but the PascalCase naming was applied by a healing pass that assumed PascalCase = agent. No validation existed to reject PascalCase in non-agent contexts.

**Fix:**
- `EnvelopeFactory.py` → `envelope_factory.py` (stays in enforcement, snake_case)
- `ExpansionStrategy.py` → `expansion_strategy_types.py` (moved to `runtime/types/` — it's an enum + dataclass)

---

## Issue 3: `AstRelocator.py` (Pascal) vs `agent_engine.py` (snake) in engine/

**Symptom:** Mixed naming conventions in the same folder. `AstRelocator.py` is PascalCase but contains a utility class (`ast.NodeVisitor`), not an agent.

**Root cause:** Same as Issue 2 — a healing pass applied PascalCase to the filename because the class name is PascalCase. No validation rejected PascalCase files in `engine/`.

**Fix:** `AstRelocator.py` → `ast_relocator.py`

---

## Issue 4: `BudgetExceededError.py` Monolith in `runtime/types/`

**Symptom:** 226-line file named after a 6-line exception class. Contains `BudgetExceededError` (6 lines), `CostGovernor` (154 lines), `UsageRecord` (10 lines), `CostGovernorManager` (10 lines), and utility functions.

**Root cause:** The file was named after its first class (the exception). The PascalCase `*Error.py` suffix correctly routes to `types/` via the EXCEPTION classification. But the file is a monolith — the exception is <3% of the content. The actual primary class is `CostGovernor`.

**Fix:** `BudgetExceededError.py` → `cost_governor_types.py` (reflects actual content, proper `_types` suffix for `runtime/types/`)

---

## Issue 5: `test_tests_golden_state_datasets.py` in `meta_prompts/`

**Symptom:** A test file (`test_` prefix, `def test_*` functions) living inside `meta_prompts/` alongside Jinja templates.

**Root cause:** The FCA classifies this as TEST (PRIORITY 3) but **had no mechanism to flag or evict** test files found outside `tests/`. The classification was correct but the placement was never challenged. Additionally, the filename has a butchered `test_tests_` double prefix.

**Fix:**
- Moved to `tests/unit/agentic_core/prompt_governance/test_golden_state_datasets.py`
- Fixed double `test_tests_` → `test_` prefix

---

## Issue 6: Dashboard Utils in `agentic_core/utils/`

**Symptom:** `verify_dashboard_e2e_playwright_util.py` and `analyze_dashboard_color_bug_util.py` are dashboard-specific tools sitting in the global `utils/` folder.

**Root cause:** The `_util.py` suffix in `SUFFIX_TO_FOLDER` maps to `"utils"`. Suffix-based routing wins over content analysis. There was no content-signal mechanism to override suffix routing for domain-specific files.

**Fix:** Both moved to `L6_observability/dashboards/`

---

## Hardening Applied

### A. Misplaced Test File Detection (`FileClassificationAgent.py`)
Added warning at PRIORITY 3 (TEST detection): when a file is classified as TEST but `"tests"` is not in `path.parts`, log a `[MISPLACED-TEST]` warning with the current location and migration guidance.

### B. Domain Content Signal (`structure_blueprint_config.py`)
Added `DOMAIN_CONTENT_SIGNALS` mapping — Python files whose filenames contain domain keywords (e.g., "dashboard", "playwright") should be routed to their domain folder (`L6_observability/dashboards/`) instead of generic `utils/`.

### C. PascalCase Placement Validation (`FileClassificationAgent.py`)
Added `validate_pascal_case_placement()` method — flags PascalCase `.py` files found in folders that don't expect them (`engine/`, `types/`, `utils/`, `config/`). PascalCase is reserved for `reasoning/`, `enforcement/`, `base_agents/`, and `mixins/`. Exception classes (`*Error.py`, `*Exception.py`) are exempt.

---

## Summary of All Changes

| File | Action | Detail |
|------|--------|--------|
| `prompt_governance/registry/domain/` | **Flattened** | Config file moved up; folder removed |
| `prompt_governance/registry/utils/` | **Relocated** | Script moved to `scripts/`; folder removed |
| `runtime/enforcement/EnvelopeFactory.py` | **Renamed** | → `envelope_factory.py` (snake_case) |
| `runtime/enforcement/ExpansionStrategy.py` | **Moved+Renamed** | → `runtime/types/expansion_strategy_types.py` |
| `runtime/engine/AstRelocator.py` | **Renamed** | → `ast_relocator.py` (snake_case) |
| `runtime/types/BudgetExceededError.py` | **Renamed** | → `cost_governor_types.py` |
| `prompt_governance/meta_prompts/test_tests_...py` | **Moved+Renamed** | → `tests/unit/.../test_golden_state_datasets.py` |
| `utils/verify_dashboard_e2e_playwright_util.py` | **Moved** | → `L6_observability/dashboards/` |
| `utils/analyze_dashboard_color_bug_util.py` | **Moved** | → `L6_observability/dashboards/` |
| `FileClassificationAgent.py` | **Hardened** | +misplaced-test warning, +PascalCase placement validator |
| `structure_blueprint_config.py` | **Hardened** | +DOMAIN_CONTENT_SIGNALS mapping |
