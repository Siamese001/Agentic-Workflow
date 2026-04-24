# W2.P2 — Initial Threshold Calibration Report

Plan: `.windsurf/plans/l0-routing-calibration-gap-audit-b3c9d4.md` §W2.P2
Generated: 2026-04-23 (W2 execution) from W0 sweep reports at `docs/reports/calibration/*_sweep.json`
SSOT: `config/routing_thresholds.yaml`

## Source data

Seed fixtures only (12–16 records each). These numbers are calibrated
against the PR curves emitted by the W0.P2 harness. **They are not
production thresholds** — re-run `tools.calibration --all` against
≥500 labeled real-trace samples per namespace before promoting.

## Threshold selection

| Key | Pre-W2 literal | W0 max-F1 | W2 default | Change | Rationale |
|---|---:|---:|---:|---|---|
| `r1b_semantic_similarity` | 0.98 | 0.93 | **0.95** | -0.03 | Moved 3pp less conservative, but held above W0 optimum until namespace-scoped precision confirmed on live traces. |
| `r5_abstain_confidence` | 0.50 | 0.49 | **0.50** | 0.00 | W0 optimum rounds to 0.50; preserve exact back-compat. |
| `r3_grounding_need` | — | 0.72 | **0.70** | new | Matches Vertex AI default and W0 optimum within rounding. |
| `c0_coverage_floor` | — | 0.62 | **0.60** | new | Matches C0 §C0.6 suggested floor and W0 optimum. |
| `r1a_freshness_ratio` | — | 0.65 | **0.65** | new | Matches W0 optimum; consumed by future check_d1_freshness gate. |

## Per-namespace overrides (W2.P1 YAML)

Tightened or loosened from the global default based on the stakes of the
namespace's agent class. All values are overridable by the
`ROUTING_THRESHOLD__*` env var at runtime.

| Namespace | `r1b_semantic_similarity` | `r5_abstain_confidence` | `r3_grounding_need` | `c0_coverage_floor` | Why |
|---|:---:|:---:|:---:|:---:|---|
| `rg` | 0.97 | — | — | — | RG outputs highly variable; hold R1B high. |
| `rfp` | 0.97 | — | — | — | Proposals long-form; reuse only on near-duplicates. |
| `research` | 0.92 | — | — | — | Boilerplate-heavy; tolerate more semantic reuse. |
| `eval` | 0.90 | 0.40 | — | — | Boilerplate + rarely needs abstain. Recall-optimized. |
| `exec` | 0.98 | 0.60 | — | — | Writes imminent — conservative on reuse, sensitive on abstain. |
| `lic` | 0.95 | — | — | — | Default inherits; no override needed yet. |
| `underwriting_ai` | 0.98 | 0.65 | 0.60 | 0.75 | High-stakes regulatory; every knob conservative. Ground more often, require stronger coverage. |

## R5 multi-signal triggers (W3.P2 contract)

6 triggers defined in YAML. 5 enabled by default, 1 (toxicity) deferred
to L5 kill-switch (ADR-042).

| Trigger | Enabled | Threshold | Reason code |
|---|:---:|:---:|---|
| `low_confidence` | ✅ | 0.50 | `r5_low_confidence` |
| `ood_detected` | ✅ | 0.70 | `r5_ood_detected` |
| `budget_exceeded` | ✅ | n/a (boolean) | `r5_budget_exceeded` |
| `circuit_breaker_open` | ✅ | n/a (boolean) | `r5_circuit_breaker_open` |
| `clarification_needed` | ✅ | n/a (boolean) | `r5_clarification_needed` |
| `toxicity_flagged` | ❌ | 0.70 | `r5_toxicity_flagged` |

## Back-compat behavior

Every existing caller of the pre-W2 hardcoded literals continues to work:

- `agentic_core.L4_state.utils.memory.semantic_cache_manager.SemanticCacheManager`
  reads `similarity_threshold=0.98` from its `__init__` as before — the
  threshold lookup is layered on top via a new helper (W3.P3).
- `agentic_core.runtime.contracts.abstain_contract.DEFAULT_ABSTAIN_THRESHOLD=0.50`
  is unchanged; callers that construct an `AbstainDecision` with the
  literal still receive the W0-aligned operating point.

Both surfaces can opt into the YAML-driven lookup via
`agentic_core.runtime.config.routing_thresholds.get_threshold(key, namespace)`
without breaking any existing call site.

## Regeneration

```bash
python -m tools.calibration --all
# Then update config/routing_thresholds.yaml from the new *_sweep.json reports
# (or run: python ops_scripts/calibration/weekly_refresh.py  — W4.P2 deliverable)
```
