---
plan_id: headline-fixed-prefix-refactor-c8e3b1
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: true
---

# Headline prompt fixed-prefix refactor (retrospective)

**Completed work:** apps_rg headline lane now enforces resume headline shape `SVP Engineering | X | Y | Z` (four segments, three ` | ` separators, 10–13 words), JSON-only R0 output with expanded `jd_alignment` / `self_check`, Anthropic-style XML slotting in `headline_tailor_v1.yaml`, stricter X2 deterministic gates (incl. briefing-not-proof and keyword-stuffing heuristic), X1D rubric `headline_x1d_v2`, dispatch mock + normalize/padding alignment. **`agentic_core` not in scope.**

> **plan_id** matches filename stem. Retrospective plan: execution already finished; this file records intent, scope, and evidence.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1  
PLAN_STATUS: COMPLETED  
CURRENT_WAVE: W1  
LAST_COMPLETED_WAVE: W1  
LAST_UPDATED: 2026-05-17

---

## Context (SCQA)

- **Situation** — Headline generation needed a fixed identity prefix, proof hierarchy (facts only; JD/briefing targeting-only), and deterministic gates/tests aligned with product contract.
- **Complication** — Prior three-segment / looser word-band prompts and validators did not match the SVP Engineering lead + four-segment + 10–13 word JSON contract.
- **Question** — How do we lock prompts, dispatch repair/padding, X1D, and X2 to the fixed-prefix contract without weakening gates or polluting core?
- **Answer** — Refactor template + PA schema copy, tighten `headline_x2.py`, bump `headline_x1d.py` rubric, adjust dispatch mock/normalize; keep all changes under `apps_rg` and tests.

---

## Status Tables (archival)

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | Template, dispatch, X2, X1D, tests, evidence bundle | ✅ DONE | X2 contract tests + slice updates | 9 paths |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Prompt YAML + `headline_pa` / R0 JSON contract | ✅ DONE |
| W1.2 | `headline_dispatch` mock, normalize, padding, repair strings | ✅ DONE |
| W1.3 | `headline_x2` + `headline_x1d` | ✅ DONE |
| W1.4 | Contract tests + closeout diff artifact | ✅ DONE |

---

## Files touched (scope)

- `apps_rg/prompt_assembly/templates/headline_tailor_v1.yaml`
- `apps_rg/runtime/dispatch/headline_dispatch.py`
- `apps_rg/runtime/dispatch/headline_pa.py`
- `apps_rg/runtime/validators/headline_x2.py`
- `apps_rg/runtime/judges/headline_x1d.py`
- `tests/_apps_contract/test_headline_runtime_slice.py`
- `tests/_apps_contract/test_headline_pa_compiled_prompt.py`
- `tests/_apps_contract/test_apps_rg_exit_g21_g22.py`
- `tests/unit/apps_rg/validators/test_headline_x2_fixed_prefix_contract.py`

---

## Evidence (SSOT)

- Full unified diff: `artifacts/apps_rg/headline_fixed_prefix/headline_fixed_prefix_full_diff.patch`
- Closeout: `artifacts/apps_rg/headline_fixed_prefix/headline_fixed_prefix_closeout.md`

---

## Verification (post-merge smoke)

```bash
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest -p pytest_timeout tests/unit/apps_rg/validators/test_headline_x2_fixed_prefix_contract.py tests/_apps_contract/test_headline_pa_compiled_prompt.py tests/_apps_contract/test_headline_runtime_slice.py tests/_apps_contract/test_apps_rg_exit_g21_g22.py -q --tb=short
python -m apps_rg.runtime.dispatch.headline_dispatch --provider mock --mock-judges --allow-non-allow-exit-zero
```

**Expect:** 45 tests pass; mock run X2 all PASS; `x3_code` = `X3_REVIEW_MOCKED_PLUMBING_ONLY` (not `X3_ALLOW`).

---

## Out of scope

- `agentic_core` changes
- Non-headline apps_rg lanes
- Weakening X2 or generic Exit modules

---

## Definition of Done (retrospective)

| # | Criterion | Met |
|---|-----------|-----|
| 1 | Fixed-prefix contract documented in template + PA | ✅ |
| 2 | X2 enforces prefix, separators, word band, stuffing heuristic, briefing flag | ✅ |
| 3 | X1D v2 rubric text aligned | ✅ |
| 4 | Tests + mock dispatch green | ✅ |
| 5 | Durable diff/closeout artifacts under `artifacts/apps_rg/headline_fixed_prefix/` | ✅ |

---

PLAN_COMPLETE: headline-fixed-prefix-refactor-c8e3b1
