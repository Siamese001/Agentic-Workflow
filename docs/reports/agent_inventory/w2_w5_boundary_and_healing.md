# W2–W5 Boundary and Healing Report

**Generated:** 2026-05-19  
**Scope:** Waves 2–5 only (no runtime behavior change; tests + docs)  
**Machine-readable:** [w2_w5_boundary_and_healing.json](w2_w5_boundary_and_healing.json)

## Executive summary

| Wave | Result | Confidence |
|------|--------|------------|
| W2 Generation model-env guards | PASS | HIGH |
| W3 Judge isolation | PASS | HIGH |
| W4 Signal-quality ownership | QUARANTINE (KEEP_STUBBED) | HIGH |
| W5 Same-authority healing guardrails | PASS | MEDIUM |

**Behavior change:** none  
**Runtime change:** none

---

## W2 — apps_rg generation model-env guards

**Tests:** [test_apps_rg_generation_model_env_boundary.py](../../../tests/_apps_contract/test_apps_rg_generation_model_env_boundary.py) — 8 passed

AST scans over canonical generation surface:

- `apps_rg/runtime/sections/`
- `apps_rg/runtime/providers/qwen_vllm_provider.py`
- `apps_rg/runtime/providers/section_qwen_slice.py`

**Proves:**

- No `agentic_core.L0_routing.config.model_registry` imports of `OPENAI_MODEL`, `GOOGLE_AI_*`, `GEMINI_*_MODEL_ID`, `OPENAI_MODEL_ID`
- No `os.getenv` for spine chat/healing model vars on generation path
- Qwen/VLLM provider module references `QWEN_VLLM_MODEL` / `VLLM_BASE_URL`

**Grep (`git grep` apps_rg):** spine symbols only in classified non-generation paths:

| Path | Role |
|------|------|
| `runtime/dry_run/executive_summary_demo.py` | Demo (non-product) |
| `runtime/judges/*` | Judge path (W3) |
| `runtime/judges/X1D_PROVIDER_CONFIG.md` | Documentation |

---

## W3 — apps_rg judge isolation

**Tests:** [test_apps_rg_judge_model_env_boundary.py](../../../tests/_apps_contract/test_apps_rg_judge_model_env_boundary.py) — 7 passed

**Proves:**

- `APPS_RG_*_JUDGE_MODEL_STANDARD` wins over `GOOGLE_AI_PRO_MODEL` / `OPENAI_MODEL` when set
- When APPS_RG unset, `GOOGLE_AI_PRO_MODEL=gemini-2.5-pro` resolves with `model_source=GOOGLE_AI_PRO_MODEL` (**LIMITED_FALLBACK**)
- When spine var is flash-tier (`gemini-2.5-flash`), forbidden for proof → `profile_default` (`gemini-2.5-pro`)

**NEEDS_DECISION:** retain `GOOGLE_AI_PRO_MODEL` in `_STANDARD_PROFILE["gemini_pro"]["env_tier"]` for production pinning vs APPS_RG-only judges.

---

## W4 — signal-quality ownership

**Decision: QUARANTINE (KEEP_STUBBED)** — do not wire `apps_shared` stubs to core in this wave.

| Location | Role |
|----------|------|
| [signal_quality_config.py](../../../agentic_core/runtime/config/signal_quality_config.py) | SSOT: `SIGNAL_*`, `QualityThresholds`, `get_signal_enhancer`, `assess_signal()` |
| [subatomic_hop_util.py](../../../apps_shared/utils/subatomic_hop_util.py) | Local no-op stub; real import commented |
| [engine_type_types.py](../../../apps_shared/types/engine_type_types.py) | Stub `assess_signal` returns empty assessment |

**Tests:** [test_apps_rg_signal_env_boundary.py](../../../tests/_apps_contract/test_apps_rg_signal_env_boundary.py) — 6 passed

- `SIGNAL_EXCELLENT_MIN` / `HIGH` / `GOOD` / `MARGINAL` not read via getenv outside SSOT in `apps_rg` or `L2_execution/healers`
- `SIGNAL_*` is **not** generation, judge, or heal-tier routing

---

## W5 — same-authority healing guardrails

**Tests:** [test_l2_same_authority_healing_guardrails.py](../../../tests/unit/agentic_core/L2_execution/test_l2_same_authority_healing_guardrails.py) — 14 passed  
**Orchestration:** `tests/unit/agentic_core/L2_execution/orchestration/` — 8 passed

**SSOT:**

- `repair_decision()` — [l2_v4_contracts.py](../../../agentic_core/L2_execution/types/l2_v4_contracts.py)
- `apply_routing_gates()` — [routing_gates.py](../../../agentic_core/L2_execution/healers/routing_gates.py)
- `HealingRouter.dispatch_to_executor()` — HITL → `executor=hitl`, no Gemini repair

**Non-healable (documented):** missing authority, policy breach, `same_authority=False`, structural `GATEWAY_BYPASS` → HITL when Gemini prohibited.

**Caveat (MEDIUM confidence):** Without `provider_prohibited_gemini`, structural failures may still route to MEDIUM/LOW — not expanded here.

---

## Command evidence

| Command | Exit |
|---------|------|
| `git status --short` | 0 |
| `python -m compileall agentic_core apps_rg apps_shared -q` | 0 |
| `pytest` W2–W5 new tests (`-p no:xdist`) | 0 (35 passed) |
| `pytest tests/unit/agentic_core/L2_execution/orchestration/` | 0 (8 passed) |
| `pytest tests/_apps_contract -k "…boundary…"` (broad) | NOT_RUN_SLOW — pre-existing unrelated failures |
| `pytest tests/unit/apps_rg -k "judge|…"` | 1 — 4 pre-existing failures outside new tests |
| `pytest tests/unit/agentic_core -k "heal|signal|…"` | 1 — 39 pre-existing failures; new W5 tests passed |

---

## Explicit non-claims

- No files deleted; no deprecation markers added
- No X2/X3 weakening; no full live `python -m apps_rg` proof
- Static/env boundary tests do not prove live generation or judge quality
