---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\test_hardening_wave1_inventory.md'
original_relative_path: 'test_hardening_wave1_inventory.md'
source_sha256: e88956ea68b15271f7f1876cf31859869e06c0985ead8e1e0e511624e12cda9d
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Wave 1: Full Test Surface Inventory & MECE Classification

## Baseline Metrics

| Metric | Count |
|--------|-------|
| Total test files scanned | 3,275 |
| Total test functions | 25,828 |
| Total findings | 3,739 |
| Unique files with skip calls | 330 |
| Files with `guardian: allow-silent-swallow` | 111 |

## MECE Classification Summary

### A. INVALID — Must Fix (355 findings)

| Sub-category | Count | Description |
|---|---|---|
| First-party import swallowers | 98 | `try/except` patterns that swallow `ImportError` for repo-owned modules |
| Import-only tests (core paths) | 233 | Tests with zero assertions, only `pass` after import |
| xfail without `strict=True` | 15 | Non-strict xfail hiding active breakage |
| Deps-unavailable skips (first-party) | 9 | `pytest.skip("deps unavailable")` for first-party code |

### B. VALID BUT AVOIDABLE — Should Reduce (798 findings)

| Sub-category | Count | Description |
|---|---|---|
| Shallow assertion-only tests | 781 | Tests with only `__name__`/`dir()` checks, no runtime validation |
| Third-party import swallowers | 17 | `try/except ImportError` for optional third-party packages |

### C. VALID REQUIRED — Keep Narrow

| Sub-category | Count | Description |
|---|---|---|
| Platform-specific skips | 0 | None found |
| External service skips (redis, API keys) | ~10 | OPENAI_API_KEY checks, redis availability |
| ADG artifact availability | ~15 | SQLite DB file existence checks |

### D. QUESTIONABLE — Needs Decision (2,423 findings)

| Sub-category | Count | Description |
|---|---|---|
| No-reason skip calls | 2,381 | `pytest.skip()` with empty reason string |
| `@pytest.mark.skipif` | 42 | Conditional skips needing review |

## Pattern Analysis

### Dominant Pattern: `_mod is None` → `pytest.skip()`
The vast majority of skip calls (2,381) follow this pattern in enhanced test files:
```python
if _mod is None:
    pytest.skip("module_name not available")
```
This is the **guardian: allow-silent-swallow** pattern where first-party modules are wrapped in `try/except (ValueError, TypeError, RuntimeError)` and set to `None` on failure. Tests then skip when `_mod is None`.

**Classification: INVALID for first-party code.** These are first-party import failures masked as optional dependencies.

### xfail Analysis (26 total)

| strict=True (VALID) | strict=False (INVALID) |
|---|---|
| 11 | 15 |

**strict=True cases** are legitimate negative-control tests (tamper detection).  
**strict=False cases** are masking unimplemented or stale features — must convert to `strict=True` or remove.

### Fixture Swallowers (7)
All in `test_execute_ssot_*.py` files. Helper functions like `_load()` and `_load_module()` silently catch `ImportError` and return `None`.

## Top 20 Files by Finding Density

| Count | File |
|---|---|
| 25 | tests/smoke/interfaces/test_interfaces_smoke.py |
| 16 | tests/unit/agentic_core/adg/extraction/test_wave_all_novel.py |
| 13 | tests/adg/test_adg_coverage_final_push.py |
| 13 | tests/unit/agentic_core/L2_execution/types/test_tool_args_types.py |
| 13 | tests/unit/agentic_core/runtime/exceptions/test_SovereignError.py |
| 13 | tests/unit/apps_lic/config/test_archetype_indicator_config.py |
| 13 | tests/unit/apps_lic/utils/test_archetype_indicator_util.py |
| 12 | tests/smoke/embeddings/test_embeddings_smoke.py |
| 12 | tests/system_learning/test_system_learning_mcp_integration.py |
| 12 | tests/unit/agentic_core/L5_safety/config/test_contract_stage_config.py |

## Wave 2 Target: INVALID Skips

Priority fixes for Wave 2:
1. Remove `guardian: allow-silent-swallow` pattern from first-party imports (111 files)
2. Convert `try/except → _mod = None → pytest.skip()` to hard imports (330 files with skips)
3. Convert 15 non-strict xfail to `strict=True` or remove
4. Fix 7 fixture swallowers in `test_execute_ssot_*.py`
5. Remove 9 explicit "deps unavailable" skips for first-party code

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

