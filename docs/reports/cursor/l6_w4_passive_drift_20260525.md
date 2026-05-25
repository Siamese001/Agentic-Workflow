# L6 W4 — Passive Surface Drift Map

**Plan:** [l6-repo-reorganization-mental-model-c4e8f2.md](../../.cursor/plans/l6-repo-reorganization-mental-model-c4e8f2.md)  
**Date:** 2026-05-25  
**Architecture path:** `PATH_RENAME_CANONICAL`  
**Wave:** W4 (map only — **no file moves**; relocations require separate Author-Gate)

**ADG evidence:** [l6_w4_adg_fanin_20260525.json](l6_w4_adg_fanin_20260525.json) (`adg_indexed_05252026_0634.sqlite`)

---

## Executive summary

Passive `agentic_core/L6_observability/` matches the mental-model tree for **8/9** subdirectories. One subdirectory (`promotion/`) and **14 root-level modules** are undocumented in [L6_mental_model.md](../../docs/reference/_notes/L6_mental_model.md). Eval capability is **split across three surfaces** with minimal cross-import between active validators and passive eval trees.

**W4 outcome:** Classify drift, record ADG fan-in, recommend deferred actions (W5+ or follow-on ADR). **No physical relocations in W4.**

---

## 1. Promotion drift (GAP-5)

### 1.1 `promotion/` subdirectory

| Module | ADG fan-in (production) | Classification | Recommended home |
|--------|-------------------------|----------------|------------------|
| [generic_l6_profile_consumer.py](../../agentic_core/L6_observability/promotion/generic_l6_profile_consumer.py) | `apps_lic/runtime/bindings/promo_binding.py` (L_APP, 4 edges) | **Active-adjacent** — consumes `RuntimeExhaustBundle`, models UWG promotion decisions | **06.7** (`system_learning/` gauntlet/promotion lane) after W5; until then keep on passive with documented handoff |

**Doctrine tension:** [LAYER.md](../../agentic_core/L6_observability/LAYER.md) states passive surface has **no promotion path**; `generic_l6_profile_consumer` encodes promotion *decision* logic (future-run + UWG). It is observer-shaped (no L4 write) but semantically belongs to the **active** 06.7 promotion chapter.

**W4 decision:** **Document + defer move.** Relocation to `system_learning/` (or `agentic_core/L6_system_learning/` post-W5) requires Author-Gate `refactor_scope` — not executed in W4.

### 1.2 Root promotion-related modules

| Module | ADG fan-in (non-test highlights) | Classification |
|--------|-----------------------------------|----------------|
| [promotion_gates.py](../../agentic_core/L6_observability/promotion_gates.py) | `apps_eval`, `apps_qna` (router copies), `apps_underwriting_ai` | **Passive statistics** — Wilson CI / rollback math; app-local shims duplicate name |
| [flywheel_promoter.py](../../agentic_core/L6_observability/flywheel_promoter.py) | Tests only (2 importers) | **Passive triage** — stages eval events to `data/eval/triage/`; observer-only |

`promotion_gates.py` fan-in is dominated by tests and app overlays; core implementation stays on passive surface. **No W4 move.**

---

## 2. Root-level module inventory (mental-model gap)

Mental model lists subdirs only; **14 `.py` files** sit at `L6_observability/` root:

| Module | Suggested bucket | Move in W4? |
|--------|------------------|-------------|
| `adg_span_annotator` | `runtime_trace/` (ADG annotation) | No — document |
| `cascade_telemetry`, `consensus_otel`, `heal_router_otel` | `runtime_trace/` / OTEL | No |
| `otel_runtime_ingest` | `runtime_trace/` (8 fan-in incl. `system_learning/_tracing`) | No |
| `decision_events_schema`, `decision_outcome_backfill`, `decision_provenance`, `routing_decision_events_schema` | `types/` | No |
| `routing_calibration_metrics`, `judge_drift`, `regret_accounting` | Cross-cutting observability KPIs | No |
| `promotion_gates`, `flywheel_promoter` | See §1 | No |

**W4 decision:** Add **Drift appendix** to [L6_observability/LAYER.md](../../agentic_core/L6_observability/LAYER.md) (documented layout, not renamed).

---

## 3. Eval overlap map (GAP-6)

| Surface | Path | ADG modules | Role | Overlap with |
|---------|------|-------------|------|--------------|
| **A — Shadow pipeline** | `shadow_eval/` | 12 | Canonical **passive** 06.x shadow-eval pipeline (`run_6a`…`run_6d`); observer-law clean | Duplicates *names* only in B |
| **B — Utils eval toolkit** | `utils/evaluation/` | 24 | Legacy/broad eval helpers (`promotion_gauntlet`, `shadow_eval_pipeline`, KPI bridges) | Functional overlap with A; **no** imports from `system_learning/validators` |
| **C — Active validators** | `system_learning/validators/` | 7 | **Active** 06.2 structural validators on ingested events | Isolated — 0 cross-refs to A/B in source scan |

### Overlap verdict

| Pair | Relationship | W4 action |
|------|--------------|-----------|
| A ↔ B | Same layer (L6 passive); parallel implementations (`shadow_eval/pipeline.py` vs `utils/evaluation/shadow_eval_pipeline.py`) | **Defer consolidation** to post-W5 ADR; mark B as `legacy_parallel` in LAYER drift table |
| A/B ↔ C | Different surface law (passive vs active) | **No merge** — validators stay on active root |
| `promotion_gauntlet` (B) vs `shadow_eval/gauntlet` (A) | Semantic duplicate | Document; single owner TBD (likely active 06.7) |

---

## 4. Deferred actions (require Author-Gate if executed)

| ID | Action | Trigger | Est. blast |
|----|--------|---------|------------|
| D1 | `git mv` `promotion/` → active `system_learning/…` or post-W5 `L6_system_learning/…` | W5.3+ or dedicated ADR | Low (1 prod importer: `apps_lic`) |
| D2 | Consolidate `utils/evaluation/*` into `shadow_eval/` or vice versa | Post-W5 stabilization ADR | High (24 modules) |
| D3 | Nest root OTEL modules under `runtime_trace/` | Optional hygiene ADR | Medium (8+ fan-in on `otel_runtime_ingest`) |

---

## 5. W4 acceptance

| Criterion | Status |
|-----------|--------|
| ADG fan-in recorded for `promotion/` + key root modules | ✅ [l6_w4_adg_fanin_20260525.json](l6_w4_adg_fanin_20260525.json) |
| Eval overlap map published | ✅ §3 above |
| No unauthorized file moves | ✅ map-only |
| Passive `LAYER.md` updated with drift appendix | ✅ |

---

## Next wave

**W5** — Physical rename (`PATH_RENAME_CANONICAL`): requires Author-Gate, W5.0 preflight (blast-radius regen, `system_learning/chapters` audit), then W5.1–W5.3.
