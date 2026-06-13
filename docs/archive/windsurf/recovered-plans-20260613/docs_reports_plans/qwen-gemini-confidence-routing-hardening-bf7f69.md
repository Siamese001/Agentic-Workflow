# Qwen vLLM + Gemini 2.5 Pro + Confidence Routing Hardening

Hardens the L2.3 healing provider adapters and confidence router so that both model paths capture real responses, share consistent thresholds, and have full test coverage.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Current State (AST Scan Findings)

### Files in scope
| File | Role |
|------|------|
| `agentic_core/L2_execution/healers/healing_provider_adapters.py` | `QwenInvokerAdapter`, `GeminiInvokerAdapter` |
| `agentic_core/L2_execution/healers/healing_tier_router.py` | Confidence scoring + routing choke point |
| `agentic_core/L2_execution/healers/healing_tier_config.py` | Thresholds, model IDs, GPU config |
| `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` | Dispatches to selected tier |
| `agentic_core/L2_execution/healers/qwen_vllm_inference.py` | WSL subprocess worker |
| `agentic_core/L2_execution/healers/qwen_meta_learning.py` | Qwen-side threshold protection |
| `agentic_core/L2_execution/types/vllm_gateway_integration_types.py` | vLLM call-path controller |
| `apps_shared/types/hardened_gemini_executor_types.py` | Tenacity-backed Gemini executor |

### Critical Gaps Found

**Gap 1 — Response discarded in both adapters (HIGH RISK)**
`invoke_qwen_vllm` calls `client.chat.completions.create(...)` but the return is never captured into `InvocationRecord.response_text`. Same for `invoke_gemini`. The model output is silently lost.

**Gap 2 — Threshold drift between files**
`healing_tier_config.py` declares `HEALING_CONFIDENCE_X = 0.80`, `Y = 0.50`.
`qwen_meta_learning.py` declares `HEALING_CONFIDENCE_X = 0.75`, `Y = 0.40`.
Two module-level constants diverge — confidence router uses one, meta-learning enforces the other.

**Gap 3 — `HardenedGeminiExecutor` not used in healing path**
`apps_shared/types/hardened_gemini_executor_types.py` provides tenacity retry + circuit breaker but `GeminiInvokerAdapter` calls `google.generativeai` directly with no retry.

**Gap 4 — Gemini model ID inconsistency**
`healing_tier_config.py` pin: `"gemini-2.5-pro"`. `HardenedGeminiConfig.MODEL_LIMITS` keys: `"gemini-2.5-flash"`, `"gemini-3-pro-preview"`. No entry for `"gemini-2.5-pro"`.

**Gap 5 — Qwen subprocess vs. adapter path divergence**
`qwen_vllm_inference.py` is a WSL subprocess worker (`LLM`, `SamplingParams` from `vllm`).
`QwenInvokerAdapter` uses `openai.OpenAI` client pointing at vLLM's OpenAI-compatible endpoint.
No integration test verifies both paths produce identical structured output.

**Gap 6 — No retry / backpressure in `QwenInvokerAdapter`**
Single-shot call to vLLM endpoint; transient `ConnectionError` causes silent failure with no retry.

**Gap 7 — `InvocationRecord` response field never populated**
Downstream consumers (meta-learning bus, audit trail) cannot inspect what the model actually said.

---

## Phase 1 — Response Capture + Threshold Unification (Wave 1)

**Scope:** `healing_provider_adapters.py`, `healing_tier_config.py`, `qwen_meta_learning.py`

**Wave 1-A: Capture model responses in adapters**
- In `QwenInvokerAdapter.invoke_qwen_vllm`: capture `completion = client.chat.completions.create(...)` and write `completion.choices[0].message.content` into `InvocationRecord`.
- In `GeminiInvokerAdapter.invoke_gemini`: capture `response = model.generate_content(...)` and write `response.text` into `InvocationRecord`.
- Add `response_text: str | None` field to `InvocationRecord` dataclass.

**Wave 1-B: Unify threshold constants**
- Remove `HEALING_CONFIDENCE_X / Y` from `qwen_meta_learning.py`.
- Import them from `healing_tier_config.py` (single source of truth).
- Update `qwen_meta_learning.validate_threshold_immutability()` to assert against the imported constants.

**Acceptance criteria:**
- `pytest tests/unit/agentic_core/L2_execution/healers/` green.
- `InvocationRecord.response_text` is non-None after successful invocation in all adapter unit tests.
- Single constant definition for X and Y confirmed by grep-test invariant.

---

## Phase 2 — Gemini Hardening: Retry + Circuit Breaker (Wave 2)

**Scope:** `healing_provider_adapters.py`, `hardened_gemini_executor_types.py`

**Wave 2-A: Wire `HardenedGeminiExecutor` into `GeminiInvokerAdapter`**
- Add model ID `"gemini-2.5-pro"` to `HardenedGeminiConfig.MODEL_LIMITS` (1M context window).
- Replace direct `google.generativeai` call in `invoke_gemini` with `HardenedGeminiExecutor.invoke(prompt)`.
- Map `ContextOverflowError` → `SovereigntyViolation` with descriptive reason code.
- Map `CircuitBreakerOpenError` → graceful downgrade to `LOCAL_AGENT` tier.

**Wave 2-B: Add retry to `QwenInvokerAdapter`**
- Wrap `client.chat.completions.create(...)` in `tenacity.retry` with `stop_after_attempt(3)`, `wait_exponential(min=1, max=10)`, retry on `ConnectionError` / `TimeoutError`.
- Emit structured log on each retry attempt.

**Acceptance criteria:**
- `GeminiInvokerAdapter` retry test: mock `google.generativeai` to fail 2 times then succeed → verifies 3rd call succeeds and `response_text` is populated.
- Circuit breaker test: mock 5 consecutive failures → assert `CircuitBreakerOpenError` raised.
- `QwenInvokerAdapter` retry test: mock vLLM endpoint to fail once then succeed.

---

## Phase 3 — Qwen WSL Subprocess Path Integration (Wave 3)

**Scope:** `qwen_vllm_inference.py`, `healing_tier_dispatcher.py`

**Wave 3-A: Structured output contract test**
- Both `qwen_vllm_inference.py` (subprocess) and `QwenInvokerAdapter` (OpenAI SDK) must return JSON with keys `{decision, reason, model, agent_name, score, gate}`.
- Write deterministic contract test: parse the `InvocationRecord.response_text` JSON and assert all keys present.

**Wave 3-B: Subprocess error propagation**
- `heal_tier_dispatcher` subprocess invocation: capture non-zero exit code and parse stderr; map to `InvocationRecord` failure with reason code.
- Add timeout enforcement (`subprocess.run(timeout=60)`) for WSL subprocess calls.

**Acceptance criteria:**
- Contract test asserts JSON schema compliance for both invocation paths.
- Timeout test: mock subprocess to hang → assert `TimeoutExpired` maps to `FAILED` record.

---

## Phase 4 — End-to-End Routing Tests + Invariant Gate (Wave 4)

**Wave 4-A: Full routing matrix test**
Axes: `[LOCAL_AGENT, QWEN_VLLM, GEMINI_2_5_PRO]` × `[success, failure, timeout, circuit_open]`
- Verify tier selection matches thresholds X=0.80, Y=0.50.
- Verify `InvocationRecord.response_text` populated on success.
- Verify meta-outcome bus gets a package after dispatch.

**Wave 4-B: Regression invariant — single threshold constant**
- Architecture test: parse `healing_provider_adapters.py`, `healing_tier_config.py`, `qwen_meta_learning.py` via `ast.parse` and assert `HEALING_CONFIDENCE_X` is only defined in `healing_tier_config.py`.

**Evidence file:** `docs/reports/sub/phase_qwen_gemini_routing_evidence.md`

---

## Risk Register

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| WSL vLLM unreachable in CI | High | All adapter unit tests mock the SDK call |
| Gemini quota exhaustion | Medium | Circuit breaker + `NullAdapter` fallback in test env |
| Threshold constant drift regression | Low | Phase 4 AST invariant test as hard gate |
| Response JSON parse failure | Medium | Defensive JSON parse with fallback to raw text |

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

