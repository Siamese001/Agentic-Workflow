# Reasoning execution audit (W1)

**Scope:** Repo state at introduction of governed reasoning receipt seam (`agentic_core/runtime/reasoning/`).  
**Goal:** Close *declared intent ≠ runtime application ≠ certified proof* with explicit ledger + consequences.

---

## CONTROL matrix

| CONTROL | DECLARED | RESOLVED | REQUIREMENT_LEVEL (pre-seam defaults) | APPLIED_LAYER | PROVED (pre-seam) | GAP | CONSEQUENCE |
|---------|----------|----------|----------------------------------------|---------------|-------------------|-----|-------------|
| `temperature` | `ReasoningPath.temperature` → `SovereignLLMGateway` `reasoning_kwargs` | Same value passed to `generate()` | OPTIONAL (transport) | TRANSPORT (if provider forwards) | **LOCAL_VLLM:** observed only after W3 via `_reasoning_transport_observed` | Pre-W3: no structured receipt; kwargs logged only via telemetry | WARN if degraded only when OPTIONAL |
| `max_tokens` | Not in `ReasoningPath`; default in `LocalVLLMProvider` / `QwenInferenceRequest` | Provider default 2048 unless caller `kwargs` | OPTIONAL | TRANSPORT | Same as temperature | Not part of `generate_with_reasoning` path table | None unless requested |
| `cot_paths` | `ReasoningPath` + `reasoning_kwargs` | Integer 0 or N | QUALITY_REQUIRED when N>0 | ORCHESTRATION (intended) | **None** — not executed as multi-path | **FAIL** — dropped at `LocalVLLMProvider` | X1D / quality cert cannot claim full reasoning proof |
| `tot_branches` | `ReasoningPath` | Integer | QUALITY_REQUIRED when >0 | ORCHESTRATION | **None** | **FAIL** | Same |
| `tot_depth` | `ReasoningPath` | Integer | QUALITY_REQUIRED when >0 | ORCHESTRATION | **None** | **FAIL** | Same |
| `reflexion_loops` | `ReasoningPath` | Integer | POLICY_REQUIRED when >0 | ORCHESTRATION | **None** | **FAIL** — silent drop | **BLOCK** if policy requires |
| `self_consistency_samples` | `ReasoningPath` | Integer | QUALITY_REQUIRED when >1 | ORCHESTRATION | **None** | **FAIL** | Cert gate denies full quality |
| `ReasoningConfig.*` (`reasoning_types.py`) | Section presets `K*_CONFIG` | Class attributes / Pydantic defaults | **Not wired** to gateway | N/A | **None** in `SovereignLLMGateway` path | **FAIL** — parallel SSOT | Intent drift vs execution |
| L0 `TIER_PARAMETER_TABLE` | `max_branches`, `max_depth`, `enable_reflection`, `allowed_modes` | `ReasoningPolicyEngine.build_profile` | Enforced via L3 envelope (separate path) | POLICY/ORCH via `ReasoningIntensityEnforcer` | Envelope hash / stage metrics | Not merged into gateway `generate_with_reasoning` receipt | Disjoint governance planes |
| M0 ToT slot | YAML / Jinja template | PA assembly | PA | PROMPT | Slot hash via PA BOM only if wired | Often **partial** vs numeric `tot_*` | Prompt claims without orch proof |
| L3 reflexion engine | Dedicated module | Workflow / engine | ORCHESTRATION | ORCHESTRATION | OTel / internal traces | Not tied to gateway kwargs | Disjoint |
| `AttemptReceipt` / `SealedL2Artifact` | `l2_envelope_adapter`, `sealed_l2_artifact` | apps pipeline | Runtime | Receipt tuples | `provider_receipts`, `model_call_refs` | No per-control reasoning ledger pre-W3 | Exit cannot consume reasoning applicability |
| `apps_rg` Qwen (`qwen_vllm_provider`) | App dispatch | HTTP JSON | TRANSPORT only | TRANSPORT | Request JSON artifacts | Orchestration knobs **absent** on wire | Bypass relative to sovereign gateway |

---

## Evidence pointers

| Area | Files |
|------|--------|
| Declarative presets | `agentic_core/runtime/config/reasoning_types.py` |
| L0 stamping | `agentic_core/L0_routing/reasoning/reasoning_policy_engine.py`, `reasoning_intensity_types.py` |
| Gateway path → kwargs | `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py` (`generate_with_reasoning`, `REASONING_PATH_TABLE`) |
| LOCAL_VLLM forward | `agentic_core/L2_execution/enforcement/_provider_local_vllm.py` → `QwenInferenceRequest` fields only |
| Qwen request shape | `agentic_core/L3_orchestration/inference/qwen_vllm/reasoning/qwen_inference_gateway.py` |
| apps_rg bypass | `apps_rg/runtime/providers/qwen_vllm_provider.py` |
| M0 meta | `agentic_core/prompt_governance/templates/slots/M0_meta_cognitive.jinja` |
| L2 seal | `agentic_core/runtime/contracts/sealed_l2_artifact.py` |
| L5 cert ref | `agentic_core/L5_safety/contracts/verify.py` (structural non-empty only) |

---

## Conclusion

**Historical (pre‑W3):** `generate_with_reasoning` forwarded orchestration-flavored kwargs into `LocalVLLMProvider.generate`, but **`QwenInferenceRequest`** only carries **temperature/max_tokens/use_cache/confidence_threshold** — orchestration controls were effectively dropped.

**Implemented (post‑W3, this rollout):**
- **`agentic_core/runtime/reasoning/`**: `ReasoningControlRequirement`, `ReasoningExecutionPlan`, `ReasoningExecutionReceipt`, `TransportCapabilities`, `resolve_gateway_receipt`, `reasoning_quality_certification_allowed`, `enforce_blocked` (`ReasoningGovernanceError`).
- **`generate_with_reasoning`** embeds **`_reasoning_execution_receipt`** and raises on aggregate **BLOCK** (e.g. active `reflexion_loops` with no orchestration runner, or scratchpad leak on observed transport).
- **`LocalVLLMProvider`**: declares **`reasoning_transport_kw_forwarded`** and echoes **`_reasoning_transport_observed`** for outbound proof.

**Residual gap:** **`apps_rg` direct HTTP** bypass remains documented above — address via **thin app-local adapter** (per plan), not expanded core literals.

**Exit (W4):** `eval_x1d` consults `exec_trace["reasoning_execution_receipt"]` when present; **`quality_certification_denied`** forces **`WARN` / `REASONING_QUALITY_NOT_CERTIFIABLE`** instead of a nominal **PASS** so X1D does not certify full reasoning quality without ledger proof.
