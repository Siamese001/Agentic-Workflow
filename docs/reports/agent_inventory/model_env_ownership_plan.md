# Model environment ownership plan

**ADG:** `artifacts/adg/adg_indexed_05172026_0651.sqlite`

Planning-only — no env defaults changed in this pass.

---

## Spine / agentic_core-only

| Env var | Resolves to | SSOT |
|---------|-------------|------|
| `GOOGLE_AI_MODEL` | `GEMINI_FLASH_MODEL_ID` | [google_ai_env.py](../../agentic_core/config/google_ai_env.py), [model_registry.py](../../agentic_core/L0_routing/config/model_registry.py) |
| `GOOGLE_AI_PRO_MODEL` | `GEMINI_PRO_MODEL_ID` | same |
| `OPENAI_MODEL` | `OPENAI_MODEL_ID` | [model_registry.py](../../agentic_core/L0_routing/config/model_registry.py) |
| `HEALING_GOOGLE_AI_PRO_MODEL` | healing pro override | [healing_cascade_registry.py](../../agentic_core/L2_execution/healers/healing_cascade_registry.py) — **not** for judges |

### Static consumers (production-oriented)

**`GOOGLE_AI_MODEL` / flash tier**

- L2: `healing_router.py`, `gemini_gateway_provisioner.py`, `confidence_aware_executor.py`
- L3: `exit_eval/judges/google_judge.py`
- L1: structured reasoning utilities, dependency graph validator, job analyzer
- apps_lic: `enterprise_campaign_orchestrator.py` (flash)
- **Must NOT:** apps_rg section body generation

**`GOOGLE_AI_PRO_MODEL` / pro tier**

- L1: `consensus_validator.py` (juror panel)
- L2: pro-tier healing, `FissionManagerAgent` paths via sub_atomic_engine
- `runtime/providers/provider_registry.py` (`google_gemini`)
- apps_rg: **fallback only** in `executive_summary_x1d.py` if `APPS_RG_GOOGLE_JUDGE_MODEL_STANDARD` unset

**`OPENAI_MODEL`**

- L1 consensus juror, `openai_judge.py`, `sovereign_config.py`, `reasoning_types.py`
- `runtime/providers/provider_registry.py` (`openai`)
- apps_rg: judge fallback + **dry_run demo hardcode** (non-product)

**`HEALING_GOOGLE_AI_PRO_MODEL`**

- `healing_cascade_registry.py` — cascade pro tier override
- Documented: judge panel MUST NOT consult this var

**Local Qwen / vLLM (spine registry, shared infrastructure)**

- `VLLM_MODEL_NAME`, `VLLM_BASE_URL`, `QWEN_LOCAL_MODEL_ID` in model_registry
- Used by consensus optional juror (`USE_QWEN_CONSENSUS_JUROR`), L2 `vllm_health_probe`, apps_rg generation

---

## apps_rg generation (product)

| Env var | Purpose |
|---------|---------|
| `QWEN_VLLM_MODEL`, `VLLM_*` | Section lanes via [qwen_vllm_provider.py](../../apps_rg/runtime/providers/qwen_vllm_provider.py) |
| `APPS_RG_EXEC_SUMMARY_QWEN_MAX_OUTPUT_TOKENS` | Lane-specific caps |
| `APPS_RG_L2_PROVIDER_MODE` | `stub_only` / `live_allowed` — CI vs external API |
| `APPS_RG_QWEN_OFFLINE_CONTRACT_STUB` | Deterministic offline only |
| `APPS_RG_R4_GENERATION_MODE` | `modular_section_lanes` (default) vs `legacy_full_resume` rollback |

**Invariant:** Section generation must not read `OPENAI_MODEL`, `GOOGLE_AI_MODEL`, or `GOOGLE_AI_PRO_MODEL` for provider selection (W2 guard).

---

## apps_rg judges (proof)

| Env var | Purpose |
|---------|---------|
| `APPS_RG_GOOGLE_JUDGE_MODEL_ENHANCED` / `_STANDARD` | Gemini judges |
| `APPS_RG_OPENAI_JUDGE_MODEL_*` | OpenAI judges |
| `APPS_RG_ANTHROPIC_JUDGE_MODEL_*` | Anthropic judges |
| `APPS_RG_*_JUDGE_MODEL` | Global per-provider override |

SSOT: [X1D_PROVIDER_CONFIG.md](../../apps_rg/runtime/judges/X1D_PROVIDER_CONFIG.md), [section_judge_profile.py](../../apps_rg/runtime/judges/section_judge_profile.py).

**Explicit:** General chat env vars are **not** used for proof judges when `APPS_RG_*` set (documented + tested in `test_section_judge_policy.py`).

---

## Wave linkage

| Wave | Action |
|------|--------|
| W2 | Generation-path import guards + `.env.example` comments |
| W3 | Judge profile audit; receipt `resolved_model_source` |
| W6 | Ensure shim retirement does not reintroduce spine vars in apps_rg binding |

---

## Explicit non-claims

- Live deployment values in operator `.env` not audited.
- Anthropic `ANTHROPIC_MODEL` spine usage not exhaustively listed (see model_registry).
