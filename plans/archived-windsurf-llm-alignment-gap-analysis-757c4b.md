---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\llm-alignment-gap-analysis-757c4b.md'
original_relative_path: 'llm-alignment-gap-analysis-757c4b.md'
source_sha256: 42e31f72d8d841a0904c19352db2c4b1776e34c68cf77224babc4883b10b8e5d
recovered_status: LOST_RECOVERED
last_commit: '20f413ffbf5'
last_commit_date: '2026-04-01 14:39:03 -0400'
created_date: '2026-03-14'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RLHF & Supervised Fine-Tuning Gap Analysis

Redis hot-cache query (live, `adg:snapshot` digest `475fba08`, 8,141 nodes) shows RLHF optimizer and reward model modules exist in `L_SL` but are **islands — nobody calls them from outside L_SL, no SFT pipeline exists anywhere, and the feedback loop from LLM outputs back to training is completely absent**.

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


## What Redis Says EXISTS (RLHF-adjacent)

### `system_learning/engines/rlhf_optimizer.py` — L_SL

| Symbol | Imported by |
|---|---|
| `RLHFOptimizer` | `meta_learning_pipeline.py` (L_SL only) |
| `DefaultDeterministicRLHFOptimizer` | `pipeline_factory.py` (L_SL only) + 2 test files |

- The module file itself (`rlhf_optimizer.py`) is imported by **nobody** at module level
- `RLHFOptimizer` feeds into `meta_learning_pipeline` — but only within L_SL
- **No `covers` edges** on the module node itself

### `system_learning/engines/rlhf_optimizer_impl.py` — L_SL

- Contains `DefaultRLHFOptimizer`, `RLHFChangePackage`
- Imported by **nobody** (module level)
- All symbol importers are a single ADG test file only
- **No `covers` edges**

### `system_learning/engines/governance_reward_model.py` — L_SL

- Contains `GovernanceRewardModel`, `RewardModelConfig`, `score_proposal`
- `GovernanceRewardModel` imported only by `meta_learning_bus.py` (L_SL)
- `score_proposal` imported only by 2 test files
- Scores `cfg.weight_policy_compliance`, `s.policy_compliance` — **governance/policy scoring, not LLM output quality**
- **No `covers` edges** on module node

### `agentic_core/L6_observability/engines/hitl_dpo_pair_generator.py` — L6

- Has `produces_preference_pair` edge → `DPOPair`
- Imported by **nobody**
- No `covers` edges

### `agentic_core/utils/workflow_engines/dpo_batch_builder.py` — L_SHARED

- Has `builds_dpo_batch` → `DPOBatch` and `produces_preference_pair` → `DPOPair`
- Module imported by **nobody**
- All symbol importers are a single ADG test file
- No `covers` edges

### `system_learning/engines/meta_learning_bus.py` — L_SL

- Imports `GovernanceRewardModel` + `OptimizationProposalEngine`
- Has `builds_dpo_batch` edges (43 total in snapshot)
- **No `covers` edges** on module node
- This is the closest thing to an RLHF loop — but it scores *governance policy compliance*, not human preference alignment

---

## What is COMPLETELY ABSENT (Redis file index scan)

Every pattern returned **zero keys** in `adg:nodes:by_file:*`:

| Pattern | Meaning |
|---|---|
| `*sft*` | Supervised Fine-Tuning pipeline |
| `*fine_tun*` | Fine-tuning in any form |
| `*finetune*` | Fine-tuning in any form |
| `*trainer*` | Training loop / trainer class |
| `*training*` | Training data or training runner |
| `*feedback_collect*` | Human feedback collection |
| `*human_feedback*` | Human feedback ingestion |
| `*annotation*` | Labeling / annotation pipeline |

---

## Gap Diagnosis

### The Core Problem: The RLHF Loop Is Broken in 3 Places

```
[LLM generates output]
        │
        │  ← GAP 1: no feedback capture from live LLM outputs
        ▼
[Human/auto preference labeling]
        │
        │  ← GAP 2: no annotation / labeling pipeline exists
        ▼
[Preference dataset]  ←  hitl_dpo_pair_generator exists but is imported by NOBODY
        │
        │  ← GAP 3: dpo_batch_builder is imported by NOBODY;
        │            rlhf_optimizer_impl is imported by NOBODY
        ▼
[RLHF / SFT training]  ← no trainer, no training loop, no SFT pipeline
        │
        ▼
[Updated model weights]  ← no fine-tune infra, no model versioning
        │
        ▼
[SovereignLLMGateway]  ← existing, but receives no signal from the above
```

### The Reward Model Is Misaligned

`GovernanceRewardModel` scores **policy compliance** (whether an optimization proposal follows governance rules), not **LLM output quality / human preference**. This is a governance reward model, not an RLHF reward model. The naming conflates the two.

### `meta_learning_bus` is a Governance Loop, not an RLHF Loop

`meta_learning_bus.py` imports `GovernanceRewardModel` + `OptimizationProposalEngine` and builds DPO batches — but these are for *agentic code proposals* evaluated against governance policy, not for fine-tuning language model weights based on human preference feedback.

---

## Precise Gap Table

| RLHF/SFT Component | Status | Evidence |
|---|---|---|
| **Reward model (LLM output quality)** | **ABSENT** | `governance_reward_model` scores policy, not LLM output |
| **Human preference collection** | **ABSENT** | No `human_feedback`, `annotation`, `feedback_collect` files |
| **Preference dataset store** | **ABSENT** | `hitl_dpo_pair_generator` exists but wired to nobody |
| **DPO training batch pipeline** | **ABSENT** | `dpo_batch_builder` imported by nobody |
| **RLHF policy optimizer (weights)** | **ABSENT** | `rlhf_optimizer_impl` imported by nobody; no training runner |
| **SFT dataset builder** | **ABSENT** | Zero `sft`/`fine_tun`/`trainer` files |
| **SFT training loop** | **ABSENT** | Zero `training`/`trainer` files |
| **Feedback loop closure** | **ABSENT** | `SovereignLLMGateway` receives no signal from L_SL |
| **RLHF optimizer** (interface) | Partial | `RLHFOptimizer` in `meta_learning_pipeline` — L_SL internal only |
| **DPO pair types** | Partial | `dpo_types.py`, `BoundedDPOPair` exist in L6 |
| **Governance reward model** | Present | Scores policy compliance only — wrong domain |

---

## Implementation Plan

### Phase 1 — Human Preference Feedback Capture (~3 days)

These modules capture LLM output quality signals from live inference — the entry point of RLHF.

| # | New Module | Layer | Purpose |
|---|---|---|---|
| 1.1 | `system_learning/alignment/feedback_collector.py` | L_SL | Capture (prompt, chosen, rejected) triples from `SovereignLLMGateway` completions |
| 1.2 | `system_learning/alignment/preference_pair_types.py` | L_SL | Types: `HumanPreferencePair`, `AutoPreferencePair`, `FeedbackSource` |
| 1.3 | `system_learning/alignment/auto_labeler.py` | L_SL | Auto-label preference pairs using `GovernanceRewardModel` + heuristics |
| 1.4 | Wire `SovereignLLMGateway` → `feedback_collector` | L2 | Post-completion hook emits feedback event |

### Phase 2 — SFT Dataset Builder (~3 days)

No SFT infrastructure exists at all.

| # | New Module | Layer | Purpose |
|---|---|---|---|
| 2.1 | `system_learning/alignment/sft_dataset_builder.py` | L_SL | Build (instruction, response) pairs from accepted completions |
| 2.2 | `system_learning/alignment/sft_dataset_store.py` | L_SL | Persist SFT examples to structured store (JSONL) |
| 2.3 | `system_learning/alignment/sft_quality_filter.py` | L_SL | Filter by `governance_reward_model` score + dedup |
| 2.4 | `system_learning/alignment/sft_pipeline_runner.py` | L_SL | Orchestrator: collect → filter → write dataset |

### Phase 3 — Wire the DPO Batch Loop (~2 days)

`dpo_batch_builder` and `hitl_dpo_pair_generator` exist but are imported by nobody.

| # | Action | File | Purpose |
|---|---|---|---|
| 3.1 | Import `hitl_dpo_pair_generator` | `system_learning/alignment/feedback_collector.py` | Route preference pairs to HITL generator |
| 3.2 | Import `dpo_batch_builder` | `system_learning/alignment/sft_pipeline_runner.py` | Close DPO batch loop |
| 3.3 | Import `rlhf_optimizer_impl` | `system_learning/alignment/sft_pipeline_runner.py` | Wire `DefaultRLHFOptimizer` into pipeline |
| 3.4 | Extend `meta_learning_pipeline.py` | L_SL | Add alignment pipeline step alongside existing healing pipeline |

### Phase 4 — LLM-Quality Reward Model (~3 days)

`governance_reward_model` scores policy compliance. A separate LLM-output-quality reward model is needed.

| # | New Module | Layer | Purpose |
|---|---|---|---|
| 4.1 | `system_learning/alignment/llm_reward_model.py` | L_SL | Score LLM output on helpfulness, harmlessness, honesty |
| 4.2 | `system_learning/alignment/reward_model_types.py` | L_SL | Types: `LLMRewardScore`, `RewardDimension` (helpfulness/harmlessness/honesty) |
| 4.3 | `system_learning/alignment/reward_model_config.py` | L_SL | Config: dimension weights, score thresholds |

### Phase 5 — Tests (~2 days)

Each new module needs ADG `covers` edges. Minimum:

| Test File | Covers |
|---|---|
| `tests/unit/system_learning/alignment/test_feedback_collector.py` | Phase 1.1 |
| `tests/unit/system_learning/alignment/test_sft_dataset_builder.py` | Phase 2.1–2.3 |
| `tests/unit/system_learning/alignment/test_sft_pipeline_runner.py` | Phase 2.4 + 3.x |
| `tests/unit/system_learning/alignment/test_llm_reward_model.py` | Phase 4.1 |
| `tests/unit/system_learning/engines/test_rlhf_optimizer_impl.py` | Existing uncovered module |

After Phase 5: `python tools/adg/adg_redis_ingest.py --force`

---

## Execution Order

```
Phase 1  →  Phase 2  →  Phase 3  →  Phase 4  →  Phase 5
(capture)   (SFT data)  (wire DPO)  (reward)    (coverage)
```

Total: ~13 dev-days. Phase 3 has zero new files — it's pure wiring of existing dead modules.

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

