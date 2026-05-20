# W11-M4C-FIX — Competencies canonical lane contract repair

**Generated:** 2026-05-19  
**Status:** PASS (superseded detail in [w11_closeout_and_next_plan_handoff.md](w11_closeout_and_next_plan_handoff.md))

## Receipt

```
STATUS: PASS
FILES_CHANGED:
- [competencies_dispatch.py](../../apps_rg/runtime/sections/competencies_lane_api.py)
- [test_competencies_canonical_lane_contract.py](../../tests/_apps_contract/test_competencies_canonical_lane_contract.py)
COMMANDS_RUN:
- git status --short -> scoped competencies files modified
- python -m compileall agentic_core apps_rg apps_shared apps_eval -q -> exit 0
- git grep x2_no_keyword_stuffing|41|42 -> located stale test + SRFS stub template
TESTS_RUN:
- test_competencies_canonical_lane_contract.py (2 failing tests) -> 2 passed
- test_competencies_canonical_lane_contract.py (full file) -> 10 passed
- tests -k "competencies and (canonical or lane or x2 or x3 or keyword)" -> 58 passed (collection errors unrelated)
- lane PA parity + canonical hygiene + deprecated quarantine -> 38 passed
ARTIFACTS_WRITTEN:
- [w11_m4c_competencies_contract_fix.md](w11_m4c_competencies_contract_fix.md)
- [w11_m4c_competencies_contract_fix.json](w11_m4c_competencies_contract_fix.json)
```

## ROOT_CAUSE

**failing_tests:**
- `test_canonical_lane_x2_gate_cardinality`
- `test_canonical_lane_mock_judge_x3_review_code`

**expected:**
- `total_x2_gates == 41`
- `x3_code == X3_REVIEW_MOCKED_PLUMBING_ONLY` (mock-judge plumbing path when X2 clean)

**actual:**
- `total_x2_gates == 42` with `failed_gates == ['x2_no_keyword_stuffing']`
- `x3_code == X3_BLOCK` (downstream of X2 failure)

**cause (two independent drifts):**

1. **Gate cardinality (41 → 42):** `append_section_input_usage_x2_gates` added section-input-usage gates after the contract test was authored (`5e2e1eba13`). Runtime count 42 is correct; test baseline 41 was stale.

2. **`x2_no_keyword_stuffing`:** Offline SRFS stub (`broad_skills_ledger` / `selected_role_fact_set` proof pool) used template phrases `governed capability cluster {i}a/b/c` across 8 categories. After deterministic repair, each category retained ≥2 terms still containing `governed`, `capability`, and `cluster` (16 repeats each). `reduce_competency_keyword_stuffing` cannot drop below 2 terms per category, so the gate legitimately failed. **Not** caused by M4C import-surface split (trace path and execution body unchanged).

## FIX_APPLIED

**files_changed:**
- `build_mock_output` SRFS branch: `_SRFS_STUB_TERM_TRIPLES` — eight category-specific phrase triples with no token repeating >5× globally.
- Contract test: `total_x2_gates` 41 → 42; assert `x2_no_keyword_stuffing` not in `failed_gates`.

**why_correct:**
- Fixes stub **output** quality for offline contract runs without changing gate thresholds or X3 policy.
- Aligns test cardinality with current `run_competencies_x2_gates` surface (42 gates).

**why_not_x2_weakening:**
- `x2_no_keyword_stuffing` threshold unchanged (`<=5 repeat non-stopword`).
- No gate disabled, no `pass` forced, no X3 override — X3 returns `X3_REVIEW_MOCKED_PLUMBING_ONLY` only because X2 now passes under stub.

## COMPETENCIES_RESULT

| Check | Result |
|-------|--------|
| failing_tests_now | 0 |
| x2_gate_count | 42 |
| x2_no_keyword_stuffing | PASS |
| x3_result | `X3_REVIEW_MOCKED_PLUMBING_ONLY` |

## REGRESSION_RESULT

- Full competencies canonical contract: **10/10 passed**
- Safety regression (parity + hygiene + quarantine): **38/38 passed**

## UPDATED_COUNTS

Unchanged (no archive/matrix mutation): `archived=1`, `delete_ready=0`, `archive_ready=0`, `migration_required=8`, `blocked=12`

## BEHAVIOR_CHANGE

false — offline stub fixture phrases only; live provider path untouched.

## RUNTIME_CHANGE

none for product/live paths.

## NEXT_RECOMMENDED_ACTION

Resume W11 fast-blocker burn follow-ups (M3.5 Rg* string migration; dispatch execution shrink) — competencies contract seam is green.

## EXPLICIT_NON_CLAIMS

- no files deleted
- no archive moves
- no X2/X3 weakened
- no live apps_rg proof
- no broad refactor
