# Environment ownership boundary (W1)

**Wave:** W1 documentation only — `.env` and runtime code unchanged.

Consolidates [model_env_ownership_plan.md](model_env_ownership_plan.md) and [signal_quality_ownership_plan.md](signal_quality_ownership_plan.md) into a single boundary reference.

---

## 5. MODEL_ENV_BOUNDARY

### Spine / shared-agent (agentic_core) — **not** apps_rg section generation

| Env var | Resolves to | SSOT | Typical consumers (static) |
|---------|-------------|------|----------------------------|
| `GOOGLE_AI_MODEL` | `GEMINI_FLASH_MODEL_ID` | [google_ai_env.py](../../../agentic_core/config/google_ai_env.py), [model_registry.py](../../../agentic_core/L0_routing/config/model_registry.py) | L2 healing flash tier, L3 google_judge, apps_lic campaign (flash) |
| `GOOGLE_AI_PRO_MODEL` | `GEMINI_PRO_MODEL_ID` | same | L1 consensus juror, L2 pro healing, provider_registry; apps_rg judge **fallback only** if `APPS_RG_GOOGLE_JUDGE_MODEL_STANDARD` unset |
| `OPENAI_MODEL` | `OPENAI_MODEL_ID` | model_registry | L1 consensus, openai_judge, sovereign_config; apps_rg judge fallback; **dry_run demo** (non-product) |
| `HEALING_GOOGLE_AI_PRO_MODEL` | healing pro override | [healing_cascade_registry.py](../../../agentic_core/L2_execution/healers/healing_cascade_registry.py) | L2 heal cascade **only** — judges must not read this |

**Invariant (documented for W2 implementation):** apps_rg **section body** generation must not select models via `OPENAI_MODEL`, `GOOGLE_AI_MODEL`, or `GOOGLE_AI_PRO_MODEL`.

### apps_rg generation (product) — Qwen / vLLM

| Env var | Role |
|---------|------|
| `VLLM_MODEL_NAME`, `VLLM_BASE_URL`, `VLLM_MAX_MODEL_LEN` | Local inference endpoint (also in spine registry as `QWEN_LOCAL_MODEL_ID`) |
| `QWEN_VLLM_MODEL` / lane-specific `APPS_RG_*_QWEN_*` | Section lane caps and overrides |
| `APPS_RG_L2_PROVIDER_MODE` | `stub_only` (CI) vs `live_allowed` — **non-product when stub** |
| `APPS_RG_QWEN_OFFLINE_CONTRACT_STUB` | Deterministic offline — **non-product** |
| `APPS_RG_R4_GENERATION_MODE` | `modular_section_lanes` (default) vs `legacy_full_resume` (rollback) |

SSOT provider: [qwen_vllm_provider.py](../../../apps_rg/runtime/providers/qwen_vllm_provider.py) — no silent mock fallback (HIGH static from module docstring).

### apps_rg proof judges — `APPS_RG_*_JUDGE_MODEL_*`

| Env var | Role |
|---------|------|
| `APPS_RG_GOOGLE_JUDGE_MODEL_ENHANCED` / `_STANDARD` | Gemini judges |
| `APPS_RG_OPENAI_JUDGE_MODEL_ENHANCED` / `_STANDARD` | OpenAI judges |
| `APPS_RG_ANTHROPIC_JUDGE_MODEL_ENHANCED` / `_STANDARD` | Anthropic judges |
| `APPS_RG_*_JUDGE_MODEL` (no tier suffix) | Global per-provider override |

SSOT: [X1D_PROVIDER_CONFIG.md](../../../apps_rg/runtime/judges/X1D_PROVIDER_CONFIG.md), [section_judge_profile.py](../../../apps_rg/runtime/judges/section_judge_profile.py).

**Explicit:** General chat vars (`OPENAI_MODEL`, `GOOGLE_AI_MODEL`, `ANTHROPIC_MODEL`) are **not** used for proof judges when `APPS_RG_*` tier vars are set (tested in `test_section_judge_policy.py` — static evidence).

---

## Signal-quality env (`SIGNAL_*`) — separate from models

| Env var | SSOT | Role |
|---------|------|------|
| `SIGNAL_EXCELLENT_MIN`, `SIGNAL_HIGH_MIN`, `SIGNAL_GOOD_MIN`, `SIGNAL_MARGINAL_MIN` | [signal_quality_config.py](../../../agentic_core/runtime/config/signal_quality_config.py) | Label content excellent → poor via `assess_signal()` |

**Does NOT drive (HIGH static):**

- apps_rg résumé generation
- apps_rg X1D judges
- L2 `HealTier` / `healing_router` routing

### apps_shared stub caveat (HIGH static)

| Path | Issue | Classification |
|------|-------|----------------|
| [subatomic_hop_util.py](../../../apps_shared/utils/subatomic_hop_util.py) | Local stub `get_signal_enhancer()` → no-op `SignalQuality()`; real import commented | NEEDS_DECISION (W4) |
| [engine_type_types.py](../../../apps_shared/types/engine_type_types.py) | Stub `signal_enhancer.assess_signal` returns empty assessment | NEEDS_DECISION (W4) |

**Do not cite stub scores as product or spine proof.**

---

## Cross-boundary quick reference

```text
                    ┌─────────────────────────────────────┐
                    │         agentic_core spine          │
                    │  OPENAI / GOOGLE_AI_* / HEALING_*   │
                    │  SIGNAL_* (quality labels)          │
                    │  E2/E3/E4 pipeline substrate        │
                    └──────────────┬──────────────────────┘
                                   │ adapters / gateway
                    ┌──────────────▼──────────────────────┐
                    │            apps_rg product            │
                    │  Generation: VLLM / QWEN_*          │
                    │  Judges: APPS_RG_*_JUDGE_*          │
                    │  X2/X3/section receipts             │
                    └─────────────────────────────────────┘
```

---

## PROOF_BOUNDARY

| Claim type | Allowed in W0/W1 |
|------------|------------------|
| Env var listed in module docstring / registry | Yes (static) |
| Env var used in live receipt | Only as **citation** of existing artifacts — no new live run |
| Stub/offline env proves product quality | **No** |

---

## Explicit non-claims

- Operator `.env` values not audited.
- No env rename or deprecation performed.
- Anthropic spine vars not exhaustively enumerated.
