---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\prompt-governance-dead-data-activation-38193f.md'
original_relative_path: 'prompt-governance-dead-data-activation-38193f.md'
source_sha256: 0e2d5bb64b7dbfba912177cbabd6535cf0a8fbf3e0fec3164958cc73d912b2a3
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Prompt Governance Dead Data Activation Plan

Activate two high-value dead data sets in `data/prompt_governance` — the `evaluations/` corpus as a data-driven pytest suite, and the `prompt_injections/` markdown as a no-missing-injection invariant — while deleting the three confirmed dead subdirectories.

---

## Resolved Open Questions

- **`governance/` deletion:** **DELETE** — org-process YAML stubs with zero code consumers; moving to `docs/` would give false legitimacy to unmaintained content.
- **`injections/misc/` floor impact:** **ZERO** — confirmed by runtime count. `misc/` contributes exactly 0 valid patterns (all 71 entries skipped due to schema mismatch). `modular/` alone yields exactly 30 patterns (5 per layer × 6 layers). Floor of ≥30 is fully satisfied post-deletion.

---

## Scope

| Action | Target | Rationale |
|---|---|---|
| ✅ Activate | `data/prompt_governance/evaluations/` | Rich test corpus, no runtime reader |
| ✅ Activate (invariant only) | `data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md` | 30-pattern canon, no guard asserting YAML completeness |
| ❌ Delete | `data/prompt_governance/injections/misc/` | 0 valid patterns loaded; schema mismatch with modular/ loader |
| ❌ Delete | `data/prompt_governance/governance/` | Org-process docs, zero code consumers, unmaintained |
| ❌ Delete | `data/prompt_governance/registry/` | Empty directory |

---

## Wave 1 — EvaluationLoader Infrastructure

**New file:** `agentic_core/prompt_governance/core/evaluation_loader.py`

- Constructor: `__init__(self, eval_dir: Path)` — validates directory exists
- `load_eval_set(name: str) -> dict` — loads `eval_dir/{name}.yaml`, caches, validates
- Raises `EvalLoadError` (file missing, YAML parse fail, OSError) and `EvalSchemaError` (non-dict root)
- `clear_cache()` and `cache_info()` for test isolation
- **No business logic** — pure infrastructure, mirrors `PromptLoader` pattern exactly

**Edits:**
- `agentic_core/prompt_governance/core/__init__.py` — export `EvaluationLoader`, `EvalLoadError`, `EvalSchemaError`
- `agentic_core/prompt_governance/__init__.py` — re-export same

---

## Wave 2 — Data-Driven Evaluation Tests

**New file:** `tests/unit/test_prompt_evaluation_corpus.py`

Uses `EvaluationLoader` pointed at `data/prompt_governance/evaluations/` via `Path(__file__).parent.parent.parent / "data/prompt_governance/evaluations"`.

### `TestEvalSetsCorpus`
- `test_loads_without_error`
- `test_resume_engine_tests_present`
- `test_outreach_engine_tests_present`
- `test_performance_benchmarks_present`
- `test_all_named_cases_have_description` — parametrized over all `name:` leaf entries

### `TestRubricCorpus`
- `test_loads_without_error`
- `test_all_criteria_have_weight` — every scoring criterion has `weight` float
- `test_weights_sum_to_one_per_category` — per category, weights sum to 1.0 ±0.01
- `test_passing_threshold_defined` — `scoring_methodology.passing_threshold` present and numeric
- `test_grade_classifications_complete` — A_plus through F all defined

### `TestRegressionTestsCorpus`
- `test_loads_without_error`
- `test_resume_engine_regression_present`
- `test_outreach_engine_regression_present`
- `test_all_cases_have_success_criteria` — parametrized over every named test case
- `test_no_case_missing_description`

### `TestStyleChecksCorpus`
- `test_loads_without_error`
- `test_resume_and_outreach_engine_styles_present`
- `test_all_checks_have_validation_method`
- `test_no_duplicate_check_names`

### `TestEvaluationLoaderErrorPaths` (branch coverage)
- `test_missing_file_raises_eval_load_error`
- `test_malformed_yaml_raises_eval_load_error`
- `test_non_dict_root_raises_eval_schema_error`
- `test_cache_hit_returns_same_object`
- `test_clear_cache_forces_reread`

---

## Wave 3 — No-Missing-Injection Invariant

**New file:** `tests/architecture/test_injection_canon_completeness.py`

**Logic:**
1. Read `data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md` (stdlib, no regex for logic)
2. Extract 30 canonical `Instruction Type` names by splitting each `|`-delimited table row, skipping header/separator lines
3. Call `get_instructional_injections()` → collect `.name` and `.description` per pattern
4. Assert each canonical name has a case-insensitive substring match in loaded corpus

**Tests:**
- `test_markdown_parses_to_exactly_30_entries` — pure parse, no YAML
- `test_all_canonical_patterns_present_in_yaml` — main completeness invariant; prints `MISSING` list on fail
- `test_loaded_count_floor` — `len(patterns) >= 30` (currently exactly 30)
- `test_no_layer_is_empty` — all 6 layers: framing, context, reasoning, tooling, safety, output have ≥1 pattern
- `test_missing_pattern_detected` — monkeypatch `get_instructional_injections` to return `[]`; assert invariant raises `AssertionError`

**Marker:** `@pytest.mark.architecture`

---

## Wave 4 — Dead Data Deletion

Delete in this order (Wave 3 floor already confirmed safe):

1. `data/prompt_governance/injections/misc/` — 7 files, 0 valid patterns
2. `data/prompt_governance/governance/` — misc/ + modular/ subtrees
3. `data/prompt_governance/registry/` — empty directory

---

## Acceptance Criteria

1. `python -m pytest -q --color=no` exits 0
2. `test_prompt_evaluation_corpus.py` contributes ≥ 25 cases
3. `test_injection_canon_completeness.py` contributes exactly 5 cases, all passing
4. `grep -r "prompt_governance/governance\|injections/misc\|prompt_governance/registry" **/*.py` → 0 results
5. All `EvaluationLoader` error paths exercised (missing file, malformed YAML, non-dict root, cache hit, clear_cache)
6. `BRANCH_INVENTORY` in evidence covers every new conditional

---

## Files Touched

| File | Action |
|---|---|
| `agentic_core/prompt_governance/core/evaluation_loader.py` | **New** |
| `agentic_core/prompt_governance/core/__init__.py` | **Edit** |
| `agentic_core/prompt_governance/__init__.py` | **Edit** |
| `tests/unit/test_prompt_evaluation_corpus.py` | **New** |
| `tests/architecture/test_injection_canon_completeness.py` | **New** |
| `data/prompt_governance/injections/misc/` | **Delete** (7 files) |
| `data/prompt_governance/governance/` | **Delete** (tree) |
| `data/prompt_governance/registry/` | **Delete** (empty) |

No changes to: any `apps_*` files, any existing test files, `pytest.ini`, `requirements.txt`.

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

