# Executive Summary Token Budget Policy — Closeout Receipt

STATUS: PASS  
SCOPE_MATCH: executive_summary lane pre-dispatch optional-only prompt budgeting  
SCOPE_DRIFT: none (no agentic_core, no judge thresholds, no provider substitution)

## Invariant (user rule)

Token trimming must **never silently alter** the evidence contract or generation prompt shape (SRFS arc, I0 sovereign regions, R0 response schema JSON, HIGH fact lines, `ALLOWED_SOURCE_FACT_IDS`). If optional trims cannot fit the budget, **block before Qwen** with `TOKEN_BUDGET_EXCEEDED_AFTER_TRIM` — do not dispatch a shape-degraded prompt.

Policy id: `executive_summary_optional_trim_only_v2`

## FILES_CHANGED

- [executive_summary_token_budget.py](apps_rg/runtime/sections/executive_summary_token_budget.py)
- [executive_summary_lane.py](apps_rg/runtime/sections/executive_summary_lane.py)
- [test_executive_summary_token_budget.py](tests/unit/apps_rg/runtime/sections/test_executive_summary_token_budget.py)
- [test_executive_summary_token_budget_contract.py](tests/_apps_contract/test_executive_summary_token_budget_contract.py)

## COMMANDS_RUN

| Command | Result |
|---------|--------|
| `python -m pytest tests/unit/apps_rg/runtime/sections/test_executive_summary_token_budget.py tests/_apps_contract/test_executive_summary_token_budget_contract.py -q` | 0 — **8 passed**, 1 skipped (live gate) |

## TESTS_GATES

- Optional-only trim preserves evidence digest + SRFS shape markers — **PASS**
- Brown-scale / oversized briefing blocks on 16k window (`TOKEN_BUDGET_EXCEEDED_AFTER_TRIM`) — **PASS**
- No global trim of SRFS style blocks inside R0 (regression: v1 falsely trimmed exemplar/contrast in R0) — **PASS**
- Contract receipt + `mock_fallback_allowed=false` on PASS path — **PASS**

## Allowed trims (optional only)

- E0 slot (style examples)
- Y0 slot (style preferences)
- JD/briefing prose (targeting-only)
- C0 optional non-protected fact lines

## Forbidden (never applied on success path)

- SRFS one-shot stub / I0 compression / R0 prose replacement
- Global XML trim of `<exemplar_paragraph>`, `srfs_style_contrast_*`, `srfs_suggested_target_shape` (these compile **inside R0** for SRFS)

## Fail-closed reasons

| Reason | When |
|--------|------|
| `TOKEN_BUDGET_EXCEEDED_AFTER_TRIM` | Still over budget after optional-only trim |
| `EVIDENCE_CONTRACT_OR_PROMPT_SHAPE_ALTERED` | Digest or shape check failed (internal guard; should not fire if only optional slots trimmed) |

## Brown & Brown on default 16k VLLM

Minimal SRFS compile ≈ **19k** estimated input tokens; with `max_output=1024` and `reserved=512`, **available ≈ 14848**. Expect **FAIL + block before Qwen** under v2 (by design). Prior v1 live run `exec_summary_20260520_134924` used aggressive trim and reached Qwen but hit X3_BLOCK on SRFS quality — not a token-budget success for product.

## ARTIFACTS

- Receipt template fields: `evidence_contract_digest_before/after`, `prompt_shape_preserved`, `dispatch_allowed`, `shape_altering_trim_forbidden`
- Live receipt (v1 run, superseded policy): [token_budget_receipt.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_134924/token_budget_receipt.json)

## EXPLICIT_NON_CLAIMS

- X3 ALLOW not achieved on prior live runs (quality/X2 blockers).
- Exact tokenizer parity with vLLM (estimate labeled approximate in receipt).
- Live Brown re-run under v2 not executed in this closeout (set `APPS_RG_EXEC_SUMMARY_LIVE_TOKEN_BUDGET=1` for contract live gate).
