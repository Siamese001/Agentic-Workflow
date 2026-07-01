# ProceduralPattern:AppsRgResidualSSOTRepair

```json
{
  "entities": [{
    "name": "ProceduralPattern:AppsRgResidualSSOTRepair",
    "entityType": "ProceduralPattern",
    "observations": [
      "Fixes residual SSOT drift after apps_rg model-pin repair: fresh briefing lane fallbacks, BGE embedding dimension mirrors, mandatory run-output filenames, and apps_lic research/model profile mirrors.",
      "For fresh briefing regressions, inspect `apps_rg/runtime/spine/section_cli_runners.py`; whole-run sections must resolve through `_resolve_section_briefing_for_spine` and fail closed when `APPS_RG_WHOLE_RUN_ENVELOPE` or `APPS_RG_CORRELATED_CLI_RUN` is set.",
      "For embedding drift, `config/model_catalog.json` plus `agentic_core.config.model_catalog.BGE_M3_EMBEDDING_DIMENSION` are the SSOT; runtime constants such as `BGE_QUERY_DIM`, `EXPECTED_BGE_DIMENSION`, `BGE_M3_DIM`, and zero-vector fallback lengths must alias the catalog export.",
      "For run-output filenames, `apps_rg/runtime/run_output_contract.py` is the SSOT; emitters and `tools/apps_rg/render_run_summary.py` must import from it instead of hardcoding mandatory artifact names.",
      "For apps_lic drift, `apps_lic/config/domain_contract/model_profiles.yaml` is fail-closed via `apps_lic/config/model_profiles.py`, and research terminal codes live in `apps_lic/integrations/research_reason_codes.py` with legacy modules re-exporting names only.",
      "Guard against the next-session misread: do not reintroduce Python fallback dictionaries that mirror YAML, and do not treat standalone lane `BRIEFING_DEFAULT` behavior as acceptable inside a correlated whole-run.",
      "discovered: 2026-07-01, validated: 2026-07-01"
    ]
  }]
}
```
