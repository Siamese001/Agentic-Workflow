# Resume Generation — Full Layer Integration Audit

**Date**: 2026-02-14
**Target**: `apps_rg/scripts/generate_resume.py`
**Objective**: Ensure resume generation leverages all agentic_core layers L0–L7

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


## Executive Summary

`generate_resume.py` currently runs in **complete isolation** from `agentic_core`. It instantiates a `SovereignContext` with a dumb buffer, calls `ResumeOrchestratorEngine.execute()`, and saves JSON. **Zero agentic_core layers are invoked.** The pipeline is deterministic, memoryless, and has no adaptive capability.

### Current Call Chain (What Runs Today)
```
generate_resume.py
  └─ SovereignContext()          # Simple dict buffer + list trace
  └─ ResumeOrchestratorEngine    # apps_rg L3-like orchestrator (NOT agentic_core L3)
       ├─ ClerkExtractionEngine   # HOP-1: Extract resume sections
       ├─ DataEnrichmentEngine    # HOP-2: Enrich with JD keywords
       ├─ GapClosureEngine        # HOP-3: Generate missing content
       ├─ ContentOptimizerEngine  # HOP-4a: Optimize content
       ├─ SectionRankerEngine     # HOP-4b: Rank sections by relevance
       ├─ ContentQualityEngine    # HOP-5a: Quality check
       └─ ATSCompatibilityEngine  # HOP-5b: ATS validation
```

**Layers touched**: NONE from agentic_core. All execution is in `apps_rg/engines/`.

---

## Layer-by-Layer Gap Analysis

### L0 — Routing (`agentic_core/L0_routing/`)

| Component | File | Purpose | Resume Gen Integration |
|-----------|------|---------|----------------------|
| `RootCustomsAgent` | `reasoning/RootCustomsAgent.py` | AST-powered input classification & file routing | Classify JD type (technical/executive/hybrid), route to specialized pipeline |
| Layer entry decorators | `enforcement/` | `@layer_entry` enforcement | Wrap HOP engines with layer boundary enforcement |

**Current usage**: ❌ None
**Gap**: No input classification. All JDs processed identically regardless of role type (engineering vs. executive vs. hybrid). No routing intelligence.

**Integration point**: Before HOP-1, run JD through L0 to classify:
- Role archetype (technical IC, people manager, executive, hybrid)
- Industry vertical (fintech, FAANG, startup, consulting)
- Seniority level (IC3-IC7, M1-M3, Director, VP, C-suite)
- This classification feeds L1 reasoning strategy selection

---

### L1 — Cognition (`agentic_core/L1_cognition/`)

| Component | File | Purpose | Resume Gen Integration |
|-----------|------|---------|----------------------|
| `CognitiveNode` | `engines/CognitiveNode.py` | Full pipeline: Perception → Reasoning → Planning → Action | Central cognitive loop for resume strategy |
| `PerceptionNode` | `engines/perception_engine.py` | Input parsing, intent classification, memory retrieval | Parse JD requirements, classify intent, retrieve similar past JDs |
| `ReasoningNode` | (in CognitiveNode) | Adaptive strategy: CoT / ToT / ReAct / Reflection | Select reasoning approach per HOP based on complexity |
| `PlanningCoordinator` | (in CognitiveNode) | Create action plans from reasoning | Plan which sections to emphasize, what to cut |
| `MetaLearningAgent` | `reasoning/MetaLearningAgent.py` | Strategy weight learning via experience replay | Learn which strategies produce best resumes over time |
| `SemanticMemory` | `memory/SemanticMemory.py` | Pattern recall from past experiences | Recall what worked for similar JDs |
| `perception_engine.py` | `engines/perception_engine.py` | Sub-atomic input processing | Parse JD into structured requirements |
| `pitch_engine.py` | `engines/pitch_engine.py` | Pitch/narrative generation | Generate resume narrative arc |
| `strategist_bio_writer.py` | `engines/strategist_bio_writer.py` | Bio/summary writing | Write executive summary tailored to JD |

**Current usage**: ❌ None
**Gap**: This is the **biggest miss**. No adaptive reasoning, no learning from past generations, no semantic memory of what worked before. Every resume generation starts from zero.

**Integration points**:
1. `PerceptionNode.process()` — Parse JD into structured requirements before HOP-1
2. `CognitiveNode.process_async()` — Run full cognitive pipeline for each HOP decision
3. `MetaLearningAgent.store_experience()` — After generation, record what strategy was used and quality score
4. `MetaLearningAgent.get_strategy_bias()` — Before each HOP, get learned strategy weights
5. `MetaLearningAgent.replay_and_learn()` — Periodically update strategy weights from experience buffer
6. `SemanticMemory.query()` — Retrieve patterns from similar past JDs
7. `pitch_engine` / `strategist_bio_writer` — Generate executive summary section

---

### L2 — Execution (`agentic_core/L2_execution/`)

| Component | File | Purpose | Resume Gen Integration |
|-----------|------|---------|----------------------|
| `UnifiedWorkflowEngine` | `config/unified_workflow_config.py` | Coordinator dispatch (8 mission focuses) | Dispatch each HOP to appropriate coordinator |
| `ReasoningCoordinator` | (in above) | Reasoning-focused missions | JD analysis, gap identification |
| `ExecutionCoordinator` | (in above) | Tool/action execution | Resume section generation |
| `SafetyCoordinator` | (in above) | Safety/guardrails | ATS compliance, content policy |
| `ValidationCoordinator` | (in above) | Compliance/integrity | Quality validation |
| `OptimizationCoordinator` | (in above) | Performance/efficiency tuning | Content optimization |

**Current usage**: ❌ None
**Gap**: All HOPs use the same execution pattern. No coordinator specialization.

**Integration point**: Replace `_run_engine()` with `UnifiedWorkflowEngine.orchestrate()`:
- HOP-1 (Extraction) → `ExecutionCoordinator`
- HOP-2 (Enrichment) → `ReasoningCoordinator` (needs JD analysis)
- HOP-3 (Gap Closure) → `ReasoningCoordinator` (needs creative generation)
- HOP-4 (Optimization) → `OptimizationCoordinator`
- HOP-5 (Validation) → `ValidationCoordinator` + `SafetyCoordinator`

---

### L3 — Orchestration (`agentic_core/L3_orchestration/`)

| Component | File | Purpose | Resume Gen Integration |
|-----------|------|---------|----------------------|
| `NervousSystemAgent` | `reasoning/NervousSystemAgent.py` | Master orchestrator: MISSION→SCENE→THINK→ACT→OBSERVE | **Should BE the orchestrator** instead of ResumeOrchestratorEngine |
| `RLOrchestratorAgent` | `enforcement/rl_strategy.py` | RL-learned phase ordering | Learn optimal HOP ordering |
| `AgentFactory` | `engines/AgentFactory.py` | Dynamic agent instantiation | Instantiate HOP engines dynamically |
| `DomainPlannerAgent` | `reasoning/DomainPlannerAgent.py` | Domain-specific planning | Plan resume generation strategy |
| `DAGManager` | `engines/dag_manager.py` | DAG-based execution | Model HOP dependencies as DAG |

**Current usage**: ❌ None. `ResumeOrchestratorEngine` is a **parallel reimplementation** of what `NervousSystemAgent` already provides.
**Gap**: The most critical architectural gap. `NervousSystemAgent` integrates L1 cognition, L4 state, L5 safety, L6 observability, and RL-learned orchestration in a single 5-step cycle. `ResumeOrchestratorEngine` is a flat sequential loop.

**Integration point**: Run resume generation as a **mission through NervousSystemAgent**:
```python
nervous_system = NervousSystemAgent(
    cognitive_plane=...,   # L1 CognitiveNode
    action_plane=...,      # HOP engines as actions
    config=OrchestratorConfig(mission_id="resume_gen_001")
)
result = await nervous_system.run_mission({
    "type": "resume_generation",
    "job_description": jd_data,
    "master_resume": resume_data,
})
```

The 5-step cycle maps to resume generation:
1. **MISSION** — "Generate customized resume for JD X"
2. **SCENE** — Gather context: JD requirements, resume data, past similar JDs
3. **THINK** — Plan: which sections to emphasize, what strategy per section
4. **ACT** — Execute: run HOP engines (extraction → enrichment → generation → optimization)
5. **OBSERVE** — Evaluate: quality score, ATS compatibility, feed back to meta-learner

---

### L4 — State (`agentic_core/L4_state/`)

| Component | File | Purpose | Resume Gen Integration |
|-----------|------|---------|----------------------|
| `CheckpointManagerAgent` | `reasoning/CheckpointManagerAgent.py` | State persistence, mirroring, recovery | Save/resume generation sessions |
| `VerifiableCheckpointManager` | `memory/verifiable_checkpoint_manager.py` | Integrity-verified checkpoints | Checkpoint after each HOP |
| `SignalLedger` | (via NervousSystem) | Signal tracking | Track generation signals |
| `SovereignReasoningMemoryLedger` | `memory/sovereign_reasoning_memory_ledger.py` | Reasoning memory | Remember reasoning for each section choice |
| `SemanticCacheManager` | `memory/semantic_cache_manager.py` | Semantic caching | Cache JD analysis results |
| `PineconeSovereignAgent` | `reasoning/PineconeSovereignAgent.py` | Long-term vector memory | Store/retrieve resume generation patterns |
| `RedisSovereignAgent` | `reasoning/RedisSovereignAgent.py` | Short-term cache | Cache intermediate HOP results |

**Current usage**: ❌ None. `SovereignContext` uses a simple Python dict (`SimpleBuffer`) with no persistence.
**Gap**: Zero state persistence. Every generation starts from scratch. No caching of JD analysis. No checkpoint/recovery if generation fails mid-pipeline. No long-term memory of what worked.

**Integration points**:
1. `CheckpointManagerAgent.create_checkpoint()` — After each HOP, save state
2. `SemanticCacheManager` — Cache JD analysis so similar JDs are faster
3. `PineconeSovereignAgent` — Store successful resume patterns in vector DB for recall
4. `RedisSovereignAgent` — Short-term cache for active generation session
5. `SovereignReasoningMemoryLedger` — Record why each section was included/excluded

---

### L5 — Safety (`agentic_core/L5_safety/`)

| Component | File | Purpose | Resume Gen Integration |
|-----------|------|---------|----------------------|
| `GovernanceAgent` | `validators/GovernanceAgent.py` | Policy enforcement | Enforce content policies |
| `L5SafetyExerciserAgent` | `reasoning/L5SafetyExerciserAgent.py` | Safety validation probes | Validate resume content safety |
| Hallucination guardrails | Various | Prevent fabricated content | Prevent metric fabrication |
| Budget enforcement | `L1_cognition/enforcement/budget_enforcer.py` | Cost/token limits | Limit LLM token spend per generation |

**Current usage**: ❌ None. `apps_rg` has its own `HallucinationDetector` but it's not wired to L5.
**Gap**: No content policy enforcement from the infrastructure layer. No cost guardrails. No governance audit trail.

**Integration points**:
1. `GovernanceAgent` — Validate generated content doesn't violate policies
2. Budget enforcer — Cap LLM API spend per resume generation
3. Wire `apps_rg/engines/hallucination_detector.py` through L5 safety layer
4. Content guardrails: no fabricated metrics, no fake company names, no hallucinated skills

---

### L6 — Observability (`agentic_core/L6_observability/`)

| Component | File | Purpose | Resume Gen Integration |
|-----------|------|---------|----------------------|
| `DashboardGenerator` | `dashboards/dashboard_generator.py` | SSOT dashboard generation | Track resume generation metrics |
| Telemetry/tracing | Various | Span tracing, metrics | Trace each HOP latency and quality |

**Current usage**: ❌ None. `apps_rg` has its own `TraceRegistry` but it's disconnected from L6.
**Gap**: No cross-run observability. No dashboard showing generation quality over time. No latency tracking.

**Integration points**:
1. Wire `TraceRegistry` into L6 telemetry pipeline
2. Emit metrics: generation time, quality score, ATS pass rate, retry count
3. Dashboard showing: success rate by JD type, average quality score, most common issues

---

### L7 — Meta-Learning (`agentic_core/L7_meta_learning/`)

| Component | File | Purpose | Resume Gen Integration |
|-----------|------|---------|----------------------|
| `MetaLearningProposalArtifact` | `types/meta_learning_types.py` | Propose strategy changes | Propose new HOP ordering or strategy |
| `MetaLearningEvaluationArtifact` | (in above) | Evaluate proposals | A/B test generation strategies |
| `MetaLearningApprovalArtifact` | (in above) | Approve/reject changes | Approve strategy updates |
| `MetaLearningDecisionArtifact` | (in above) | Record decisions | Audit trail of strategy evolution |
| `MetaLearningChangePackageArtifact` | (in above) | Package approved changes | Deploy improved strategies |
| Experience replay types | `types/offline_replay_types.py` | Offline learning | Learn from batch of past generations |
| Rollout types | `types/rollout_types.py` | Strategy rollouts | Gradually roll out improved strategies |

**Current usage**: ❌ None
**Gap**: No learning loop. Every generation uses the same fixed logic. No ability to improve over time based on results.

**Integration points**:
1. After each generation, create `MetaLearningProposalArtifact` if quality < threshold
2. Store generation outcomes for offline replay
3. Propose strategy changes: "For executive JDs, emphasize leadership section first"
4. Evaluate proposals against baseline
5. Approve/reject and deploy via rollout

---

## Recommended Integration Architecture

```
generate_resume.py (Entry Point)
│
├─ L0: RootCustomsAgent.classify_jd()
│    → JD archetype, industry, seniority
│
├─ L3: NervousSystemAgent.run_mission()  ← REPLACES ResumeOrchestratorEngine
│    │
│    ├─ MISSION: Define resume generation goal
│    │
│    ├─ SCENE (L1 Perception):
│    │    ├─ PerceptionNode: Parse JD → structured requirements
│    │    ├─ SemanticMemory: Recall similar past JDs
│    │    └─ MetaLearningAgent: Get strategy bias
│    │
│    ├─ THINK (L1 Reasoning + L2 Coordination):
│    │    ├─ CognitiveNode: Plan section emphasis
│    │    ├─ UnifiedWorkflowEngine: Select coordinator per HOP
│    │    └─ RLOrchestratorAgent: Optimize HOP ordering
│    │
│    ├─ ACT (apps_rg HOP Engines via L2 Execution):
│    │    ├─ HOP-1: ClerkExtractionEngine     [ExecutionCoordinator]
│    │    ├─ HOP-2: DataEnrichmentEngine       [ReasoningCoordinator]
│    │    ├─ HOP-3: GapClosureEngine           [ReasoningCoordinator]
│    │    ├─ HOP-4: ContentOptimizer + Ranker  [OptimizationCoordinator]
│    │    └─ HOP-5: Quality + ATS              [ValidationCoordinator]
│    │    Each HOP:
│    │      ├─ L4: CheckpointManager.save() after completion
│    │      ├─ L5: GovernanceAgent.validate() content
│    │      └─ L6: Telemetry.emit() span trace
│    │
│    └─ OBSERVE (L1 Meta-Learning + L6 Observability):
│         ├─ MetaLearningAgent.store_experience()
│         ├─ L6 Dashboard: Emit final metrics
│         └─ L7: MetaLearningProposalArtifact if quality < threshold
│
├─ L4: CheckpointManager.save_final() — Persist complete generation
├─ L4: PineconeSovereignAgent.store() — Store in vector DB for recall
└─ Output: generated_resume.json
```

---

## Implementation Priority

| Priority | Layer | Effort | Impact | Description |
|----------|-------|--------|--------|-------------|
| **P0** | L3 | High | Critical | Wire through `NervousSystemAgent` as mission orchestrator |
| **P1** | L1 | Medium | High | Integrate `CognitiveNode` + `MetaLearningAgent` for adaptive reasoning |
| **P2** | L4 | Medium | High | Add `CheckpointManager` for state persistence + `SemanticCache` |
| **P3** | L5 | Low | Medium | Wire hallucination detection through L5 `GovernanceAgent` |
| **P4** | L2 | Low | Medium | Use `UnifiedWorkflowEngine` coordinator dispatch |
| **P5** | L0 | Low | Medium | Add JD classification via `RootCustomsAgent` |
| **P6** | L6 | Low | Medium | Wire tracing into L6 observability pipeline |
| **P7** | L7 | Low | High (long-term) | Meta-learning proposal/evaluation loop |

---

## Blockers & Prerequisites

1. **NervousSystemAgent** has complex dependencies (L4 storage adapter, L5 safety layer, SignalLedger). Need to verify these can be instantiated for resume gen context.
2. **MetaLearningAgent** extends `SovereignBaseAgent` which requires mixin chain. Need to verify MRO works when used from apps_rg.
3. **SemanticMemory** may require Pinecone/Redis connections. Need fallback for local-only mode.
4. **Budget enforcer** requires LLM API configuration. Currently HOPs don't call LLMs (placeholder logic).
5. **L7 meta_learning types** import from `L0_routing.types.v15_p2_types` — verify this chain resolves.

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

