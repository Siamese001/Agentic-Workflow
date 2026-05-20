# Live Qwen pre-dispatch + executive_summary dispatch proof

## STATUS: PARTIAL

Preflight and live Qwen dispatch proved. X3 is **not** ALLOW (judge soft-fail). Process exit **1** is expected without `--allow-non-allow-exit-zero`.

## SCOPE_MATCH

Canonical `python -m apps_rg --section executive_summary` only; no offline stub; no mock provider; no `--allow-non-allow-exit-zero`.

## COMMANDS_RUN

```text
python -m apps_rg \
  --section executive_summary \
  --target-company "CI Probe Company" \
  --target-role "CI Probe Role" \
  --jd tests/_fixtures/ci-probe-jd.txt \
  --manual-brief tests/_fixtures/ci-probe-briefing.txt
```

| Result | Value |
|--------|-------|
| Exit code | **1** |
| Env | `APPS_RG_QWEN_OFFLINE_CONTRACT_STUB` unset; `APPS_RG_ALLOW_NON_ALLOW_EXIT_ZERO` unset |

Stdout preflight line:

```text
pre_dispatch_preflight: dispatch_started=True jd_status=PASS manual_brief_status=PASS qwen_health=PASS qwen_model_ready=PASS
APPS_RG_QWEN_LIVE provider=qwen_vllm base_url=http://localhost:8000/… restart=disabled probe=pass
```

## PREFLIGHT_RECEIPT

| Field | Value |
|-------|-------|
| path | [pre_dispatch_executive_summary_20260520_085831.json](artifacts/apps_rg/preflight_receipts/pre_dispatch_executive_summary_20260520_085831.json) |
| jd_status | PASS |
| manual_brief_status | PASS |
| provider_resolution_source | DEV_DEFAULT_QWEN_VLLM |
| qwen_health_status | PASS |
| qwen_model_ready_status | PASS |
| dispatch_started | **true** |

## LATEST_RUN_DIR

[exec_summary_20260520_125832](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832)

## ARTIFACTS_INSPECTED

| Artifact | Present | Notes |
|----------|---------|-------|
| [run_manifest.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/run_manifest.json) | yes | `runtime_generation_status=REAL_LLM`, `provider_attempted=true`, `test_only_mock_provider=false` |
| [compiled_prompt_artifact.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/compiled_prompt_artifact.json) | yes | SRFS-bound prompt; `proof_source=srfs` |
| [provider_request.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/provider_request.json) | yes | `mock_fallback_allowed=false`, model `Qwen/Qwen2.5-32B-Instruct-AWQ` |
| [provider_response.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/provider_response.json) | yes | Live chat completion; `runtime_generation_status=REAL_LLM` |
| [x2_gate_outputs.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/x2_gate_outputs.json) | yes | `x2_passed=68`, `x2_failed=0`, `failed_gates=[]` |
| [x3_disposition.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/x3_disposition.json) | yes | `X3_REVIEW_JUDGE_SOFT_FAIL` |
| [section_metric_receipt.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/section_metric_receipt.json) | yes | `product_quality_status=PASS`, `x2_srfs_gate_status=PASS` |
| [l6_shadow_eval_package.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/l6_shadow_eval_package.json) | yes | `offline_only=true`; shadow handoff only |

## RUNTIME_FINDINGS

**Provider actually called:** yes — `qwen_vllm` → `http://localhost:8000/v1`, model `Qwen/Qwen2.5-32B-Instruct-AWQ`, `provider_available=true`, no `exact_provider_error`.

**Generated output preview** (from [l2_output.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/l2_output.json)):

> Engineering executive building governed agentic AI platforms for regulated enterprise environments. Designs and operationalizes deterministic routing, multi-agent orchestration, GraphRAG retrieval, sandboxed execution, policy gating, and validation controls for regulated enterprise workflows. Leads platform lifecycle across architecture, operating model, and engineering scale-out…

**X2 status:** PASS — 68/68 gates, `product_quality_status=PASS`, `x2_no_silent_mock_fallback` PASS.

**X3 disposition:** `X3_REVIEW_JUDGE_SOFT_FAIL` — `pass=false`, `authorization_scope=REVIEW_ONLY`, `proceed_to_runtime=false`.

**X3 blocker:** `anthropic_claude` soft-failed (score 3.5 vs threshold 4.0). Gemini Pro and OpenAI ChatGPT passed. Not a pre-dispatch or Qwen transport failure.

## PROOF_CLASSIFICATION

| Class | Met |
|-------|-----|
| **LIVE_QWEN_PREFLIGHT_AND_DISPATCH_PROOF** | **yes** — preflight PASS, dispatch_started=true, REAL_LLM provider_response on disk |
| **LIVE_RUNTIME_X3_ALLOW_PROOF** | **no** — X3 is REVIEW soft-fail, not ALLOW |

Overall: **PARTIAL** — live pre-dispatch + generation proved; product authorization blocked on X1D soft-fail.

## EXPLICIT_NON_CLAIMS

- **X3_ALLOW** not claimed — artifact shows `X3_REVIEW_JUDGE_SOFT_FAIL`.
- **Release eligibility** not claimed — `proof_eligible=false`, `NOT_RELEASE_SIGNOFF=true` in CLI report.
- **Full R4 coverage** not claimed — section lane only.
- **DEV_DEFAULT_MOCK** not used — resolution label is `DEV_DEFAULT_QWEN_VLLM` (default lane provider name for `qwen_vllm`, not mock transport).

## FORBIDDEN

- No code changes (no defect in pre-dispatch gates).
- No smoke/dispatch substitution.
- No offline stub.
- No mock fallback (`mock_fallback_allowed=false`, `x2_no_silent_mock_fallback` PASS).
