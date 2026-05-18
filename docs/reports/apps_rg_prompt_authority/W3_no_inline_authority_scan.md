# W3 — Report-only: active `build_prompt_messages` paths (no gate)

**Purpose:** inventory for W10 strict enforcement (`test_apps_rg_no_inline_prompt_authority`).  
**Policy this pass:** list only — **do not fail** CI or gates on this scan.

## Definitions (`def build_prompt_messages`)

| Path | Notes |
|------|--------|
| `apps_rg/runtime/dispatch/competencies_dispatch.py` | Primary inline prompt assembly seam for competencies (**not** a product CLI; canonical entry `python -m apps_rg --section competencies`) |
| `apps_rg/runtime/dispatch/executive_summary_dispatch.py` | Primary inline prompt assembly for executive summary lane |
| `apps_rg/runtime/dispatch/headline_dispatch.py` | Primary inline prompt assembly for headline lane |
| `apps_rg/runtime/dispatch/ibm_bullets_dispatch.py` | Import-only shim; canonical IBM bullets prompt assembly in ``sections/ibm_bullets_lane.py`` |
| `apps_rg/runtime/dispatch/ibm_narrative_dispatch.py` | Primary inline prompt assembly IBM narrative |
| `apps_rg/runtime/dispatch/unify_bullets_dispatch.py` | Primary inline prompt assembly Unify bullets |
| `apps_rg/runtime/dispatch/unify_narrative_dispatch.py` | Primary inline prompt assembly Unify narrative |

## Test-only imports (reference)

- `tests/_apps_contract/test_exec_summary_runtime_slice.py` — imports `build_prompt_messages` for structural/runtime slice checks (not an active dispatch module).

## Adapter status (W3)

- `apps_rg/runtime/bindings/section_prompt_adapter.py` added — **no** dispatch module imports it yet (see `tests/_apps_contract/test_apps_rg_section_prompt_adapter.py`).
