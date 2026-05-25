# W1 Closeout — Same-Authority Thread + vLLM messages[]

**Plan:** [core-same-authority-incremental-regen-e7a4b1.md](../../../.cursor/plans/core-same-authority-incremental-regen-e7a4b1.md)  
**Date:** 2026-05-25

## STATUS: PASS

## Deliverables

| Phase | Output | Status |
|-------|--------|--------|
| W1.0 | `PromptMessages.append_same_authority_turn` + `agentic_core/L2_execution/regen/*` | DONE |
| W1.1 | `VLLMRequest.messages`, `QwenInferenceRequest.messages`, `LocalVLLMProvider.generate(messages=...)` | DONE |
| W1.2 | NC-1..NC-3 tests | DONE |

## FILES_CHANGED

- [\_\_init\_\_.py](../../../agentic_core/L2_execution/regen/__init__.py)
- [same_authority_bundle.py](../../../agentic_core/L2_execution/regen/same_authority_bundle.py)
- [same_authority_errors.py](../../../agentic_core/L2_execution/regen/same_authority_errors.py)
- [same_authority_thread.py](../../../agentic_core/L2_execution/regen/same_authority_thread.py)
- [prefix_digest.py](../../../agentic_core/L2_execution/regen/prefix_digest.py)
- [prompt_messages.py](../../../agentic_core/L2_execution/reasoning/prompt_messages.py)
- [_provider_local_vllm.py](../../../agentic_core/L2_execution/enforcement/_provider_local_vllm.py)
- [optimized_vllm_client.py](../../../agentic_core/L3_orchestration/inference/qwen_vllm/engines/optimized_vllm_client.py)
- [qwen_inference_gateway.py](../../../agentic_core/L3_orchestration/inference/qwen_vllm/reasoning/qwen_inference_gateway.py)
- [test_same_authority_prefix.py](../../../tests/unit/agentic_core/L2_execution/regen/test_same_authority_prefix.py)
- [test_vllm_messages_dispatch.py](../../../tests/unit/agentic_core/L2_execution/regen/test_vllm_messages_dispatch.py)

## COMMANDS_RUN

| Command | Result |
|---------|--------|
| `python -m compileall agentic_core apps_rg -q` | exit 0 |
| `python -m pytest tests/unit/agentic_core/L2_execution/regen/ tests/unit/agentic_core/L2_execution/reasoning/test_prompt_messages.py -q -o addopts=` | exit 0, **19 passed** |

## TESTS_GATES

- NC-1 `test_nc1_prefix_mutation_after_append_fails` — PASS
- NC-2 `test_nc2_bundle_drift_fails` — PASS
- NC-3 `test_nc3_preserves_compile_ref_and_new_delta_hash_only` — PASS
- `test_append_same_authority_turn_chat_shape` — roles `system, developer, user, assistant, user`
- `test_local_vllm_provider_accepts_messages_kwarg` — PASS

## ARTIFACTS

NONE (runtime proof deferred to W3 live Brown)

## NOTES

- W2 adds `SameAuthorityRegenRunner`, receipts, delta shape guards, boundary CI.
- Boundary CI `check_same_authority_regen_boundary.py` not yet created (W2).
