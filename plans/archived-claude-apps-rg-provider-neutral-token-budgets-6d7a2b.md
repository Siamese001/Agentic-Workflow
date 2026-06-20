---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\apps-rg-provider-neutral-token-budgets-6d7a2b.md'
original_relative_path: 'apps-rg-provider-neutral-token-budgets-6d7a2b.md'
source_sha256: 220bbf6112b4fd9098a0c4f5cc5e169af266de09da6486cc7430a42503f42d14
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps-rg Provider-Neutral Token Budgets

Plan ID: `apps-rg-provider-neutral-token-budgets-6d7a2b`
Status: Completed
Created: 2026-06-07
Notion: https://app.notion.com/p/37827693f55c814aaaaae493a39e6477

## Context

apps_rg section lanes now support `external_claude` alongside the historical `qwen_vllm` lane. Several section output-token constants still use `*_QWEN_MAX_TOKENS` names even though the same values are forwarded to provider-neutral request builders and the external Claude transport path.

The local vLLM context-window constants remain intentionally Qwen/vLLM-specific. `VLLM_MAX_MODEL_LEN` and `QWEN_LOCAL_MAX_MODEL_LEN` describe the served local model and should not be renamed in this wave.

## Status Tables

### Wave Progress

| Wave | Focus | Status |
|---|---|---|
| W1 | Rename provider-neutral section output budgets and verify focused contracts | Completed |

## Wave 1

### Scope

Rename apps_rg section output budget constants from Qwen-specific names to provider-neutral names:

- `HEADLINE_QWEN_MAX_TOKENS` -> `HEADLINE_MAX_OUTPUT_TOKENS`
- `UNIFY_QWEN_MAX_TOKENS` -> `UNIFY_MAX_OUTPUT_TOKENS`
- `IBM_QWEN_MAX_TOKENS` -> `IBM_MAX_OUTPUT_TOKENS`
- `NARRATIVE_QWEN_MAX_TOKENS` -> `NARRATIVE_MAX_OUTPUT_TOKENS`
- `COMPETENCIES_QWEN_MAX_TOKENS` -> `COMPETENCIES_MAX_OUTPUT_TOKENS`
- `APPS_RG_EXEC_SUMMARY_QWEN_MAX_OUTPUT_TOKENS` -> `APPS_RG_EXEC_SUMMARY_MAX_OUTPUT_TOKENS`
- `APPS_RG_EXEC_SUMMARY_QWEN_REGEN_MAX_OUTPUT_TOKENS` -> `APPS_RG_EXEC_SUMMARY_REGEN_MAX_OUTPUT_TOKENS`

The old executive-summary env names remain accepted as deprecated fallbacks during operator migration.

### Non-Goals

- Do not rename `VLLM_MAX_MODEL_LEN`, `QWEN_LOCAL_MAX_MODEL_LEN`, or vLLM serving profile limits.
- Do not alter token values or provider behavior.
- Do not remove Qwen/vLLM as a supported local provider.

### Verification

- Focused grep confirms no live code references to `*_QWEN_MAX_TOKENS`.
- Focused pytest covers local-vLLM max-model-length SSOT, apps_rg prompt budgeting, and provider-gateway Wave 10 routing.
- Diff review confirms only naming changed for output-token budgets.

### Outcome

Completed on 2026-06-07. Focused verification:

`python -m pytest -o addopts= tests/unit/agentic_core/L0_routing/config/test_max_model_len_ssot.py tests/unit/apps_rg/test_prompt_budget.py tests/unit/apps_rg/test_provider_gateway_wave10.py tests/unit/apps_rg/runtime/sections/test_executive_summary_context_limits.py tests/unit/apps_rg/test_executive_summary_token_budget_regen.py tests/_apps_contract/test_executive_summary_operator_guide_w3.py tests/_apps_contract/test_executive_summary_token_budget_contract.py -q`

Result: 36 passed, 1 skipped.
