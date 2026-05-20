# Executive Summary Targeting Cap — Live Runtime Proof Receipt

STATUS: PASS (LIVE_RUNTIME_PROOF)  
SCOPE_MATCH: executive_summary capsule-mode targeting-only JD/briefing cap + token budget  
SCOPE_DRIFT: none

## LATEST_RUN_DIR

[exec_summary_20260520_144839](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_144839)

## EVIDENCE_CAPSULE_RECEIPT_PATH

[evidence_capsule_receipt.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_144839/evidence_capsule_receipt.json)

## TOKEN_BUDGET_RECEIPT_PATH

[token_budget_receipt.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_144839/token_budget_receipt.json)

## TARGETING_CAP_SUMMARY

| Field | Value |
|-------|------:|
| targeting_cap_applied | true |
| targeting_cap_strategy | `executive_summary_capsule_mode_targeting_cap_v1` |
| targeting_tokens_before_cap | 4708 |
| targeting_tokens_after_cap | 943 |
| jd cap | 1640 → 212 est. tokens |
| manual_briefing cap | 2623 → 285 est. tokens |
| trim_applied after cap | false (not needed) |

## TOKEN_BUDGET_SUMMARY

| Field | Value |
|-------|------:|
| status | **PASS** |
| capsule_applied | true |
| before_capsule_prompt_estimate | 24184 |
| after_capsule_prompt_estimate | 17519 |
| after_targeting_cap_prompt_estimate | **13753** |
| available_input_tokens | 14848 |
| forbidden_trim_violations | [] |
| evidence_contract_preserved | true |

## PROVIDER_DISPATCH_OCCURRED

**yes** — `provider_attempted: true`, `real_llm_used: true`, non-empty `raw_model_output` in [provider_response.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_144839/provider_response.json)

## PROVIDER_REQUEST_PROOF

[max_tokens=1024](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_144839/provider_request.json), `compiled_prompt_tokens_after_trim=13753` ≤ `available_input_tokens=14848`, `mock_fallback_allowed=false`

## PROVIDER_RESPONSE_PROOF

REAL_LLM JSON output with `resume_display_text` and `claim_ledger` rows citing allowed fact IDs.

## X2_RESULT

**Product quality PASS** — all deterministic gates passed including SRFS sentence count, density, responsibility shape.

## X3_RESULT

**X3_BLOCK** — decisive X1D judge failures (gemini_pro, anthropic_claude); not generation plumbing failure.

## PROOF_CLASSIFICATION

**LIVE_RUNTIME_PROOF** — capsule + targeting cap cleared 16k budget; Qwen dispatched; X2 PASS.

## EXPLICIT_NON_CLAIMS

- Not RELEASE_ELIGIBLE_PROOF (`proof_eligible: false`, X3_BLOCK on judges)
- Not X3 ALLOW
