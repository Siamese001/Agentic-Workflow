# Executive summary graph-only generation — blocker report (Wave 3)

**Previous status:** FAIL (validator) / PARTIAL (graph-only authority PASS, runtime BLOCKED)

**Latest run:** [exec_summary_20260519_101306](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_101306)

## Exact root cause

The `local-qwen-vllm` Docker container was **stopped** (`Exited (137)`). The canonical Qwen slice performs a fail-closed HTTP `GET /v1/models` preflight before any chat completion. With nothing listening on `localhost:8000`, preflight fails and L2 records `runtime_generation_status=BLOCKED`.

This is **not** a graph-only authority defect, mock provider, smoke dispatch, or base-résumé/old-ledger authority leak.

## Primary failing check

| Field | Expected | Actual |
|-------|----------|--------|
| Validator `runtime_generation_real_llm` | `REAL_LLM` | `BLOCKED` |
| `provider_response.runtime_generation_status` | `REAL_LLM` | `BLOCKED` |
| `run_manifest.runtime_generation_status` | `REAL_LLM` | `BLOCKED` |

## Source localization

| Layer | File | Mechanism |
|-------|------|-----------|
| Preflight gate | [section_qwen_slice.py](apps_rg/runtime/providers/section_qwen_slice.py) `call_qwen_vllm` | `ensure_http_preflight_and_banner_for_slice` → returns `BLOCKED` when `/v1/models` fails |
| Error text | [provider_response.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_101306/provider_response.json) | `http_v1_models_probe_failure` |
| Infrastructure | Docker `local-qwen-vllm` | Container not running |

## Cascade failures (secondary — empty model output)

X2 gates failed because **no LLM output** was produced (`raw_model_output=""`):

- `x2_schema_valid` — no JSON
- `x2_claim_ledger_present` — empty
- `x2_json_parse_valid`, `x2_required_fields_complete`, etc.

X3: `X3_BLOCK` with `decisive_reason: X2 deterministic gate failure`.

## Preserved at failure (graph-only proof)

- `proof_pool_type=augmented_skills_graph`
- `c03_graphrag_bound_status=BOUND`, 39 `graph_expansion_refs`
- `broad_skills_ledger_used=false`, base_resume `DEPRECATED_NON_AUTHORITY`
- `mock_provider_flags=[]`, `smoke_dispatch_reference_count=0`

## `DEV_DEFAULT_QWEN_VLLM` decision

**Acceptable** for real product proof when the resolved provider is `qwen_vllm` and vLLM responds on `VLLM_BASE_URL`. It only means the CLI did not pass `--provider`; resolution is still the real Qwen lane ([section_cli_defaults.py](apps_rg/runtime/section_cli_defaults.py)). Not the same as `DEV_DEFAULT_MOCK` with a mock provider.

## Wave 4 remediation (no gate weakening)

1. `docker start local-qwen-vllm`
2. Wait for `http://localhost:8000/v1/models` → HTTP 200
3. Re-run canonical CLI

Optional operator convenience: `APPS_RG_QWEN_VLLM_DOCKER_RESTART=1` (if_unhealthy restart before section lanes).
