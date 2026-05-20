# Signal quality ownership plan

Planning-only — no stub removal in this pass.

---

## SSOT (real — KEEP_CORE)

[signal_quality_config.py](../../agentic_core/runtime/config/signal_quality_config.py):

| Mechanism | Env / API |
|-----------|-----------|
| Tier thresholds | `SIGNAL_EXCELLENT_MIN`, `SIGNAL_HIGH_MIN`, `SIGNAL_GOOD_MIN`, `SIGNAL_MARGINAL_MIN` |
| Types | `QualityThresholds`, `SignalAssessment`, `SignalQuality` enum |
| API | `signal_enhancer.assess_signal()`, `get_signal_enhancer()` |

**Role:** Label content excellent / high / good / marginal / poor for shared runtime quality assessment.

**Does NOT drive (HIGH confidence, static):**

- apps_rg résumé section generation (Qwen/vLLM)
- apps_rg X1D proof judges (`APPS_RG_*_JUDGE_MODEL_*`)
- L2 heal tier routing (`HealTier`, `healing_router` — uses failure signals, not SIGNAL_*)

**Tests:** [test_signal_quality_config.py](../../tests/unit/agentic_core/runtime/config/test_signal_quality_config.py) — SSOT only.

---

## Stubbed / mimics real behavior (QUARANTINE)

| Path | Evidence | Confidence |
|------|----------|------------|
| [subatomic_hop_util.py](../../apps_shared/utils/subatomic_hop_util.py) | Lines 85–148: real import commented; local `QualityThresholds`, `get_signal_enhancer()` → `SignalQuality()` no-op | HIGH |
| [engine_type_types.py](../../apps_shared/types/engine_type_types.py) | Lines 22–47: stub classes; `assess_signal` returns empty `SignalAssessment` | HIGH |

**Risk:** Code calling stubs reports fake quality scores — must not be cited as runtime proof.

**Related:** [talent_signal_enhancer_validator.py](../../apps_shared/validators/talent_signal_enhancer_validator.py) — verify fan-in in W4 (ADG).

---

## W4 decision matrix (NEEDS_DECISION)

| Option | Pros | Cons |
|--------|------|------|
| **A. Wire to SSOT** | Single truth; real thresholds | apps_shared → agentic_core import; blast radius |
| **B. Quarantine stubs** | No coupling change | Stale code remains; eval confusion |
| **C. Migrate consumers off stubs** | Clean boundary | Requires consumer inventory |

**Recommendation for planning:** B short-term (manifest + ADR), A only for product paths with ADG fan-in proof.

---

## Wave linkage

- **W4:** Decision + tests or quarantine markers
- **W11:** Delete stub classes only if fan-in zero

---

## Explicit non-claims

- No runtime measurement of stub vs SSOT score divergence.
- `standard_type_types.py` duplicate `QualityThresholds` shapes not fully traced.
