# Executive Summary Token Budget v2 — Brown & Brown LIVE_BLOCK_PROOF

STATUS: PASS (LIVE_BLOCK_PROOF only)  
SCOPE_MATCH: executive_summary lane, v2 optional-only token budget, default 16k VLLM context  
SCOPE_DRIFT: none — proof-only wave, no code changes

## FILES_CHANGED

- [executive_summary_token_budget_v2_live_block_proof_receipt.md](docs/reports/apps_rg/executive_summary_token_budget_v2_live_block_proof_receipt.md) (this receipt)

## COMMANDS_RUN

| Command | Exit code |
|---------|----------:|
| `$env:APPS_RG_EXEC_SUMMARY_MAX_OUTPUT_TOKENS='1024'; python -m apps_rg --section executive_summary --target-company "Brown & Brown" --target-role "Senior Vice President, IT Strategy & Innovation" --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.txt` | **0** (CLI inspection path; L2 generation **BLOCKED**) |

No `--allow-non-allow-exit-zero` used.

## LATEST_RUN_DIR

[exec_summary_20260520_142647](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_142647)

Supersedes invalid v1 proof: [exec_summary_20260520_134924](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_134924) (`executive_summary_deterministic_priority_trim_v1`, REAL_LLM dispatch).

## TOKEN_BUDGET_RECEIPT_PATH

[token_budget_receipt.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_142647/token_budget_receipt.json)

## TOKEN_BUDGET_SUMMARY

| Field | Value |
|-------|------:|
| status | **FAIL** |
| trim_strategy | `executive_summary_optional_trim_only_v2` |
| provider_context_window | 16384 |
| requested_max_output_tokens | 1024 |
| available_input_tokens | 14848 |
| compiled_prompt_tokens_before_trim | 24184 |
| compiled_prompt_tokens_after_trim | 21985 |
| trim_applied | true (E0 + Y0 only) |
| evidence_contract_digest_before | `5d8388cf32234230` |
| evidence_contract_digest_after | `5d8388cf32234230` |
| evidence_contract_preserved | true |
| prompt_shape_preserved | true |
| forbidden_trim_violations | **[]** |
| dispatch_allowed | false |
| fail_closed_reason | **TOKEN_BUDGET_EXCEEDED_AFTER_TRIM** |

Protected labels in receipt: `system`, `response_schema`, `evidence_law`, `allowed_source_fact_ids`, `selected_role_fact_set`, `claim_ledger_rules`, `jd_targeting_only_rule`.

Optional trims applied: `e0_examples`, `y0_style_preferences` only — **no** `srfs_style_only_oneshot`, **no** `i0_instructions`, **no** global R0 style XML trim.

## BLOCK_REASON

`L2_BLOCK:TOKEN_BUDGET_EXCEEDED_AFTER_TRIM` — recorded in [real_l2_generation_result.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_142647/real_l2_generation_result.json), [l2_output.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_142647/l2_output.json), [runtime_payload.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_142647/runtime_payload.json) (`token_budget_policy`).

## PROVIDER_DISPATCH_OCCURRED

**no** — [run_manifest.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_142647/run_manifest.json): `provider_attempted: false`, `runtime_generation_status: BLOCKED`. [proof_eligibility_receipt.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_142647/proof_eligibility_receipt.json): `real_llm_used: false`, `provider_classification: blocked`.

## PROVIDER_REQUEST_EXISTS

**yes** (block stub, not transport) — [provider_request.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_142647/provider_request.json): `blocked_before_dispatch: true`, `provider_attempted: false`, `mock_fallback_allowed: false`.

## PROVIDER_RESPONSE_EXISTS

**yes** (block stub, not model output) — [provider_response.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_142647/provider_response.json): `raw_model_output: ""`, `token_budget_blocked: true`, `stub: false`.

## PROVIDER_RESPONSE_RAW_MODEL

**empty** — no [raw_model_output.txt](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_142647/raw_model_output.txt) in bundle.

## COMPILED_PROMPT_INTEGRITY

[compiled_prompt.txt](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_142647/compiled_prompt.txt) retains full E0 examples, `SRFS_FIVE_PART_EXEC_ARCH_V1`, `<srfs_style_only_oneshot>`, INPUT_AUTHORITY `ALLOWED_SOURCE_FACT_IDS`, and R0 schema JSON — **no** `E0 compressed`, `I0 compressed`, or `OMITTED_FOR_TOKEN_BUDGET` markers (fail path does not apply trimmed prompt to artifacts).

## X2_X3_ARTIFACTS

| Artifact | Result |
|----------|--------|
| [x3_disposition.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_142647/x3_disposition.json) | **X3_BLOCK** — decisive: X2 deterministic gate failure (empty generation) |
| [x2_gate_outputs.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_142647/x2_gate_outputs.json) | Product quality FAIL; token gates **PASS**: `x2_no_silent_mock_fallback`, `x2_qwen_provider_stub_transport_zero` |
| X1D judges | Ran on empty/stub input (scores 0) — not generation proof |

## PROOF_CLASSIFICATION

**LIVE_BLOCK_PROOF** — v2 fail-closed before Qwen on Brown & Brown at default 16k.

## FORBIDDEN_FILES_TOUCHED

- agentic_core: **none**
- Unrelated lanes: **none**
- Judge thresholds / SRFS gates: **none**
- Mock fallback: **none**

## EXPLICIT_NON_CLAIMS

- **Not** LIVE_RUNTIME_PROOF (no Qwen generation).
- **Not** RELEASE_ELIGIBLE_PROOF.
- **Not** REAL_LLM for executive_summary generator.
- Shell exit code 0 is CLI inspection semantics only; `runtime_generation_status` is **BLOCKED**.
- X1D judge artifacts exist for plumbing; they do not constitute successful product generation.

## v1 vs v2 contrast (same Brown inputs)

| Run | Policy | Receipt status | After trim (est.) | Qwen dispatch |
|-----|--------|----------------|-------------------|---------------|
| exec_summary_20260520_134924 | v1 aggressive | PASS | 11525 | yes (REAL_LLM) |
| exec_summary_20260520_142647 | v2 optional-only | FAIL | 21985 | **no** |
