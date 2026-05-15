# apps_rg Executive Summary Runtime Overlay Manifest

Purpose: surgical overlay to prove one app-local executive_summary runtime seam.

This overlay does not replace apps_rg wholesale. It adds one runnable section path:

```bash
python -m apps_rg.runtime.dispatch.executive_summary_dispatch --provider qwen_vllm --x1d-judges gemini_pro,openai_chatgpt,anthropic_claude --allow-non-allow-exit-zero
```

## Files added

- `apps_rg/runtime/dispatch/executive_summary_dispatch.py`
- `apps_rg/runtime/providers/qwen_vllm_provider.py`
- `apps_rg/runtime/validators/executive_summary_x2.py`
- `apps_rg/runtime/judges/executive_summary_x1d.py`
- `apps_rg/runtime/exit/executive_summary_x3.py`
- `apps_rg/runtime/shadow/executive_summary_l6.py`
- package `__init__.py` files under the new runtime subpackages
- `tests/_apps_contract/test_exec_summary_runtime_slice.py`
- `RUNBOOK.md`

## Explicit non-goals

- Does not activate registry.
- Does not edit v1 prompts.
- Does not edit `agentic_core`.
- Does not implement Unify, IBM, competencies, DOCX, locked copy, or full resume assembly.
- Does not claim production runtime is complete.

## Safety rules encoded

- Qwen/vLLM generation uses temperature `0.45`, within the executive summary profile `0.35-0.55`.
- Qwen/vLLM unavailable is `BLOCKED`, never silent mock fallback.
- Mocked or blocked judges cannot produce `X3_ALLOW`.
- `X3_ALLOW` requires REAL_LLM, product_quality_status PASS, X2 pass, and all judge rows MODEL_BACKED.
- L6 is offline only and cannot approve or mutate runtime learning.
