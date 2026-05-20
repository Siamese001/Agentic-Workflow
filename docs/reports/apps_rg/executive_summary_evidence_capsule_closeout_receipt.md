# Executive Summary Evidence Capsule — Closeout Receipt

STATUS: PASS (CONTRACT_TEST_PROOF + LIVE_BLOCK_PROOF with capsule)  
SCOPE_MATCH: executive_summary SRFS evidence capsule + token budget integration  
SCOPE_DRIFT: none (no agentic_core, no judge thresholds, no unrelated lanes)

## FILES_CHANGED

- [executive_summary_evidence_capsule.py](apps_rg/runtime/sections/executive_summary_evidence_capsule.py)
- [executive_summary_pa.py](apps_rg/runtime/sections/executive_summary_pa.py)
- [executive_summary_lane.py](apps_rg/runtime/sections/executive_summary_lane.py)
- [executive_summary_token_budget.py](apps_rg/runtime/sections/executive_summary_token_budget.py)
- [test_executive_summary_evidence_capsule.py](tests/unit/apps_rg/runtime/sections/test_executive_summary_evidence_capsule.py)
- [test_executive_summary_evidence_capsule_contract.py](tests/_apps_contract/test_executive_summary_evidence_capsule_contract.py)

## COMMANDS_RUN

| Command | Exit code |
|---------|----------:|
| `python -m pytest tests/unit/.../test_executive_summary_evidence_capsule.py tests/_apps_contract/test_executive_summary_evidence_capsule_contract.py tests/unit/.../test_executive_summary_token_budget.py tests/_apps_contract/test_executive_summary_token_budget_contract.py -q` | 0 — **14 passed**, 1 skipped |
| `$env:APPS_RG_EXEC_SUMMARY_QWEN_MAX_OUTPUT_TOKENS='1024'; python -m apps_rg --section executive_summary ...` (Brown & Brown) | 0 — L2 **BLOCKED** `TOKEN_BUDGET_EXCEEDED_AFTER_TRIM` |

## TESTS_GATES

- HIGH facts preserved in capsule — PASS  
- allowed_fact_ids exact (no normalization) — PASS  
- style-only SRFS prose excluded when capsule active — PASS  
- capsule digest deterministic — PASS  
- PA retains evidence law / allowed IDs / JD-not-proof — PASS  
- token budget v2 tests — PASS (regression)

## LATEST_RUN_DIR

[exec_summary_20260520_144110](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_144110)

## EVIDENCE_CAPSULE_RECEIPT_PATH

[evidence_capsule_receipt.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_144110/evidence_capsule_receipt.json)

## EVIDENCE_CAPSULE_SUMMARY

| Field | Value |
|-------|------:|
| status | PASS |
| capsule_version | `executive_summary_evidence_capsule_v1` |
| preserved_high_fact_ids | 7/7 |
| dropped_high_fact_ids | [] |
| source_fact_id_preservation_status | PASS |
| metric_anchor_preservation_status | PASS |
| capsule_reduction_estimate | **22608** (prompt-level est. vs verbose SRFS) |
| optional_content_removed | srfs oneshot, exemplar, style contrast, verbose appendix |

## TOKEN_BUDGET_RECEIPT_PATH

[token_budget_receipt.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_144110/token_budget_receipt.json)

## TOKEN_BUDGET_SUMMARY

| Field | Value |
|-------|------:|
| status | FAIL |
| capsule_applied | true |
| before_capsule_prompt_estimate | 24184 |
| after_capsule_prompt_estimate | 17519 |
| after_optional_trim_estimate | 15320 |
| available_input_tokens | 14848 |
| fail_closed_reason | TOKEN_BUDGET_EXCEEDED_AFTER_TRIM |
| evidence_contract_preserved | true |
| forbidden_trim_violations | [] |

Capsule removed ~**6.7k** est. tokens; optional E0/Y0 trim removed ~**2.2k** more; still ~**472** est. tokens over 16k budget (JD/briefing targeting block dominates remainder).

## PROVIDER_DISPATCH_OCCURRED

**no** — `provider_attempted: false`, `real_llm_used: false`

## PROVIDER_REQUEST_PROOF

[block stub](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_144110/provider_request.json): `blocked_before_dispatch: true`, `fail_closed_reason: TOKEN_BUDGET_EXCEEDED_AFTER_TRIM`

## X2_RESULT

Product quality **FAIL** (empty generation) — expected for block path.

## X3_RESULT

**X3_BLOCK** — X2 failure on blocked run; not token-budget regression.

## PROOF_CLASSIFICATION

- **CONTRACT_TEST_PROOF** — unit + contract pytest  
- **LIVE_BLOCK_PROOF** — Brown canonical CLI with capsule + token budget receipts; no protected evidence loss  
- **Not** LIVE_RUNTIME_PROOF (still over 16k after capsule + optional trim)  
- **Not** RELEASE_ELIGIBLE_PROOF

## FORBIDDEN_FILES_TOUCHED

- agentic_core: **none**  
- Unrelated lanes: **none**  
- Judge thresholds / mock fallback: **none**

## EXPLICIT_NON_CLAIMS

- Qwen did not generate executive summary text on this run.  
- Capsule alone does not yet fit Brown briefing+JD in 14848 available input tokens; further targeting-only briefing compression or larger `VLLM_MAX_MODEL_LEN` would be a separate seam.  
- SRFS arc contract is carried via compact markers + S0/I0/X2 gates, not full style-onshot prose (by design).

## Disable capsule (debug)

`APPS_RG_EXEC_SUMMARY_EVIDENCE_CAPSULE=0`
