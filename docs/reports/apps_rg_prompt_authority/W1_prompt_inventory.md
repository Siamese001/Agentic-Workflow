# W1 — Prompt inventory and gap classification (W0–W3 tranche)

## Surfaces scanned

Representative roots per program doc:

- `apps_rg/prompt_assembly/templates/*.yaml`
- `apps_rg/prompt_assembly/section_contracts/*.yaml`
- `apps_rg/prompt_assembly/examples/*.yaml`, `rubrics/*.yaml`
- `forbidden_ai_phrases.yaml`, `jd_calibration_contract.yaml`
- `apps_rg/runtime/dispatch/*_dispatch.py`
- `prompt_registry.yaml`, `prompt_bom.yaml`, `spine_manifest.yaml` (read-only classification)

## Classification deliverable

Machine-readable: `artifacts/apps_rg/prompt_authority/template_classification.json`  
Runtime inline-authority map: `artifacts/apps_rg/prompt_authority/runtime_bypass_map.json`

## Inline `build_prompt_messages` (active dispatch)

| File | Classification |
|------|----------------|
| `apps_rg/runtime/sections/competencies_lane_api.py` | INLINE_BUILD_PROMPT_MESSAGES → adapter W5 |
| `apps_rg/runtime/sections/executive_summary_lane_api.py` | INLINE_BUILD_PROMPT_MESSAGES → adapter W4 |
| `apps_rg/runtime/dispatch/headline_dispatch.py` | INLINE_BUILD_PROMPT_MESSAGES → adapter W6 |
| `apps_rg/runtime/sections/ibm_bullets_lane_api.py` | Import-only re-export shim → canonical lane ``ibm_bullets_lane`` + PA adapter W7 |
| `apps_rg/runtime/sections/ibm_narrative_lane_api.py` | INLINE_BUILD_PROMPT_MESSAGES → adapter W7 |
| `apps_rg/runtime/sections/unify_bullets_lane_api.py` | INLINE_BUILD_PROMPT_MESSAGES → adapter W7 |
| `apps_rg/runtime/sections/unify_narrative_lane_api.py` | INLINE_BUILD_PROMPT_MESSAGES → adapter W7 |

Slice tests may import `build_prompt_messages` for shape checks — see `runtime_bypass_map.json`.

## Registry vs on-disk gaps (examples)

Several dispatch-backed templates (headline, executive summary scratch, IBM, unify bullets/narrative, competencies) exist on disk but are **not** top-level `templates:` keys in `prompt_registry.yaml` today — tracked as `RUNTIME_UNREGISTERED` in `template_classification.json` for W9 integrity work. **No registry edits in this pass.**
