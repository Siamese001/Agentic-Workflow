# LLM Alignment Architecture Gap Analysis & Implementation Plan

Query of the ADG (8,141 nodes, 221,154 edges) reveals that RLHF, SFT, and related LLM alignment concepts are **partially present as surface-level terms but completely absent as first-class architectural abstractions**, with 4 critical dead-import seams in the LLM gateway layer.

---

## ADG Query Findings

### Concept Presence/Absence (PROD nodes only)

**ABSENT — zero nodes anywhere in prod:**
- Fine-Tuning / SFT
- Honesty constraint
- Safety Filter
- Toxicity Detection
- Uncertainty Estimation
- Refusal Policy
- Content Moderation
- Jailbreak Prevention

**PRESENT but shallow (term appears in names, not as dedicated abstractions):**

| Concept | Node Count | Notes |
|---|---|---|
| RLHF | 15 | Scattered across L_SL embedders + L5 DDD checks |
| Reward Modeling | 5 | Only in L_SL preference embedder names |
| DPO | 43 | Mostly test stubs, L0 routing types |
| PPO | 11 | Routing config only |
| Constitutional AI | 45 | `DDDAlignmentAgent` (L5) — DDD structural, NOT LLM constitutional AI |
| Preference Data | 31 | `path_d_preference_embedder` in L_SL |
| Guardrails | 172 | `guardrails_util.py` in L1 — **most mature alignment surface** |
| Human Feedback | 45 | Comments/doc strings, no dedicated module |
| Hallucination Detection | 17 | Scattered, no dedicated module |
| Grounding/Factuality | 12 | RAG orchestrator in L_PG |

> **Critical insight:** "alignment" in this codebase means *structural/DDD alignment* (file location, naming conventions), NOT LLM behavioral alignment. `DDDAlignmentAgent` validates domain-driven design rules, not model outputs.

---

### Existing LLM Infrastructure (foundation to build on)

**L2 Execution — LLM Gateway:**
- `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py` — single choke-point for all LLM calls
- `agentic_core/L2_execution/healers/qwen_vllm_inference.py` — local vLLM (Qwen) inference
- `agentic_core/L2_execution/healers/vllm_process_manager.py` — vLLM process lifecycle
- `agentic_core/L2_execution/types/llm_replay_types.py` — replay/determinism modes
- `agentic_core/L2_execution/types/vllm_*` — backpressure, serving profiles, token budgets

**L1 Cognition — closest existing alignment logic:**
- `agentic_core/L1_cognition/utils/guardrails_util.py` — runtime guardrails ✓
- `agentic_core/L1_cognition/utils/filter_inappropriate_content_util.py` — content filter ✓
- `agentic_core/L1_cognition/validators/truth_keeper_validator.py` — factuality ✓
- `agentic_core/L1_cognition/validators/dark_reasoning_visitor_validator.py` — dark reasoning detection ✓
- `agentic_core/L1_cognition/validators/semantic_gatekeeper_validator.py` ✓
- **Missing:** reward signal, preference collection, fine-tuning loop, RLHF trainer

**L5 Safety:**
- `agentic_core/L5_safety/reasoning/DDDAlignmentAgent.py` — structural, not behavioral alignment
- `agentic_core/L5_safety/types/heal_llm_seam_types.py` — LLM healing seam contracts

**L_SL System Learning (closest to RLHF infrastructure):**
- `system_learning/engines/path_d_preference_embedder.py` — `PathDPreferenceEmbedder` ✓
- `system_learning/engines/openai_embedder.py` — `OpenAIEmbedder`, `BGEEmbedder` ✓
- `system_learning/engines/prompt_outcome_embedder.py` — `PromptOutcomeEmbedder` ✓
- `system_learning/arbitration/engine.py` — arbitration engine ✓
- `system_learning/confidence/engine.py` — confidence scoring ✓

**L_PG Prompt Governance:**
- `agentic_core/knowledge/engine/rag_orchestrator.py` — `SovereignRagOrchestrator` ✓
- `agentic_core/prompt_governance/` — prompt contracts ✓

---

### Dead Import Seams (Broken LLM Wiring)

| Layer | File | Dead Symbol |
|---|---|---|
| L_RUNTIME | `agentic_core/runtime/exceptions/workflow_exceptions.py` | `LLMResponse` (core_contracts_types) |
| L_SHARED | `agentic_core/interfaces/execution_agents.py` | `EmbeddingSovereignAgent` |
| L_SHARED | `agentic_core/interfaces/gateway.py` | `SovereignLLMGateway` |
| L_TOOLS | `tools/canonical_hash.py` | `vllm_boundary_client.canonical_hash` |

The `interfaces/gateway.py` dead import of `SovereignLLMGateway` is most critical — the shared interface layer cannot reach the L2 gateway.

---

### LLM Import Fan-Out (Dependency Heat Map)

```
L2   → L2:          43 imports  (self-contained vLLM stack)
TOOLS→ L2:          15 imports
APP  → SHARED:       8 imports
SHARED→ L5:          7 imports
SHARED→ L2:          4 imports
L0   → L2:           2 imports
L3   → L2:           1 import
L1   → L2:           0 imports  ← L1 has NO direct LLM imports (all through L2 gateway)
```

L1 has zero direct LLM imports — cognition calls all route through L2 gateway. This is correct per layer gravity but means alignment logic must also route through L2.

---

## Gap Summary

### Tier 1 — Completely Absent (No Architecture Support)

1. **RLHF training loop** — No reward model, no human feedback collection, no policy gradient
2. **Supervised Fine-Tuning (SFT)** — No fine-tuning pipeline, dataset management, or training config
3. **Preference dataset collection** — `PathDPreferenceEmbedder` exists but no pipeline to generate/store preference pairs from live agent outputs
4. **Refusal policy engine** — No dedicated module decides when/how to refuse; `guardrails_util` is closest but rule-based only
5. **Safety classifier / content moderation** — `filter_inappropriate_content_util.py` exists but no toxicity model or moderation scorer
6. **Uncertainty/calibration** — No calibration layer on vLLM outputs; L_SL confidence scoring is internal arbitration, not model calibration
7. **Jailbreak / prompt injection defense** — `sovereign_precommit_no_raw_prompts_util.py` is pre-commit only; no runtime defense

### Tier 2 — Partial / Shallow (Needs Depth)

8. **Constitutional AI** — `DDDAlignmentAgent` does structural validation only; no principles-based self-critique loop
9. **Hallucination detection** — 17 nodes but no dedicated hallucination scorer; scattered logic
10. **Grounding** — `SovereignRagOrchestrator` provides retrieval but no grounding verifier against retrieved docs
11. **Human feedback integration** — `PromptOutcomeEmbedder` and `PathDPreferenceEmbedder` exist but no ingestion pipeline tying agent outputs → preference dataset → L_SL
12. **LLM gateway dead seams** — `interfaces/gateway.py` cannot reach `SovereignLLMGateway` (dead import must be fixed first)

---

## Implementation Plan

### Phase 0 — Fix Dead Seams (prerequisite, ~1 day)

| # | Action | File |
|---|---|---|
| 0.1 | Fix `SovereignLLMGateway` dead import | `agentic_core/interfaces/gateway.py` |
| 0.2 | Fix `EmbeddingSovereignAgent` dead import | `agentic_core/interfaces/execution_agents.py` |
| 0.3 | Fix `LLMResponse` dead import | `agentic_core/runtime/exceptions/workflow_exceptions.py` |
| 0.4 | Fix `vllm_boundary_client.canonical_hash` dead import | `tools/canonical_hash.py` |

### Phase 1 — L2 Alignment Seam (~3 days)

Add alignment hooks into `SovereignLLMGateway`:

| # | New Module | Purpose |
|---|---|---|
| 1.1 | `agentic_core/L2_execution/alignment/alignment_seam_types.py` | Types: `AlignmentSignal`, `RewardSignal`, `RefusalDecision` |
| 1.2 | `agentic_core/L2_execution/alignment/refusal_policy.py` | Pluggable refusal engine; wraps `guardrails_util` |
| 1.3 | `agentic_core/L2_execution/alignment/output_classifier.py` | Post-generation safety classification hook |
| 1.4 | `agentic_core/L2_execution/alignment/alignment_telemetry.py` | Emit alignment signals to L6 observability |
| 1.5 | Wire into `SovereignLLMGateway.py` | Pre/post-generation hooks call alignment seam |

### Phase 2 — L1 Cognition Alignment Validators (~2 days)

| # | New/Modified Module | Purpose |
|---|---|---|
| 2.1 | `agentic_core/L1_cognition/validators/hallucination_validator.py` | Grounding check against retrieved context |
| 2.2 | `agentic_core/L1_cognition/validators/uncertainty_validator.py` | Calibration/confidence threshold gate |
| 2.3 | `agentic_core/L1_cognition/utils/constitutional_filter_util.py` | Principles-based self-critique (extends DDD pattern) |
| 2.4 | Extend `guardrails_util.py` | Add toxicity scoring hook (pluggable classifier) |

### Phase 3 — L_SL Preference Pipeline (~4 days)

Connect existing embedders into a coherent feedback loop:

| # | New Module | Purpose |
|---|---|---|
| 3.1 | `system_learning/alignment/__init__.py` | New sub-package |
| 3.2 | `system_learning/alignment/preference_collector.py` | Capture agent output pairs for preference labeling |
| 3.3 | `system_learning/alignment/reward_model_client.py` | Interface to reward model (local or API) |
| 3.4 | `system_learning/alignment/sft_dataset_builder.py` | Build SFT training datasets from `PromptOutcomeEmbedder` |
| 3.5 | `system_learning/alignment/rlhf_signal_aggregator.py` | Aggregate preference signals → RLHF training batches |
| 3.6 | Wire `PathDPreferenceEmbedder` → `preference_collector` | Close the feedback loop |

### Phase 4 — L5 Safety Constitutional Layer (~2 days)

| # | New/Modified Module | Purpose |
|---|---|---|
| 4.1 | `agentic_core/L5_safety/reasoning/LLMAlignmentAgent.py` | New agent: behavioral (not DDD) alignment checks |
| 4.2 | `agentic_core/L5_safety/config/alignment_principles_config.py` | Constitutional principles registry |
| 4.3 | `agentic_core/L5_safety/validators/jailbreak_validator.py` | Runtime prompt injection / jailbreak defense |
| 4.4 | `agentic_core/L5_safety/validators/content_moderation_validator.py` | Toxicity/moderation scoring validator |

### Phase 5 — Tests & ADG Re-ingest (~2 days)

Minimum new test targets (all need ADG `covers` edges):
- `test_refusal_policy.py`
- `test_hallucination_validator.py`
- `test_preference_collector.py`
- `test_llm_alignment_agent.py`
- `test_jailbreak_validator.py`

After each phase: `python tools/adg/adg_redis_ingest.py --force` to refresh ADG.

---

## Layer Assignment Rationale

```
L2 Execution  → Gateway-level alignment seam (refusal, output classification)
L1 Cognition  → Reasoning-level validators (hallucination, uncertainty, constitutional)
L_SL          → Learning loop (preference collection, reward model, SFT dataset)
L5 Safety     → Enforcement-level alignment (constitutional principles, jailbreak)
L_PG          → Prompt governance (RAG grounding; extend for factuality verification)
```

All alignment logic must either:
1. **Pre-generation** — run in L1 validators before the LLM call, or
2. **Post-generation** — hook into L2 gateway's output pipeline

This respects existing layer-gravity rules: `L_APP → L_SHARED → L5 → L2 → L1 → L0`.
