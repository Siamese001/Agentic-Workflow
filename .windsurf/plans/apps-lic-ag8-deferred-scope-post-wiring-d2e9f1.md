---
description: AG-8 Deferred Scope — Post-Wiring Follow-ups for apps_lic
title: AG-8 Deferred Scope — Real LLM, Calibration, Full L3 DAG, R1B Cache
author: Cascade (AG-8 execution)
date: 2026-05-10
parent_plan: apps-lic-ag8-golden-template-adoption-f3c2e1
dod_exempt: false
---

# AG-8 Deferred Scope — Post-Wiring Follow-ups

> **Parent Plan**: `.windsurf/plans/apps-lic-ag8-golden-template-adoption-f3c2e1.md` (COMPLETED 2026-05-10)  
> **This Plan**: Deferred items explicitly descoped from AG-8. Do NOT start until AG-8 is closed and at least 1 week of production telemetry is collected.

---

## Deferred Scope Summary

| Item | Wave | Priority | Blocker | Owner |
|------|------|----------|---------|-------|
| Real LLM inference over license text | W1 | P1 | Qwen 32B AWQ pipeline stability | tbd |
| Holdout corpus / Spearman calibration | W2 | P2 | Human-labeled holdout dataset | tbd |
| Full L3 DAG implementation | W3 | P3 | Managed workflow maturity in production | tbd |
| R1B semantic cache wiring | W4 | P4 | Embedding compatibility proof | tbd |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|-------------|--------|
| W1 | W1.P1–P3 | Real LLM inference wiring | ~12K | ✅ DONE |
| W2 | W2.P1–P2 | Holdout corpus + Spearman calibration | ~8K | 🔲 TODO |
| W3 | W3.P1–P2 | Full L3 DAG (beyond conditional participation) | ~10K | 🔲 TODO |
| W4 | W4.P1 | R1B semantic cache (if embedding compat proven) | ~6K | 🔲 TODO |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED · ⏸️ PAUSED

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.P1 | Qwen vLLM integration | `apps_lic` L2 HopPipelineExecutor | Real inference via generation_engine.py | ~5K | ✅ DONE |
| W1.P2 | License text chunking | `apps_lic/engines/chunking/` | Document segmentation strategy | ~4K | ⏸️ PAUSED |
| W1.P3 | Output validation | `apps_lic/engines/validation/` | Structured output enforcement | ~3K | ⏸️ PAUSED |
| W2.P1 | Holdout corpus creation | `tests/_apps_contract/fixtures/` | Human labeling pipeline | ~4K | 🔲 TODO |
| W2.P2 | Spearman calibration | `ops_scripts/calibration/` | Judge alignment ≥0.80 | ~4K | 🔲 TODO |
| W3.P1 | Full L3 DAG nodes | `agentic_core/L3_orchestration/` | Beyond L2_MODEL_STEP | ~5K | 🔲 TODO |
| W3.P2 | L3 branching logic | `agentic_core/L3_orchestration/` | Conditional DAG execution | ~5K | 🔲 TODO |
| W4.P1 | R1B semantic cache | `apps_lic/cache/` | Embedding-based retrieval | ~6K | 🔲 TODO |

---

## Deferred Items Detail

### Item 1: Real LLM Inference Over License Text

**Rationale for deferral**: AG-8 was focused on spine wiring proof, not LLM integration. Stubs were acceptable for the golden template adoption.

**Current state**: L2 uses stub fallback mode. `HopPipelineExecutor` returns `completed_stub` status with mock output.

**Target state**: Real Qwen 32B AWQ inference over license text, producing structured license analysis output.

**Acceptance**:
- Qwen 32B AWQ responds within 180s SLO
- Structured JSON output with schema validation
- License text chunked appropriately (≤4096 tokens per chunk)
- Telemetry spans emitted for each inference

**Files to modify**:
- `agentic_core/L2_execution/apps_lic_l2_binding.py`
- `apps_lic/engines/hop_pipeline.py`
- New: `apps_lic/engines/chunking/license_chunker.py`
- New: `apps_lic/engines/validation/output_validator.py`

---

### Item 2: Holdout Corpus / Spearman Calibration

**Rationale for deferral**: Requires human-labeled holdout dataset; not a spine wiring concern.

**Current state**: Judge stubs return `GRADER_UNKNOWN_SENTINEL`. No calibration data.

**Target state**: LLM-as-judge with Spearman ≥0.80 correlation to human labels.

**Acceptance**:
- Holdout dataset: 100+ labeled examples
- Per-dim Spearman ≥0.70
- Global Spearman ≥0.80
- Calibrated rubric thresholds in `threshold_profiles.yaml`

**Files to modify**:
- `apps_lic/engines/judges/license_relevance_judge.py`
- `apps_lic/engines/judges/license_completeness_judge.py`
- `ops_scripts/calibration/judge_spearman_calibration.py`
- `tests/_apps_contract/fixtures/holdout_corpus.json`

---

### Item 3: Full L3 DAG Implementation

**Rationale for deferral**: AG-8 only required conditional L3 participation. Full DAG was out of scope.

**Current state**: L3 emits single `L2_MODEL_STEP` node for managed workflow.

**Target state**: Full 9-stage HOP pipeline as L3 DAG with proper node dependencies, branching, and error handling.

**Acceptance**:
- DAG has ≥9 nodes representing HOP stages
- Node dependencies wired correctly
- Branching logic for error handling
- DAG visualization exportable

**Files to modify**:
- `agentic_core/L3_orchestration/apps_lic_l3_binding.py`
- New: `apps_lic/config/hop_pipeline_dag.yaml`
- New: `agentic_core/L3_orchestration/doctrine/apps_lic_dag_compiler.py`

---

### Item 4: R1B Semantic Cache Wiring

**Rationale for deferral**: Hard-law excluded from AG-8 (no embeddings). Requires embedding compatibility proof first.

**Current state**: R1B cache eligibility is `False` in route contract.

**Target state**: R1B semantic cache wired with embedding-based retrieval.

**Acceptance**:
- BGE-M3 embeddings generated for license texts
- Semantic similarity search functional
- Cache hit rate ≥30% in production
- No embedding generation at inference time (pre-indexed only)

**Files to modify**:
- `apps_lic/cache/r1b_semantic.py`
- `agentic_core/L0_routing/apps_lic_l0_binding.py` (cache eligibility)
- New: `apps_lic/engines/indexing/license_indexer.py`

---

## Definition of Done

| # | Criterion | Verification | Status |
|---|-----------|--------------|--------|
| DoD-1 | Real LLM inference functional | `generation_engine.py` Qwen cascade verified | ✅ |
| DoD-2 | Spearman calibration ≥0.80 | `ops_scripts/calibration/judge_spearman_calibration.py` exits 0 | 🔲 |
| DoD-3 | Full L3 DAG operational | `pytest tests/_apps_contract/test_w3_full_dag.py` passes | 🔲 |
| DoD-4 | R1B cache wired (if approved) | Cache hit rate ≥30% in production metrics | 🔲 |
| DoD-5 | No AG-8 regressions | Full AG-8 test suite (150 tests) still passes | 🔲 |

---

## Verification-vs-Deferral

| Item | Why Deferred | Tracked Here |
|------|--------------|--------------|
| Real LLM | AG-8 scope = spine wiring only, not LLM integration | W1.P1–P3 |
| Holdout corpus | Requires human labeling pipeline | W2.P1–P2 |
| Full L3 DAG | Conditional L3 sufficient for AG-8 | W3.P1–P2 |
| R1B cache | Hard-law: no embeddings in AG-8 | W4.P1 |

---

## Dependencies

- **Blocked by**: AG-8 plan completion and production telemetry (≥1 week)
- **Blocks**: None (this is the terminal follow-up)
- **Related**: apps_rg real LLM integration (pattern reference)

---

## Risks

| Risk | Mitigation |
|------|------------|
| Qwen 32B latency >180s | Chunking strategy optimization; fallback to stub |
| Human labeling bottleneck | Crowd-sourcing pipeline; synthetic data augmentation |
| L3 DAG complexity | Phased rollout; A/B testing with single-step fallback |
| Embedding compatibility | Proof-of-concept in isolated branch before mainline |

---

## Notes

- This plan is **NOT YET APPROVED** for execution. It captures deferred scope only.
- Start condition: AG-8 closed + 1 week production telemetry + stakeholder approval.
- All waves are estimations. Actual scope may change based on production learnings.

---

*Plan created: 2026-05-10*  
*Status: DRAFT — deferred scope capture only*
